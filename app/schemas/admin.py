from pydantic import BaseModel
from decimal import Decimal
from app.enums.roles import UserRole

class UserRoleUpdate(BaseModel):
    role: UserRole

class EventStats(BaseModel):
    draft: int
    published: int
    cancelled: int

class DashboardStatsResponse(BaseModel):
    total_users: int
    total_revenue: Decimal
    total_tickets_sold: int
    events_breakdown: EventStats
