from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.venue import Venue
from app.schemas.venue import VenueCreate, VenueUpdate

class VenueRepository:
    @staticmethod
    async def create(db: AsyncSession, venue: Venue) -> Venue:
        """
        Inserts a new Venue model instance into PostgreSQL.
        """
        db.add(venue)
        await db.commit()
        await db.refresh(venue)
        return venue

    @staticmethod
    async def get_by_id(db: AsyncSession, venue_id: UUID) -> Venue | None:
        """
        Fetches a single venue by its primary key UUID.
        """
        result = await db.execute(select(Venue).filter(Venue.id == venue_id))
        return result.scalars().first()

    @staticmethod
    async def get_all(db: AsyncSession) -> list[Venue]:
        """
        Fetches all venues in the database.
        """
        result = await db.execute(select(Venue))
        return list(result.scalars().all())

    @staticmethod
    async def update(db: AsyncSession, venue: Venue, venue_data: VenueUpdate) -> Venue:
        """
        Updates specific attributes of an existing Venue record.
        """
        update_data = venue_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(venue, key, value)
        await db.commit()
        await db.refresh(venue)
        return venue

    @staticmethod
    async def delete(db: AsyncSession, venue: Venue) -> None:
        """
        Deletes a Venue record.
        """
        await db.delete(venue)
        await db.commit()
