from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    phone: str
    first_name: str
    last_name: str
    id_number: str
    town: str
    email: Optional[str] = None
    address: Optional[str] = None
    role: Optional[str] = "client"

class UserResponse(BaseModel):
    id: str
    phone: str
    first_name: str
    last_name: str
    full_name: str
    display_name: str
    id_number: str
    town: str
    email: Optional[str] = None
    address: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Fixer schemas
class FixerCreate(BaseModel):
    user_id: str
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

# Enhanced Auth schemas
class SignupRequest(BaseModel):
    phone: str
    first_name: str
    last_name: str
    id_number: str
    town: str
    email: Optional[str] = None
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    phone: str
    password: Optional[str] = None

class SetPasswordRequest(BaseModel):
    phone: str
    password: str
    confirm_password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class LoginResponse(BaseModel):
    user: dict
    role_info: dict
    display_name: str
    welcome_message: str
    token: str
    requires_password: bool = False  # If user needs to set password

# Payment schemas
class FixerPaymentCreate(BaseModel):
    fixer_id: str
    amount: float
    payment_type: str
    description: Optional[str] = None

class FixerPaymentResponse(BaseModel):
    id: str
    fixer_id: str
    amount: float
    payment_type: str
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    status: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Verification schemas  
class FixerVerificationCreate(BaseModel):
    fixer_id: str
    id_document_url: Optional[str] = None

class FixerVerificationResponse(BaseModel):
    id: str
    fixer_id: str
    id_document_url: Optional[str] = None
    verification_status: str
    admin_notes: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Emergency Alert schemas
class EmergencyAlertCreate(BaseModel):
    job_id: Optional[str] = None
    alert_type: str = "emergency"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    description: Optional[str] = None

class EmergencyAlertResponse(BaseModel):
    id: str
    user_id: str
    job_id: Optional[str] = None
    alert_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    description: Optional[str] = None
    status: str
    police_notified: bool
    police_reference: Optional[str] = None
    emergency_contacts_notified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Fixer Application schemas
class FixerApplicationCreate(BaseModel):
    services_offered: str  # JSON string of services
    experience_years: int
    qualifications: Optional[str] = None
    previous_work: Optional[str] = None
    why_fixer: str
    id_document: str  # Base64 encoded image
    proof_of_address: Optional[str] = None
    qualifications_cert: Optional[str] = None
    criminal_clearance: Optional[str] = None

class FixerApplicationResponse(BaseModel):
    id: str
    user_id: str
    services_offered: str
    experience_years: int
    qualifications: Optional[str] = None
    previous_work: Optional[str] = None
    why_fixer: str
    status: str
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    submitted_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class FixerApplicationReview(BaseModel):
    status: str  # approved, rejected, needs_documents
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = None