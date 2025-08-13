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
import uuid
import hashlib
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path
import tempfile
import shutil

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
        
        return JobResponse(
            success=True,
            message="Job created successfully",
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
async def get_jobs(client_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Get jobs (optionally filtered by client_id)"""
    try:
        # Use raw SQL to match actual database schema
        if client_id:
            query = text("""
                SELECT id, user_id, service, description, location, status, 
                       estimated_price, priority_level, created_at, fixer_id
                FROM jobs 
                WHERE user_id = :client_id 
                ORDER BY created_at DESC
            """)
            result = db.execute(query, {'client_id': client_id}).fetchall()
        else:
            query = text("""
                SELECT id, user_id, service, description, location, status, 
                       estimated_price, priority_level, created_at, fixer_id
                FROM jobs 
                ORDER BY created_at DESC
            """)
            result = db.execute(query).fetchall()
        
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
async def get_dashboard(user_id: str, db: Session = Depends(get_db)):
    """Get dashboard statistics for a user"""
    try:
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
            # Fixer dashboard statistics
            fixer_query = text("""
                SELECT 
                    jobs_completed,
                    rating,
                    total_earned,
                    is_active
                FROM fixers 
                WHERE user_id = :user_id
            """)
            
            fixer_result = db.execute(fixer_query, {'user_id': user_id}).fetchone()
            
            if fixer_result:
                return {
                    "success": True,
                    "user_id": user_id,
                    "role": user_role,
                    "stats": {
                        "jobs_completed": fixer_result[0] or 0,
                        "rating": float(fixer_result[1] or 5.0),
                        "total_earned": float(fixer_result[2] or 0),
                        "is_active": fixer_result[3] or False
                    }
                }
            else:
                # Default stats for fixer without profile
                return {
                    "success": True,
                    "user_id": user_id,
                    "role": user_role,
                    "stats": {
                        "jobs_completed": 0,
                        "rating": 5.0,
                        "total_earned": 0,
                        "is_active": False
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
        from dateutil.relativedelta import relativedelta
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
        from dateutil.relativedelta import relativedelta
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

# Include other routes and main execution
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)