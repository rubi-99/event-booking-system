from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.venue import Venue
from app.schemas.venue import VenueCreate, VenueUpdate
from app.repositories.venue_repository import VenueRepository

class VenueService:
    @staticmethod
    async def create_venue(db: AsyncSession, venue_data: VenueCreate) -> Venue:
        """
        Creates a new venue after validating there are no duplicates with the same name and location.
        """
        venues = await VenueRepository.get_all(db)
        for v in venues:
            if v.name.lower() == venue_data.name.lower() and v.location.lower() == venue_data.location.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A venue with this name and location already exists."
                )
        import uuid
        new_venue = Venue(
            id=uuid.uuid4(),
            name=venue_data.name,
            location=venue_data.location,
            capacity=venue_data.capacity
        )
        return await VenueRepository.create(db, new_venue)

    @staticmethod
    async def get_venue(db: AsyncSession, venue_id: UUID) -> Venue:
        """
        Fetches a venue by ID or raises HTTP 404.
        """
        venue = await VenueRepository.get_by_id(db, venue_id)
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venue not found."
            )
        return venue

    @staticmethod
    async def get_all_venues(db: AsyncSession) -> list[Venue]:
        """
        Fetches all venues.
        """
        return await VenueRepository.get_all(db)

    @staticmethod
    async def update_venue(db: AsyncSession, venue_id: UUID, venue_data: VenueUpdate) -> Venue:
        """
        Updates an existing venue.
        """
        venue = await VenueService.get_venue(db, venue_id)
        return await VenueRepository.update(db, venue, venue_data)

    @staticmethod
    async def delete_venue(db: AsyncSession, venue_id: UUID) -> None:
        """
        Deletes a venue.
        """
        venue = await VenueService.get_venue(db, venue_id)
        await VenueRepository.delete(db, venue)
