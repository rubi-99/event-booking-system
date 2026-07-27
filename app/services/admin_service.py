from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.models.event import Event
from app.models.booking import Booking
from app.enums.roles import UserRole
from app.enums.booking import BookingStatus
from app.repositories.admin_repository import AdminRepository
from app.repositories.user_repository import UserRepository
from app.repositories.event_repository import EventRepository
from app.repositories.booking_repository import BookingRepository

class AdminService:
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> dict:
        """
        Retrieves global metrics for the admin console dashboard.
        """
        return await AdminRepository.get_global_stats(db)

    @staticmethod
    async def update_user_role(db: AsyncSession, user_id: UUID, new_role: UserRole) -> User:
        """
        Updates a user's role (e.g. promoting them to organizer or admin).
        """
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )
        
        user.role = new_role
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def admin_cancel_event(db: AsyncSession, event_id: UUID) -> Event:
        """
        Orchestrates an event cancellation by the system administration,
        automatically cascading cancellations and refunds to all confirmed bookings.
        """
        event = await EventRepository.get_by_id(db, event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found."
            )

        if event.status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event is already cancelled."
            )

        # 1. Update the parent Event status to cancelled
        event.status = "cancelled"

        # 2. Retrieve all active (confirmed and pending) bookings for this event and mark them refunded
        all_bookings = await BookingRepository.get_all_bookings(db, event_id=event_id)
        for booking in all_bookings:
            if booking.status in (BookingStatus.CONFIRMED, BookingStatus.PENDING):
                booking.status = BookingStatus.REFUNDED

        await db.commit()
        await db.refresh(event)
        return event
