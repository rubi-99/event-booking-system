from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.models.booking import Booking
from app.models.event import Event
from app.enums.booking import BookingStatus

class BookingRepository:
    @staticmethod
    async def create(db: AsyncSession, booking: Booking) -> Booking:
        """Add a new Booking entity to the DB and return the refreshed instance with loaded relationships."""
        booking_id = booking.id
        db.add(booking)
        await db.commit()
        result = await db.execute(
            select(Booking)
            .options(
                joinedload(Booking.event).joinedload(Event.venue),
                joinedload(Booking.event).joinedload(Event.organizer),
                joinedload(Booking.user)
            )
            .where(Booking.id == booking_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_id(db: AsyncSession, booking_id: UUID) -> Booking | None:
        """
        Fetches a booking by its primary key UUID.
        """
        result = await db.execute(
            select(Booking)
            .options(
                joinedload(Booking.event).joinedload(Event.venue),
                joinedload(Booking.event).joinedload(Event.organizer),
                joinedload(Booking.user)
            )
            .filter(Booking.id == booking_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_all_bookings(db: AsyncSession, event_id: UUID = None, user_id: UUID = None) -> list[Booking]:
        """
        Fetches all bookings in the database, with optional filtering by event or user.
        """
        query = select(Booking).options(
            joinedload(Booking.event).joinedload(Event.venue),
            joinedload(Booking.event).joinedload(Event.organizer),
            joinedload(Booking.user)
        )
        if event_id:
            query = query.filter(Booking.event_id == event_id)
        if user_id:
            query = query.filter(Booking.user_id == user_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_confirmed_bookings(db: AsyncSession, event_id: UUID = None, user_id: UUID = None) -> list[Booking]:
        """
        Fetches confirmed bookings, with optional filtering by event or user.
        """
        query = select(Booking).options(
            joinedload(Booking.event).joinedload(Event.venue),
            joinedload(Booking.event).joinedload(Event.organizer),
            joinedload(Booking.user)
        ).filter(Booking.status == BookingStatus.CONFIRMED)
        if event_id:
            query = query.filter(Booking.event_id == event_id)
        if user_id:
            query = query.filter(Booking.user_id == user_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_cancelled_bookings(db: AsyncSession, event_id: UUID = None, user_id: UUID = None) -> list[Booking]:
        """
        Fetches cancelled bookings, with optional filtering by event or user.
        """
        query = select(Booking).options(
            joinedload(Booking.event).joinedload(Event.venue),
            joinedload(Booking.event).joinedload(Event.organizer),
            joinedload(Booking.user)
        ).filter(Booking.status == BookingStatus.CANCELLED)
        if event_id:
            query = query.filter(Booking.event_id == event_id)
        if user_id:
            query = query.filter(Booking.user_id == user_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_refunded_bookings(db: AsyncSession, event_id: UUID = None, user_id: UUID = None) -> list[Booking]:
        """
        Fetches refunded bookings, with optional filtering by event or user.
        """
        query = select(Booking).options(
            joinedload(Booking.event).joinedload(Event.venue),
            joinedload(Booking.event).joinedload(Event.organizer),
            joinedload(Booking.user)
        ).filter(Booking.status == BookingStatus.REFUNDED)
        if event_id:
            query = query.filter(Booking.event_id == event_id)
        if user_id:
            query = query.filter(Booking.user_id == user_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_booked_tickets_count(db: AsyncSession, event_id: UUID) -> int:
        """
        Sums up all active ticket reservations (CONFIRMED and PENDING holds) on a specific event.
        Returns 0 if no tickets have been booked yet.
        """
        result = await db.execute(
            select(func.sum(Booking.num_tickets))
            .filter(Booking.event_id == event_id)
            .filter(Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]))
        )
        count = result.scalar()
        return count if count is not None else 0

    @staticmethod
    async def update(db: AsyncSession, booking: Booking) -> Booking:
        """
        Commits updates made to a booking record.
        """
        booking_id = booking.id
        await db.commit()
        result = await db.execute(
            select(Booking)
            .options(
                joinedload(Booking.event).joinedload(Event.venue),
                joinedload(Booking.event).joinedload(Event.organizer),
                joinedload(Booking.user)
            )
            .where(Booking.id == booking_id)
        )
        return result.scalars().first()
