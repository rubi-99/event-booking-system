from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field

class WebhookPayload(BaseModel):
    booking_id: UUID
    status: str = Field(..., description="Payment status: payment_success or payment_failed")
    transaction_id: Optional[str] = Field(None, description="External payment provider reference ID")

class WebhookResponse(BaseModel):
    status: str
    message: str
    booking_id: UUID
