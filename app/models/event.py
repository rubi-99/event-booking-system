import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Numeric, ForeignKey, DateTime, Index
from uuid import UUID
from app.base import Base, TimestampMixin
from app.enums.categories import EventCategory

class Event(Base, TimestampMixin):
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    
    # Store category as a string enum representation in the database
    category: Mapped[EventCategory] = mapped_column(
        String(50),
        nullable=False
    )
    event_poster_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    # Foreign Keys referencing venues and users tables
    venue_id: Mapped[UUID] = mapped_column(ForeignKey("venues.id"), nullable=False)
    organizer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Timezone-aware date fields
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Ticketing inventory & Pricing details
    total_tickets: Mapped[int] = mapped_column(Integer, nullable=False)
    ticket_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Status can be draft, published, cancelled
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)

    # Relationships with back_populates
    venue: Mapped["Venue"] = relationship("Venue", back_populates="events")
    organizer: Mapped["User"] = relationship("User", back_populates="events")
    bookings: Mapped[list["Booking"]] = relationship("Booking", back_populates="event")

# Compound index to speed up customer filtering queries
Index("idx_events_filter", Event.status, Event.category, Event.start_time)
