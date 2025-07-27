from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    phone: str
    name: str
    email: Optional[str] = None
    address: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    phone: str
    name: str
    email: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Fixer schemas
class FixerCreate(BaseModel):
    phone: str
    name: str
    email: Optional[str] = None
    services: str
    location: str

class FixerResponse(BaseModel):
    id: str
    phone: str
    name: str
    email: Optional[str] = None
    services: str
    location: str
    rating: float
    total_jobs: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Job schemas
class JobCreate(BaseModel):
    user_id: str
    service: str
    description: str
    location: str
    estimated_price: Optional[float] = None
    scheduled_at: Optional[datetime] = None

class JobUpdate(BaseModel):
    fixer_id: Optional[str] = None
    status: Optional[str] = None
    estimated_price: Optional[float] = None
    final_price: Optional[float] = None
    scheduled_at: Optional[datetime] = None

class JobResponse(BaseModel):
    id: str
    user_id: str
    fixer_id: Optional[str] = None
    service: str
    description: str
    location: str
    status: str
    estimated_price: Optional[float] = None
    final_price: Optional[float] = None
    scheduled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Review schemas
class ReviewCreate(BaseModel):
    job_id: str
    user_id: str
    fixer_id: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: str
    job_id: str
    user_id: str
    fixer_id: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Auth schemas
class LoginRequest(BaseModel):
    phone: str

class LoginResponse(BaseModel):
    user: UserResponse
    token: str