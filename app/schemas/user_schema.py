from pydantic import BaseModel,EmailStr, ConfigDict
from typing import Optional
from uuid import UUID

from app.enums.user_role import UserRole
from datetime import datetime

class UserCreate(BaseModel):
    first_name : str
    last_name : str
    email: EmailStr
    password : str
    phone_number: str
    

class UserUpdate(BaseModel):
    first_name: Optional[str] = None    
    last_name : Optional[str] = None 
    phone_number: Optional[str] = None 
   


class UserResponse(BaseModel):
    id: UUID
    first_name : str
    last_name : str
    email: EmailStr
    phone_number : str
    role: UserRole
    created_at: datetime
    updated_at : datetime


    model_config = ConfigDict(from_attributes=True)