from sqlalchemy.orm import Session
from app.repositories.user_repositories import UserRepository
from app.schemas.user_schema import UserCreate , UserUpdate
from app.models.user import User

from fastapi import HTTPException,status
from app.enums.user_role import UserRole

from uuid import UUID


class UserService:
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register_user(self, db: Session, user_data : UserCreate) -> User:
        existing_user = self.user_repository.get_by_email(db,user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail= "User already exists"
            )
        
        hashed_password = user_data.password

        user = User(
            first_name = user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            hashed_password=hashed_password,
            phone_number=user_data.phone_number,
            role=UserRole.USER
            
        )

        return self.user_repository.create(db, user)
          

    def get_user_by_id(self,db:Session,user_id: UUID) -> User:


        user = self.user_repository.get_by_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            ) 
        
        return user
    
    def get_user_by_email(self,db: Session, email: str) -> User:
        user = self.user_repository.get_by_email(db, email)    
        if not user:
              raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        return user
    
    def get_all_users(self, db: Session) -> list[User]:
        return self.user_repository.get_all(db)
    
    def update_user(
        self,
        db: Session,
        user_id: UUID,
        user_data: UserUpdate
    ) -> User:

        user = self.get_user_by_id(db, user_id)

        if user_data.first_name is not None:
            user.first_name = user_data.first_name

        if user_data.last_name is not None:
            user.last_name = user_data.last_name

        if user_data.phone_number is not None:
            user.phone_number = user_data.phone_number

        return self.user_repository.update(db, user)
    
    def delete_user(self, db: Session,user_id: UUID) -> None:
        user = self.get_user_by_id(db,user_id)

        self.user_repository.delete(db,user)