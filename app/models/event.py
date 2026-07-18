from database.base import Base
from app.enums.event_status import EventStatus
from app.enums.event_category import EventCategory


from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String,Enum,Integer,DateTime,UUID,Text,ForeignKey

from datetime import datetime
import uuid


class Event(Base):

    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4    
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    category : Mapped[EventCategory] = mapped_column(
        Enum(EventCategory),
        nullable=False,
    )

    description : Mapped[str | None] = mapped_column(
        Text,
        nullable=True

    )
    
    status : Mapped[EventStatus] = mapped_column(
        Enum(EventStatus),
        nullable=False,
        default=EventStatus.CREATED
    )

    price : Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0 
    )

    event_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )
    organizer_id : Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    venue : Mapped[str] = mapped_column(
        String(100),nullable=False
    )

    max_attendees : Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    registration_deadline : Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
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

#many event has one user
    organizer  : Mapped["User"]= relationship(
        back_populates="events"
    )

    bookings : Mapped[list["Booking"]] = relationship(
        back_populates="event"
    )


