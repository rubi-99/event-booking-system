from uuid import UUID
import uuid
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.event import Event
from app.models.booking import Booking
from app.enums.booking import BookingStatus
from app.repositories.booking_repository import BookingRepository
from app.repositories.event_repository import EventRepository

class BookingService:
    @staticmethod
    async def create_booking(db: AsyncSession, user_id: UUID, event_id: UUID, num_tickets: int) -> Booking:
        """
        Creates a new booking record using transaction-level pessimistic locking
        to prevent overbooking under high concurrent traffic.
        """
        from app.dependencies.lock import DistributedLock
        async with DistributedLock(f"event:{event_id}"):
            # 1. Lock the Event row in Postgres for the duration of this transaction
            stmt = select(Event).filter(Event.id == event_id).with_for_update()
            result = await db.execute(stmt)
            event = result.scalars().first()
            
            if not event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Event not found."
                )

            # 2. Verify booking rules
            if event.status != "published":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot book tickets for an event that is not published."
                )
                
            now = datetime.now(timezone.utc) if event.start_time.tzinfo else datetime.utcnow()
            if event.start_time < now:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot book tickets for an event that has already started."
                )

            # 3. Calculate tickets availability
            booked_tickets = await BookingRepository.get_booked_tickets_count(db, event_id)
            available_tickets = event.total_tickets - booked_tickets

            if num_tickets > available_tickets:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough tickets available. Requested: {num_tickets}, Available: {available_tickets}."
                )

            # 4. Calculate total price, set hold expiration, and build Booking instance
            total_price = event.ticket_price * num_tickets
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
            new_booking = Booking(
                id=uuid.uuid4(),
                user_id=user_id,
                event_id=event_id,
                num_tickets=num_tickets,
                total_price=total_price,
                status=BookingStatus.PENDING,
                expires_at=expires_at,
            )
            # Delegate persistence to the repository (thin DB layer)
            return await BookingRepository.create(db, new_booking)

    @staticmethod
    async def get_booking(db: AsyncSession, booking_id: UUID, user_id: UUID, is_admin: bool) -> Booking:
        """
        Fetches booking by ID with ownership checks.
        """
        booking = await BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found."
            )

        # Ownership check
        if not is_admin and booking.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this booking."
            )
            
        return booking

    @staticmethod
    async def cancel_booking(db: AsyncSession, booking_id: UUID, user_id: UUID, is_admin: bool) -> Booking:
        """
        Cancels a booking, restoring ticket inventory availability.
        """
        booking = await BookingService.get_booking(db, booking_id, user_id, is_admin)

        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This booking is already cancelled."
            )

        now = datetime.now(timezone.utc) if booking.event.start_time.tzinfo else datetime.utcnow()
        if booking.event.start_time < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel booking for an event that has already started."
            )

        booking.status = BookingStatus.CANCELLED
        return await BookingRepository.update(db, booking)

    @staticmethod
    async def confirm_booking(db: AsyncSession, booking_id: UUID, transaction_id: str | None = None) -> Booking:
        """
        Transitions a booking status from PENDING to CONFIRMED upon successful payment webhook payload.
        Sends confirmation email to the user.
        """
        from app.email import EmailMessage, send_email

        booking = await BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found."
            )

        if booking.status == BookingStatus.CONFIRMED:
            return booking

        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot confirm payment for a cancelled or expired booking."
            )

        booking.status = BookingStatus.CONFIRMED
        booking.expires_at = None
        updated_booking = await BookingRepository.update(db, booking)

        # Dispatch confirmation email
        user_email = updated_booking.user.email if updated_booking.user else "customer@example.com"
        event_title = updated_booking.event.title if updated_booking.event else "Event"
        email_msg = EmailMessage(
            to=user_email,
            subject=f"Confirmed: Tickets for {event_title}",
            html=f"<h3>Your booking is confirmed!</h3><p>Booking ID: {booking.id}</p><p>Tickets: {booking.num_tickets}</p><p>Total Paid: ${booking.total_price}</p>"
        )
        await send_email(email_msg)
        return updated_booking

    @staticmethod
    async def release_expired_bookings(db: AsyncSession) -> list[Booking]:
        """
        Finds all PENDING bookings where expires_at < NOW(), updates status to CANCELLED,
        releasing ticket holds, and dispatches hold-release notification emails.
        """
        from app.email import EmailMessage, send_email

        now = datetime.now(timezone.utc)
        stmt = (
            select(Booking)
            .filter(Booking.status == BookingStatus.PENDING)
            .filter(Booking.expires_at < now)
        )
        result = await db.execute(stmt)
        expired_bookings = list(result.scalars().all())

        for booking in expired_bookings:
            booking.status = BookingStatus.CANCELLED
            await BookingRepository.update(db, booking)

            user_email = booking.user.email if booking.user else "customer@example.com"
            event_title = booking.event.title if booking.event else "Event"
            email_msg = EmailMessage(
                to=user_email,
                subject=f"Expired: Reservation for {event_title}",
                html=f"<p>Your 10-minute hold for {booking.num_tickets} ticket(s) on {event_title} has expired and tickets have been released.</p>"
            )
            await send_email(email_msg)

        return expired_bookings

    @staticmethod
    async def refund_booking(db: AsyncSession, booking_id: UUID) -> Booking:
        """
        Refunds a booking. Restricted to Admins.
        """
        booking = await BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found."
            )

        if booking.status == BookingStatus.REFUNDED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This booking is already refunded."
            )

        booking.status = BookingStatus.REFUNDED
        return await BookingRepository.update(db, booking)
