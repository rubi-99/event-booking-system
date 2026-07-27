from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.venue import VenueCreate, VenueUpdate, VenueResponse
from app.services.venue_service import VenueService
from app.dependencies.auth import get_current_user, require_role
from app.enums.roles import UserRole
from app.models.user import User

router = APIRouter(prefix="/venues", tags=["Venues"])

@router.post("", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
async def create_venue(
    venue_data: VenueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Creates a new venue. Restricted to Admins.
    """
    return await VenueService.create_venue(db, venue_data)

@router.get("/{id}", response_model=VenueResponse)
async def get_venue(id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Fetches a single venue by ID. Public access.
    """
    return await VenueService.get_venue(db, id)

@router.get("", response_model=list[VenueResponse])
async def get_all_venues(db: AsyncSession = Depends(get_db)):
    """
    Fetches all venues. Public access.
    """
    return await VenueService.get_all_venues(db)

@router.put("/{id}", response_model=VenueResponse)
async def update_venue(
    id: UUID,
    venue_data: VenueUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Updates an existing venue. Restricted to Admins.
    """
    return await VenueService.update_venue(db, id, venue_data)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_venue(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Deletes a venue. Restricted to Admins.
    """
    await VenueService.delete_venue(db, id)
