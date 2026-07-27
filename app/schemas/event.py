from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional
from app.enums.categories import EventCategory
from app.schemas.venue import VenueResponse
from app.schemas.user import UserResponse

class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)
    category: EventCategory
    event_poster_url: Optional[str] = Field(None, max_length=500)
    venue_id: UUID
    start_time: datetime
    end_time: datetime
    total_tickets: int = Field(..., gt=0)
    ticket_price: Decimal = Field(..., ge=0.0)
    status: str = Field("draft", max_length=20)

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[EventCategory] = None
    event_poster_url: Optional[str] = Field(None, max_length=500)
    venue_id: Optional[UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_tickets: Optional[int] = Field(None, gt=0)
    ticket_price: Optional[Decimal] = Field(None, ge=0.0)
    status: Optional[str] = Field(None, max_length=20)

class EventResponse(EventBase):
    id: UUID
    organizer_id: UUID
    created_at: datetime
    updated_at: datetime
    
    venue: Optional[VenueResponse] = None
    organizer: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
