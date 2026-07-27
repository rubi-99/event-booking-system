from uuid import UUID
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.services.event_service import EventService
from app.dependencies.auth import get_current_user, require_role
from app.enums.roles import UserRole
from app.enums.categories import EventCategory
from app.models.user import User

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ORGANIZER, UserRole.ADMIN]))
):
    """
    Creates a new event. Restricted to Organizers and Admins.
    """
    return await EventService.create_event(db, current_user.id, event_data)

@router.get("/{id}", response_model=EventResponse)
async def get_event(id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Fetches details of a single event by ID. Public access.
    """
    return await EventService.get_event(db, id)

@router.get("", response_model=list[EventResponse])
async def get_all_events(
    search_query: str = Query(None, description="Search term matching title or description"),
    category: EventCategory = Query(None, description="Filter by event category"),
    venue_id: UUID = Query(None, description="Filter by venue"),
    status: str = Query("published", description="Filter by status (default published)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches a list of events. Public access.
    By default, only published events are shown.
    """
    return await EventService.get_all_events(
        db, search_query=search_query, category=category, venue_id=venue_id, status=status
    )

@router.put("/{id}", response_model=EventResponse)
async def update_event(
    id: UUID,
    event_data: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ORGANIZER, UserRole.ADMIN]))
):
    """
    Updates an existing event. Restricted to the organizing user or an Admin.
    """
    is_admin = current_user.role == UserRole.ADMIN
    return await EventService.update_event(
        db, id, current_user.id, is_admin, event_data
    )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_event(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ORGANIZER, UserRole.ADMIN]))
):
    """
    Deletes an event. Restricted to the organizing user or an Admin.
    """
    is_admin = current_user.role == UserRole.ADMIN
    await EventService.delete_event(db, id, current_user.id, is_admin)

@router.post("/{id}/poster", response_model=EventResponse)
async def upload_event_poster(
    id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ORGANIZER, UserRole.ADMIN]))
):
    """
    Uploads an image file to serve as the event poster.
    Restricted to the organizing user or an Admin.
    """
    # 1. Enforce content-type mime-type limit (image/jpeg, image/png, image/webp)
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: '{file.content_type}'. Supported image formats: JPEG, PNG, WEBP."
        )

    # 2. Enforce file size limit (5MB = 5 * 1024 * 1024 bytes)
    max_size = 5 * 1024 * 1024
    file_bytes = await file.read()
    if len(file_bytes) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the maximum limit of 5MB."
        )

    is_admin = current_user.role == UserRole.ADMIN
    return await EventService.upload_event_poster(
        db=db,
        event_id=id,
        organizer_id=current_user.id,
        is_admin=is_admin,
        file_name=file.filename,
        file_bytes=file_bytes,
        content_type=file.content_type
    )
