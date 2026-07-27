from pydantic import BaseModel, EmailStr, Field,ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.enums.roles import UserRole

# 1. Base schema with common attributes
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.USER

# 2. Signup payload validation
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")

# 3. Profile update payload validation
class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)

# 4. Outgoing response formatting
class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    # Tells Pydantic to read from SQLAlchemy objects
    model_config = ConfigDict(from_attributes=True)

# 5. Login payload validation
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 6. Role update payload (admin only)
class RoleUpdate(BaseModel):
    role: UserRole

# 7. Login token return model
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
