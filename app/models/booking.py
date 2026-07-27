import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Numeric, ForeignKey, DateTime, Enum as SQLEnum
from uuid import UUID
from app.base import Base, TimestampMixin
from app.enums.booking import BookingStatus

class Booking(Base, TimestampMixin):
    __tablename__ = "bookings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_id: Mapped[UUID] = mapped_column(ForeignKey("events.id"), nullable=False)
    
    # Represents the total number of tickets booked in this transaction
    num_tickets: Mapped[int] = mapped_column(Integer, nullable=False)
    
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)  # price calculated at creation
    
    # Holds the datetime until which the ticket hold is valid (10‑minute window)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    status: Mapped[BookingStatus] = mapped_column(
        SQLEnum(BookingStatus, name="booking_status", native_enum=False),
        default=BookingStatus.PENDING,
        nullable=False
    )

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="bookings")
    user: Mapped["User"] = relationship("User", back_populates="bookings")
