from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.booking import BookingCreate, BookingResponse
from app.schemas.payment import WebhookPayload, WebhookResponse
from app.services.booking_service import BookingService
from app.repositories.booking_repository import BookingRepository
from app.dependencies.auth import get_current_user, require_role
from app.enums.roles import UserRole
from app.models.user import User

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new booking (purchasing tickets) for a published event.
    """
    return await BookingService.create_booking(
        db, current_user.id, booking_data.event_id, booking_data.num_tickets
    )

@router.post("/webhook", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
async def payment_webhook(
    payload: WebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Simulated Webhook endpoint for Stripe/Razorpay payment gateway callbacks.
    Transitions booking status from PENDING to CONFIRMED or CANCELLED based on payment status.
    """
    if payload.status == "payment_success":
        booking = await BookingService.confirm_booking(db, payload.booking_id, payload.transaction_id)
        return WebhookResponse(status="success", message="Booking confirmed", booking_id=booking.id)
    else:
        booking = await BookingService.cancel_booking(db, payload.booking_id, user_id=None, is_admin=True)
        return WebhookResponse(status="cancelled", message="Payment failed, booking cancelled", booking_id=booking.id)

@router.get("/my", response_model=list[BookingResponse])
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the ticket booking history of the authenticated user.
    """
    return await BookingRepository.get_all_bookings(db, user_id=current_user.id)

@router.get("/{id}", response_model=BookingResponse)
async def get_booking(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves booking details. Restricted to the owner or an Admin.
    """
    is_admin = current_user.role == UserRole.ADMIN
    return await BookingService.get_booking(db, id, current_user.id, is_admin)

@router.post("/{id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancels a booking, freeing event ticket inventory. Restricted to the owner or an Admin.
    """
    is_admin = current_user.role == UserRole.ADMIN
    return await BookingService.cancel_booking(db, id, current_user.id, is_admin)

@router.post("/{id}/refund", response_model=BookingResponse)
async def refund_booking(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Refunds a booking. Restricted to Admins.
    """
    return await BookingService.refund_booking(db, id)
