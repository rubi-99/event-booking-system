from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.enums.roles import UserRole

class UserRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: UUID) -> User | None:
        """
        Executes a database query to select a user by their UUID.
        Returns the User object if found, otherwise None.
        """
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, user: User) -> User:
        """
        Inserts a new User model instance into PostgreSQL.
        """
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update(db: AsyncSession, user: User, schema: UserUpdate) -> User:
        """
        Updates an existing user profile details in Postgres.
        """
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def set_role(db: AsyncSession, user_id: UUID, role: UserRole) -> User | None:
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        if not user:
            return None
        user.role = role
        await db.commit()
        await db.refresh(user)
        return user
