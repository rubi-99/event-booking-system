from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.user import get_user_service

from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserResponse
)

from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/",
            response_model= UserResponse,
            status_code= status.HTTP_201_CREATED
)
def register_user(user: UserCreate, db: Session = Depends(get_db), service : UserService = Depends(get_user_service)):
    return service.register_user(db, user)

@router.get("/{user_id}",response_model=UserResponse)
def get_user(user_id : UUID, db:Session = Depends(get_db),service: UserService = Depends(get_user_service)):
    return service.get_user_by_id(db,user_id)

@router.get( "/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db),service: UserService = Depends(get_user_service)):
    return service.get_all_users(db)

@router.put(
    "/{user_id}",
    response_model=UserResponse
)
def update_user(
    user_id: UUID,
    user: UserUpdate,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)
):

    return service.update_user(
        db,
        user_id,
        user
    )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service)):

    service.delete_user(
        db,
        user_id
    )