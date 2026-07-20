from app.repositories.user_repositories import UserRepository
from fastapi import Depends

from app.services.user_service import UserService

def get_user_repository():
    return UserRepository()

def get_user_service(repository: UserRepository = Depends(get_user_repository)):
    return UserService(repository)
