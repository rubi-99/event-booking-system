import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from uuid import UUID
from app.base import Base, TimestampMixin

class Venue(Base, TimestampMixin):
    __tablename__ = "venues"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationship back-populating to events
    events: Mapped[list["Event"]] = relationship("Event", back_populates="venue")
