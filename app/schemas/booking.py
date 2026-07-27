from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional
from app.enums.booking import BookingStatus
from app.schemas.event import EventResponse
from app.schemas.user import UserResponse

class BookingBase(BaseModel):
    event_id: UUID
    num_tickets: int = Field(..., gt=0, description="Number of tickets to book must be greater than 0")

class BookingCreate(BookingBase):
    pass

class BookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    event_id: UUID
    num_tickets: int
    total_price: Decimal
    status: BookingStatus
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Optional eager relations
    event: Optional[EventResponse] = None
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
