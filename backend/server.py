from fastapi import FastAPI, APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import json
import uuid
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

# Import services and models
from database import get_db, engine
from models import Base, User, Job, EmergencyAlert, WhatsAppStatistics, Announcement, AnnouncementChat
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

@app.post("/api/auth/client/login", response_model=UserResponse)
async def client_login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Client login endpoint"""
    try:
        user = db.query(User).filter(
            User.phone == login_data.phone,
            User.role == "client"
        ).first()
        
        if not user:
            return UserResponse(success=False, message="Invalid phone number or password")
        
        # Simple password check (in production, use proper password hashing)
        if login_data.password != "client123":
            return UserResponse(success=False, message="Invalid phone number or password")
        
        # Generate simple token (in production, use JWT)
        token = f"client_token_{user.id}"
        
        return UserResponse(
            success=True,
            message="Login successful",
            token=token,
            user={
                "id": user.id,
                "name": user.name or f"{user.first_name} {user.last_name}",
                "phone": user.phone,
                "role": user.role.value
            }
        )
    except Exception as e:
        return UserResponse(success=False, message=str(e))

@app.post("/api/auth/fixer/login", response_model=UserResponse)
async def fixer_login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Fixer login endpoint"""
    try:
        user = db.query(User).filter(
            User.phone == login_data.phone,
            User.role == "fixer"
        ).first()
        
        if not user:
            return UserResponse(success=False, message="Invalid phone number or password")
        
        # Simple password check (in production, use proper password hashing)
        if login_data.password != "fixer123":
            return UserResponse(success=False, message="Invalid phone number or password")
        
        # Generate simple token (in production, use JWT)
        token = f"fixer_token_{user.id}"
        
        return UserResponse(
            success=True,
            message="Login successful",
            token=token,
            user={
                "id": user.id,
                "name": user.name or f"{user.first_name} {user.last_name}",
                "phone": user.phone,
                "role": user.role.value
            }
        )
    except Exception as e:
        return UserResponse(success=False, message=str(e))

@app.post("/api/auth/admin/login", response_model=UserResponse)
async def admin_login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Admin login endpoint"""
    try:
        user = db.query(User).filter(
            User.phone == login_data.phone,
            User.role == "admin"
        ).first()
        
        if not user:
            return UserResponse(success=False, message="Invalid phone number or password")
        
        # Simple password check (in production, use proper password hashing)
        if login_data.password != "admin123":
            return UserResponse(success=False, message="Invalid phone number or password")
        
        # Generate simple token (in production, use JWT)
        token = f"admin_token_{user.id}"
        
        return UserResponse(
            success=True,
            message="Login successful",
            token=token,
            user={
                "id": user.id,
                "name": user.name or f"{user.first_name} {user.last_name}",
                "phone": user.phone,
                "role": user.role.value
            }
        )
    except Exception as e:
        return UserResponse(success=False, message=str(e))

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

# Serve React static files
frontend_build_path = Path(__file__).parent.parent / "frontend" / "build"
static_path = Path(__file__).parent.parent / "frontend" / "build" / "static"

print(f"🔍 Looking for React build at: {frontend_build_path}")
print(f"🔍 Static path exists: {static_path.exists()}")
print(f"🔍 Frontend build exists: {frontend_build_path.exists()}")

if frontend_build_path.exists():
    # Mount static files
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
        print("✅ Static files mounted from React build")
    
    # Serve React app
    @app.get("/")
    async def serve_react_app():
        index_file = frontend_build_path / "index.html"
        if index_file.exists():
            print(f"🔍 Index.html references: main.a2ae5212.js")
            return FileResponse(str(index_file))
        return {"error": "React app not found"}
    
    # Catch-all route for React Router
    @app.get("/{full_path:path}")
    async def serve_react_routes(full_path: str):
        # Serve specific files if they exist
        file_path = frontend_build_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        
        # For React routes, serve index.html
        index_file = frontend_build_path / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        
        return {"error": "File not found", "path": full_path}

else:
    print("⚠️ React build directory not found")
    @app.get("/")
    async def root():
        return {"message": "FixMate-SA API Server with Emergency Services", "frontend": "build not found"}

# Serve marketing website
website_path = Path(__file__).parent.parent / "website"
if website_path.exists():
    app.mount("/website", StaticFiles(directory=str(website_path), html=True), name="website")
    print("✅ Marketing website mounted at /website")

# Development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)