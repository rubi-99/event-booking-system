from uuid import UUID, uuid4
from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate
from app.repositories.event_repository import EventRepository
from app.repositories.venue_repository import VenueRepository
from app.enums.categories import EventCategory
import app.supabase
from app.config import settings

class EventService:
    @staticmethod
    async def create_event(db: AsyncSession, organizer_id: UUID, event_data: EventCreate) -> Event:
        """
        Creates a new event after checking date bounds, venue existence, and seat capacity.
        """
        # 1. Date window validation
        if event_data.end_time <= event_data.start_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event end_time must be strictly after start_time."
            )
        if event_data.start_time < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event start_time cannot be in the past."
            )

        # 2. Venue validation
        venue = await VenueRepository.get_by_id(db, event_data.venue_id)
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The selected Venue does not exist."
            )

        # 3. Seating Capacity validation
        if event_data.total_tickets > venue.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The event total tickets ({event_data.total_tickets}) cannot exceed the venue capacity ({venue.capacity})."
            )

        new_event = Event(
            id=uuid4(),
            title=event_data.title,
            description=event_data.description,
            category=event_data.category,
            event_poster_url=event_data.event_poster_url,
            venue_id=event_data.venue_id,
            organizer_id=organizer_id,
            start_time=event_data.start_time,
            end_time=event_data.end_time,
            total_tickets=event_data.total_tickets,
            ticket_price=event_data.ticket_price,
            status=event_data.status
        )
        created_event = await EventRepository.create(db, new_event)
        from app.redis import delete_cache_pattern
        await delete_cache_pattern("events:catalog:*")
        return created_event

    @staticmethod
    async def get_event(db: AsyncSession, event_id: UUID) -> Event:
        """
        Fetches an event by ID with Redis caching.
        """
        event = await EventRepository.get_by_id(db, event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found."
            )
        return event

    @staticmethod
    async def get_all_events(
        db: AsyncSession,
        search_query: str = None,
        category: EventCategory = None,
        venue_id: UUID = None,
        status: str = "published"
    ) -> list[Event]:
        """
        Fetches filterable catalog events.
        """
        return await EventRepository.get_all_events(
            db, search_query=search_query, category=category, venue_id=venue_id, status=status
        )

    @staticmethod
    async def update_event(
        db: AsyncSession,
        event_id: UUID,
        organizer_id: UUID,
        is_admin: bool,
        event_data: EventUpdate
    ) -> Event:
        """
        Updates an existing event with validation checks.
        """
        event = await EventService.get_event(db, event_id)

        # 1. RBAC Ownership check
        if not is_admin and event.organizer_id != organizer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this event."
            )

        # 2. Validate dates if modified
        start = event_data.start_time or event.start_time
        end = event_data.end_time or event.end_time
        if start and end and end <= start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event end_time must be strictly after start_time."
            )

        # 3. Validate venue & capacity if venue_id or total_tickets is changing
        venue_id = event_data.venue_id or event.venue_id
        total_tickets = event_data.total_tickets or event.total_tickets

        venue = await VenueRepository.get_by_id(db, venue_id)
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The selected Venue does not exist."
            )

        if total_tickets > venue.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"The event total tickets ({total_tickets}) cannot exceed the venue capacity ({venue.capacity})."
            )

        updated_event = await EventRepository.update(db, event, event_data)
        from app.redis import delete_cache, delete_cache_pattern
        await delete_cache(f"event:{event_id}")
        await delete_cache_pattern("events:catalog:*")
        return updated_event

    @staticmethod
    async def delete_event(db: AsyncSession, event_id: UUID, organizer_id: UUID, is_admin: bool) -> None:
        """
        Deletes an event.
        """
        event = await EventService.get_event(db, event_id)

        # RBAC Ownership check
        if not is_admin and event.organizer_id != organizer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this event."
            )

        await EventRepository.delete(db, event)
        from app.redis import delete_cache, delete_cache_pattern
        await delete_cache(f"event:{event_id}")
        await delete_cache_pattern("events:catalog:*")

    @staticmethod
    async def upload_event_poster(
        db: AsyncSession,
        event_id: UUID,
        organizer_id: UUID,
        is_admin: bool,
        file_name: str,
        file_bytes: bytes,
        content_type: str
    ) -> Event:
        """
        Uploads an image file to Supabase storage and associates the URL with the event.
        """
        event = await EventService.get_event(db, event_id)

        # RBAC Ownership check
        if not is_admin and event.organizer_id != organizer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this event."
            )

        # Generate a unique path inside the bucket to prevent name collisions
        file_extension = file_name.split(".")[-1] if "." in file_name else "jpg"
        unique_filename = f"{uuid4()}.{file_extension}"
        storage_path = f"events/{event_id}/{unique_filename}"

        # Upload the file using the Supabase helper
        try:
            public_url = app.supabase.upload_to_storage(
                bucket_name=settings.SUPABASE_STORAGE_BUCKET,
                file_path=storage_path,
                file_bytes=file_bytes,
                content_type=content_type
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image to Supabase Storage: {str(e)}"
            )

        # Update the event's event_poster_url field in the database
        event_update = EventUpdate(event_poster_url=public_url)
        updated = await EventRepository.update(db, event, event_update)
        from app.redis import delete_cache, delete_cache_pattern
        await delete_cache(f"event:{event_id}")
        await delete_cache_pattern("events:catalog:*")
        return updated
