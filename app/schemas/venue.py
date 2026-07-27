from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

class VenueBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    location: str = Field(..., min_length=1, max_length=255)
    capacity: int = Field(..., gt=0, description="Capacity must be a positive integer")

class VenueCreate(VenueBase):
    pass

class VenueUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    capacity: Optional[int] = Field(None, gt=0)

class VenueResponse(VenueBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
