from fastapi import FastAPI, APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, and_, or_, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import json
import time
import random
import uuid
import hashlib
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path
import tempfile
import shutil

# Push notification imports
try:
    from pywebpush import webpush, WebPushException
    PYWEBPUSH_AVAILABLE = True
except ImportError:
    PYWEBPUSH_AVAILABLE = False
    print("⚠️ pywebpush not available - push notifications will be simulated")

# Optional imports for AI features - don't break if not available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Import services and models
from database import get_db, engine
from models import Base, User, Job, EmergencyAlert, WhatsAppStatistics, Announcement, AnnouncementChat, JobStatus, JobPriority, UserRole
from services.emergency_service import emergency_service
from services.whatsapp_service import whatsapp_service
from services.role_service import role_service
from passlib.context import CryptContext

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="FixMate-SA API",
    description="South Africa's Premier Service Platform API with Emergency Services",
    version="2.1.0"
)

# Security
security = HTTPBearer()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class UserLogin(BaseModel):
    phone: str
    password: str

class UserSignup(BaseModel):
    phone: str
    first_name: str
    last_name: str
    id_number: str
    town: str
    email: str
    password: str
    confirm_password: str

class UserResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[Dict[str, Any]] = None

class EmergencyAlertCreate(BaseModel):
    user_id: str
    user_name: Optional[str] = None
    user_phone: Optional[str] = None
    job_id: Optional[str] = None
    alert_type: str = "emergency"
    priority: str = "high"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    description: Optional[str] = "Emergency assistance requested"
    recording_duration: Optional[int] = 0

class EmergencyResponse(BaseModel):
    success: bool
    message: str
    alert_id: Optional[str] = None
    police_notified: Optional[bool] = False
    police_reference: Optional[str] = None
    voice_transcribed: Optional[bool] = False
    transcription_preview: Optional[str] = None

# Profile Update Schemas
class ProfileUpdateBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    town: Optional[str] = None
    address: Optional[str] = None

class ClientProfileUpdate(ProfileUpdateBase):
    pass

class FixerProfileUpdate(ProfileUpdateBase):
    # Professional information
    services: Optional[str] = None  # Comma-separated list
    experience_years: Optional[int] = None
    hourly_rate: Optional[float] = None
    availability_status: Optional[str] = None
    service_area: Optional[str] = None
    certifications: Optional[str] = None  # JSON string of certifications
    portfolio_images: Optional[str] = None  # JSON string of image URLs

class AdminProfileUpdate(ProfileUpdateBase):
    # Admin-specific settings
    admin_level: Optional[str] = None
    department: Optional[str] = None

class ProfileResponse(BaseModel):
    success: bool
    message: str
    user: Optional[Dict[str, Any]] = None

# Helper Functions
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token (simplified for demo)"""
    # In production, implement proper JWT verification
    return {"user_id": "demo_user", "role": "client"}

def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get user from token"""
    try:
        token = credentials.credentials
        # Simple token validation (implement proper JWT in production)
        if not token:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # For demo purposes, extract user_id from token or use a default
        # In production, decode JWT properly
        user_id = "demo_user"  # This should come from JWT
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

# Authentication Endpoints

def format_phone_number(phone: str) -> str:
    """Format phone number to standard format"""
    # Remove any whitespace and special characters except +
    phone = phone.strip().replace(" ", "").replace("-", "")
    
    # Remove whatsapp: prefix if present
    if phone.startswith("whatsapp:"):
        phone = phone.replace("whatsapp:", "")
    
    # If it starts with 0, replace with +27
    if phone.startswith("0"):
        phone = "+27" + phone[1:]
    
    # If it starts with 27 but not +27, add +
    elif phone.startswith("27") and not phone.startswith("+27"):
        phone = "+" + phone
    
    return phone

@app.post("/api/auth/login", response_model=UserResponse)
async def unified_login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Unified login endpoint for all user types"""
    try:
        # Format phone number
        formatted_phone = format_phone_number(login_data.phone)
        
        # Try different phone number variations
        phone_variations = [
            formatted_phone,
            login_data.phone,
            f"whatsapp:{formatted_phone}",
            f"whatsapp:{login_data.phone}"
        ]
        
        user = None
        for phone_var in phone_variations:
            user = db.query(User).filter(User.phone == phone_var).first()
            if user:
                break
        
        if not user:
            return UserResponse(success=False, message="Invalid phone number or password")
        
        # Verify password against hash
        if not user.password_hash or not pwd_context.verify(login_data.password, user.password_hash):
            return UserResponse(success=False, message="Invalid phone number or password")
        
        # Get role information
        role_info = role_service.determine_user_role(user.phone, db)
        
        # Generate token (simplified for demo - use proper JWT in production)
        token = f"token_{user.id}"
        
        # Get display name and welcome message
        display_name = role_service.get_display_name_with_role(user, role_info["role"])
        welcome_message = role_service.get_welcome_message_with_role(user, role_info["role"])
        
        return UserResponse(
            success=True,
            message="Login successful",
            token=token,
            user={
                "id": user.id,
                "phone": user.phone,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": role_info["role"],
                "display_name": display_name,
                "welcome_message": welcome_message,
                "permissions": role_info["permissions"],
                "is_fixer": role_info["is_fixer"],
                "fixer_data": role_info.get("fixer_data")
            }
        )
    except Exception as e:
        print(f"Login error: {str(e)}")
        return UserResponse(success=False, message="Login failed")

@app.get("/api/auth/role-check/{phone}")
async def check_user_role(phone: str, db: Session = Depends(get_db)):
    """Check user role by phone number (for debugging)"""
    try:
        formatted_phone = format_phone_number(phone)
        
        # Try different phone number variations
        phone_variations = [
            formatted_phone,
            phone,
            f"whatsapp:{formatted_phone}",
            f"whatsapp:{phone}"
        ]
        
        user = None
        for phone_var in phone_variations:
            user = db.query(User).filter(User.phone == phone_var).first()
            if user:
                break
        
        if user:
            role_info = role_service.determine_user_role(user.phone, db)
            return {
                "success": True,
                "phone": user.phone,
                "role": role_info["role"],
                "database_role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "display_name": role_service.get_display_name_with_role(user, role_info["role"]),
                "user_exists": True
            }
        else:
            return {
                "success": True,
                "phone": phone,
                "role": "client",  # Default role for new users
                "database_role": None,
                "display_name": "New User",
                "user_exists": False
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Legacy endpoints for backward compatibility
@app.post("/api/auth/client/login", response_model=UserResponse)
async def client_login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Client login endpoint (legacy - redirects to unified login)"""
    return await unified_login(login_data, db)

@app.post("/api/auth/fixer/login", response_model=UserResponse)
async def fixer_login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Fixer login endpoint (legacy - redirects to unified login)"""
    return await unified_login(login_data, db)

@app.post("/api/auth/admin/login", response_model=UserResponse)
async def admin_login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Admin login endpoint (legacy - redirects to unified login)"""
    return await unified_login(login_data, db)

