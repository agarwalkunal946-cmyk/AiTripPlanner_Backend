from pydantic import BaseModel, Field, field_validator
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *args, **kwargs):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class ItineraryItem(BaseModel):
    day: int = Field(..., gt=0)
    description: str = Field(..., min_length=1)
    location: Optional[str] = None
    time: Optional[str] = None
    cost: Optional[float] = Field(None, ge=0)

class TripBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    destination: str = Field(..., min_length=1, max_length=100)
    duration_days: int = Field(..., gt=0, le=365)
    price: float = Field(..., ge=0)
    description: Optional[str] = Field(None, max_length=1000)
    itinerary: List[ItineraryItem] = []
    max_participants: Optional[int] = Field(None, gt=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = Field(None, max_length=50)
    difficulty_level: Optional[str] = Field(None, max_length=20)
    image_url: Optional[str] = None

    @field_validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if v and 'start_date' in values.data and values.data['start_date'] and v <= values.data['start_date']:
            raise ValueError('End date must be after start date')
        return v

class TripCreate(TripBase):
    host_id: str

class TripInDB(TripBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    host_id: str
    joined_users: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    status: str = Field(default="upcoming", max_length=20)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class TripResponse(BaseModel):
    id: str
    title: str
    destination: str
    duration_days: int
    price: float
    description: Optional[str] = None
    itinerary: List[ItineraryItem] = []
    max_participants: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    image_url: Optional[str] = None
    host_id: str
    joined_users: List[str] = []
    created_at: datetime
    status: str
    current_participants: int = 0

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class TripUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    destination: Optional[str] = Field(None, min_length=1, max_length=100)
    duration_days: Optional[int] = Field(None, gt=0, le=365)
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = Field(None, max_length=1000)
    itinerary: Optional[List[ItineraryItem]] = None
    max_participants: Optional[int] = Field(None, gt=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = Field(None, max_length=50)
    difficulty_level: Optional[str] = Field(None, max_length=20)
    image_url: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)

class TripSearch(BaseModel):
    destination: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    difficulty_level: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None