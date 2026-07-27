from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.admin import DashboardStatsResponse, UserRoleUpdate
from app.schemas.event import EventResponse
from app.schemas.user import UserResponse
from app.services.admin_service import AdminService
from app.dependencies.auth import require_role
from app.enums.roles import UserRole
from app.models.user import User

# Lock all routes in this router behind Admin authorization by default
router = APIRouter(
    prefix="/admin",
    tags=["Admin Operations"],
    dependencies=[Depends(require_role([UserRole.ADMIN]))]
)

@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """
    Retrieves global platform statistics (Total users, Revenue, Tickets sold, Event status breakdown).
    Restricted to Admins.
    """
    return await AdminService.get_dashboard_stats(db)

@router.put("/users/{id}/role", response_model=UserResponse)
async def update_user_role(
    id: UUID,
    role_data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Updates the role of a user profile (e.g. promoting them to Organizer or Admin).
    Restricted to Admins.
    """
    return await AdminService.update_user_role(db, id, role_data.role)

@router.post("/events/{id}/cancel", response_model=EventResponse)
async def admin_cancel_event(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Force-cancels an event globally, automatically refunding all tickets purchased for it.
    Restricted to Admins.
    """
    return await AdminService.admin_cancel_event(db, id)