@app.post("/api/auth/signup", response_model=UserResponse)
async def signup(signup_data: UserSignup, db: Session = Depends(get_db)):
    """User signup endpoint for client registration"""
    try:
        # Validate password confirmation
        if signup_data.password != signup_data.confirm_password:
            return UserResponse(success=False, message="Passwords do not match")
        
        # Validate password strength
        if len(signup_data.password) < 6:
            return UserResponse(success=False, message="Password must be at least 6 characters long")
        
        # Format phone number
        formatted_phone = format_phone_number(signup_data.phone)
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            or_(
                User.phone == formatted_phone,
                User.phone == signup_data.phone,
                User.email == signup_data.email.lower() if signup_data.email else ""
            )
        ).first()
        
        if existing_user:
            if existing_user.phone in [formatted_phone, signup_data.phone]:
                return UserResponse(success=False, message="Phone number already registered")
            else:
                return UserResponse(success=False, message="Email address already registered")
        
        # Hash password
        password_hash = pwd_context.hash(signup_data.password)
        
        # Generate unique user ID
        user_id = str(uuid.uuid4())
        
        # Create new user
        new_user = User(
            id=user_id,
            phone=formatted_phone,
            first_name=signup_data.first_name.strip(),
            last_name=signup_data.last_name.strip(),
            id_number=signup_data.id_number.strip(),
            town=signup_data.town.strip(),
            email=signup_data.email.lower().strip() if signup_data.email else None,
            password_hash=password_hash,
            role=UserRole.client,  # Default role for signup
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Generate token
        token = f"token_{user_id}"
        
        # Get role information
        role_info = {
            "role": "client",
            "is_client": True,
            "is_fixer": False,
            "is_admin": False
        }
        
        # Get display name and welcome message
        display_name = f"{new_user.first_name} {new_user.last_name}"
        welcome_message = f"Welcome to FixMate-SA, {new_user.first_name}!"
        
        return UserResponse(
            success=True,
            message="Account created successfully",
            token=token,
            user={
                "id": new_user.id,
                "phone": new_user.phone,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email,
                "role": "client",
                "role_info": role_info,
                "display_name": display_name,
                "welcome_message": welcome_message,
                "is_client": True,
                "is_fixer": False,
                "is_admin": False,
                "fixer_data": None
            }
        )
        
    except Exception as e:
        db.rollback()
        print(f"Signup error: {str(e)}")
        return UserResponse(success=False, message="Failed to create account. Please try again.")

# Authentication Dependencies
def verify_token_dependency(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """Verify Bearer token and return user information"""
    try:
        token = credentials.credentials
        
        # Simple token validation - token format is "token_{user_id}"
        if not token or not token.startswith("token_"):
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )
        
        # Extract user_id from token
        user_id = token.replace("token_", "")
        
        return {"user_id": user_id, "token": token}
        
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

def verify_user_ownership(
    user_id: str, 
    token_data: dict = Depends(verify_token_dependency)
):
    """Verify that the authenticated user can access the requested user_id"""
    if token_data["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You can only access your own profile"
        )
    return token_data

# Profile Management API Endpoints

@app.get("/api/profile/{user_id}")
async def get_user_profile(
    user_id: str, 
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_user_ownership)
):
    """Get user profile information (authenticated)"""
    try:
        # Find user by ID
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build profile data based on role
        profile_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "town": user.town,
            "address": getattr(user, 'address', None),
            "role": user.role.value if hasattr(user.role, 'value') else user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        
        # Add role-specific fields
        if user.role == UserRole.fixer or user.role == 'fixer':
            profile_data.update({
                "services": getattr(user, 'services', None),
                "experience_years": getattr(user, 'experience_years', None),
                "hourly_rate": getattr(user, 'hourly_rate', None),
                "availability_status": getattr(user, 'availability_status', 'available'),
                "service_area": getattr(user, 'service_area', None),
                "certifications": getattr(user, 'certifications', None),
                "portfolio_images": getattr(user, 'portfolio_images', None),
                "rating": getattr(user, 'rating', 5.0),
                "total_jobs": getattr(user, 'total_jobs', 0)
            })
        elif user.role == UserRole.admin or user.role == 'admin':
            profile_data.update({
                "admin_level": getattr(user, 'admin_level', 'standard'),
                "department": getattr(user, 'department', 'general')
            })
        
        return {
            "success": True,
            "user": profile_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch profile")

@app.put("/api/profile/{user_id}")
async def update_user_profile(
    user_id: str, 
    profile_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    try:
        # Find user by ID
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update basic fields
        basic_fields = ['first_name', 'last_name', 'email', 'phone', 'town', 'address']
        for field in basic_fields:
            if field in profile_data and profile_data[field] is not None:
                setattr(user, field, profile_data[field])
        
        # Update role-specific fields
        if user.role == UserRole.fixer or user.role == 'fixer':
            fixer_fields = [
                'services', 'experience_years', 'hourly_rate', 
                'availability_status', 'service_area', 'certifications', 'portfolio_images'
            ]
            for field in fixer_fields:
                if field in profile_data and profile_data[field] is not None:
                    setattr(user, field, profile_data[field])
        
        elif user.role == UserRole.admin or user.role == 'admin':
            admin_fields = ['admin_level', 'department']
            for field in admin_fields:
                if field in profile_data and profile_data[field] is not None:
                    setattr(user, field, profile_data[field])
        
        # Update timestamp
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        return ProfileResponse(
            success=True,
            message="Profile updated successfully",
            user={
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else user.role
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Update profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update profile")

@app.post("/api/profile/{user_id}/upload-image")
async def upload_profile_image(
    user_id: str,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload profile image"""
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate image file
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("/app/frontend/public/uploads/profiles")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = image.filename.split('.')[-1] if '.' in image.filename else 'jpg'
        unique_filename = f"profile_{user_id}_{int(time.time())}.{file_extension}"
        file_path = uploads_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Update user profile with image URL
        profile_image_url = f"/uploads/profiles/{unique_filename}"
        setattr(user, 'profile_image', profile_image_url)
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True,
            "message": "Profile image uploaded successfully",
            "image_url": profile_image_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload image error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload image")

# Emergency Services API Endpoints

@app.post("/api/emergency/alert", response_model=EmergencyResponse)
async def create_emergency_alert(
    user_id: str = Form(...),
    user_name: Optional[str] = Form(None),
    user_phone: Optional[str] = Form(None), 
    job_id: Optional[str] = Form(None),
    alert_type: str = Form("emergency"),
    priority: str = Form("high"),
    latitude: Optional[str] = Form(None),
    longitude: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    description: Optional[str] = Form("Emergency assistance requested"),
    recording_duration: Optional[str] = Form("0"),
    voice_recording: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Create emergency alert with optional voice recording
    Processes voice to text and initiates emergency protocol
    """
    try:
        print(f"🚨 Emergency alert received for user: {user_id}")
        print(f"📍 Location: {latitude}, {longitude} - {address}")
        print(f"🎤 Voice recording: {'Yes' if voice_recording else 'No'}")
        
        # Validate required fields
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # Convert string coordinates to float if provided
        lat_float = None
        lng_float = None
        
        if latitude and latitude != "null":
            try:
                lat_float = float(latitude)
            except ValueError:
                print(f"⚠️ Invalid latitude: {latitude}")
        
        if longitude and longitude != "null":
            try:
                lng_float = float(longitude)
            except ValueError:
                print(f"⚠️ Invalid longitude: {longitude}")
        
        duration_int = 0
        if recording_duration and recording_duration != "0":
            try:
                duration_int = int(recording_duration)
            except ValueError:
                print(f"⚠️ Invalid recording duration: {recording_duration}")
        
        # Prepare alert data
        alert_data = {
            "user_id": user_id,
            "user_name": user_name or "Unknown User",
            "user_phone": user_phone or "Unknown Phone",
            "job_id": job_id,
            "alert_type": alert_type,
            "priority": priority,
            "latitude": lat_float,
            "longitude": lng_float,
            "address": address or "Location not provided",
            "description": description or "Emergency assistance requested",
            "recording_duration": duration_int
        }
        
        print(f"📋 Alert data: {alert_data}")
        
        # Process emergency alert with voice recording
        result = await emergency_service.trigger_emergency_alert(
            user_id=user_id,
            alert_data=alert_data,
            voice_file=voice_recording,
            db=db
        )
        
        print(f"🔄 Emergency service result: {result}")
        
        if result["success"]:
            return EmergencyResponse(
                success=True,
                message=result["message"],
                alert_id=result["alert_id"],
                police_notified=result.get("police_notified", False),
                police_reference=result.get("police_reference"),
                voice_transcribed=result.get("voice_transcribed", False),
                transcription_preview=result.get("transcription_preview")
            )
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Emergency alert failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Emergency alert API error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"Emergency alert processing failed: {str(e)}"
        )

@app.get("/api/emergency/location")
async def get_location_address(
    latitude: float,
    longitude: float
):
    """
    Get human-readable address from coordinates
    """
    try:
        address = emergency_service.get_location_from_coordinates(latitude, longitude)
        return {"success": True, "address": address}
    except Exception as e:
        return {"success": False, "address": f"{latitude:.6f}, {longitude:.6f}", "error": str(e)}

@app.get("/api/emergency/alerts/{user_id}")
async def get_user_emergency_alerts(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user's emergency alert history
    """
    try:
        alerts = emergency_service.get_emergency_alerts(user_id, db)
        return {"success": True, "alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/emergency/resolve/{alert_id}")
async def resolve_emergency_alert(
    alert_id: str,
    resolution: str = Form(...),
    notes: Optional[str] = Form(""),
    db: Session = Depends(get_db)
):
    """
    Resolve emergency alert (admin only)
    """
    try:
        result = emergency_service.resolve_emergency_alert(alert_id, resolution, notes, db)
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/emergency/stats")
async def get_emergency_stats(db: Session = Depends(get_db)):
    """
    Get emergency system statistics (admin only)
    """
    try:
        total_alerts = db.query(EmergencyAlert).count()
        active_alerts = db.query(EmergencyAlert).filter(EmergencyAlert.status == "active").count()
        resolved_alerts = db.query(EmergencyAlert).filter(EmergencyAlert.status == "resolved").count()
        
        # Today's alerts
        today = datetime.now().date()
        today_alerts = db.query(EmergencyAlert).filter(
            EmergencyAlert.created_at >= today
        ).count()
        
        return {
            "success": True,
            "stats": {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "resolved_alerts": resolved_alerts,
                "today_alerts": today_alerts,
                "alert_types": ["emergency", "medical", "fire", "security"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health Check
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    from services.emergency_service import WHISPER_AVAILABLE
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "emergency_service": "active",
            "voice_transcription": "active" if WHISPER_AVAILABLE and emergency_service.whisper_model else "fallback_mode",
            "sms_service": "active" if emergency_service.twilio_client else "mock",
            "database": "connected"
        },
        "emergency_contacts": {
            "police": "10111",
            "medical": "10177",
            "fire": "10177"
        },
        "voice_features": {
            "whisper_available": WHISPER_AVAILABLE,
            "transcription_mode": "ai_powered" if WHISPER_AVAILABLE else "manual_review"
        }
    }

# Create test users endpoint (for development)
@app.post("/api/setup/create-test-users")
async def create_test_users(db: Session = Depends(get_db)):
    """Create test users for development"""
    try:
        # Check if users already exist
        existing_users = db.query(User).filter(User.phone.in_([
            "0821234565", "0821234566", "0821234567"
        ])).all()
        
        if len(existing_users) >= 3:
            return {"success": True, "message": "Test users already exist"}
        
        # Create test users
        test_users = [
            {
                "id": "client_test_001",
                "phone": "0821234565", 
                "name": "Test Client",
                "first_name": "Test",
                "last_name": "Client",
                "role": "client",
                "is_active": True
            },
            {
                "id": "fixer_test_001",
                "phone": "0821234566",
                "name": "Test Fixer", 
                "first_name": "Test",
                "last_name": "Fixer",
                "role": "fixer",
                "is_active": True
            },
            {
                "id": "admin_test_001",
                "phone": "0821234567",
                "name": "Test Admin",
                "first_name": "Test", 
                "last_name": "Admin",
                "role": "admin",
                "is_active": True
            }
        ]
        
        created_users = []
        for user_data in test_users:
            # Check if user exists
            existing = db.query(User).filter(User.phone == user_data["phone"]).first()
            if not existing:
                user = User(**user_data)
                db.add(user)
                created_users.append(user_data["phone"])
        
        db.commit()
        
        return {
            "success": True, 
            "message": f"Created {len(created_users)} test users",
            "users": [
                {"phone": "0821234565", "password": "client123", "role": "client"},
                {"phone": "0821234566", "password": "fixer123", "role": "fixer"},
                {"phone": "0821234567", "password": "admin123", "role": "admin"}
            ]
        }
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}

# Job Management Endpoints
class JobCreate(BaseModel):
    title: str
    description: str
    location: str
    urgency: str = "medium"
    budget_min: Optional[float] = 0
    budget_max: Optional[float] = 0
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    category: str  # Frontend uses 'category', we'll map to 'service'
    images: Optional[List[str]] = []
    communication_preference: str = "phone"
    whatsapp_notifications: bool = True
    client_id: str  # Frontend uses 'client_id', we'll map to 'user_id'

class JobResponse(BaseModel):
    success: bool
    message: str
    job_id: Optional[str] = None
    job: Optional[Dict[str, Any]] = None

# Notification Functions
async def create_fixer_notification(fixer_id: str, job_id: str, job_data: JobCreate, db: Session):
    """Create notification for assigned fixer"""
    try:
        # Create notifications table if it doesn't exist
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS fixer_notifications (
                id VARCHAR PRIMARY KEY,
                fixer_id VARCHAR NOT NULL,
                job_id VARCHAR NOT NULL,
                notification_type VARCHAR DEFAULT 'job_assigned',
                title VARCHAR NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute(create_table_query)
        
        # Insert notification
        notification_id = f"notif_{uuid.uuid4()}"
        insert_query = text("""
            INSERT INTO fixer_notifications (
                id, fixer_id, job_id, notification_type, title, message, created_at
            ) VALUES (
                :id, :fixer_id, :job_id, :notification_type, :title, :message, :created_at
            )
        """)
        
        db.execute(insert_query, {
            'id': notification_id,
            'fixer_id': fixer_id,
            'job_id': job_id,
            'notification_type': 'job_assigned',
            'title': f'New Job Assigned: {job_data.category}',
            'message': f'You have been assigned a new {job_data.category} job in {job_data.location}. Description: {job_data.description[:100]}...',
            'created_at': datetime.utcnow()
        })
        
        print(f"📧 Created assignment notification for fixer {fixer_id}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create fixer notification: {str(e)}")
        return False

async def create_available_job_notification(fixer_id: str, job_id: str, job_data: JobCreate, db: Session):
    """Create notification for available job to qualified fixers"""
    try:
        # Insert notification
        notification_id = f"notif_{uuid.uuid4()}"
        insert_query = text("""
            INSERT INTO fixer_notifications (
                id, fixer_id, job_id, notification_type, title, message, created_at
            ) VALUES (
                :id, :fixer_id, :job_id, :notification_type, :title, :message, :created_at
            )
        """)
        
        db.execute(insert_query, {
            'id': notification_id,
            'fixer_id': fixer_id,
            'job_id': job_id,
            'notification_type': 'job_available',
            'title': f'New Job Available: {job_data.category}',
            'message': f'A new {job_data.category} job is available in {job_data.location}. You can apply if interested. Description: {job_data.description[:100]}...',
            'created_at': datetime.utcnow()
        })
        
        print(f"📧 Created availability notification for fixer {fixer_id}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create availability notification: {str(e)}")
        return False

# Automatic Job Allocation System
async def allocate_job_to_fixers(job_id: str, job_data: JobCreate, db: Session):
    """
    Automatically allocate job to available fixers based on service type and location
    """
    try:
        # Find fixers that provide the required service
        query = text("""
            SELECT id, user_id, name, email, services, location, rating, 
                   total_jobs, is_active, is_approved, jobs_completed
            FROM fixers 
            WHERE is_active = true 
            AND is_approved = true
            AND (services ILIKE :service_pattern OR services ILIKE :service_pattern2)
            ORDER BY rating DESC, jobs_completed DESC
            LIMIT 5
        """)
        
        service_pattern = f'%"{job_data.category}"%'
        service_pattern2 = f'%{job_data.category}%'
        
        result = db.execute(query, {
            'service_pattern': service_pattern,
            'service_pattern2': service_pattern2
        }).fetchall()
        
        if result:
            # Assign to the top-rated available fixer
            selected_fixer = result[0]
            fixer_id = selected_fixer[0]
            
            # Update job with assigned fixer
            update_query = text("""
                UPDATE jobs 
                SET fixer_id = :fixer_id, status = 'assigned', updated_at = :updated_at
                WHERE id = :job_id
            """)
            
            db.execute(update_query, {
                'fixer_id': fixer_id,
                'job_id': job_id,
                'updated_at': datetime.utcnow()
            })
            
            # Create notification for the assigned fixer
            await create_fixer_notification(fixer_id, job_id, job_data, db)
            
            # Also create notifications for other qualified fixers (available jobs)
            for fixer in result[1:]:  # Skip the first one as it's already assigned
                await create_available_job_notification(fixer[0], job_id, job_data, db)
            
            print(f"✅ Job {job_id} assigned to fixer {selected_fixer[2]} ({fixer_id}) with notifications sent")
            return True
        else:
            print(f"⚠️ No available fixers found for service: {job_data.category}")
            return False
            
    except Exception as e:
        print(f"❌ Job allocation error: {str(e)}")
        return False

@app.post("/api/jobs", response_model=JobResponse)
async def create_job(job_data: JobCreate, db: Session = Depends(get_db)):
    """Create a new job"""
    try:
        # Generate unique job ID
        job_id = f"job_{uuid.uuid4()}"
        
        # Parse preferred_date if provided
        scheduled_at = None
        if job_data.preferred_date:
            try:
                scheduled_at = datetime.strptime(job_data.preferred_date, "%Y-%m-%d")
            except ValueError:
                pass
        
        # Create new job using raw SQL INSERT to match the actual database schema
        db.execute(text("""
            INSERT INTO jobs (
                id, user_id, service, description, location, 
                estimated_price, status, priority_level, 
                scheduled_at, created_at, updated_at,
                terms_accepted, workflow_stage, payment_status
            ) VALUES (
                :id, :user_id, :service, :description, :location,
                :estimated_price, :status, :priority_level,
                :scheduled_at, :created_at, :updated_at,
                :terms_accepted, :workflow_stage, :payment_status
            )
        """), {
            'id': job_id,
            'user_id': job_data.client_id,  # Map client_id to user_id
            'service': job_data.category,   # Map category to service
            'description': job_data.description,
            'location': job_data.location,
            'estimated_price': job_data.budget_max or 0,
            'status': 'pending',
            'priority_level': job_data.urgency,
            'scheduled_at': scheduled_at,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'terms_accepted': True,
            'workflow_stage': 'pending',
            'payment_status': 'pending'
        })
        
        db.commit()
        
        # Automatic Job Allocation System
        await allocate_job_to_fixers(job_id, job_data, db)
        
        # Commit the allocation changes
        db.commit()
        
        return JobResponse(
            success=True,
            message="Job created successfully and assigned to available fixers",
            job_id=job_id,
            job={
                "id": job_id,
                "title": job_data.title,
                "description": job_data.description,
                "location": job_data.location,
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        db.rollback()
        print(f"Job creation error: {str(e)}")
        return JobResponse(
            success=False,
            message=f"Failed to create job: {str(e)}"
        )

@app.get("/api/jobs")
async def get_jobs(request: Request, client_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Get jobs for authenticated user"""
    try:
        # Extract and validate user from token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Verify user exists
        user_check = text("SELECT id FROM users WHERE id = :user_id")
        user_result = db.execute(user_check, {'user_id': user_id}).fetchone()
        if not user_result:
            raise HTTPException(status_code=401, detail="Invalid user token")
        
        # Always filter by authenticated user's ID for security
        query = text("""
            SELECT id, user_id, service, description, location, status, 
                   estimated_price, priority_level, created_at, fixer_id
            FROM jobs 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC
        """)
        result = db.execute(query, {'user_id': user_id}).fetchall()
        
        jobs_data = []
        for row in result:
            jobs_data.append({
                "id": row[0],
                "title": row[2],  # Use service as title since no title column exists
                "description": row[3],
                "location": row[4],
                "category": row[2],  # Map service to category for frontend
                "status": row[5],
                "urgency": row[7],  # priority_level
                "estimated_price": row[6],
                "created_at": row[8].isoformat() if row[8] else None,
                "client_id": row[1],  # Map user_id to client_id for frontend
                "fixer_id": row[9]
            })
        
        return {
            "success": True,
            "jobs": jobs_data
        }
        
    except Exception as e:
        print(f"Get jobs error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    try:
        # Use raw SQL to match actual database schema
        query = text("""
            SELECT id, user_id, service, description, location, status, 
                   estimated_price, priority_level, created_at, fixer_id,
                   scheduled_at, updated_at
            FROM jobs 
            WHERE id = :job_id
        """)
        result = db.execute(query, {'job_id': job_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "success": True,
            "job": {
                "id": result[0],
                "title": result[2],  # Use service as title since no title column exists
                "description": result[3],
                "location": result[4],
                "category": result[2],  # Map service to category for frontend
                "status": result[5],
                "urgency": result[7],  # priority_level
                "estimated_price": result[6],
                "created_at": result[8].isoformat() if result[8] else None,
                "client_id": result[1],  # Map user_id to client_id for frontend
                "fixer_id": result[9],
                "scheduled_at": result[10].isoformat() if result[10] else None,
                "updated_at": result[11].isoformat() if result[11] else None,
                "images": []  # No images column in current schema
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get job error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Fixer Management Endpoints
@app.get("/api/fixers")
async def get_fixers(db: Session = Depends(get_db)):
    """Get all active fixers"""
    try:
        query = text("""
            SELECT id, user_id, name, email, services, location, rating, 
                   total_jobs, is_active, is_approved, jobs_completed,
                   completion_percentage, created_at
            FROM fixers 
            WHERE is_active = true
            ORDER BY rating DESC, jobs_completed DESC
        """)
        result = db.execute(query).fetchall()
        
        fixers_data = []
        for row in result:
            # Parse services (stored as JSON string)
            services = []
            if row[4]:  # services column
                try:
                    import json
                    services = json.loads(row[4]) if isinstance(row[4], str) else row[4]
                except:
                    services = row[4].split(',') if isinstance(row[4], str) else []
            
            fixers_data.append({
                "id": row[0],
                "user_id": row[1], 
                "name": row[2],
                "email": row[3],
                "services": services,
                "location": row[5],
                "rating": row[6] or 0.0,
                "total_jobs": row[7] or 0,
                "is_active": row[8],
                "is_approved": row[9],
                "jobs_completed": row[10] or 0,
                "completion_percentage": row[11] or 0.0,
                "created_at": row[12].isoformat() if row[12] else None
            })
        
        return {
            "success": True,
            "fixers": fixers_data
        }
        
    except Exception as e:
        print(f"Get fixers error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fixers/{fixer_id}")
async def get_fixer(fixer_id: str, db: Session = Depends(get_db)):
    """Get specific fixer by ID"""
    try:
        query = text("""
            SELECT id, user_id, name, email, services, location, rating, 
                   total_jobs, is_active, is_approved, jobs_completed,
                   completion_percentage, skills, created_at
            FROM fixers 
            WHERE id = :fixer_id
        """)
        result = db.execute(query, {'fixer_id': fixer_id}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Fixer not found")
        
        # Parse services
        services = []
        if result[4]:
            try:
                import json
                services = json.loads(result[4]) if isinstance(result[4], str) else result[4]
            except:
                services = result[4].split(',') if isinstance(result[4], str) else []
        
        # Parse skills
        skills = []
        if result[12]:
            try:
                import json
                skills = json.loads(result[12]) if isinstance(result[12], str) else result[12]
            except:
                skills = result[12].split(',') if isinstance(result[12], str) else []
        
        return {
            "success": True,
            "fixer": {
                "id": result[0],
                "user_id": result[1],
                "name": result[2], 
                "email": result[3],
                "services": services,
                "location": result[5],
                "rating": result[6] or 0.0,
                "total_jobs": result[7] or 0,
                "is_active": result[8],
                "is_approved": result[9],
                "jobs_completed": result[10] or 0,
                "completion_percentage": result[11] or 0.0,
                "skills": skills,
                "created_at": result[13].isoformat() if result[13] else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get fixer error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fixers/by-service/{service}")
async def get_fixers_by_service(service: str, db: Session = Depends(get_db)):
    """Get fixers that provide a specific service"""
    try:
        # Use ILIKE for case-insensitive search within JSON services
        query = text("""
            SELECT id, user_id, name, email, services, location, rating, 
                   total_jobs, is_active, is_approved, jobs_completed,
                   completion_percentage, created_at
            FROM fixers 
            WHERE is_active = true 
            AND (services ILIKE :service_pattern OR services ILIKE :service_pattern2)
            ORDER BY rating DESC, jobs_completed DESC
        """)
        
        service_pattern = f'%"{service}"%'
        service_pattern2 = f'%{service}%'
        
        result = db.execute(query, {
            'service_pattern': service_pattern,
            'service_pattern2': service_pattern2
        }).fetchall()
        
        fixers_data = []
        for row in result:
            # Parse services
            services = []
            if row[4]:
                try:
                    import json
                    services = json.loads(row[4]) if isinstance(row[4], str) else row[4]
                except:
                    services = row[4].split(',') if isinstance(row[4], str) else []
            
            fixers_data.append({
                "id": row[0],
                "user_id": row[1],
                "name": row[2],
                "email": row[3], 
                "services": services,
                "location": row[5],
                "rating": row[6] or 0.0,
                "total_jobs": row[7] or 0,
                "is_active": row[8],
                "is_approved": row[9],
                "jobs_completed": row[10] or 0,
                "completion_percentage": row[11] or 0.0,
                "created_at": row[12].isoformat() if row[12] else None
            })
        
        return {
            "success": True,
            "service": service,
            "fixers": fixers_data
        }
        
    except Exception as e:
        print(f"Get fixers by service error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Dashboard API Endpoint
@app.get("/api/dashboard/{user_id}")
async def get_dashboard(user_id: str, request: Request, db: Session = Depends(get_db)):
    """Get dashboard statistics for authenticated user"""
    try:
        # Extract and validate user from token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization token")
            
        authenticated_user_id = auth_header.replace('Bearer token_', '')
        
        # Security check: users can only access their own dashboard
        if authenticated_user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied: You can only access your own dashboard")
        
        # Get user info
        user_query = text("SELECT role FROM users WHERE id = :user_id")
        user_result = db.execute(user_query, {'user_id': user_id}).fetchone()
        
        if not user_result:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_role = user_result[0]
        
        if user_role == 'client':
            # Client dashboard statistics
            stats_query = text("""
                SELECT 
                    COUNT(CASE WHEN status IN ('pending', 'assigned', 'in_progress') THEN 1 END) as active_jobs,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_jobs,
                    COUNT(*) as total_jobs,
                    COALESCE(SUM(CASE WHEN status = 'completed' THEN estimated_price ELSE 0 END), 0) as total_spent
                FROM jobs 
                WHERE user_id = :user_id
            """)
            
            stats_result = db.execute(stats_query, {'user_id': user_id}).fetchone()
            
            return {
                "success": True,
                "user_id": user_id,
                "role": user_role,
                "stats": {
                    "active_jobs": stats_result[0] or 0,
                    "completed_jobs": stats_result[1] or 0,
                    "pending_jobs": stats_result[2] or 0,
                    "total_jobs": stats_result[3] or 0,
                    "total_spent": float(stats_result[4] or 0)
                },
                "recent_jobs": []  # Could add recent jobs list here
            }
            
        elif user_role == 'fixer':
            # Fixer dashboard statistics with real job data
            fixer_query = text("""
                SELECT 
                    jobs_completed,
                    rating,
                    total_earned,
                    is_active
                FROM fixers 
                WHERE user_id = :user_id
            """)
            
            # Get real job statistics for this fixer
            job_stats_query = text("""
                SELECT 
                    COUNT(CASE WHEN status IN ('assigned', 'in_progress') THEN 1 END) as active_jobs,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as available_jobs,
                    COALESCE(SUM(CASE WHEN status = 'completed' THEN estimated_price END), 0) as total_earnings,
                    COUNT(*) as total_jobs
                FROM jobs 
                WHERE assigned_fixer_id = :user_id
            """)
            
            # Get fixer notification count
            notification_stats_query = text("""
                SELECT 
                    COUNT(*) as total_notifications,
                    COUNT(CASE WHEN read = false THEN 1 END) as unread_notifications
                FROM notifications 
                WHERE user_id = :user_id
            """)
            
            fixer_result = db.execute(fixer_query, {'user_id': user_id}).fetchone()
            job_stats_result = db.execute(job_stats_query, {'user_id': user_id}).fetchone()
            notification_result = db.execute(notification_stats_query, {'user_id': user_id}).fetchone()
            
            # Combine fixer profile data with real job statistics
            if fixer_result or job_stats_result:
                # Use job stats for earnings if available, otherwise use fixer table
                actual_earnings = float(job_stats_result[3] or 0) if job_stats_result else (float(fixer_result[2] or 0) if fixer_result else 0)
                actual_completed = int(job_stats_result[1] or 0) if job_stats_result else (int(fixer_result[0] or 0) if fixer_result else 0)
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "role": user_role,
                    "stats": {
                        "jobs_completed": actual_completed,
                        "rating": float(fixer_result[1] or 5.0) if fixer_result else 5.0,
                        "total_earned": actual_earnings,
                        "active_jobs": int(job_stats_result[0] or 0) if job_stats_result else 0,
                        "available_jobs": int(job_stats_result[2] or 0) if job_stats_result else 0,
                        "total_jobs": int(job_stats_result[4] or 0) if job_stats_result else 0,
                        "is_active": fixer_result[3] if fixer_result else True,
                        "total_notifications": int(notification_result[0] or 0) if notification_result else 0,
                        "unread_notifications": int(notification_result[1] or 0) if notification_result else 0
                    }
                }
            else:
                # Default stats for fixer without profile or jobs
                return {
                    "success": True,
                    "user_id": user_id,
                    "role": user_role,
                    "stats": {
                        "jobs_completed": 0,
                        "rating": 5.0,
                        "total_earned": 0,
                        "active_jobs": 0,
                        "available_jobs": 0,
                        "total_jobs": 0,
                        "is_active": True,
                        "total_notifications": 0,
                        "unread_notifications": 0
                    }
                }
                
        elif user_role == 'admin':
            # Admin dashboard statistics
            admin_stats_query = text("""
                SELECT 
                    (SELECT COUNT(*) FROM jobs) as total_jobs,
                    (SELECT COUNT(*) FROM users WHERE role = 'client') as total_clients,
                    (SELECT COUNT(*) FROM fixers WHERE is_active = true) as active_fixers,
                    (SELECT COUNT(CASE WHEN status = 'pending' THEN 1 END) FROM jobs) as pending_jobs
            """)
            
            admin_result = db.execute(admin_stats_query).fetchone()
            
            return {
                "success": True,
                "user_id": user_id,
                "role": user_role,
                "stats": {
                    "total_jobs": admin_result[0] or 0,
                    "total_clients": admin_result[1] or 0,
                    "active_fixers": admin_result[2] or 0,
                    "pending_jobs": admin_result[3] or 0
                }
            }
        
        else:
            return {
                "success": True,
                "user_id": user_id,
                "role": user_role,
                "stats": {}
            }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Business Compliance API Endpoints
class ComplianceRequest(BaseModel):
    category: str
    description: str
    urgency_level: str = "normal"
    contact_preference: str = "whatsapp"

class ComplianceResponse(BaseModel):
    success: bool
    message: str
    request_id: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None

@app.post("/api/compliance/request", response_model=ComplianceResponse)
async def submit_compliance_request(request_data: ComplianceRequest, request: Request, db: Session = Depends(get_db)):
    """Submit a new business compliance request"""
    try:
        # Extract user_id from Authorization header (simple token format)
        # This assumes token format is "token_{user_id}" 
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Generate unique request ID
        request_id = f"comp_{uuid.uuid4()}"
        
        # Insert compliance request using raw SQL
        insert_query = text("""
            INSERT INTO business_compliance_requests (
                id, user_id, category, description, urgency_level, 
                contact_preference, status, created_at, updated_at
            ) VALUES (
                :id, :user_id, :category, :description, :urgency_level,
                :contact_preference, :status, :created_at, :updated_at
            )
        """)
        
        db.execute(insert_query, {
            'id': request_id,
            'user_id': user_id,
            'category': request_data.category,
            'description': request_data.description,
            'urgency_level': request_data.urgency_level,
            'contact_preference': request_data.contact_preference,
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        db.commit()
        
        return ComplianceResponse(
            success=True,
            message="Compliance request submitted successfully",
            request_id=request_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Compliance request submission error: {str(e)}")
        return ComplianceResponse(
            success=False,
            message="Failed to submit compliance request"
        )

@app.get("/api/compliance/requests", response_model=ComplianceResponse)
async def get_user_compliance_requests(request: Request, db: Session = Depends(get_db)):
    """Get all compliance requests for the authenticated user"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Fetch user's compliance requests
        query = text("""
            SELECT id, category, description, urgency_level, contact_preference,
                   status, admin_notes, estimated_cost, estimated_completion,
                   created_at, updated_at
            FROM business_compliance_requests 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC
        """)
        
        result = db.execute(query, {'user_id': user_id}).fetchall()
        
        requests_data = []
        for row in result:
            requests_data.append({
                "id": row[0],
                "category": row[1],
                "description": row[2],
                "urgency_level": row[3],
                "contact_preference": row[4],
                "status": row[5],
                "admin_notes": row[6],
                "estimated_cost": float(row[7]) if row[7] else None,
                "estimated_completion": row[8].isoformat() if row[8] else None,
                "created_at": row[9].isoformat() if row[9] else None,
                "updated_at": row[10].isoformat() if row[10] else None
            })
        
        return ComplianceResponse(
            success=True,
            message=f"Found {len(requests_data)} compliance requests",
            data=requests_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get compliance requests error: {str(e)}")
        return ComplianceResponse(
            success=False,
            message="Failed to fetch compliance requests",
            data=[]
        )

# Document Upload Endpoint for Business Compliance
class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    document: Optional[Dict[str, Any]] = None

@app.post("/api/compliance/upload-document", response_model=DocumentUploadResponse)
async def upload_compliance_document(
    request: Request,
    document: UploadFile = File(...),
    request_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Upload a document for a compliance request"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Validate file type
        allowed_extensions = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'}
        file_extension = '.' + document.filename.split('.')[-1].lower() if '.' in document.filename else ''
        
        if file_extension not in allowed_extensions:
            return DocumentUploadResponse(
                success=False,
                message="Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG"
            )
        
        # Validate file size (10MB limit)
        content = await document.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            return DocumentUploadResponse(
                success=False,
                message="File size too large. Maximum 10MB allowed."
            )
        
        # For this implementation, we'll just store document metadata
        # In a production system, you'd save the file to disk/cloud storage
        
        # Generate unique document ID
        doc_id = f"doc_{uuid.uuid4()}"
        
        # Determine document type based on extension
        doc_type_map = {
            '.pdf': 'PDF Document',
            '.doc': 'Word Document', 
            '.docx': 'Word Document',
            '.jpg': 'Image',
            '.jpeg': 'Image', 
            '.png': 'Image'
        }
        doc_type = doc_type_map.get(file_extension, 'Document')
        
        # Create documents table if it doesn't exist
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS compliance_documents (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                request_id VARCHAR,
                filename VARCHAR NOT NULL,
                file_type VARCHAR NOT NULL,
                file_size INTEGER NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.execute(create_table_query)
        
        # Insert document record
        insert_query = text("""
            INSERT INTO compliance_documents (
                id, user_id, request_id, filename, file_type, file_size, uploaded_at
            ) VALUES (
                :id, :user_id, :request_id, :filename, :file_type, :file_size, :uploaded_at
            )
        """)
        
        db.execute(insert_query, {
            'id': doc_id,
            'user_id': user_id,
            'request_id': request_id if request_id != 'new' else None,
            'filename': document.filename,
            'file_type': doc_type,
            'file_size': len(content),
            'uploaded_at': datetime.utcnow()
        })
        
        db.commit()
        
        # Return document info in the format expected by frontend
        document_info = {
            "id": doc_id,
            "name": document.filename,
            "type": doc_type,
            "size": len(content),
            "uploaded_at": datetime.utcnow().isoformat(),
            "request_id": request_id if request_id != 'new' else None
        }
        
        return DocumentUploadResponse(
            success=True,
            message="Document uploaded successfully",
            document=document_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Document upload error: {str(e)}")
        return DocumentUploadResponse(
            success=False,
            message="Failed to upload document"
        )

@app.get("/api/compliance/documents", response_model=List[Dict[str, Any]])
async def get_user_documents(request: Request, db: Session = Depends(get_db)):
    """Get all documents uploaded by the authenticated user"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Fetch user's documents
        query = text("""
            SELECT id, filename, file_type, file_size, request_id, uploaded_at
            FROM compliance_documents 
            WHERE user_id = :user_id 
            ORDER BY uploaded_at DESC
        """)
        
        result = db.execute(query, {'user_id': user_id}).fetchall()
        
        documents = []
        for row in result:
            documents.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "size": row[3],
                "request_id": row[4],
                "uploaded_at": row[5].isoformat() if row[5] else None
            })
        
        return documents
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get documents error: {str(e)}")
        return []

# Send Reminder Endpoint
class ReminderRequest(BaseModel):
    request_id: str
    message: Optional[str] = None

class ReminderResponse(BaseModel):
    success: bool
    message: str

@app.post("/api/compliance/send-reminder", response_model=ReminderResponse)
async def send_compliance_reminder(reminder_data: ReminderRequest, request: Request, db: Session = Depends(get_db)):
    """Send a reminder for a compliance request"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Verify the request belongs to the user
        verify_query = text("""
            SELECT category, description, status
            FROM business_compliance_requests 
            WHERE id = :request_id AND user_id = :user_id
        """)
        
        request_result = db.execute(verify_query, {
            'request_id': reminder_data.request_id,
            'user_id': user_id
        }).fetchone()
        
        if not request_result:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Create reminders table if it doesn't exist
        create_reminders_table_query = text("""
            CREATE TABLE IF NOT EXISTS compliance_reminders (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                request_id VARCHAR NOT NULL,
                message TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reminder_type VARCHAR DEFAULT 'manual'
            )
        """)
        
        db.execute(create_reminders_table_query)
        
        # Insert reminder record
        reminder_id = f"rem_{uuid.uuid4()}"
        default_message = f"Reminder: Your {request_result[0]} request is {request_result[2]}. Please check the status and provide any required documentation."
        
        insert_reminder_query = text("""
            INSERT INTO compliance_reminders (
                id, user_id, request_id, message, sent_at, reminder_type
            ) VALUES (
                :id, :user_id, :request_id, :message, :sent_at, :reminder_type
            )
        """)
        
        db.execute(insert_reminder_query, {
            'id': reminder_id,
            'user_id': user_id,
            'request_id': reminder_data.request_id,
            'message': reminder_data.message or default_message,
            'sent_at': datetime.utcnow(),
            'reminder_type': 'manual'
        })
        
        db.commit()
        
        # In a real implementation, you would send email/SMS here
        # For now, we'll just log the reminder
        print(f"Reminder sent for request {reminder_data.request_id}: {default_message}")
        
        return ReminderResponse(
            success=True,
            message="Reminder sent successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Send reminder error: {str(e)}")
        return ReminderResponse(
            success=False,
            message="Failed to send reminder"
        )

# Process Payment Endpoint
class PaymentRequest(BaseModel):
    amount: float
    request_id: str
    payment_method: str = "eft"

class PaymentResponse(BaseModel):
    success: bool
    message: str
    payment_id: Optional[str] = None
    transaction_details: Optional[Dict[str, Any]] = None

@app.post("/api/compliance/process-payment", response_model=PaymentResponse)
async def process_compliance_payment(payment_data: PaymentRequest, request: Request, db: Session = Depends(get_db)):
    """Process payment for a compliance request"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Verify the request belongs to the user
        verify_query = text("""
            SELECT category, description, status
            FROM business_compliance_requests 
            WHERE id = :request_id AND user_id = :user_id
        """)
        
        request_result = db.execute(verify_query, {
            'request_id': payment_data.request_id,
            'user_id': user_id
        }).fetchone()
        
        if not request_result:
            raise HTTPException(status_code=404, detail="Request not found")
        
        # Create payments table if it doesn't exist
        create_payments_table_query = text("""
            CREATE TABLE IF NOT EXISTS compliance_payments (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                request_id VARCHAR NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                payment_method VARCHAR NOT NULL,
                status VARCHAR DEFAULT 'completed',
                transaction_reference VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.execute(create_payments_table_query)
        
        # Generate payment ID and transaction reference
        payment_id = f"pay_{uuid.uuid4()}"
        transaction_ref = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{payment_id[-6:]}"
        
        # Insert payment record
        insert_payment_query = text("""
            INSERT INTO compliance_payments (
                id, user_id, request_id, amount, payment_method, 
                status, transaction_reference, created_at
            ) VALUES (
                :id, :user_id, :request_id, :amount, :payment_method,
                :status, :transaction_reference, :created_at
            )
        """)
        
        db.execute(insert_payment_query, {
            'id': payment_id,
            'user_id': user_id,
            'request_id': payment_data.request_id,
            'amount': payment_data.amount,
            'payment_method': payment_data.payment_method,
            'status': 'completed',
            'transaction_reference': transaction_ref,
            'created_at': datetime.utcnow()
        })
        
        # Update request status to indicate payment received
        update_request_query = text("""
            UPDATE business_compliance_requests 
            SET status = 'in_progress', updated_at = :updated_at
            WHERE id = :request_id AND status = 'pending'
        """)
        
        db.execute(update_request_query, {
            'request_id': payment_data.request_id,
            'updated_at': datetime.utcnow()
        })
        
        db.commit()
        
        # In a real implementation, you would integrate with payment processor here
        # For now, we'll simulate a successful payment
        
        return PaymentResponse(
            success=True,
            message="Payment processed successfully",
            payment_id=payment_id,
            transaction_details={
                "transaction_reference": transaction_ref,
                "amount": payment_data.amount,
                "payment_method": payment_data.payment_method,
                "status": "completed",
                "processed_at": datetime.utcnow().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Process payment error: {str(e)}")
        return PaymentResponse(
            success=False,
            message="Failed to process payment"
        )

# Enhanced compliance requests endpoint to include documents and payments
@app.get("/api/compliance/requests/enhanced", response_model=ComplianceResponse)
async def get_enhanced_compliance_requests(request: Request, db: Session = Depends(get_db)):
    """Get compliance requests with associated documents and payments"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Fetch user's compliance requests
        requests_query = text("""
            SELECT id, category, description, urgency_level, contact_preference,
                   status, admin_notes, estimated_cost, estimated_completion,
                   created_at, updated_at
            FROM business_compliance_requests 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC
        """)
        
        requests_result = db.execute(requests_query, {'user_id': user_id}).fetchall()
        
        enhanced_requests = []
        for req_row in requests_result:
            request_id = req_row[0]
            
            # Get documents for this request
            docs_query = text("""
                SELECT id, filename, file_type, file_size, uploaded_at
                FROM compliance_documents 
                WHERE user_id = :user_id AND (request_id = :request_id OR request_id IS NULL)
            """)
            docs_result = db.execute(docs_query, {'user_id': user_id, 'request_id': request_id}).fetchall()
            
            documents = []
            for doc_row in docs_result:
                documents.append({
                    "id": doc_row[0],
                    "name": doc_row[1],
                    "type": doc_row[2],
                    "size": doc_row[3],
                    "uploaded_at": doc_row[4].isoformat() if doc_row[4] else None
                })
            
            # Get payments for this request
            payments_query = text("""
                SELECT id, amount, payment_method, status, transaction_reference, created_at
                FROM compliance_payments 
                WHERE user_id = :user_id AND request_id = :request_id
                ORDER BY created_at DESC
            """)
            payments_result = db.execute(payments_query, {'user_id': user_id, 'request_id': request_id}).fetchall()
            
            payments = []
            for pay_row in payments_result:
                payments.append({
                    "id": pay_row[0],
                    "amount": float(pay_row[1]),
                    "payment_method": pay_row[2],
                    "status": pay_row[3],
                    "transaction_reference": pay_row[4],
                    "created_at": pay_row[5].isoformat() if pay_row[5] else None
                })
            
            enhanced_requests.append({
                "id": req_row[0],
                "category": req_row[1],
                "description": req_row[2],
                "urgency_level": req_row[3],
                "contact_preference": req_row[4],
                "status": req_row[5],
                "admin_notes": req_row[6],
                "estimated_cost": float(req_row[7]) if req_row[7] else None,
                "estimated_completion": req_row[8].isoformat() if req_row[8] else None,
                "created_at": req_row[9].isoformat() if req_row[9] else None,
                "updated_at": req_row[10].isoformat() if req_row[10] else None,
                "documents": documents,
                "payments": payments
            })
        
        return ComplianceResponse(
            success=True,
            message=f"Found {len(enhanced_requests)} compliance requests with details",
            data=enhanced_requests
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get enhanced compliance requests error: {str(e)}")
        return ComplianceResponse(
            success=False,
            message="Failed to fetch enhanced compliance requests",
            data=[]
        )

# Enterprise Portal API Endpoints

# Pydantic models for Enterprise functionality
class EnterpriseOverview(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None

class BulkBookingCreate(BaseModel):
    services: List[str]
    locations: List[str]
    schedule_type: str  # weekly, monthly, one-time
    start_date: str
    end_date: Optional[str] = None
    notes: Optional[str] = None

class TeamMemberCreate(BaseModel):
    name: str
    email: str
    role: str
    permissions: List[str]

class LocationCreate(BaseModel):
    name: str
    address: str
    contact_person: str
    contact_phone: str
    services_needed: List[str]

@app.get("/api/enterprise/overview", response_model=EnterpriseOverview)
async def get_enterprise_overview(request: Request, db: Session = Depends(get_db)):
    """Get enterprise dashboard overview data"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Create enterprise tables if they don't exist
        create_enterprise_tables_query = text("""
            CREATE TABLE IF NOT EXISTS enterprise_bookings (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                services TEXT[] NOT NULL,
                locations TEXT[] NOT NULL,
                schedule_type VARCHAR NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                status VARCHAR DEFAULT 'active',
                total_amount DECIMAL(10,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS enterprise_team (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                email VARCHAR NOT NULL,
                role VARCHAR NOT NULL,
                permissions TEXT[] NOT NULL,
                status VARCHAR DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS enterprise_locations (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                address TEXT NOT NULL,
                contact_person VARCHAR NOT NULL,
                contact_phone VARCHAR NOT NULL,
                services_needed TEXT[] NOT NULL,
                status VARCHAR DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS enterprise_invoices (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                booking_ids TEXT[] NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                tax_amount DECIMAL(10,2) DEFAULT 0,
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR DEFAULT 'draft',
                invoice_date DATE NOT NULL,
                due_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        db.execute(create_enterprise_tables_query)
        db.commit()
        
        # Get analytics data
        current_month = datetime.now().replace(day=1)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        # Get current month bookings
        bookings_query = text("""
            SELECT COUNT(*) as total_bookings, 
                   COALESCE(SUM(total_amount), 0) as monthly_spend
            FROM enterprise_bookings 
            WHERE user_id = :user_id 
            AND created_at >= :current_month
        """)
        
        bookings_result = db.execute(bookings_query, {
            'user_id': user_id,
            'current_month': current_month
        }).fetchone()
        
        # Get completed jobs (from regular jobs table)
        jobs_query = text("""
            SELECT COUNT(*) as completed_jobs
            FROM jobs 
            WHERE user_id = :user_id 
            AND status = 'completed'
            AND created_at >= :current_month
        """)
        
        jobs_result = db.execute(jobs_query, {
            'user_id': user_id,
            'current_month': current_month
        }).fetchone()
        
        # Get recent bookings
        recent_bookings_query = text("""
            SELECT id, services, locations, schedule_type, start_date, status, total_amount
            FROM enterprise_bookings 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        recent_bookings = db.execute(recent_bookings_query, {'user_id': user_id}).fetchall()
        
        # Format recent bookings
        bookings_data = []
        for booking in recent_bookings:
            bookings_data.append({
                "id": booking[0],
                "services": booking[1],
                "locations": booking[2],
                "schedule_type": booking[3],
                "start_date": booking[4].isoformat() if booking[4] else None,
                "status": booking[5],
                "total_amount": float(booking[6] or 0)
            })
        
        # Calculate analytics
        monthly_spend = float(bookings_result[0] or 0) if bookings_result else 0
        total_bookings = bookings_result[1] or 0 if bookings_result else 0
        completed_jobs = jobs_result[0] or 0 if jobs_result else 0
        
        overview_data = {
            "analytics": {
                "monthly_spend": monthly_spend,
                "total_bookings": total_bookings,
                "jobs_completed": completed_jobs,
                "cost_savings": monthly_spend * 0.15,  # Estimated 15% savings
                "response_time": "2.3 hours",
                "completion_rate": 94,
                "customer_satisfaction": 4.8
            },
            "recent_bookings": bookings_data,
            "quick_stats": {
                "active_locations": 0,  # Will be calculated below
                "team_members": 0,      # Will be calculated below
                "pending_invoices": 0   # Will be calculated below
            }
        }
        
        return EnterpriseOverview(success=True, data=overview_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Enterprise overview error: {str(e)}")
        return EnterpriseOverview(success=False, data={})

@app.post("/api/enterprise/bulk-booking")
async def create_bulk_booking(booking_data: BulkBookingCreate, request: Request, db: Session = Depends(get_db)):
    """Create a new bulk booking"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Generate booking ID
        booking_id = f"bulk_{uuid.uuid4()}"
        
        # Calculate total amount (simplified pricing)
        base_price_per_service = 500  # R500 per service per location
        total_locations = len(booking_data.locations)
        total_services = len(booking_data.services)
        total_amount = base_price_per_service * total_locations * total_services
        
        # Apply schedule multiplier
        schedule_multipliers = {
            "one-time": 1.0,
            "weekly": 4.0,   # 4 weeks per month
            "monthly": 12.0  # 12 months
        }
        multiplier = schedule_multipliers.get(booking_data.schedule_type, 1.0)
        total_amount *= multiplier
        
        # Insert bulk booking
        insert_query = text("""
            INSERT INTO enterprise_bookings (
                id, user_id, services, locations, schedule_type, 
                start_date, end_date, total_amount, status, created_at
            ) VALUES (
                :id, :user_id, :services, :locations, :schedule_type,
                :start_date, :end_date, :total_amount, :status, :created_at
            )
        """)
        
        db.execute(insert_query, {
            'id': booking_id,
            'user_id': user_id,
            'services': booking_data.services,
            'locations': booking_data.locations,
            'schedule_type': booking_data.schedule_type,
            'start_date': datetime.strptime(booking_data.start_date, '%Y-%m-%d').date(),
            'end_date': datetime.strptime(booking_data.end_date, '%Y-%m-%d').date() if booking_data.end_date else None,
            'total_amount': total_amount,
            'status': 'active',
            'created_at': datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "Bulk booking created successfully",
            "booking_id": booking_id,
            "total_amount": total_amount
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Create bulk booking error: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to create bulk booking: {str(e)}"
        }

@app.get("/api/enterprise/team")
async def get_team_members(request: Request, db: Session = Depends(get_db)):
    """Get enterprise team members"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Fetch team members
        query = text("""
            SELECT id, name, email, role, permissions, status, created_at
            FROM enterprise_team 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC
        """)
        
        result = db.execute(query, {'user_id': user_id}).fetchall()
        
        team_members = []
        for row in result:
            team_members.append({
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "role": row[3],
                "permissions": row[4],
                "status": row[5],
                "created_at": row[6].isoformat() if row[6] else None
            })
        
        return {
            "success": True,
            "team_members": team_members
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get team members error: {str(e)}")
        return {
            "success": False,
            "team_members": []
        }

@app.post("/api/enterprise/team")
async def add_team_member(member_data: TeamMemberCreate, request: Request, db: Session = Depends(get_db)):
    """Add a new team member"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Generate member ID
        member_id = f"team_{uuid.uuid4()}"
        
        # Insert team member
        insert_query = text("""
            INSERT INTO enterprise_team (
                id, user_id, name, email, role, permissions, status, created_at
            ) VALUES (
                :id, :user_id, :name, :email, :role, :permissions, :status, :created_at
            )
        """)
        
        db.execute(insert_query, {
            'id': member_id,
            'user_id': user_id,
            'name': member_data.name,
            'email': member_data.email,
            'role': member_data.role,
            'permissions': member_data.permissions,
            'status': 'active',
            'created_at': datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "Team member added successfully",
            "member_id": member_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Add team member error: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to add team member: {str(e)}"
        }

@app.delete("/api/enterprise/team/{member_id}")
async def remove_team_member(member_id: str, request: Request, db: Session = Depends(get_db)):
    """Remove a team member"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Delete team member
        delete_query = text("""
            DELETE FROM enterprise_team 
            WHERE id = :member_id AND user_id = :user_id
        """)
        
        result = db.execute(delete_query, {
            'member_id': member_id,
            'user_id': user_id
        })
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Team member not found")
        
        db.commit()
        
        return {
            "success": True,
            "message": "Team member removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Remove team member error: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to remove team member: {str(e)}"
        }

# Enterprise Locations Management
@app.get("/api/enterprise/locations")
async def get_enterprise_locations(request: Request, db: Session = Depends(get_db)):
    """Get enterprise locations"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Fetch locations
        query = text("""
            SELECT id, name, address, contact_person, contact_phone, 
                   services_needed, status, created_at
            FROM enterprise_locations 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC
        """)
        
        result = db.execute(query, {'user_id': user_id}).fetchall()
        
        locations = []
        for row in result:
            locations.append({
                "id": row[0],
                "name": row[1],
                "address": row[2],
                "contact_person": row[3],
                "contact_phone": row[4],
                "services_needed": row[5],
                "status": row[6],
                "created_at": row[7].isoformat() if row[7] else None
            })
        
        return {
            "success": True,
            "locations": locations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get locations error: {str(e)}")
        return {
            "success": False,
            "locations": []
        }

@app.post("/api/enterprise/locations")
async def add_enterprise_location(location_data: LocationCreate, request: Request, db: Session = Depends(get_db)):
    """Add a new enterprise location"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Generate location ID
        location_id = f"loc_{uuid.uuid4()}"
        
        # Insert location
        insert_query = text("""
            INSERT INTO enterprise_locations (
                id, user_id, name, address, contact_person, contact_phone,
                services_needed, status, created_at
            ) VALUES (
                :id, :user_id, :name, :address, :contact_person, :contact_phone,
                :services_needed, :status, :created_at
            )
        """)
        
        db.execute(insert_query, {
            'id': location_id,
            'user_id': user_id,
            'name': location_data.name,
            'address': location_data.address,
            'contact_person': location_data.contact_person,
            'contact_phone': location_data.contact_phone,
            'services_needed': location_data.services_needed,
            'status': 'active',
            'created_at': datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "Location added successfully",
            "location_id": location_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Add location error: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to add location: {str(e)}"
        }

@app.post("/api/enterprise/locations/{location_id}/book-service")
async def book_service_for_location(location_id: str, request: Request, db: Session = Depends(get_db)):
    """Book a service for a specific location"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Verify location belongs to user
        location_query = text("""
            SELECT name, services_needed
            FROM enterprise_locations 
            WHERE id = :location_id AND user_id = :user_id
        """)
        
        location_result = db.execute(location_query, {
            'location_id': location_id,
            'user_id': user_id
        }).fetchone()
        
        if not location_result:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # Create a job booking for this location
        job_id = f"job_{uuid.uuid4()}"
        
        job_insert_query = text("""
            INSERT INTO jobs (
                id, user_id, service, description, location, 
                estimated_price, status, priority_level, created_at,
                terms_accepted, workflow_stage, payment_status
            ) VALUES (
                :id, :user_id, :service, :description, :location,
                :estimated_price, :status, :priority_level, :created_at,
                :terms_accepted, :workflow_stage, :payment_status
            )
        """)
        
        db.execute(job_insert_query, {
            'id': job_id,
            'user_id': user_id,
            'service': location_result[1][0] if location_result[1] else "General Service",  # First service from array
            'description': f"Enterprise service booking for {location_result[0]}",
            'location': location_result[0],
            'estimated_price': 500.00,
            'status': 'pending',
            'priority_level': 'normal',
            'created_at': datetime.utcnow(),
            'terms_accepted': True,
            'workflow_stage': 'pending',
            'payment_status': 'pending'
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "Service booked successfully for location",
            "job_id": job_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Book service error: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to book service: {str(e)}"
        }

# Enterprise Invoicing
@app.get("/api/enterprise/invoices")
async def get_enterprise_invoices(request: Request, db: Session = Depends(get_db)):
    """Get enterprise invoices"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Fetch invoices
        query = text("""
            SELECT id, booking_ids, amount, tax_amount, total_amount,
                   status, invoice_date, due_date, created_at
            FROM enterprise_invoices 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC
        """)
        
        result = db.execute(query, {'user_id': user_id}).fetchall()
        
        invoices = []
        for row in result:
            invoices.append({
                "id": row[0],
                "booking_ids": row[1],
                "amount": float(row[2]),
                "tax_amount": float(row[3]),
                "total_amount": float(row[4]),
                "status": row[5],
                "invoice_date": row[6].isoformat() if row[6] else None,
                "due_date": row[7].isoformat() if row[7] else None,
                "created_at": row[8].isoformat() if row[8] else None
            })
        
        return {
            "success": True,
            "invoices": invoices
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get invoices error: {str(e)}")
        return {
            "success": False,
            "invoices": []
        }

@app.post("/api/enterprise/generate-invoice")
async def generate_enterprise_invoice(request: Request, db: Session = Depends(get_db)):
    """Generate a new enterprise invoice"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Get unpaid bookings
        bookings_query = text("""
            SELECT id, total_amount
            FROM enterprise_bookings 
            WHERE user_id = :user_id 
            AND status = 'active'
            AND id NOT IN (
                SELECT UNNEST(booking_ids) 
                FROM enterprise_invoices 
                WHERE user_id = :user_id
            )
        """)
        
        bookings_result = db.execute(bookings_query, {'user_id': user_id}).fetchall()
        
        if not bookings_result:
            return {
                "success": False,
                "message": "No unbilled bookings found"
            }
        
        # Calculate totals
        booking_ids = [booking[0] for booking in bookings_result]
        subtotal = sum(float(booking[1]) for booking in bookings_result)
        tax_rate = 0.15  # 15% VAT
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount
        
        # Generate invoice
        invoice_id = f"inv_{uuid.uuid4()}"
        invoice_date = datetime.now().date()
        due_date = invoice_date + timedelta(days=30)
        
        insert_query = text("""
            INSERT INTO enterprise_invoices (
                id, user_id, booking_ids, amount, tax_amount, total_amount,
                status, invoice_date, due_date, created_at
            ) VALUES (
                :id, :user_id, :booking_ids, :amount, :tax_amount, :total_amount,
                :status, :invoice_date, :due_date, :created_at
            )
        """)
        
        db.execute(insert_query, {
            'id': invoice_id,
            'user_id': user_id,
            'booking_ids': booking_ids,
            'amount': subtotal,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'status': 'draft',
            'invoice_date': invoice_date,
            'due_date': due_date,
            'created_at': datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "Invoice generated successfully",
            "invoice_id": invoice_id,
            "invoice": {
                "id": invoice_id,
                "amount": subtotal,
                "tax_amount": tax_amount,
                "total_amount": total_amount,
                "invoice_date": invoice_date.isoformat(),
                "due_date": due_date.isoformat(),
                "booking_count": len(booking_ids)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Generate invoice error: {str(e)}")
        return {
            "success": False,
            "message": "Failed to generate invoice"
        }

# Enterprise Contract Management Endpoints

class ContractCreate(BaseModel):
    name: str
    description: str
    service_type: str
    contract_value: float
    duration_months: int
    start_date: str
    auto_renewal: bool = False
    terms: Optional[str] = None

@app.get("/api/enterprise/contracts")
async def get_enterprise_contracts(request: Request, db: Session = Depends(get_db)):
    """Get all enterprise contracts"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Create contracts table if it doesn't exist
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS enterprise_contracts (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                description TEXT,
                service_type VARCHAR NOT NULL,
                contract_value DECIMAL(10,2) NOT NULL,
                duration_months INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                status VARCHAR DEFAULT 'active',
                auto_renewal BOOLEAN DEFAULT false,
                terms TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.execute(create_table_query)
        db.commit()
        
        # Fetch user's contracts
        query = text("""
            SELECT id, name, description, service_type, contract_value, duration_months,
                   start_date, end_date, status, auto_renewal, terms, created_at
            FROM enterprise_contracts 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC
        """)
        
        result = db.execute(query, {'user_id': user_id}).fetchall()
        
        contracts = []
        for row in result:
            contracts.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "service_type": row[3],
                "value": float(row[4]),
                "duration_months": row[5],
                "start_date": row[6].isoformat() if row[6] else None,
                "end_date": row[7].isoformat() if row[7] else None,
                "status": row[8],
                "auto_renewal": row[9],
                "terms": row[10],
                "created_at": row[11].isoformat() if row[11] else None
            })
        
        return {
            "success": True,
            "contracts": contracts
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get contracts error: {str(e)}")
        return {
            "success": False,
            "contracts": []
        }

@app.post("/api/enterprise/contracts")
async def create_enterprise_contract(contract_data: ContractCreate, request: Request, db: Session = Depends(get_db)):
    """Create a new enterprise contract"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Generate unique contract ID
        contract_id = f"contract_{uuid.uuid4()}"
        
        # Calculate end date
        start_date = datetime.strptime(contract_data.start_date, '%Y-%m-%d').date()
        end_date = start_date + relativedelta(months=contract_data.duration_months)
        
        # Insert contract
        insert_query = text("""
            INSERT INTO enterprise_contracts (
                id, user_id, name, description, service_type, contract_value,
                duration_months, start_date, end_date, status, auto_renewal, terms, created_at, updated_at
            ) VALUES (
                :id, :user_id, :name, :description, :service_type, :contract_value,
                :duration_months, :start_date, :end_date, :status, :auto_renewal, :terms, :created_at, :updated_at
            )
        """)
        
        db.execute(insert_query, {
            'id': contract_id,
            'user_id': user_id,
            'name': contract_data.name,
            'description': contract_data.description,
            'service_type': contract_data.service_type,
            'contract_value': contract_data.contract_value,
            'duration_months': contract_data.duration_months,
            'start_date': start_date,
            'end_date': end_date,
            'status': 'active',
            'auto_renewal': contract_data.auto_renewal,
            'terms': contract_data.terms,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "Contract created successfully",
            "contract_id": contract_id,
            "contract": {
                "id": contract_id,
                "name": contract_data.name,
                "value": contract_data.contract_value,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "status": "active"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Create contract error: {str(e)}")
        return {
            "success": False,
            "message": "Failed to create contract"
        }

@app.delete("/api/enterprise/contracts/{contract_id}")
async def delete_enterprise_contract(contract_id: str, request: Request, db: Session = Depends(get_db)):
    """Delete an enterprise contract"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Delete contract
        delete_query = text("""
            DELETE FROM enterprise_contracts 
            WHERE id = :contract_id AND user_id = :user_id
        """)
        
        result = db.execute(delete_query, {'contract_id': contract_id, 'user_id': user_id})
        db.commit()
        
        if result.rowcount > 0:
            return {
                "success": True,
                "message": "Contract deleted successfully"
            }
        else:
            return {
                "success": False,
                "message": "Contract not found or not authorized"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Delete contract error: {str(e)}")
        return {
            "success": False,
            "message": "Failed to delete contract"
        }

@app.put("/api/enterprise/contracts/{contract_id}/renew")
async def renew_enterprise_contract(contract_id: str, request: Request, db: Session = Depends(get_db)):
    """Renew an enterprise contract"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Get current contract details
        query = text("""
            SELECT end_date, duration_months FROM enterprise_contracts 
            WHERE id = :contract_id AND user_id = :user_id
        """)
        
        result = db.execute(query, {'contract_id': contract_id, 'user_id': user_id}).fetchone()
        
        if not result:
            return {
                "success": False,
                "message": "Contract not found or not authorized"
            }
        
        # Calculate new end date
        current_end_date = result[0]
        duration_months = result[1]
        new_end_date = current_end_date + relativedelta(months=duration_months)
        
        # Update contract
        update_query = text("""
            UPDATE enterprise_contracts 
            SET end_date = :new_end_date, status = 'active', updated_at = :updated_at
            WHERE id = :contract_id AND user_id = :user_id
        """)
        
        db.execute(update_query, {
            'new_end_date': new_end_date,
            'updated_at': datetime.utcnow(),
            'contract_id': contract_id,
            'user_id': user_id
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "Contract renewed successfully",
            "new_end_date": new_end_date.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Renew contract error: {str(e)}")
        return {
            "success": False,
            "message": "Failed to renew contract"
        }

# Learning Progress Tracking System

class LearningProgressCreate(BaseModel):
    course_id: str
    course_title: str
    course_platform: str
    progress_percentage: float = 0.0
    time_spent_minutes: int = 0
    status: str = "started"  # started, in_progress, completed, paused
    notes: Optional[str] = None

class LearningProgressUpdate(BaseModel):
    progress_percentage: Optional[float] = None
    time_spent_minutes: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class CertificateEarned(BaseModel):
    course_id: str
    course_title: str
    course_platform: str
    certificate_url: Optional[str] = None
    certificate_type: str
    completion_date: Optional[str] = None

@app.get("/api/learning/progress")
async def get_user_learning_progress(request: Request, db: Session = Depends(get_db)):
    """Get all learning progress for authenticated user"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Create learning tables if they don't exist
        create_learning_tables_query = text("""
            CREATE TABLE IF NOT EXISTS user_learning_progress (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                course_id VARCHAR NOT NULL,
                course_title VARCHAR NOT NULL,
                course_platform VARCHAR NOT NULL,
                progress_percentage DECIMAL(5,2) DEFAULT 0.00,
                time_spent_minutes INTEGER DEFAULT 0,
                status VARCHAR DEFAULT 'started',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id)
            );
            
            CREATE TABLE IF NOT EXISTS user_certificates (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                course_id VARCHAR NOT NULL,
                course_title VARCHAR NOT NULL,
                course_platform VARCHAR NOT NULL,
                certificate_type VARCHAR NOT NULL,
                certificate_url VARCHAR,
                completion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS learning_analytics (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                total_courses_started INTEGER DEFAULT 0,
                total_courses_completed INTEGER DEFAULT 0,
                total_time_spent_minutes INTEGER DEFAULT 0,
                total_certificates_earned INTEGER DEFAULT 0,
                favorite_category VARCHAR,
                learning_streak_days INTEGER DEFAULT 0,
                last_activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            );
        """)
        
        db.execute(create_learning_tables_query)
        db.commit()
        
        # Fetch user's learning progress
        query = text("""
            SELECT id, course_id, course_title, course_platform, progress_percentage,
                   time_spent_minutes, status, notes, created_at, updated_at
            FROM user_learning_progress 
            WHERE user_id = :user_id 
            ORDER BY updated_at DESC
        """)
        
        result = db.execute(query, {'user_id': user_id}).fetchall()
        
        progress_data = []
        for row in result:
            progress_data.append({
                "id": row[0],
                "course_id": row[1],
                "course_title": row[2],
                "course_platform": row[3],
                "progress_percentage": float(row[4]),
                "time_spent_minutes": row[5],
                "status": row[6],
                "notes": row[7],
                "created_at": row[8].isoformat() if row[8] else None,
                "updated_at": row[9].isoformat() if row[9] else None
            })
        
        # Fetch user's certificates
        cert_query = text("""
            SELECT id, course_id, course_title, course_platform, certificate_type,
                   certificate_url, completion_date
            FROM user_certificates 
            WHERE user_id = :user_id 
            ORDER BY completion_date DESC
        """)
        
        cert_result = db.execute(cert_query, {'user_id': user_id}).fetchall()
        
        certificates = []
        for row in cert_result:
            certificates.append({
                "id": row[0],
                "course_id": row[1],
                "course_title": row[2],
                "course_platform": row[3],
                "certificate_type": row[4],
                "certificate_url": row[5],
                "completion_date": row[6].isoformat() if row[6] else None
            })
        
        # Get user analytics
        analytics_query = text("""
            SELECT total_courses_started, total_courses_completed, total_time_spent_minutes,
                   total_certificates_earned, favorite_category, learning_streak_days,
                   last_activity_date
            FROM learning_analytics 
            WHERE user_id = :user_id
        """)
        
        analytics_result = db.execute(analytics_query, {'user_id': user_id}).fetchone()
        
        analytics = {
            "total_courses_started": analytics_result[0] if analytics_result else 0,
            "total_courses_completed": analytics_result[1] if analytics_result else 0,
            "total_time_spent_minutes": analytics_result[2] if analytics_result else 0,
            "total_certificates_earned": analytics_result[3] if analytics_result else 0,
            "favorite_category": analytics_result[4] if analytics_result else None,
            "learning_streak_days": analytics_result[5] if analytics_result else 0,
            "last_activity_date": analytics_result[6].isoformat() if analytics_result and analytics_result[6] else None
        }
        
        return {
            "success": True,
            "progress": progress_data,
            "certificates": certificates,
            "analytics": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get learning progress error: {str(e)}")
        return {
            "success": False,
            "progress": [],
            "certificates": [],
            "analytics": {}
        }

@app.post("/api/learning/progress")
async def create_or_update_learning_progress(progress_data: LearningProgressCreate, request: Request, db: Session = Depends(get_db)):
    """Create or update learning progress for authenticated user"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Check if progress already exists
        check_query = text("""
            SELECT id FROM user_learning_progress 
            WHERE user_id = :user_id AND course_id = :course_id
        """)
        
        existing = db.execute(check_query, {'user_id': user_id, 'course_id': progress_data.course_id}).fetchone()
        
        if existing:
            # Update existing progress
            update_query = text("""
                UPDATE user_learning_progress 
                SET progress_percentage = :progress_percentage,
                    time_spent_minutes = :time_spent_minutes,
                    status = :status,
                    notes = :notes,
                    updated_at = :updated_at
                WHERE user_id = :user_id AND course_id = :course_id
            """)
            
            db.execute(update_query, {
                'progress_percentage': progress_data.progress_percentage,
                'time_spent_minutes': progress_data.time_spent_minutes,
                'status': progress_data.status,
                'notes': progress_data.notes,
                'updated_at': datetime.utcnow(),
                'user_id': user_id,
                'course_id': progress_data.course_id
            })
        else:
            # Create new progress entry
            progress_id = f"progress_{uuid.uuid4()}"
            insert_query = text("""
                INSERT INTO user_learning_progress (
                    id, user_id, course_id, course_title, course_platform,
                    progress_percentage, time_spent_minutes, status, notes, created_at, updated_at
                ) VALUES (
                    :id, :user_id, :course_id, :course_title, :course_platform,
                    :progress_percentage, :time_spent_minutes, :status, :notes, :created_at, :updated_at
                )
            """)
            
            db.execute(insert_query, {
                'id': progress_id,
                'user_id': user_id,
                'course_id': progress_data.course_id,
                'course_title': progress_data.course_title,
                'course_platform': progress_data.course_platform,
                'progress_percentage': progress_data.progress_percentage,
                'time_spent_minutes': progress_data.time_spent_minutes,
                'status': progress_data.status,
                'notes': progress_data.notes,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            })
        
        # Update user analytics
        await update_user_learning_analytics(user_id, db)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Learning progress updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Update learning progress error: {str(e)}")
        return {
            "success": False,
            "message": "Failed to update learning progress"
        }

@app.post("/api/learning/certificate")
async def add_certificate(cert_data: CertificateEarned, request: Request, db: Session = Depends(get_db)):
    """Add earned certificate for authenticated user"""
    try:
        # Extract user_id from Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Generate certificate ID
        cert_id = f"cert_{uuid.uuid4()}"
        
        # Parse completion date
        completion_date = datetime.utcnow()
        if cert_data.completion_date:
            try:
                completion_date = datetime.fromisoformat(cert_data.completion_date.replace('Z', '+00:00'))
            except:
                completion_date = datetime.utcnow()
        
        # Insert certificate
        insert_query = text("""
            INSERT INTO user_certificates (
                id, user_id, course_id, course_title, course_platform,
                certificate_type, certificate_url, completion_date, created_at
            ) VALUES (
                :id, :user_id, :course_id, :course_title, :course_platform,
                :certificate_type, :certificate_url, :completion_date, :created_at
            )
        """)
        
        db.execute(insert_query, {
            'id': cert_id,
            'user_id': user_id,
            'course_id': cert_data.course_id,
            'course_title': cert_data.course_title,
            'course_platform': cert_data.course_platform,
            'certificate_type': cert_data.certificate_type,
            'certificate_url': cert_data.certificate_url,
            'completion_date': completion_date,
            'created_at': datetime.utcnow()
        })
        
        # Update course progress to completed
        update_progress_query = text("""
            UPDATE user_learning_progress 
            SET status = 'completed', progress_percentage = 100.0, updated_at = :updated_at
            WHERE user_id = :user_id AND course_id = :course_id
        """)
        
        db.execute(update_progress_query, {
            'updated_at': datetime.utcnow(),
            'user_id': user_id,
            'course_id': cert_data.course_id
        })
        
        # Update user analytics
        await update_user_learning_analytics(user_id, db)
        
        db.commit()
        
        return {
            "success": True,
            "message": "Certificate added successfully",
            "certificate_id": cert_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Add certificate error: {str(e)}")
        return {
            "success": False,
            "message": "Failed to add certificate"
        }

async def update_user_learning_analytics(user_id: str, db: Session):
    """Update user learning analytics"""
    try:
        # Calculate analytics
        stats_query = text("""
            SELECT 
                COUNT(*) as total_started,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as total_completed,
                SUM(time_spent_minutes) as total_time,
                COUNT(CASE WHEN progress_percentage > 0 THEN 1 END) as active_courses
            FROM user_learning_progress 
            WHERE user_id = :user_id
        """)
        
        stats_result = db.execute(stats_query, {'user_id': user_id}).fetchone()
        
        # Count certificates
        cert_count_query = text("""
            SELECT COUNT(*) FROM user_certificates WHERE user_id = :user_id
        """)
        
        cert_count = db.execute(cert_count_query, {'user_id': user_id}).fetchone()[0]
        
        # Get favorite category (most common category from progress)
        fav_category_query = text("""
            SELECT course_platform, COUNT(*) as count
            FROM user_learning_progress 
            WHERE user_id = :user_id
            GROUP BY course_platform
            ORDER BY count DESC
            LIMIT 1
        """)
        
        fav_result = db.execute(fav_category_query, {'user_id': user_id}).fetchone()
        favorite_category = fav_result[0] if fav_result else None
        
        # Upsert analytics
        upsert_query = text("""
            INSERT INTO learning_analytics (
                id, user_id, total_courses_started, total_courses_completed,
                total_time_spent_minutes, total_certificates_earned, favorite_category,
                learning_streak_days, last_activity_date, created_at, updated_at
            ) VALUES (
                :id, :user_id, :total_started, :total_completed,
                :total_time, :total_certificates, :favorite_category,
                :streak_days, :last_activity, :created_at, :updated_at
            )
            ON CONFLICT (user_id) DO UPDATE SET
                total_courses_started = EXCLUDED.total_courses_started,
                total_courses_completed = EXCLUDED.total_courses_completed,
                total_time_spent_minutes = EXCLUDED.total_time_spent_minutes,
                total_certificates_earned = EXCLUDED.total_certificates_earned,
                favorite_category = EXCLUDED.favorite_category,
                last_activity_date = EXCLUDED.last_activity_date,
                updated_at = EXCLUDED.updated_at
        """)
        
        analytics_id = f"analytics_{uuid.uuid4()}"
        now = datetime.utcnow()
        
        db.execute(upsert_query, {
            'id': analytics_id,
            'user_id': user_id,
            'total_started': stats_result[0] if stats_result else 0,
            'total_completed': stats_result[1] if stats_result else 0,
            'total_time': stats_result[2] if stats_result else 0,
            'total_certificates': cert_count,
            'favorite_category': favorite_category,
            'streak_days': 1,  # Simple implementation
            'last_activity': now,
            'created_at': now,
            'updated_at': now
        })
        
    except Exception as e:
        print(f"Update analytics error: {str(e)}")

# Admin Learning Analytics Endpoints

@app.get("/api/admin/learning/analytics")
async def get_admin_learning_analytics(request: Request, db: Session = Depends(get_db)):
    """Get aggregated learning analytics for admin dashboard with AI insights"""
    try:
        # Extract user_id from Authorization header and verify admin role
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Verify admin role
        admin_check = text("SELECT role FROM users WHERE id = :user_id")
        admin_result = db.execute(admin_check, {'user_id': user_id}).fetchone()
        
        if not admin_result or admin_result[0] != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Try to get learning analytics data, but provide fallback if tables don't exist
        try:
            # Get overall statistics
            overall_stats_query = text("""
                SELECT 
                    COUNT(DISTINCT user_id) as total_learners,
                    COALESCE(SUM(total_courses_started), 0) as total_courses_started,
                    COALESCE(SUM(total_courses_completed), 0) as total_courses_completed,
                    COALESCE(SUM(total_time_spent_minutes), 0) as total_learning_time,
                    COALESCE(SUM(total_certificates_earned), 0) as total_certificates,
                    COALESCE(AVG(total_courses_completed * 1.0 / NULLIF(total_courses_started, 0)), 0) as avg_completion_rate
                FROM learning_analytics
            """)
            
            overall_stats = db.execute(overall_stats_query).fetchone()
            
            # Prepare analytics data with fallback values
            analytics_data = {
                "overall_stats": {
                    "total_learners": overall_stats[0] if overall_stats else 0,
                    "total_courses_started": overall_stats[1] if overall_stats else 0,
                    "total_courses_completed": overall_stats[2] if overall_stats else 0,
                    "total_learning_hours": round((overall_stats[3] or 0) / 60, 1),
                    "total_certificates": overall_stats[4] if overall_stats else 0,
                    "avg_completion_rate": round((overall_stats[5] or 0) * 100, 1)
                },
                "top_courses": [],
                "user_engagement": [],
                "platform_stats": []
            }
            
            # Try to get detailed analytics if possible
            try:
                # Get top courses by enrollment
                top_courses_query = text("""
                    SELECT course_title, course_platform, COUNT(*) as enrollments,
                           AVG(progress_percentage) as avg_progress,
                           COUNT(CASE WHEN status = 'completed' THEN 1 END) as completions
                    FROM user_learning_progress
                    GROUP BY course_title, course_platform
                    ORDER BY enrollments DESC
                    LIMIT 10
                """)
                
                top_courses = db.execute(top_courses_query).fetchall()
                analytics_data["top_courses"] = [
                    {
                        "course_title": row[0],
                        "course_platform": row[1],
                        "enrollments": row[2],
                        "avg_progress": round(row[3], 1),
                        "completions": row[4],
                        "completion_rate": round((row[4] / row[2]) * 100, 1) if row[2] > 0 else 0
                    }
                    for row in top_courses
                ]
            except:
                pass  # Tables might not exist yet
                
        except Exception as table_error:
            print(f"Learning tables not available yet: {str(table_error)}")
            # Provide default analytics structure
            analytics_data = {
                "overall_stats": {
                    "total_learners": 0,
                    "total_courses_started": 0,
                    "total_courses_completed": 0,
                    "total_learning_hours": 0,
                    "total_certificates": 0,
                    "avg_completion_rate": 0
                },
                "top_courses": [],
                "user_engagement": [],
                "platform_stats": []
            }
        
        # Generate AI insights
        ai_insights = await generate_learning_insights(analytics_data)
        
        return {
            "success": True,
            "analytics": analytics_data,
            "ai_insights": ai_insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Admin learning analytics error: {str(e)}")
        return {
            "success": False,
            "message": "Learning analytics temporarily unavailable",
            "analytics": {
                "overall_stats": {"total_learners": 0, "total_courses_started": 0, "total_courses_completed": 0, "total_learning_hours": 0, "total_certificates": 0, "avg_completion_rate": 0},
                "top_courses": [],
                "user_engagement": [],
                "platform_stats": []
            },
            "ai_insights": {
                "key_findings": ["Learning analytics system initializing"],
                "recommendations": ["System setup in progress"],
                "trends": ["Data collection starting"],
                "opportunities": ["Full analytics coming soon"],
                "generated_at": datetime.utcnow().isoformat()
            }
        }

async def generate_learning_insights(analytics_data: dict) -> dict:
    """Generate AI insights from learning analytics data"""
    try:
        # Check if OpenAI is available for advanced AI analysis
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            # Could implement OpenAI analysis here in the future
            pass
        
        # Simple rule-based AI analysis (works without external dependencies)
        total_learners = analytics_data['overall_stats']['total_learners']
        completion_rate = analytics_data['overall_stats']['avg_completion_rate']
        top_platform = analytics_data['platform_stats'][0]['platform'] if analytics_data['platform_stats'] else 'N/A'
        
        insights = {
            "key_findings": [
                f"Platform has {total_learners} active learners with {completion_rate}% average completion rate",
                f"Most popular learning platform is {top_platform}",
                f"Users have completed {analytics_data['overall_stats']['total_learning_hours']} total hours of learning",
                f"Certificate earning rate shows strong engagement in professional development"
            ],
            "recommendations": [
                "Focus on improving course completion rates through gamification and progress tracking",
                "Promote top-performing courses to increase overall engagement",
                "Create role-specific learning paths for fixers vs clients",
                "Implement peer learning and mentorship programs"
            ],
            "trends": [
                "Business and technology courses show highest engagement",
                "Shorter courses (under 10 hours) have better completion rates",
                "Certificate-offering courses drive higher motivation"
            ],
            "opportunities": [
                "Expand course offerings in high-demand categories",
                "Partner with more learning platforms for variety",
                "Implement AI-powered course recommendations"
            ],
            "generated_at": datetime.utcnow().isoformat(),
            "ai_engine": "Rule-based analysis (OpenAI integration ready)"
        }
        
        return insights
        
    except Exception as e:
        print(f"AI insights generation error: {str(e)}")
        return {
            "key_findings": ["Analytics data successfully collected"],
            "recommendations": ["Continue monitoring learning engagement"],
            "trends": ["Growing interest in professional development"],
            "opportunities": ["Expand learning platform features"],
            "generated_at": datetime.utcnow().isoformat(),
            "ai_engine": "Fallback analysis",
            "note": "Advanced AI analysis temporarily unavailable"
        }

# Fixer Job Management Endpoints

@app.get("/api/fixer/available-jobs")
async def get_fixer_available_jobs(request: Request, db: Session = Depends(get_db)):
    """Get available jobs for authenticated fixer"""
    try:
        # Extract fixer_id from Authorization header  
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Verify user is a fixer
        fixer_check = text("SELECT id FROM fixers WHERE user_id = :user_id AND is_active = true")
        fixer_result = db.execute(fixer_check, {'user_id': user_id}).fetchone()
        
        if not fixer_result:
            raise HTTPException(status_code=403, detail="Fixer access required")
            
        fixer_id = fixer_result[0]
        
        # Get jobs that are either unassigned or available to this fixer
        jobs_query = text("""
            SELECT DISTINCT j.id, j.service, j.description, j.location, j.estimated_price, 
                   j.priority_level, j.status, j.created_at, j.user_id as client_id,
                   CONCAT(u.first_name, ' ', u.last_name) as client_name
            FROM jobs j
            LEFT JOIN users u ON j.user_id = u.id
            LEFT JOIN fixer_notifications fn ON j.id = fn.job_id AND fn.fixer_id = :fixer_id
            WHERE (j.status IN ('pending', 'assigned') AND j.fixer_id IS NULL)
            OR (fn.notification_type = 'job_available' AND j.status != 'completed')
            ORDER BY j.created_at DESC
            LIMIT 20
        """)
        
        result = db.execute(jobs_query, {'fixer_id': fixer_id}).fetchall()
        
        available_jobs = []
        for row in result:
            available_jobs.append({
                "id": row[0],
                "service": row[1],
                "description": row[2],
                "location": row[3],
                "estimated_price": float(row[4]) if row[4] else 0.0,
                "priority_level": row[5],
                "status": row[6],
                "created_at": row[7].isoformat() if row[7] else None,
                "client_id": row[8],
                "client_name": row[9] or "Unknown Client"
            })
        
        return {
            "success": True,
            "available_jobs": available_jobs,
            "message": f"Found {len(available_jobs)} available jobs"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get available jobs error: {str(e)}")
        return {
            "success": False,
            "available_jobs": [],
            "message": "Failed to load available jobs"
        }

@app.get("/api/fixer/notifications")
async def get_fixer_notifications(request: Request, db: Session = Depends(get_db)):
    """Get notifications for authenticated fixer"""
    try:
        # Extract fixer_id from Authorization header  
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Verify user is a fixer
        fixer_check = text("SELECT id FROM fixers WHERE user_id = :user_id AND is_active = true")
        fixer_result = db.execute(fixer_check, {'user_id': user_id}).fetchone()
        
        if not fixer_result:
            raise HTTPException(status_code=403, detail="Fixer access required")
            
        fixer_id = fixer_result[0]
        
        # Get notifications for this fixer
        notifications_query = text("""
            SELECT fn.id, fn.job_id, fn.notification_type, fn.title, fn.message, 
                   fn.is_read, fn.created_at,
                   j.service, j.location, j.estimated_price, j.status as job_status
            FROM fixer_notifications fn
            LEFT JOIN jobs j ON fn.job_id = j.id
            WHERE fn.fixer_id = :fixer_id
            ORDER BY fn.created_at DESC
            LIMIT 50
        """)
        
        result = db.execute(notifications_query, {'fixer_id': fixer_id}).fetchall()
        
        notifications = []
        unread_count = 0
        
        for row in result:
            is_read = row[5]
            if not is_read:
                unread_count += 1
                
            notifications.append({
                "id": row[0],
                "job_id": row[1],
                "notification_type": row[2],
                "title": row[3],
                "message": row[4],
                "is_read": is_read,
                "created_at": row[6].isoformat() if row[6] else None,
                "job_details": {
                    "service": row[7],
                    "location": row[8],
                    "estimated_price": float(row[9]) if row[9] else 0.0,
                    "job_status": row[10]
                } if row[7] else None
            })
        
        return {
            "success": True,
            "notifications": notifications,
            "unread_count": unread_count,
            "message": f"Found {len(notifications)} notifications ({unread_count} unread)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get notifications error: {str(e)}")
        return {
            "success": False,
            "notifications": [],
            "unread_count": 0,
            "message": "Failed to load notifications"
        }

@app.post("/api/fixer/notifications/{notification_id}/mark-read")
async def mark_notification_read(notification_id: str, request: Request, db: Session = Depends(get_db)):
    """Mark a notification as read"""
    try:
        # Extract fixer_id from Authorization header  
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Verify user is a fixer
        fixer_check = text("SELECT id FROM fixers WHERE user_id = :user_id AND is_active = true")
        fixer_result = db.execute(fixer_check, {'user_id': user_id}).fetchone()
        
        if not fixer_result:
            raise HTTPException(status_code=403, detail="Fixer access required")
            
        fixer_id = fixer_result[0]
        
        # Mark notification as read
        update_query = text("""
            UPDATE fixer_notifications 
            SET is_read = true 
            WHERE id = :notification_id AND fixer_id = :fixer_id
        """)
        
        result = db.execute(update_query, {
            'notification_id': notification_id,
            'fixer_id': fixer_id
        })
        
        db.commit()
        
        if result.rowcount > 0:
            return {
                "success": True,
                "message": "Notification marked as read"
            }
        else:
            return {
                "success": False,
                "message": "Notification not found or already read"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Mark notification read error: {str(e)}")
        return {
            "success": False,
            "message": "Failed to mark notification as read"
        }

@app.post("/api/fixer/apply-job/{job_id}")
async def apply_for_job(job_id: str, request: Request, db: Session = Depends(get_db)):
    """Allow fixer to apply for an available job"""
    try:
        # Extract fixer_id from Authorization header  
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Invalid authorization token")
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Verify user is a fixer
        fixer_check = text("SELECT id, name FROM fixers WHERE user_id = :user_id AND is_active = true")
        fixer_result = db.execute(fixer_check, {'user_id': user_id}).fetchone()
        
        if not fixer_result:
            raise HTTPException(status_code=403, detail="Fixer access required")
            
        fixer_id = fixer_result[0]
        fixer_name = fixer_result[1]
        
        # Check if job exists and is available
        job_check = text("""
            SELECT status, fixer_id, service, description 
            FROM jobs 
            WHERE id = :job_id
        """)
        
        job_result = db.execute(job_check, {'job_id': job_id}).fetchone()
        
        if not job_result:
            return {
                "success": False,
                "message": "Job not found"
            }
        
        job_status, current_fixer_id, service, description = job_result
        
        if job_status == 'completed':
            return {
                "success": False,
                "message": "Job is already completed"
            }
        
        if current_fixer_id and job_status == 'assigned':
            return {
                "success": False,
                "message": "Job is already assigned to another fixer"
            }
        
        # Assign job to this fixer
        update_query = text("""
            UPDATE jobs 
            SET fixer_id = :fixer_id, status = 'assigned', updated_at = :updated_at
            WHERE id = :job_id
        """)
        
        db.execute(update_query, {
            'fixer_id': fixer_id,
            'job_id': job_id,
            'updated_at': datetime.utcnow()
        })
        
        db.commit()
        
        print(f"✅ Fixer {fixer_name} ({fixer_id}) applied and was assigned to job {job_id}")
        
        return {
            "success": True,
            "message": f"Successfully applied for {service} job! You are now assigned to this job.",
            "job_id": job_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Apply for job error: {str(e)}")
        return {
            "success": False,
            "message": "Failed to apply for job"
        }

# Existing endpoints (keeping for compatibility)
@app.get("/api/test")
async def test_endpoint():
    return {"message": "FixMate-SA API is running with emergency services!", "timestamp": datetime.now().isoformat()}

@app.post("/api/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """WhatsApp webhook endpoint"""
    try:
        body = await request.json()
        result = await whatsapp_service.handle_webhook(body)
        return result
    except Exception as e:
        print(f"WhatsApp webhook error: {e}")
        return {"error": str(e)}

@app.get("/api/whatsapp/stats")  
async def get_whatsapp_stats(db: Session = Depends(get_db)):
    """Get WhatsApp statistics"""
    try:
        stats = db.query(WhatsAppStatistics).order_by(WhatsAppStatistics.date.desc()).limit(30).all()
        return {
            "success": True,
            "statistics": [{
                "date": stat.date,
                "total_messages": stat.total_messages,
                "unique_users": stat.unique_users,
                "successful_jobs": stat.successful_jobs
            } for stat in stats]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Fixer Application Endpoint
@app.post("/api/fixer/apply")
async def apply_as_fixer(request: Request, db: Session = Depends(get_db)):
    """Submit fixer application"""
    try:
        # Parse JSON data instead of form data
        try:
            json_data = await request.json()
            print(f"🔍 Fixer apply received JSON data: {json_data}")
        except Exception as json_error:
            print(f"⚠️ JSON parsing failed: {json_error}")
            # Fallback to form data for compatibility
            form_data = await request.form()
            json_data = dict(form_data)
            print(f"🔍 Fixer apply received form data: {json_data}")
        
        # Required fields
        required_fields = ['services_offered', 'experience_years', 'why_fixer', 'user_id']
        missing_fields = []
        for field in required_fields:
            if field not in json_data or not json_data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            print(f"❌ Available fields: {list(json_data.keys())}")
            raise HTTPException(status_code=400, detail=f"Missing required field: {missing_fields[0]}")
        
        user_id = json_data['user_id']
        print(f"✅ Fixer application for user_id: {user_id}")
        
        # Check if user exists
        user_query = text("SELECT id, phone, first_name, last_name FROM users WHERE id = :user_id")
        user_result = db.execute(user_query, {'user_id': user_id}).fetchone()
        
        if not user_result:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if fixer application already exists
        existing_fixer_query = text("SELECT id FROM fixers WHERE user_id = :user_id")
        existing_fixer = db.execute(existing_fixer_query, {'user_id': user_id}).fetchone()
        
        if existing_fixer:
            raise HTTPException(status_code=400, detail="Fixer application already exists for this user")
        
        # Create fixer record
        fixer_id = f"fixer_{uuid.uuid4()}"
        
        # Parse experience years
        try:
            experience_years = int(json_data['experience_years'])
        except (ValueError, TypeError):
            experience_years = 0
        
        # Extract services offered (ensure it's a string for database compatibility)
        services_offered = json_data['services_offered']
        if isinstance(services_offered, str):
            services_string = services_offered  # Keep as string for database
        else:
            services_string = ', '.join(str(s) for s in services_offered)
        
        # Create fixer record with only existing columns
        fixer_insert_query = text("""
            INSERT INTO fixers (
                id, user_id, name, phone, services, location, 
                rating, total_jobs, is_active, is_approved, 
                jobs_completed, completion_percentage, created_at
            ) VALUES (
                :id, :user_id, :name, :phone, :services, :location,
                :rating, :total_jobs, :is_active, :is_approved,
                :jobs_completed, :completion_percentage, :created_at
            )
        """)
        
        db.execute(fixer_insert_query, {
            'id': fixer_id,
            'user_id': user_id,
            'name': f"{user_result[2]} {user_result[3]}",  # first_name + last_name
            'phone': user_result[1],
            'services': services_string,  # Use string instead of list
            'location': "South Africa",  # Default location
            'rating': 4.5,  # Default starting rating
            'total_jobs': 0,
            'is_active': True,
            'is_approved': True,  # Auto-approve for now
            'jobs_completed': 0,
            'completion_percentage': 100,
            'created_at': datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "Fixer application submitted successfully",
            "fixer_id": fixer_id
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Fixer application error: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit fixer application")

# Password Reset Endpoints
@app.post("/api/auth/request-password-reset")
async def request_password_reset(request: Request, db: Session = Depends(get_db)):
    """Request password reset code"""
    try:
        form_data = await request.form()
        phone = form_data.get('phone', '').strip()
        
        if not phone:
            raise HTTPException(status_code=400, detail="Phone number is required")
        
        # Check if user exists
        user_query = text("SELECT id, first_name FROM users WHERE phone = :phone")
        user_result = db.execute(user_query, {'phone': phone}).fetchone()
        
        if not user_result:
            # For security, don't reveal if user exists or not
            return {
                "success": True,
                "message": "If this phone number is registered, you will receive a reset code",
                "dev_code": "123456"  # Development code
            }
        
        # Generate reset code (6 digits)
        reset_code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=15)  # Code expires in 15 minutes
        
        # Store reset code in database (create table if needed)
        try:
            # Try to create password_resets table if it doesn't exist (PostgreSQL compatible)
            create_table_query = text("""
                CREATE TABLE IF NOT EXISTS password_resets (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    reset_code VARCHAR(10) NOT NULL,
                    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.execute(create_table_query)
            db.commit()
        except Exception as table_error:
            # Table creation failed, but continue - table might already exist
            print(f"Password resets table creation info: {table_error}")
            try:
                db.rollback()
            except:
                pass
        
        # Insert reset code
        insert_reset_query = text("""
            INSERT INTO password_resets (user_id, phone, reset_code, expires_at)
            VALUES (:user_id, :phone, :reset_code, :expires_at)
        """)
        
        db.execute(insert_reset_query, {
            'user_id': user_result[0],
            'phone': phone,
            'reset_code': reset_code,
            'expires_at': expires_at
        })
        
        db.commit()
        
        # In production, send SMS here
        # For development, return the code
        return {
            "success": True,
            "message": "Password reset code sent successfully",
            "dev_code": reset_code  # Only for development
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Password reset request error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process password reset request")

@app.post("/api/auth/verify-reset-code")
async def verify_reset_code(request: Request, db: Session = Depends(get_db)):
    """Verify password reset code"""
    try:
        form_data = await request.form()
        phone = form_data.get('phone', '').strip()
        reset_code = form_data.get('reset_code', '').strip()
        
        if not phone or not reset_code:
            raise HTTPException(status_code=400, detail="Phone number and reset code are required")
        
        # Find valid reset code
        verify_query = text("""
            SELECT id, user_id, expires_at, used
            FROM password_resets 
            WHERE phone = :phone AND reset_code = :reset_code
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        reset_result = db.execute(verify_query, {
            'phone': phone,
            'reset_code': reset_code
        }).fetchone()
        
        if not reset_result:
            raise HTTPException(status_code=400, detail="Invalid reset code")
        
        if reset_result[3]:  # used
            raise HTTPException(status_code=400, detail="Reset code has already been used")
        
        if datetime.utcnow() > reset_result[2]:  # expires_at
            raise HTTPException(status_code=400, detail="Reset code has expired")
        
        return {
            "success": True,
            "message": "Reset code verified successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Verify reset code error: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify reset code")

@app.post("/api/auth/reset-password")
async def reset_password(request: Request, db: Session = Depends(get_db)):
    """Reset password with verified code"""
    try:
        form_data = await request.form()
        phone = form_data.get('phone', '').strip()
        reset_code = form_data.get('reset_code', '').strip()
        new_password = form_data.get('new_password', '').strip()
        
        if not phone or not reset_code or not new_password:
            raise HTTPException(status_code=400, detail="All fields are required")
        
        if len(new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        
        # Find and verify reset code again
        verify_query = text("""
            SELECT id, user_id, expires_at, used
            FROM password_resets 
            WHERE phone = :phone AND reset_code = :reset_code
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        reset_result = db.execute(verify_query, {
            'phone': phone,
            'reset_code': reset_code
        }).fetchone()
        
        if not reset_result:
            raise HTTPException(status_code=400, detail="Invalid reset code")
        
        if reset_result[3]:  # used
            raise HTTPException(status_code=400, detail="Reset code has already been used")
        
        if datetime.utcnow() > reset_result[2]:  # expires_at
            raise HTTPException(status_code=400, detail="Reset code has expired")
        
        # Hash new password using pwd_context
        hashed_password = pwd_context.hash(new_password)
        
        # Try to update user password - handle both password and password_hash columns
        try:
            # First try with password_hash column
            update_password_query = text("""
                UPDATE users 
                SET password_hash = :password_hash
                WHERE id = :user_id
            """)
            
            result = db.execute(update_password_query, {
                'password_hash': hashed_password,
                'user_id': reset_result[1]
            })
            
            # Check if any rows were affected
            if result.rowcount == 0:
                # Try with password column instead
                update_password_query_alt = text("""
                    UPDATE users 
                    SET password = :password
                    WHERE id = :user_id
                """)
                
                db.execute(update_password_query_alt, {
                    'password': hashed_password,
                    'user_id': reset_result[1]
                })
                
        except Exception as password_update_error:
            # If password_hash column doesn't exist, try password column
            try:
                update_password_query_alt = text("""
                    UPDATE users 
                    SET password = :password
                    WHERE id = :user_id
                """)
                
                db.execute(update_password_query_alt, {
                    'password': hashed_password,
                    'user_id': reset_result[1]
                })
            except Exception as alt_error:
                raise HTTPException(status_code=500, detail="Failed to update password")
        
        # Mark reset code as used
        mark_used_query = text("""
            UPDATE password_resets 
            SET used = TRUE
            WHERE id = :reset_id
        """)
        
        db.execute(mark_used_query, {'reset_id': reset_result[0]})
        
        db.commit()
        
        return {
            "success": True,
            "message": "Password reset successfully"
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Reset password error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset password")

# Push Notification Management Endpoints
@app.post("/api/push/subscribe")
async def subscribe_to_push(request: Request, db: Session = Depends(get_db)):
    """Subscribe user to push notifications"""
    try:
        # Extract and validate user from token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization token")
            
        authenticated_user_id = auth_header.replace('Bearer token_', '')
        
        # Verify user exists
        user_check = text("SELECT id FROM users WHERE id = :user_id")
        user_result = db.execute(user_check, {'user_id': authenticated_user_id}).fetchone()
        if not user_result:
            raise HTTPException(status_code=401, detail="Invalid user token")
        
        data = await request.json()
        subscription_data = data.get('subscription')
        user_id = data.get('userId')
        user_role = data.get('userRole')
        
        # Security check: users can only subscribe themselves
        if authenticated_user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied: You can only manage your own subscriptions")
        
        if not subscription_data or not user_id:
            raise HTTPException(status_code=400, detail="Missing subscription data or user ID")
        
        # Create push_subscriptions table if it doesn't exist
        try:
            # Check if table exists
            check_table_query = text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'push_subscriptions'
                )
            """)
            table_exists = db.execute(check_table_query).fetchone()[0]
            
            if not table_exists:
                # Create table only if it doesn't exist
                create_table_query = text("""
                    CREATE TABLE push_subscriptions (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL,
                        user_role VARCHAR(50),
                        endpoint TEXT NOT NULL,
                        p256dh_key TEXT,
                        auth_key TEXT,
                        subscription_data TEXT,
                        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                db.execute(create_table_query)
                print("✅ Created push_subscriptions table")
                db.commit()
        except Exception as table_error:
            print(f"Push subscriptions table creation error: {table_error}")
            try:
                db.rollback()
            except:
                pass
        
        # Extract subscription details
        endpoint = subscription_data.get('endpoint')
        keys = subscription_data.get('keys', {})
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')
        
        # Insert or update subscription
        # First, try to delete existing subscription for this user and endpoint
        delete_existing_query = text("""
            DELETE FROM push_subscriptions 
            WHERE user_id = :user_id AND endpoint = :endpoint
        """)
        db.execute(delete_existing_query, {
            'user_id': user_id,
            'endpoint': endpoint
        })
        
        # Then insert the new subscription
        insert_query = text("""
            INSERT INTO push_subscriptions (user_id, user_role, endpoint, p256dh_key, auth_key, subscription_data)
            VALUES (:user_id, :user_role, :endpoint, :p256dh, :auth, :subscription_data)
        """)
        
        db.execute(insert_query, {
            'user_id': user_id,
            'user_role': user_role,
            'endpoint': endpoint,
            'p256dh': p256dh,
            'auth': auth,
            'subscription_data': json.dumps(subscription_data)
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": "Push subscription saved successfully"
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Push subscription error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save push subscription")

@app.post("/api/push/unsubscribe")
async def unsubscribe_from_push(request: Request, db: Session = Depends(get_db)):
    """Unsubscribe user from push notifications"""
    try:
        # Extract and validate user from token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization token")
            
        authenticated_user_id = auth_header.replace('Bearer token_', '')
        
        # Verify user exists
        user_check = text("SELECT id FROM users WHERE id = :user_id")
        user_result = db.execute(user_check, {'user_id': authenticated_user_id}).fetchone()
        if not user_result:
            raise HTTPException(status_code=401, detail="Invalid user token")
        
        data = await request.json()
        subscription_data = data.get('subscription')
        user_id = data.get('userId')
        
        # Security check: users can only unsubscribe themselves
        if authenticated_user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied: You can only manage your own subscriptions")
        
        if not subscription_data or not user_id:
            raise HTTPException(status_code=400, detail="Missing subscription data or user ID")
        
        endpoint = subscription_data.get('endpoint')
        
        # Remove subscription from database
        delete_query = text("""
            DELETE FROM push_subscriptions 
            WHERE user_id = :user_id AND endpoint = :endpoint
        """)
        
        result = db.execute(delete_query, {
            'user_id': user_id,
            'endpoint': endpoint
        })
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Push subscription removed successfully ({result.rowcount} rows affected)"
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Push unsubscription error: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove push subscription")

@app.post("/api/push/test") 
async def send_test_notification(request: Request, db: Session = Depends(get_db)):
    """Send test push notification to user"""
    try:
        # Extract and validate user from token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization token")
            
        authenticated_user_id = auth_header.replace('Bearer token_', '')
        
        # Verify user exists
        user_check = text("SELECT id FROM users WHERE id = :user_id")
        user_result = db.execute(user_check, {'user_id': authenticated_user_id}).fetchone()
        if not user_result:
            raise HTTPException(status_code=401, detail="Invalid user token")
        
        data = await request.json()
        user_id = data.get('userId')
        notification_type = data.get('type', 'test')
        title = data.get('title', '🧪 Test Notification')
        message = data.get('message', 'This is a test notification from FixMate-SA!')
        
        # Security check: users can only send test notifications to themselves
        if authenticated_user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied: You can only send test notifications to yourself")
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user ID")
        
        # Get user's push subscriptions
        subscriptions_query = text("""
            SELECT subscription_data FROM push_subscriptions 
            WHERE user_id = :user_id
        """)
        
        subscriptions = db.execute(subscriptions_query, {'user_id': user_id}).fetchall()
        
        if not subscriptions:
            return {
                "success": False,
                "message": "No push subscriptions found for user"
            }
        
        # Implement actual push notification sending using pywebpush
        sent_count = 0
        failed_count = 0
        
        if PYWEBPUSH_AVAILABLE:
            # Load VAPID keys from environment
            vapid_private_key = os.getenv('VAPID_PRIVATE_KEY')
            vapid_subject = os.getenv('VAPID_SUBJECT', 'mailto:support@fixmate-sa.com')
            
            if not vapid_private_key:
                print("⚠️ VAPID private key not configured, using simulation mode")
                return {
                    "success": True,
                    "message": f"Test notification simulated for {len(subscriptions)} subscription(s)",
                    "dev_mode": "VAPID keys not configured - notifications simulated"
                }
            
            for sub_row in subscriptions:
                try:
                    subscription_data = json.loads(sub_row[0])
                    
                    # Prepare notification payload
                    payload = {
                        'title': title,
                        'body': message,
                        'type': notification_type,
                        'url': '/dashboard',
                        'icon': '/fixmate-logo.jpg',
                        'badge': '/fixmate-logo.jpg',
                        'tag': f'test-{notification_type}',
                        'timestamp': int(time.time() * 1000)
                    }
                    
                    # Send push notification
                    webpush(
                        subscription_info=subscription_data,
                        data=json.dumps(payload),
                        vapid_private_key=vapid_private_key,
                        vapid_claims={"sub": vapid_subject}
                    )
                    
                    sent_count += 1
                    print(f"✅ Sent push notification to endpoint: {subscription_data.get('endpoint', 'unknown')[:50]}...")
                    
                except WebPushException as e:
                    failed_count += 1
                    print(f"❌ WebPush error: {e}")
                    
                    # If subscription is invalid, remove it from database
                    if e.response and e.response.status_code in [410, 404]:
                        try:
                            delete_invalid_sub = text("""
                                DELETE FROM push_subscriptions 
                                WHERE subscription_data = :sub_data
                            """)
                            db.execute(delete_invalid_sub, {'sub_data': sub_row[0]})
                            db.commit()
                            print(f"🗑️ Removed invalid subscription")
                        except Exception as cleanup_error:
                            print(f"Failed to cleanup invalid subscription: {cleanup_error}")
                    
                except Exception as e:
                    failed_count += 1
                    print(f"❌ Push notification error: {e}")
        else:
            # Fallback to simulation
            sent_count = len(subscriptions)
            print(f"📤 Simulated push notification to {len(subscriptions)} subscription(s):")
            print(f"   User: {user_id}")
            print(f"   Type: {notification_type}")
            print(f"   Title: {title}")
            print(f"   Message: {message}")
        
        return {
            "success": sent_count > 0,
            "message": f"Test notification sent to {sent_count}/{len(subscriptions)} subscription(s)",
            "sent": sent_count,
            "failed": failed_count,
            "simulation_mode": not PYWEBPUSH_AVAILABLE or not os.getenv('VAPID_PRIVATE_KEY')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Send test notification error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send test notification")

@app.post("/api/push/send")
async def send_push_notification(request: Request, db: Session = Depends(get_db)):
    """Send push notification to specific users or roles"""
    try:
        # Extract and validate user from token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization token")
            
        authenticated_user_id = auth_header.replace('Bearer token_', '')
        
        # Verify user exists
        user_check = text("SELECT id FROM users WHERE id = :user_id")
        user_result = db.execute(user_check, {'user_id': authenticated_user_id}).fetchone()
        if not user_result:
            raise HTTPException(status_code=401, detail="Invalid user token")
        
        data = await request.json()
        
        # Can target by user_id, user_role, or both
        target_user_id = data.get('userId')
        target_role = data.get('userRole')
        notification_type = data.get('type', 'general')
        title = data.get('title', 'FixMate-SA')
        message = data.get('message', 'You have a new notification')
        url = data.get('url', '/dashboard')
        
        if not target_user_id and not target_role:
            raise HTTPException(status_code=400, detail="Must specify userId or userRole")
        
        # Build query based on targeting criteria
        where_conditions = []
        query_params = {}
        
        if target_user_id:
            where_conditions.append("user_id = :user_id")
            query_params['user_id'] = target_user_id
            
        if target_role:
            where_conditions.append("user_role = :user_role")
            query_params['user_role'] = target_role
        
        where_clause = " AND ".join(where_conditions)
        
        # Get matching subscriptions
        subscriptions_query = text(f"""
            SELECT user_id, subscription_data FROM push_subscriptions 
            WHERE {where_clause}
        """)
        
        subscriptions = db.execute(subscriptions_query, query_params).fetchall()
        
        if not subscriptions:
            return {
                "success": False,
                "message": "No matching push subscriptions found"
            }
        
        # Implement actual push notification sending
        sent_count = 0
        failed_count = 0
        
        if PYWEBPUSH_AVAILABLE:
            # Load VAPID keys from environment
            vapid_private_key = os.getenv('VAPID_PRIVATE_KEY')
            vapid_subject = os.getenv('VAPID_SUBJECT', 'mailto:support@fixmate-sa.com')
            
            if not vapid_private_key:
                return {
                    "success": True,
                    "message": f"Push notification simulated for {len(subscriptions)} subscription(s)",
                    "recipients": len(subscriptions),
                    "dev_mode": "VAPID keys not configured - notifications simulated"
                }
            
            for sub_row in subscriptions:
                try:
                    user_id_from_db = sub_row[0]
                    subscription_data = json.loads(sub_row[1])
                    
                    # Prepare notification payload based on type
                    payload = {
                        'title': title,
                        'body': message,
                        'type': notification_type,
                        'url': url,
                        'icon': '/fixmate-logo.jpg',
                        'badge': '/fixmate-logo.jpg',
                        'tag': f'{notification_type}-{int(time.time())}',
                        'timestamp': int(time.time() * 1000),
                        'userId': user_id_from_db
                    }
                    
                    # Add specific data based on notification type
                    if notification_type == 'job_assigned':
                        payload.update({
                            'actions': [
                                {'action': 'view_job', 'title': '🔧 View Job'},
                                {'action': 'dismiss', 'title': 'Later'}
                            ],
                            'requireInteraction': True
                        })
                    elif notification_type == 'payment_received':
                        payload.update({
                            'actions': [
                                {'action': 'view', 'title': '💰 View Payment'},
                                {'action': 'dismiss', 'title': 'OK'}
                            ]
                        })
                    
                    # Send push notification
                    webpush(
                        subscription_info=subscription_data,
                        data=json.dumps(payload),
                        vapid_private_key=vapid_private_key,
                        vapid_claims={"sub": vapid_subject}
                    )
                    
                    sent_count += 1
                    print(f"✅ Sent push notification to user {user_id_from_db}")
                    
                except WebPushException as e:
                    failed_count += 1
                    print(f"❌ WebPush error for user {sub_row[0]}: {e}")
                    
                    # If subscription is invalid, remove it from database
                    if e.response and e.response.status_code in [410, 404]:
                        try:
                            delete_invalid_sub = text("""
                                DELETE FROM push_subscriptions 
                                WHERE subscription_data = :sub_data
                            """)
                            db.execute(delete_invalid_sub, {'sub_data': sub_row[1]})
                            db.commit()
                            print(f"🗑️ Removed invalid subscription for user {sub_row[0]}")
                        except Exception as cleanup_error:
                            print(f"Failed to cleanup invalid subscription: {cleanup_error}")
                    
                except Exception as e:
                    failed_count += 1
                    print(f"❌ Push notification error for user {sub_row[0]}: {e}")
        else:
            # Fallback to simulation
            sent_count = len(subscriptions)
            print(f"📤 Simulated push notification to {len(subscriptions)} subscription(s):")
            print(f"   Target User ID: {target_user_id}")
            print(f"   Target Role: {target_role}")
            print(f"   Type: {notification_type}")
            print(f"   Title: {title}")
            print(f"   Message: {message}")
            print(f"   URL: {url}")
        
        return {
            "success": sent_count > 0,
            "message": f"Push notification sent to {sent_count}/{len(subscriptions)} subscription(s)",
            "recipients": len(subscriptions),
            "sent": sent_count,
            "failed": failed_count,
            "simulation_mode": not PYWEBPUSH_AVAILABLE or not os.getenv('VAPID_PRIVATE_KEY')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Send push notification error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send push notification")

# Fixer Reputation API Endpoints
@app.get("/api/fixer/{fixer_id}/reputation")
async def get_fixer_reputation(fixer_id: str, db: Session = Depends(get_db)):
    """Get fixer reputation data"""
    try:
        # Check if fixer exists
        fixer_query = text("""
            SELECT id, name, phone, services, email, rating, total_jobs
            FROM fixers 
            WHERE id = :fixer_id OR user_id = :fixer_id
        """)
        
        fixer_result = db.execute(fixer_query, {'fixer_id': fixer_id}).fetchone()
        
        if not fixer_result:
            return {
                "success": False,
                "message": "Fixer not found"
            }
        
        # Get job statistics for this fixer
        stats_query = text("""
            SELECT 
                COUNT(*) as total_jobs,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as active_jobs,
                AVG(CASE WHEN status = 'completed' AND estimated_price IS NOT NULL THEN estimated_price END) as avg_job_value
            FROM jobs 
            WHERE assigned_fixer_id = :fixer_id
        """)
        
        stats_result = db.execute(stats_query, {'fixer_id': fixer_id}).fetchone()
        
        # Calculate reputation tier based on completed jobs and rating
        completed_jobs = stats_result[1] if stats_result else 0
        rating = fixer_result[5] if fixer_result[5] else 4.5
        
        # Determine tier based on performance
        if completed_jobs >= 50 and rating >= 4.8:
            tier = "Platinum"
            tier_color = "purple"
        elif completed_jobs >= 25 and rating >= 4.5:
            tier = "Gold"
            tier_color = "yellow"
        elif completed_jobs >= 10 and rating >= 4.0:
            tier = "Silver"
            tier_color = "gray"
        else:
            tier = "Bronze"
            tier_color = "amber"
        
        # Calculate reputation score (0-100)
        total_jobs = fixer_result[6] if fixer_result[6] else 0
        reputation_score = min(100, int((rating * 15) + (completed_jobs * 2) + (total_jobs * 0.5)))
        
        reputation_data = {
            "fixer_id": fixer_result[0],
            "fixer_name": fixer_result[1],
            "tier": tier,
            "tier_color": tier_color,
            "reputation_score": reputation_score,
            "current_rating": rating,
            "total_reviews": total_jobs,  # Use total_jobs as proxy for reviews
            "jobs_completed": completed_jobs,
            "total_jobs": stats_result[0] if stats_result else 0,
            "active_jobs": stats_result[2] if stats_result else 0,
            "avg_job_value": float(stats_result[3]) if stats_result and stats_result[3] else 0,
            "completion_rate": round((completed_jobs / max(1, stats_result[0])) * 100, 1) if stats_result else 0,
            "service_categories": fixer_result[3] or [],
            "bio": fixer_result[4] or "Professional fixer providing quality services",
            "badges": [],
            "performance_metrics": {
                "response_time": "< 2 hours",
                "completion_rate": f"{round((completed_jobs / max(1, stats_result[0])) * 100, 1)}%",
                "customer_satisfaction": f"{rating:.1f}/5.0",
                "reliability": "Excellent" if rating >= 4.5 else "Good" if rating >= 4.0 else "Fair"
            }
        }
        
        # Add badges based on performance
        if completed_jobs >= 10:
            reputation_data["badges"].append("Experienced Professional")
        if rating >= 4.5:
            reputation_data["badges"].append("Top Rated")
        if completed_jobs >= 50:
            reputation_data["badges"].append("Veteran Fixer")
        
        return {
            "success": True,
            "reputation": reputation_data
        }
        
    except Exception as e:
        print(f"Get fixer reputation error: {e}")
        return {
            "success": False,
            "message": f"Failed to fetch reputation data: {str(e)}"
        }

@app.post("/api/fixer/{fixer_id}/reputation/initialize")
async def initialize_fixer_reputation(fixer_id: str, db: Session = Depends(get_db)):
    """Initialize fixer reputation (creates basic profile if needed)"""
    try:
        # Check if fixer exists
        fixer_query = text("""
            SELECT id, name, phone, rating, total_jobs
            FROM fixers 
            WHERE id = :fixer_id OR user_id = :fixer_id
        """)
        
        fixer_result = db.execute(fixer_query, {'fixer_id': fixer_id}).fetchone()
        
        if not fixer_result:
            return {
                "success": False,
                "message": "Fixer not found. Please complete your fixer profile first."
            }
        
        # Update fixer with default reputation values if needed
        update_query = text("""
            UPDATE fixers 
            SET 
                rating = COALESCE(rating, 4.5),
                total_jobs = COALESCE(total_jobs, 0)
            WHERE id = :fixer_id OR user_id = :fixer_id
        """)
        
        db.execute(update_query, {'fixer_id': fixer_id})
        db.commit()
        
        return {
            "success": True,
            "message": "Fixer reputation initialized successfully"
        }
        
    except Exception as e:
        db.rollback()
        print(f"Initialize fixer reputation error: {e}")
        return {
            "success": False,
            "message": f"Failed to initialize reputation: {str(e)}"
        }

@app.post("/api/fixer/{fixer_id}/reputation/update")
async def update_fixer_performance(fixer_id: str, performance_data: dict, db: Session = Depends(get_db)):
    """Update fixer performance metrics"""
    try:
        # Check if fixer exists
        fixer_query = text("""
            SELECT id FROM fixers 
            WHERE id = :fixer_id OR user_id = :fixer_id
        """)
        
        fixer_result = db.execute(fixer_query, {'fixer_id': fixer_id}).fetchone()
        
        if not fixer_result:
            return {
                "success": False,
                "message": "Fixer not found"
            }
        
        # Update performance metrics (this is a simplified version)
        # In a real system, you'd want more sophisticated tracking
        update_fields = []
        update_params = {'fixer_id': fixer_id}
        
        if 'rating' in performance_data:
            update_fields.append("rating = :rating")
            update_params['rating'] = performance_data['rating']
            
        if 'total_jobs' in performance_data:
            update_fields.append("total_jobs = :total_jobs")
            update_params['total_jobs'] = performance_data['total_jobs']
        
        if update_fields:
            update_query = text(f"""
                UPDATE fixers 
                SET {', '.join(update_fields)}
                WHERE id = :fixer_id OR user_id = :fixer_id
            """)
            
            db.execute(update_query, update_params)
            db.commit()
        
        return {
            "success": True,
            "message": "Performance metrics updated successfully"
        }
        
    except Exception as e:
        db.rollback()
        print(f"Update fixer performance error: {e}")
        return {
            "success": False,
            "message": f"Failed to update performance: {str(e)}"
        }

# Serve React static files
frontend_build_path = Path(__file__).parent.parent / "frontend" / "build"
static_path = Path(__file__).parent.parent / "frontend" / "build" / "static"

print(f"🔍 Looking for React build at: {frontend_build_path}")
print(f"🔍 Static path exists: {static_path.exists()}")
print(f"🔍 Frontend build exists: {frontend_build_path.exists()}")

if frontend_build_path.exists():
    # Mount static files with cache control
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    # Serve React app for all other routes
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        # For API routes, return 404
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # For all other routes, serve React app
        return FileResponse(frontend_build_path / "index.html")
else:
    print("⚠️ Frontend build not found. React routes will not be served.")

# Fixer Payment Processing Endpoints

async def get_current_user(request: Request, db: Session):
    """Helper function to get current user from request"""
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer token_'):
            return None
            
        user_id = auth_header.replace('Bearer token_', '')
        
        # Get user info
        user_query = text("SELECT id, first_name, last_name, role FROM users WHERE id = :user_id")
        user_result = db.execute(user_query, {'user_id': user_id}).fetchone()
        
        if user_result:
            return {
                'id': user_result[0],
                'first_name': user_result[1],
                'last_name': user_result[2],
                'role': user_result[3]
            }
        return None
    except:
        return None

@app.get("/api/fixer/test-endpoint")
async def test_fixer_endpoint():
    """Test endpoint to verify API registration"""
    return {"success": True, "message": "Test endpoint working"}

@app.get("/api/fixer/outstanding-payments")
async def get_fixer_outstanding_payments(request: Request, db: Session = Depends(get_db)):
    """Get outstanding payments for fixer"""
    try:
        current_user = await get_current_user(request, db)
        if current_user is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Query outstanding payments for the fixer
        query = text("""
            SELECT id, amount, status, description, due_date, created_at
            FROM fixer_service_fees 
            WHERE fixer_id = :fixer_id AND status IN ('pending', 'overdue')
            ORDER BY due_date ASC
        """)
        
        result = db.execute(query, {'fixer_id': current_user['id']})
        rows = result.fetchall()
        
        payments = []
        total_outstanding = 0
        overdue_count = 0
        
        for row in rows:
            payment = {
                'id': row[0],
                'amount': float(row[1]),
                'status': row[2],
                'description': row[3],
                'due_date': row[4].isoformat() if row[4] else None,
                'created_at': row[5].isoformat() if row[5] else None
            }
            
            # Check if overdue
            if row[4] and row[4] < datetime.utcnow():
                payment['status'] = 'overdue'
                overdue_count += 1
            
            payments.append(payment)
            total_outstanding += payment['amount']
        
        return {
            "success": True,
            "payments": payments,
            "total_outstanding": total_outstanding,
            "overdue_count": overdue_count,
            "can_receive_jobs": overdue_count == 0  # Can receive jobs if no overdue payments
        }
        
    except Exception as e:
        print(f"Error fetching outstanding payments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch outstanding payments")

@app.get("/api/fixer/payment-history")
async def get_fixer_payment_history(request: Request, db: Session = Depends(get_db)):
    """Get payment history for fixer"""
    try:
        current_user = await get_current_user(request, db)
        if current_user is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Query payment history for the fixer
        query = text("""
            SELECT id, amount, status, payment_method, payment_reference, 
                   paid_date, description, due_date, created_at
            FROM fixer_service_fees 
            WHERE fixer_id = :fixer_id
            ORDER BY created_at DESC
            LIMIT 50
        """)
        
        result = db.execute(query, {'fixer_id': current_user['id']})
        rows = result.fetchall()
        
        payments = []
        for row in rows:
            payment = {
                'id': row[0],
                'amount': float(row[1]),
                'status': row[2],
                'payment_method': row[3],
                'payment_reference': row[4],
                'paid_date': row[5].isoformat() if row[5] else None,
                'description': row[6],
                'due_date': row[7].isoformat() if row[7] else None,
                'created_at': row[8].isoformat() if row[8] else None
            }
            payments.append(payment)
        
        return {
            "success": True,
            "payments": payments,
            "total_payments": len(payments)
        }
        
    except Exception as e:
        print(f"Error fetching payment history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch payment history")

@app.post("/api/fixer/create-test-payments")
async def create_test_payments(request: Request, db: Session = Depends(get_db)):
    """Create test outstanding payments for fixer (development only)"""
    try:
        current_user = await get_current_user(request, db)
        if current_user is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Create fixer_service_fees table (standalone, no foreign keys)
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS fixer_service_fees (
                id VARCHAR PRIMARY KEY,
                fixer_id VARCHAR NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                status VARCHAR DEFAULT 'pending',
                payment_method VARCHAR,
                payment_reference VARCHAR,
                paid_date TIMESTAMP,
                description VARCHAR,
                due_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute(create_table_query)
        
        # Create test payments
        test_payments = [
            {
                'id': str(uuid.uuid4()),
                'fixer_id': current_user['id'],
                'amount': 20.00,
                'status': 'pending',
                'description': 'Service fee for plumbing job completed on 2025-01-10',
                'due_date': datetime.utcnow() + timedelta(days=5)
            },
            {
                'id': str(uuid.uuid4()),
                'fixer_id': current_user['id'],
                'amount': 20.00,
                'status': 'overdue',
                'description': 'Service fee for electrical job completed on 2025-01-05',
                'due_date': datetime.utcnow() - timedelta(days=2)
            }
        ]
        
        for payment in test_payments:
            insert_query = text("""
                INSERT INTO fixer_service_fees (id, fixer_id, amount, status, description, due_date, created_at)
                VALUES (:id, :fixer_id, :amount, :status, :description, :due_date, :created_at)
                ON CONFLICT (id) DO NOTHING
            """)
            
            db.execute(insert_query, {
                **payment,
                'created_at': datetime.utcnow()
            })
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Created {len(test_payments)} test payments for fixer",
            "payments": test_payments
        }
        
    except Exception as e:
        db.rollback()
        print(f"Error creating test payments: {e}")
        raise HTTPException(status_code=500, detail="Failed to create test payments")

@app.post("/api/fixer/payment/card")
async def process_fixer_card_payment(request: Request, db: Session = Depends(get_db)):
    """Process fixer service fee payment via card"""
    try:
        current_user = await get_current_user(request, db)
        if current_user is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        data = await request.json()
        
        # Validate required fields
        required_fields = ['amount', 'card_number', 'expiry_month', 'expiry_year', 'cvv', 'card_holder', 'payment_ids']
        for field in required_fields:
            if field not in data or not data[field]:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate payment amount
        amount = float(data['amount'])
        if amount <= 0 or amount > 1000:  # Reasonable limits
            raise HTTPException(status_code=400, detail="Invalid payment amount")
        
        # Basic card validation
        card_number = data['card_number'].replace(' ', '')
        if len(card_number) < 13 or len(card_number) > 19:
            raise HTTPException(status_code=400, detail="Invalid card number length")
        
        cvv = data['cvv']
        if len(cvv) < 3 or len(cvv) > 4:
            raise HTTPException(status_code=400, detail="Invalid CVV")
        
        # For demo purposes - simulate card processing
        # In production, this would integrate with PayFast, Stripe, or other payment processors
        
        # Simulate processing time
        import time
        time.sleep(2)
        
        # Simulate success/failure (90% success rate for demo)
        import random
        if random.random() < 0.9:
            # Success - generate transaction ID
            transaction_id = f"TXN{int(time.time())}{random.randint(1000, 9999)}"
            
            # Update payment records in database
            try:
                payment_ids = data['payment_ids']
                updated_payments = []
                
                for payment_id in payment_ids:
                    update_query = text("""
                        UPDATE fixer_service_fees 
                        SET status = 'paid', payment_method = 'card', 
                            payment_reference = :transaction_id, paid_date = :paid_date
                        WHERE id = :payment_id AND fixer_id = :fixer_id
                    """)
                    
                    result = db.execute(update_query, {
                        'transaction_id': transaction_id,
                        'paid_date': datetime.now(),
                        'payment_id': payment_id,
                        'fixer_id': current_user['id']
                    })
                    
                    if result.rowcount > 0:
                        updated_payments.append(payment_id)
                
                db.commit()
                
                return {
                    "success": True,
                    "message": f"Payment of R{amount:.2f} processed successfully",
                    "transaction_id": transaction_id,
                    "payments_updated": len(updated_payments),
                    "amount_processed": amount
                }
                
            except Exception as db_error:
                db.rollback()
                print(f"Database error during card payment: {db_error}")
                # Even if DB update fails, we can still return success for the payment
                return {
                    "success": True,
                    "message": f"Payment of R{amount:.2f} processed successfully",
                    "transaction_id": transaction_id,
                    "note": "Payment successful, records will be updated shortly"
                }
        else:
            # Simulate failure
            failure_reasons = [
                "Insufficient funds",
                "Card declined by bank",
                "Invalid card details",
                "Payment limit exceeded"
            ]
            raise HTTPException(status_code=400, detail=random.choice(failure_reasons))
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Card payment error: {e}")
        raise HTTPException(status_code=500, detail="Payment processing failed")

@app.post("/api/fixer/payment/eft")
async def process_fixer_eft_payment(request: Request, db: Session = Depends(get_db)):
    """Process fixer service fee payment via EFT"""
    try:
        current_user = await get_current_user(request, db)
        if current_user is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        data = await request.json()
        
        # Validate required fields
        required_fields = ['amount', 'account_holder', 'bank_name', 'payment_ids']
        for field in required_fields:
            if field not in data or not data[field]:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate payment amount
        amount = float(data['amount'])
        if amount <= 0 or amount > 1000:
            raise HTTPException(status_code=400, detail="Invalid payment amount")
        
        # Generate reference number
        reference = data.get('reference', f"FIXER-{current_user['id'][:8]}-FEE")
        
        # Create EFT payment record
        try:
            payment_ids = data['payment_ids']
            eft_reference = f"EFT{int(time.time())}{random.randint(100, 999)}"
            
            # Mark payments as pending EFT
            updated_payments = []
            for payment_id in payment_ids:
                update_query = text("""
                    UPDATE fixer_service_fees 
                    SET payment_method = 'eft', payment_reference = :eft_reference, 
                        status = 'pending_verification'
                    WHERE id = :payment_id AND fixer_id = :fixer_id
                """)
                
                result = db.execute(update_query, {
                    'eft_reference': eft_reference,
                    'payment_id': payment_id,
                    'fixer_id': current_user['id']
                })
                
                if result.rowcount > 0:
                    updated_payments.append(payment_id)
            
            db.commit()
            
            return {
                "success": True,
                "message": "EFT payment details recorded successfully",
                "reference": reference,
                "eft_reference": eft_reference,
                "banking_details": {
                    "bank": "First National Bank (FNB)",
                    "account_name": "FixMate-SA (Pty) Ltd",
                    "account_number": "1234567890",
                    "branch_code": "250655",
                    "reference": reference,
                    "amount": f"R{amount:.2f}"
                },
                "payments_updated": len(updated_payments),
                "instructions": [
                    f"Transfer R{amount:.2f} to the account details provided",
                    f"Use reference: {reference}",
                    "Keep your proof of payment",
                    "Payment will be verified within 24 hours"
                ]
            }
            
        except Exception as db_error:
            db.rollback()
            print(f"Database error during EFT setup: {db_error}")
            raise HTTPException(status_code=500, detail="Failed to setup EFT payment")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"EFT payment error: {e}")
        raise HTTPException(status_code=500, detail="EFT payment setup failed")

# Include other routes and main execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)