from pydantic import BaseModel, Field, EmailStr, field_validator
from bson import ObjectId
from typing import Optional, Any, Annotated
from datetime import datetime

def validate_object_id(v: Any) -> ObjectId:
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")

PyObjectId = Annotated[ObjectId, Field(description="MongoDB ObjectId"), field_validator('*', mode='before')(validate_object_id)]

class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="Username must be between 1 and 50 characters")
    email: EmailStr = Field(..., description="Valid email address")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters long")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name of the user")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=ObjectId, alias="_id")
    hashed_password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    profile_picture: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    profile_picture: Optional[str] = None

    model_config = {
        "arbitrary_types_allowed": True
    }

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., description="User password")

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    profile_picture: Optional[str] = None