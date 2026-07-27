from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate, TokenResponse, RoleUpdate
from app.dependencies.auth import require_role
from app.services.user_service import UserService
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.enums.roles import UserRole
from uuid import UUID
from app.supabase import supabase_client

# Instantiate the authentication router
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user profile. Authenticates with Supabase first,
    then saves user details locally in PostgreSQL.
    """
    return await UserService.register_user(db, user_data)

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user credentials. Returns a signed JWT access token
    from Supabase and their local database profile.
    """
    return await UserService.login_user(db, user_data.email, user_data.password)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve the authenticated user's profile metadata.
    """

    return current_user

@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the authenticated user's profile details.
    """
    return await UserService.update_profile(db, current_user.id, user_data)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Invalidates the active session on the authentication provider.
    """
    try:
        supabase_client.auth.sign_out()
        print("user logout--------------")
    except Exception:
        # Ignore errors if the session has already expired
        pass

@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: UUID,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Update a user's role. Restricted to Admins.
    """
    return await UserService.promote_user(db, user_id, role_data.role)
