from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.enums.roles import UserRole
from app.repositories.user_repository import UserRepository
from app.supabase import supabase_client
from supabase import AuthApiError

class UserService:
    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: UUID) -> User:
        """
        Business Rule: Retrieves a user profile by ID. 
        Raises HTTP 404 if profile does not exist.
        """
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        return user

    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
        """
        Business Rule: Signs up credentials with Supabase Auth,
        then calls the Repository layer to save metadata profile locally.
        """
        # 1. Register credentials in Supabase Auth
        try:
            auth_response = supabase_client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password
            })
        except AuthApiError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Authentication registration failed: {e.message}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication service error: {str(e)}"
            )

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user registration info."
            )

        supabase_user_id = UUID(auth_response.user.id)

        # 2. Override role — never trust client-provided role on signup
        user_data.role = UserRole.USER

        # 3. Construct User model instance in service layer
        new_user = User(
            id=supabase_user_id,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role
        )
        try:
            return await UserRepository.create(db, new_user)
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Auth credentials created, but local profile failed: {str(e)}"
            )

    @staticmethod
    async def login_user(db: AsyncSession, email: str, password: str) -> dict:
        """
        Business Rule: Authenticates against Supabase, gets token,
        and retrieves matching local profile.
        """
        try:
            auth_response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
        except AuthApiError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {e.message}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login systems error: {str(e)}"
            )

        if not auth_response.user or not auth_response.session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed."
            )

        user_id = UUID(auth_response.user.id)
        db_user = await UserService.get_user_profile(db, user_id)

        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "user": db_user
        }

    @staticmethod
    async def update_profile(db: AsyncSession, user_id: UUID, schema: UserUpdate) -> User:
        """
        Business Rule: Checks profile existence first, then calls
        Repository layer to execute updates.
        """
        user = await UserService.get_user_profile(db, user_id)
        try:
            return await UserRepository.update(db, user, schema)
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Profile update failed: {str(e)}"
            )

    @staticmethod
    async def promote_user(db: AsyncSession, target_user_id: UUID, new_role: UserRole) -> User:
        user = await UserRepository.set_role(db, target_user_id, new_role)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
