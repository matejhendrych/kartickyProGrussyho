"""
Pydantic schemas for data validation and serialization
"""
from typing import Optional, List
from datetime import datetime, time
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# User schemas
class UserBase(BaseModel):
    """Base user schema"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    second_name: Optional[str] = None
    card_number: Optional[str] = None
    chip_number: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation"""
    password: str
    username: str
    email: EmailStr


class UserUpdate(UserBase):
    """Schema for user update"""
    password: Optional[str] = None


class UserInDB(UserBase):
    """Schema for user in database"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    verified: bool = False
    access: str = "U"
    

class User(UserInDB):
    """Schema for user response"""


# Authentication schemas
class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    username: str
    password: str


# Group schemas
class GroupBase(BaseModel):
    """Base group schema"""
    group_name: str
    access_time_from: Optional[time] = None
    access_time_to: Optional[time] = None
    Monday: bool = False
    Tuesday: bool = False
    Wednesday: bool = False
    Thursday: bool = False
    Friday: bool = False
    Saturday: bool = False
    Sunday: bool = False


class GroupCreate(GroupBase):
    """Schema for group creation"""


class GroupUpdate(GroupBase):
    """Schema for group update"""
    group_name: Optional[str] = None


class Group(GroupBase):
    """Schema for group response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int


# Timecard/Reader schemas
class TimecardBase(BaseModel):
    """Base timecard schema"""
    timecard_head: str
    identreader: str
    pushopen: str
    description: Optional[str] = None


class TimecardCreate(TimecardBase):
    """Schema for timecard creation"""


class Timecard(TimecardBase):
    """Schema for timecard response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int


# Card access log schemas
class CardAccessBase(BaseModel):
    """Base card access schema"""
    card_number: str
    time: datetime
    id_card_reader: int
    id_user: int
    access: bool


class CardAccessCreate(CardAccessBase):
    """Schema for card access creation"""


class CardAccess(CardAccessBase):
    """Schema for card access response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int


# Monthly report schemas
class MonthlyReportRequest(BaseModel):
    """Schema for monthly report request"""
    year: int = Field(ge=2000, le=2100)
    month: int = Field(ge=1, le=12)
    user_id: Optional[int] = None


class MonthlyReportResponse(BaseModel):
    """Schema for monthly report response"""
    user_id: int
    user_name: str
    year: int
    month: int
    total_hours: float
    entries: List[dict]
