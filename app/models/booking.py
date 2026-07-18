from app.database.base import Base
from app.enums.booking_status import BookingStatus

from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String,UUID,ForeignKey,Enum,Integer,DateTime

import uuid
from datetime import datetime

class Booking(Base):

    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    event_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.id"),
        nullable=False
    )

    ticket_quantity : Mapped[int] = mapped_column(
        Integer,
        nullable=False,

    )
    total_price : Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    qr_code_token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    checked_in: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    status : Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus),
        nullable=False,
        default=BookingStatus.CONFIRMED
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )



    user : Mapped["User"] = relationship(
        back_populates="bookings"
    )

    event : Mapped["Event"] = relationship(
        back_populates="bookings"
    )