from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.models.event import Event
from app.schemas.event import EventCreate, EventUpdate
from app.enums.categories import EventCategory

class EventRepository:
    @staticmethod
    async def create(db: AsyncSession, event: Event) -> Event:
        """
        Inserts a new Event model instance into PostgreSQL and re-loads associated relationships.
        """
        event_id = event.id
        db.add(event)
        await db.commit()
        result = await db.execute(
            select(Event)
            .options(joinedload(Event.venue), joinedload(Event.organizer))
            .where(Event.id == event_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_id(db: AsyncSession, event_id: UUID) -> Event | None:
        """
        Fetches a single Event by UUID, eagerly loading associated venue and organizer profiles
        to prevent N+1 query loops.
        """
        result = await db.execute(
            select(Event)
            .options(joinedload(Event.venue), joinedload(Event.organizer))
            .filter(Event.id == event_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_all_events(
        db: AsyncSession,
        search_query: str = None,
        category: EventCategory = None,
        venue_id: UUID = None,
        status: str = "published"
    ) -> list[Event]:
        """
        Fetches a filterable list of all events (without pagination).
        """
        query = select(Event).options(joinedload(Event.venue), joinedload(Event.organizer))

        # Apply status filter
        if status:
            query = query.filter(Event.status == status)

        # Apply category filter
        if category:
            query = query.filter(Event.category == category)

        # Apply venue filter
        if venue_id:
            query = query.filter(Event.venue_id == venue_id)

        # Apply search query filter (matches title or description case-insensitively)
        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.filter(
                (Event.title.ilike(search_pattern)) | 
                (Event.description.ilike(search_pattern))
            )

        # Apply sorting (order by start_time ascending)
        query = query.order_by(Event.start_time.asc())

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update(db: AsyncSession, event: Event, event_data: EventUpdate) -> Event:
        """
        Updates specific attributes of an existing Event record.
        """
        update_data = event_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(event, key, value)
        event_id = event.id
        await db.commit()
        result = await db.execute(
            select(Event)
            .options(joinedload(Event.venue), joinedload(Event.organizer))
            .where(Event.id == event_id)
        )
        return result.scalars().first()

    @staticmethod
    async def delete(db: AsyncSession, event: Event) -> None:
        """
        Deletes an Event record.
        """
        await db.delete(event)
        await db.commit()
