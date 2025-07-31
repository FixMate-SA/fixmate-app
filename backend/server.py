from fastapi import FastAPI, APIRouter, Depends, HTTPException, File, UploadFile, Form, Request
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from typing import List, Optional
import json
import uuid
from datetime import datetime, timedelta

from database import get_db, drop_and_recreate_tables
from models import User, Fixer, Job, Review, FixerPayment, FixerVerification, EmergencyAlert, FixerApplication, DataInsight
from schemas import (
    UserCreate, UserResponse, FixerCreate, FixerResponse,
    JobCreate, JobUpdate, JobResponse, ReviewCreate, ReviewResponse,
    SignupRequest, LoginRequest, LoginResponse, SetPasswordRequest, ChangePasswordRequest,
    FixerPaymentCreate, FixerPaymentResponse,
    FixerVerificationCreate, FixerVerificationResponse,
    EmergencyAlertCreate, EmergencyAlertResponse,
    FixerApplicationCreate, FixerApplicationResponse, FixerApplicationReview
)
from services.ai_service import ai_service
from services.sms_service import sms_service
from services.payment_service import payment_service
from services.ussd_service import ussd_service
from services.role_service import role_service
from services.emergency_service import emergency_service
from services.whatsapp_service import whatsapp_service
from services.business_compliance_service import business_compliance_service
from services.conversation_service import conversation_service
from services.payfast_service import payfast_service
from services.job_workflow_service import job_workflow_service
from services.smart_matching_service import smart_matching_service
from services.photo_verification_service import photo_verification_service
from services.dispute_resolution_service import dispute_resolution_service
from services.real_time_tracking_service import real_time_tracking_service
from services.gamification_service import gamification_service
from services.ai_multilingual_assistant import ai_assistant

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create tables (commented out to prevent data loss)
# drop_and_recreate_tables()
# Create tables on first run only
from database import engine
from models import Base
Base.metadata.create_all(bind=engine)  # Only create if they don't exist

# Create the main app without a prefix
app = FastAPI(title="FixMate-SA API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Authentication dependency
from fastapi import Header
from typing import Optional

async def get_current_user(authorization: Optional[str] = Header(None), token: str = None, db: Session = Depends(get_db)):
    """
    Get current user from token (simplified for demo)
    In production, use proper JWT validation
    """
    # Try to get token from Authorization header first, then from parameter
    auth_token = None
    if authorization and authorization.startswith("Bearer "):
        auth_token = authorization.replace("Bearer ", "")
    elif token:
        auth_token = token
    
    if not auth_token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Extract user_id from token (simplified)
    if not auth_token.startswith("token_"):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    user_id = auth_token.replace("token_", "")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# Voice and AI endpoints
@api_router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio file using AI service.
    """
    try:
        audio_data = await audio.read()
        transcription = ai_service.transcribe_audio(audio_data)
        return {"transcription": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@api_router.post("/classify-service")
async def classify_service(description: str = Form(...)):
    """
    Classify service request using AI.
    """
    try:
        classification = ai_service.classify_service_request(description)
        return {"classification": classification}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@api_router.post("/analyze-sentiment")
async def analyze_sentiment(text: str = Form(...)):
    """
    Analyze sentiment of text using AI.
    """
    try:
        sentiment = ai_service.analyze_sentiment(text)
        return {"sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

# Payment endpoints
@api_router.post("/payment/eft")
async def create_eft_payment(amount: float = Form(...), description: str = Form(...), user_email: str = Form(...), user_name: str = Form(...)):
    """
    Create EFT payment request
    """
    try:
        result = payment_service.create_payment_request(amount, description, user_email, user_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EFT payment creation failed: {str(e)}")

@api_router.post("/payment/airtime")
async def create_airtime_payment(phone_number: str = Form(...), amount: float = Form(...), description: str = Form(...)):
    """
    Create airtime payment
    """
    try:
        result = payment_service.create_airtime_payment(phone_number, amount, description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Airtime payment creation failed: {str(e)}")

@api_router.post("/payment/cash")
async def create_cash_payment(location: str = Form(...), amount: float = Form(...), description: str = Form(...)):
    """
    Create cash collection point payment
    """
    try:
        result = payment_service.create_cash_collection_point(location, amount, description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cash payment creation failed: {str(e)}")

@api_router.post("/payment/stokvel")
async def create_stokvel_payment(stokvel_name: str = Form(...), amount: float = Form(...), description: str = Form(...)):
    """
    Create stokvel payment
    """
    try:
        result = payment_service.create_stokvel_payment(stokvel_name, amount, description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stokvel payment creation failed: {str(e)}")

@api_router.post("/payment/layby")
async def create_layby_payment(total_amount: float = Form(...), deposit_amount: float = Form(...), description: str = Form(...), installments: int = Form(...)):
    """
    Create lay-by payment
    """
    try:
        result = payment_service.create_layby_payment(total_amount, deposit_amount, description, installments)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Layby payment creation failed: {str(e)}")

@api_router.post("/payment/verify")
async def verify_payment(payment_id: str = Form(...), payment_type: str = Form(...)):
    """
    Verify payment status
    """
    try:
        result = payment_service.verify_payment(payment_id, payment_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment verification failed: {str(e)}")

# Fixer payment management endpoints
@api_router.get("/fixer/{fixer_id}/payment-status")
async def get_fixer_payment_status(fixer_id: str, db: Session = Depends(get_db)):
    """
    Check fixer payment status and ability to receive jobs
    """
    try:
        status = payment_service.check_fixer_payment_status(fixer_id, db)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payment status: {str(e)}")

@api_router.post("/fixer/{fixer_id}/create-service-fee")
async def create_fixer_service_fee(fixer_id: str, description: str = Form(...), db: Session = Depends(get_db)):
    """
    Create R20 service fee for fixer (called when job is assigned)
    """
    try:
        result = payment_service.create_fixer_service_fee(fixer_id, description, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create service fee: {str(e)}")

@api_router.post("/fixer/payment/{payment_id}/settle")
async def settle_fixer_payment(payment_id: str, payment_method: str = Form(...), reference: str = Form(...), db: Session = Depends(get_db)):
    """
    Mark fixer payment as settled
    """
    try:
        result = payment_service.settle_payment(payment_id, payment_method, reference, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to settle payment: {str(e)}")

@api_router.get("/fixer/{fixer_id}/payment-history")
async def get_fixer_payment_history(fixer_id: str, db: Session = Depends(get_db)):
    """
    Get payment history for fixer
    """
    try:
        history = payment_service.get_fixer_payment_history(fixer_id, db)
        return {"payments": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payment history: {str(e)}")

@api_router.post("/admin/update-payment-statuses")
async def update_payment_statuses(db: Session = Depends(get_db)):
    """
    Admin endpoint to update overdue payment statuses (should be run daily)
    """
    try:
        result = payment_service.update_fixer_payment_status(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update payment statuses: {str(e)}")

# USSD endpoints
@api_router.post("/ussd")
async def handle_ussd(phone_number: str = Form(...), text: str = Form(...), session_id: str = Form(...)):
    """
    Handle USSD requests
    """
    try:
        result = ussd_service.handle_ussd_request(phone_number, text, session_id)
        return Response(content=result['response'], media_type="text/plain")
    except Exception as e:
        return Response(content=f"END Service temporarily unavailable. Please try again later.", media_type="text/plain")

@api_router.get("/ussd/stats")
async def get_ussd_stats():
    """
    Get USSD usage statistics
    """
    try:
        stats = ussd_service.get_session_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get USSD stats: {str(e)}")

# Enhanced offline support endpoints
@api_router.post("/offline/sync")
async def sync_offline_data(data: dict):
    """
    Sync offline data when connection is restored
    """
    try:
        # Process offline queue data
        results = []
        for item in data.get('queue', []):
            # Process each queued item based on action type
            if item['action'] == 'CREATE_JOB':
                job_result = await create_job(JobCreate(**item['data']))
                results.append({'item_id': item['id'], 'result': job_result})
            elif item['action'] == 'UPDATE_JOB':
                job_result = await update_job(item['data']['id'], JobUpdate(**item['data']))
                results.append({'item_id': item['id'], 'result': job_result})
            elif item['action'] == 'CREATE_REVIEW':
                review_result = await create_review(ReviewCreate(**item['data']))
                results.append({'item_id': item['id'], 'result': review_result})
        
        return {'success': True, 'synced_items': len(results), 'results': results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Offline sync failed: {str(e)}")

@api_router.get("/offline/status")
async def get_offline_status():
    """
    Get offline service status
    """
    return {
        'offline_mode_enabled': True,
        'last_sync': datetime.utcnow().isoformat(),
        'supported_actions': ['CREATE_JOB', 'UPDATE_JOB', 'CREATE_REVIEW', 'UPDATE_PROFILE']
    }

# Authentication endpoints
@api_router.post("/auth/signup")
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Complete user registration with detailed information
    """
    try:
        # Validate passwords match
        if request.password != request.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        if len(request.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Format phone number to match database format
        phone = request.phone
        if phone.startswith('0') and len(phone) == 10:
            phone = f"whatsapp:+27{phone[1:]}"
        elif phone.startswith('+') and len(phone) == 12:
            phone = f"whatsapp:{phone}"
        elif not phone.startswith("whatsapp:"):
            phone = f"whatsapp:{phone}"
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            or_(User.phone == phone, User.id_number == request.id_number)
        ).first()
        
        if existing_user:
            if existing_user.phone == phone:
                raise HTTPException(status_code=400, detail="Phone number already registered")
            else:
                raise HTTPException(status_code=400, detail="ID number already registered")
        
        # Create user data
        user_data = {
            "phone": phone,  # Use formatted phone
            "first_name": request.first_name.strip(),
            "last_name": request.last_name.strip(),
            "id_number": request.id_number.strip(),
            "town": request.town.strip(),
            "email": request.email.strip() if request.email else None
        }
        
        # Create user
        user = role_service.create_or_update_user(user_data, db)
        
        # Set password
        user.set_password(request.password)
        db.commit()
        
        # Get complete profile data
        profile_data = role_service.get_user_profile_data(user, db)
        
        # Generate token
        token = f"token_{user.id}"
        
        return {
            "user": profile_data["user"],
            "role_info": profile_data["role_info"],
            "display_name": profile_data["display_name"],
            "welcome_message": profile_data["welcome_message"],
            "token": token,
            "requires_password": False,
            "message": "Account created successfully!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@api_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Enhanced login with password-based authentication and role detection
    """
    try:
        # Format phone number and try multiple formats to find user
        original_phone = request.phone
        
        # Generate possible phone number formats
        phone_formats = []
        
        # Clean the input phone
        clean_phone = original_phone.replace('whatsapp:', '').replace(' ', '').replace('-', '')
        
        # Format 1: Standard +27 format (CLI created users)
        if clean_phone.startswith('0') and len(clean_phone) == 10:
            standard_format = f"+27{clean_phone[1:]}"
            phone_formats.append(standard_format)
            phone_formats.append(f"whatsapp:{standard_format}")
        elif clean_phone.startswith('+27') and len(clean_phone) == 12:
            phone_formats.append(clean_phone)
            phone_formats.append(f"whatsapp:{clean_phone}")
        elif clean_phone.startswith('27') and len(clean_phone) == 11:
            standard_format = f"+{clean_phone}"
            phone_formats.append(standard_format)
            phone_formats.append(f"whatsapp:{standard_format}")
        else:
            # Add original formats
            phone_formats.append(clean_phone)
            phone_formats.append(f"whatsapp:{clean_phone}")
            if not clean_phone.startswith('whatsapp:'):
                phone_formats.append(f"whatsapp:{original_phone}")
        
        # Try to find user with any of the phone formats
        user = None
        for phone_format in phone_formats:
            user = db.query(User).filter(User.phone == phone_format).first()
            if user:
                print(f"✅ Found user with phone format: {phone_format}")
                break
        
        if not user:
            raise HTTPException(status_code=404, detail="Account not found. Please sign up first.")
        
        # Check password
        if not request.password:
            raise HTTPException(status_code=400, detail="Password is required")
        
        if not user.is_password_set or not user.check_password(request.password):
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Get complete profile data with role information
        profile_data = role_service.get_user_profile_data(user, db)
        
        # Simple token for now (in production, use JWT)
        token = f"token_{user.id}"
        
        # Return enhanced response with role information
        return {
            "user": profile_data["user"],
            "role_info": profile_data["role_info"],
            "display_name": profile_data["display_name"],
            "welcome_message": profile_data["welcome_message"],
            "token": token,
            "requires_password": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@api_router.post("/auth/set-password")
async def set_password(request: SetPasswordRequest, db: Session = Depends(get_db)):
    """
    Set password for new users or users without passwords
    """
    try:
        if request.password != request.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        if len(request.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        user = db.query(User).filter(User.phone == request.phone).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Set password
        user.set_password(request.password)
        db.commit()
        
        return {"success": True, "message": "Password set successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set password: {str(e)}")

@api_router.post("/auth/change-password")
async def change_password(request: ChangePasswordRequest, user_id: str = Form(...), db: Session = Depends(get_db)):
    """
    Change password for existing users
    """
    try:
        if request.new_password != request.confirm_password:
            raise HTTPException(status_code=400, detail="New passwords do not match")
        
        if len(request.new_password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.check_password(request.current_password):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Change password
        user.set_password(request.new_password)
        db.commit()
        
        return {"success": True, "message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change password: {str(e)}")

# Emergency Alert endpoints
@api_router.post("/emergency/alert")
async def create_emergency_alert(
    alert: EmergencyAlertCreate, 
    user_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Trigger emergency alert - notify police and send location
    """
    try:
        alert_data = {
            "job_id": alert.job_id,
            "alert_type": alert.alert_type,
            "latitude": alert.latitude,
            "longitude": alert.longitude,
            "address": alert.address,
            "description": alert.description
        }
        
        result = emergency_service.trigger_emergency_alert(user_id, alert_data, db)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency alert failed: {str(e)}")

@api_router.get("/emergency/alerts/{user_id}")
async def get_user_emergency_alerts(user_id: str, db: Session = Depends(get_db)):
    """
    Get user's emergency alert history
    """
    try:
        alerts = emergency_service.get_emergency_alerts(user_id, db)
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get emergency alerts: {str(e)}")

@api_router.post("/emergency/resolve/{alert_id}")
async def resolve_emergency_alert(
    alert_id: str, 
    resolution: str = Form(...), 
    db: Session = Depends(get_db)
):
    """
    Mark emergency alert as resolved (admin only)
    """
    try:
        result = emergency_service.resolve_emergency_alert(alert_id, resolution, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")

@api_router.get("/emergency/location")
async def get_location_info(latitude: float, longitude: float):
    """
    Get human-readable address from coordinates
    """
    try:
        address = emergency_service.get_location_from_coordinates(latitude, longitude)
        return {"address": address, "latitude": latitude, "longitude": longitude}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get location info: {str(e)}")

# Fixer Application endpoints
@api_router.post("/fixer/apply")
async def submit_fixer_application(
    application: FixerApplicationCreate,
    user_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Submit fixer application for vetting
    """
    try:
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user already has a pending application
        existing_application = db.query(FixerApplication).filter(
            FixerApplication.user_id == user_id,
            FixerApplication.status.in_(["pending", "under_review", "needs_documents"])
        ).first()
        
        if existing_application:
            raise HTTPException(status_code=400, detail="You already have a pending fixer application")
        
        # Create application
        fixer_application = FixerApplication(
            user_id=user_id,
            services_offered=application.services_offered,
            experience_years=application.experience_years,
            qualifications=application.qualifications,
            previous_work=application.previous_work,
            why_fixer=application.why_fixer,
            id_document=application.id_document,
            proof_of_address=application.proof_of_address,
            qualifications_cert=application.qualifications_cert,
            criminal_clearance=application.criminal_clearance,
            status="pending"
        )
        
        db.add(fixer_application)
        db.commit()
        db.refresh(fixer_application)
        
        return {
            "success": True,
            "application_id": fixer_application.id,
            "message": "Fixer application submitted successfully. You will be notified once reviewed."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit application: {str(e)}")

@api_router.get("/fixer/applications/{user_id}")
async def get_user_fixer_applications(user_id: str, db: Session = Depends(get_db)):
    """
    Get user's fixer applications
    """
    try:
        applications = db.query(FixerApplication).filter(
            FixerApplication.user_id == user_id
        ).order_by(FixerApplication.submitted_at.desc()).all()
        
        return {"applications": applications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get applications: {str(e)}")

@api_router.get("/admin/fixer-applications")
async def get_all_fixer_applications(db: Session = Depends(get_db)):
    """
    Get all fixer applications for admin review
    """
    try:
        applications = db.query(FixerApplication).order_by(
            FixerApplication.submitted_at.desc()
        ).all()
        
        return {"applications": applications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get applications: {str(e)}")

@api_router.post("/admin/fixer-applications/{application_id}/review")
async def review_fixer_application(
    application_id: str,
    review: FixerApplicationReview,
    admin_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Admin review of fixer application
    """
    try:
        application = db.query(FixerApplication).filter(
            FixerApplication.id == application_id
        ).first()
        
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Update application
        application.status = review.status
        application.admin_notes = review.admin_notes
        application.rejection_reason = review.rejection_reason
        application.reviewed_by = admin_id
        application.reviewed_at = datetime.utcnow()
        
        if review.status == "approved":
            application.approved_at = datetime.utcnow()
            
            # Create approved fixer record
            user = db.query(User).filter(User.id == application.user_id).first()
            
            fixer = Fixer(
                user_id=application.user_id,
                application_id=application.id,
                phone=user.phone,
                name=user.full_name,
                email=user.email,
                services=application.services_offered,
                location=user.town,
                is_active=True,
                is_approved=True,
                approval_date=datetime.utcnow()
            )
            
            db.add(fixer)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Application {review.status} successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to review application: {str(e)}")

@api_router.get("/auth/profile/{user_id}")
async def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    """
    Get complete user profile with role information
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile_data = role_service.get_user_profile_data(user, db)
        return profile_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")

@api_router.get("/auth/role-check/{phone}")
async def check_user_role(phone: str, db: Session = Depends(get_db)):
    """
    Check user role by phone number (for debugging/admin purposes)
    """
    try:
        role_info = role_service.determine_user_role(phone, db)
        return role_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Role check failed: {str(e)}")

# User endpoints
@api_router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@api_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@api_router.get("/users", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# Fixer endpoints
@api_router.post("/fixers", response_model=FixerResponse)
async def create_fixer(fixer: FixerCreate, db: Session = Depends(get_db)):
    db_fixer = Fixer(**fixer.dict())
    db.add(db_fixer)
    db.commit()
    db.refresh(db_fixer)
    return db_fixer

@api_router.get("/fixers", response_model=List[FixerResponse])
async def get_fixers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    fixers = db.query(Fixer).filter(Fixer.is_active == True).offset(skip).limit(limit).all()
    return fixers

@api_router.get("/fixers/{fixer_id}", response_model=FixerResponse)
async def get_fixer(fixer_id: str, db: Session = Depends(get_db)):
    fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
    if not fixer:
        raise HTTPException(status_code=404, detail="Fixer not found")
    return fixer

@api_router.get("/fixers/by-service/{service}")
async def get_fixers_by_service(service: str, db: Session = Depends(get_db)):
    fixers = db.query(Fixer).filter(
        Fixer.services.contains(service),
        Fixer.is_active == True
    ).all()
    return fixers

# Job endpoints
@api_router.post("/jobs", response_model=JobResponse)
async def create_job(job: JobCreate, db: Session = Depends(get_db)):
    # AI-powered service classification
    classification = ai_service.classify_service_request(job.description)
    
    # Create job
    db_job = Job(**job.dict())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Send SMS notification to user
    user = db.query(User).filter(User.id == job.user_id).first()
    if user:
        sms_service.send_job_notification(
            user.phone, 
            str(db_job.id), 
            job.service, 
            'created'
        )
    
    return db_job

@api_router.get("/jobs", response_model=List[JobResponse])
async def get_jobs(user_id: str = None, fixer_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Job)
    
    if user_id:
        query = query.filter(Job.user_id == user_id)
    if fixer_id:
        query = query.filter(Job.fixer_id == fixer_id)
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs

@api_router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@api_router.put("/jobs/{job_id}", response_model=JobResponse)
async def update_job(job_id: str, job_update: JobUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    old_status = job.status
    old_fixer_id = job.fixer_id
    
    # Check if we're assigning a fixer to the job
    if job_update.fixer_id and job_update.fixer_id != old_fixer_id:
        # Check fixer payment status
        payment_status = payment_service.check_fixer_payment_status(job_update.fixer_id, db)
        
        if not payment_status.get("can_receive_jobs", False):
            raise HTTPException(
                status_code=400,
                detail=f"Fixer cannot receive jobs due to outstanding payments. Outstanding: R{payment_status.get('total_outstanding', 0):.2f}"
            )
        
        # Create service fee for the fixer when job is assigned
        if job_update.status == "assigned":
            service_fee_result = payment_service.create_fixer_service_fee(
                job_update.fixer_id,
                f"Service fee for job: {job.service} - {job.description[:50]}",
                db
            )
            if not service_fee_result.get("success"):
                raise HTTPException(status_code=500, detail="Failed to create service fee")
    
    for key, value in job_update.dict(exclude_unset=True).items():
        setattr(job, key, value)
    
    job.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(job)
    
    # Send SMS notification if status changed
    if old_status != job.status:
        user = db.query(User).filter(User.id == job.user_id).first()
        if user:
            sms_service.send_job_notification(
                user.phone,
                str(job.id),
                job.service,
                job.status
            )
    
    return job

# Enhanced Job Workflow Endpoints

@api_router.post("/jobs/workflow", response_model=dict)
async def create_job_with_workflow(job_data: dict, db: Session = Depends(get_db)):
    """Create job with comprehensive workflow validation and processing"""
    user_id = job_data.get('user_id')
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    success, message, job = job_workflow_service.create_job_with_workflow(db, user_id, job_data)
    
    if success:
        return {
            "success": True,
            "message": message,
            "job_id": job.id if job else None,
            "workflow_status": job_workflow_service.get_job_workflow_status(db, job.id) if job else {}
        }
    else:
        raise HTTPException(status_code=400, detail=message)

@api_router.post("/terms/accept")
async def accept_platform_terms(request: dict, db: Session = Depends(get_db)):
    """Accept current platform terms"""
    user_id = request.get('user_id')
    ip_address = request.get('ip_address')
    user_agent = request.get('user_agent', '')
    method = request.get('method', 'web')
    
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    
    success = job_workflow_service.accept_terms(db, user_id, ip_address, user_agent, method)
    
    if success:
        return {"success": True, "message": "Terms accepted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to accept terms")

@api_router.get("/terms/check/{user_id}")
async def check_terms_acceptance(user_id: str, db: Session = Depends(get_db)):
    """Check if user has accepted current platform terms"""
    has_accepted = job_workflow_service.check_terms_acceptance(db, user_id)
    return {"has_accepted": has_accepted}

@api_router.post("/jobs/{job_id}/accept")
async def accept_job(job_id: str, request: dict, db: Session = Depends(get_db)):
    """Fixer accepts a job (first come, first serve)"""
    fixer_id = request.get('fixer_id')
    if not fixer_id:
        raise HTTPException(status_code=400, detail="fixer_id is required")
    
    success, message = job_workflow_service.accept_job(db, job_id, fixer_id)
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

@api_router.post("/jobs/{job_id}/complete")
async def complete_job_workflow(job_id: str, request: dict, db: Session = Depends(get_db)):
    """Complete job and process R20 platform fee"""
    fixer_id = request.get('fixer_id')
    if not fixer_id:
        raise HTTPException(status_code=400, detail="fixer_id is required")
    
    completion_data = request.get('completion_data', {})
    success, message = job_workflow_service.complete_job(db, job_id, fixer_id, completion_data)
    
    if success:
        return {"success": True, "message": message}
    else:
        raise HTTPException(status_code=400, detail=message)

@api_router.get("/jobs/{job_id}/workflow-status")
async def get_job_workflow_status(job_id: str, db: Session = Depends(get_db)):
    """Get complete workflow status for a job"""
    status = job_workflow_service.get_job_workflow_status(db, job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return status

@api_router.post("/fixer/{fixer_id}/location")
async def update_fixer_location(fixer_id: str, request: dict, db: Session = Depends(get_db)):
    """Update fixer location for live tracking"""
    latitude = request.get('latitude')
    longitude = request.get('longitude')
    
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail="latitude and longitude are required")
    
    success = job_workflow_service.update_fixer_location(db, fixer_id, float(latitude), float(longitude))
    
    if success:
        return {"success": True, "message": "Location updated successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update location")

@api_router.get("/fixer/{fixer_id}/eligible-jobs")
async def get_eligible_jobs(fixer_id: str, db: Session = Depends(get_db)):
    """Get jobs available for fixer to accept"""
    # Get fixer details
    fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
    if not fixer:
        raise HTTPException(status_code=404, detail="Fixer not found")
    
    # Get jobs in notification stage
    eligible_jobs = db.query(Job).filter(
        Job.status == "notifying_fixers",
        Job.assignment_timeout > datetime.utcnow()
    ).all()
    
    # Filter jobs where this fixer is eligible
    available_jobs = []
    for job in eligible_jobs:
        if job.eligible_fixers:
            eligible_fixer_ids = json.loads(job.eligible_fixers)
            if fixer_id in eligible_fixer_ids:
                available_jobs.append({
                    "job_id": job.id,
                    "service": job.service,
                    "description": job.description,
                    "location": job.location,
                    "estimated_price": job.estimated_price,
                    "assignment_timeout": job.assignment_timeout.isoformat(),
                    "priority_level": job.priority_level,
                    "is_emergency": job.is_emergency_escalated
                })
    
    return {"available_jobs": available_jobs}

@api_router.post("/admin/fixer/{fixer_id}/override")
async def admin_override_fixer_restriction(fixer_id: str, request: dict, db: Session = Depends(get_db)):
    """Admin override for fixer restrictions"""
    admin_id = request.get('admin_id')
    reason = request.get('reason', '')
    
    if not admin_id:
        raise HTTPException(status_code=400, detail="admin_id is required")
    
    # Verify admin permissions (you might want to add proper auth check here)
    admin = db.query(User).filter(User.id == admin_id, User.role.in_(['admin', 'super_admin'])).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = job_workflow_service.admin_override_fixer_restriction(db, fixer_id, admin_id, reason)
    
    if success:
        return {"success": True, "message": "Override applied successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to apply override")

@api_router.get("/fixer/{fixer_id}/behavior-analysis")
async def get_fixer_behavior_analysis(fixer_id: str, db: Session = Depends(get_db)):
    """Get AI behavior analysis for fixer"""
    from models import FixerBehaviorAnalysis
    
    analysis = db.query(FixerBehaviorAnalysis).filter(
        FixerBehaviorAnalysis.fixer_id == fixer_id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="No behavior analysis found")
    
    return {
        "fixer_id": analysis.fixer_id,
        "analysis_period": analysis.analysis_period,
        "completion_rate": analysis.completion_rate,
        "cancellation_rate": analysis.cancellation_rate,
        "reliability_score": analysis.reliability_score,
        "risk_level": analysis.risk_level,
        "behavior_flags": json.loads(analysis.behavior_flags) if analysis.behavior_flags else [],
        "ai_recommendations": json.loads(analysis.ai_recommendations) if analysis.ai_recommendations else [],
        "admin_attention_required": analysis.admin_attention_required,
        "last_analyzed_at": analysis.last_analyzed_at.isoformat()
    }

# AI-Powered Smart Matching Endpoints

@api_router.post("/jobs/{job_id}/smart-match")
async def find_smart_matches_for_job(job_id: str, request: dict, db: Session = Depends(get_db)):
    """
    Find best fixer matches for a job using AI-powered smart matching.
    Returns ranked list of fixers with match scores and explanations.
    """
    try:
        # Get the job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get matching parameters
        limit = request.get('limit', 10)
        auto_notify = request.get('auto_notify', False)
        
        # Find best matches using AI
        matches = smart_matching_service.find_best_fixers_for_job(db, job, limit)
        
        if not matches:
            return {
                'success': True,
                'message': 'No suitable fixers found for this job',
                'matches': [],
                'job_id': job_id,
                'search_performed': True
            }
        
        # Auto-notify fixers if requested
        notification_result = None
        if auto_notify and matches:
            # Select top matches for notification (max 5)
            top_matches = matches[:5]
            notification_result = smart_matching_service.notify_selected_fixers(db, job, top_matches)
        
        return {
            'success': True,
            'message': f'Found {len(matches)} suitable fixers',
            'matches': matches,
            'job_id': job_id,
            'search_performed': True,
            'notification_result': notification_result
        }
        
    except Exception as e:
        logger.error(f"Smart matching error for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Smart matching failed: {str(e)}")

@api_router.get("/jobs/{job_id}/match-insights")
async def get_job_match_insights(job_id: str, db: Session = Depends(get_db)):
    """
    Get AI insights about matching opportunities for a specific job.
    """
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Get potential matches (without full scoring)
        potential_fixers = smart_matching_service._get_eligible_fixers(db, job)
        
        if not potential_fixers:
            return {
                'job_id': job_id,
                'insights': {
                    'status': 'no_fixers',
                    'message': 'No eligible fixers found in the system',
                    'recommendations': [
                        'Consider expanding service categories',
                        'Review location coverage',
                        'Check if more fixers need approval'
                    ]
                }
            }
        
        # Prepare data for analysis
        job_data = smart_matching_service._prepare_job_data(job)
        fixer_data = [smart_matching_service._enrich_fixer_data(db, fixer, job) for fixer in potential_fixers]
        
        # Get AI insights
        insights = ai_service.generate_matching_insights(job_data, [])
        
        # Add additional statistics
        insights.update({
            'total_eligible_fixers': len(potential_fixers),
            'avg_distance': sum(f['distance_km'] for f in fixer_data if f['distance_km'] != float('inf')) / max(1, len([f for f in fixer_data if f['distance_km'] != float('inf')])),
            'available_now': sum(1 for f in fixer_data if f['is_available']),
            'highly_rated': sum(1 for f in fixer_data if f['rating'] >= 4.0),
            'service_area_coverage': len([f for f in fixer_data if f['distance_km'] <= 20])
        })
        
        return {
            'job_id': job_id,
            'insights': insights
        }
        
    except Exception as e:
        logger.error(f"Error getting match insights for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@api_router.get("/fixer/{fixer_id}/match-history")
async def get_fixer_match_history(fixer_id: str, days: int = 30, db: Session = Depends(get_db)):
    """
    Get fixer's matching performance history and statistics.
    """
    try:
        # Verify fixer exists
        fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
        if not fixer:
            raise HTTPException(status_code=404, detail="Fixer not found")
        
        # Get match history
        history = smart_matching_service.get_fixer_match_history(db, fixer_id, days)
        
        if 'error' in history:
            raise HTTPException(status_code=500, detail=history['error'])
        
        return {
            'success': True,
            'fixer_id': fixer_id,
            'fixer_name': fixer.name,
            'match_history': history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting match history for fixer {fixer_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get match history: {str(e)}")

@api_router.post("/fixer/{fixer_id}/match-test")
async def test_fixer_matching(fixer_id: str, request: dict, db: Session = Depends(get_db)):
    """
    Test how well a fixer would match against a hypothetical job.
    Useful for fixer onboarding and skill assessment.
    """
    try:
        # Verify fixer exists
        fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
        if not fixer:
            raise HTTPException(status_code=404, detail="Fixer not found")
        
        # Create mock job from request
        mock_job_data = {
            'id': 'test-job',
            'service': request.get('service', 'handyman'),
            'description': request.get('description', 'Test job description'),
            'location': request.get('location', 'Cape Town'),
            'latitude': request.get('latitude'),
            'longitude': request.get('longitude'),
            'estimated_price': request.get('estimated_price', 500.0),
            'priority_level': request.get('priority_level', 'normal'),
            'is_emergency': False,
            'client_language': request.get('client_language', 'english')
        }
        
        # Create mock job object for distance calculation
        class MockJob:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        mock_job = MockJob(mock_job_data)
        
        # Enrich fixer data
        fixer_data = smart_matching_service._enrich_fixer_data(db, fixer, mock_job)
        
        # Calculate match score
        match_result = ai_service.calculate_smart_match_score(fixer_data, mock_job_data)
        
        return {
            'success': True,
            'fixer_id': fixer_id,
            'fixer_name': fixer.name,
            'test_job': mock_job_data,
            'match_result': match_result,
            'recommendation': match_result['recommendation'],
            'explanation': match_result['explanation']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing match for fixer {fixer_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Match test failed: {str(e)}")

@api_router.get("/admin/matching-performance")
async def get_matching_performance(days: int = 7, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get overall matching performance analytics (Admin only).
    """
    # Check admin permissions
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        performance = smart_matching_service.analyze_matching_performance(db, days)
        
        if 'error' in performance:
            raise HTTPException(status_code=500, detail=performance['error'])
        
        return {
            'success': True,
            'performance_analysis': performance,
            'analyzed_by': current_user.display_name,
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting matching performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance data: {str(e)}")

@api_router.post("/admin/improve-matching")
async def get_matching_improvement_suggestions(request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get AI-powered suggestions for improving matching performance (Admin only).
    """
    # Check admin permissions
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        days = request.get('analysis_days', 30)
        
        # Get performance data
        performance = smart_matching_service.analyze_matching_performance(db, days)
        
        # Get recent problematic jobs
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        unassigned_jobs = db.query(Job).filter(
            Job.created_at >= cutoff_date,
            Job.fixer_id == None,
            Job.status != 'cancelled'
        ).limit(10).all()
        
        # Prepare data for AI analysis
        problem_data = {
            'performance': performance,
            'unassigned_jobs': [
                {
                    'service': job.service,
                    'description': job.description,
                    'location': job.location,
                    'created_hours_ago': (datetime.utcnow() - job.created_at).total_seconds() / 3600
                }
                for job in unassigned_jobs
            ]
        }
        
        # Generate AI recommendations
        if ai_service.model:
            prompt = f"""
            Analyze this FixMate-SA matching performance data and provide specific improvement recommendations:
            
            Performance Data: {json.dumps(problem_data, indent=2)}
            
            Provide 3-5 specific, actionable recommendations to improve job-to-fixer matching success rates.
            Focus on:
            1. Geographic coverage gaps
            2. Service category imbalances
            3. Fixer availability optimization
            4. Quality threshold adjustments
            5. Notification strategy improvements
            
            Format as a JSON array of recommendation objects with 'category', 'recommendation', and 'impact' fields.
            """
            
            try:
                response = ai_service.model.generate_content(prompt)
                ai_recommendations = response.text.strip()
            except:
                ai_recommendations = "AI recommendations unavailable - please review performance data manually"
        else:
            ai_recommendations = "AI service not configured"
        
        return {
            'success': True,
            'analysis_period_days': days,
            'performance_summary': performance,
            'problematic_jobs_count': len(unassigned_jobs),
            'ai_recommendations': ai_recommendations,
            'analyzed_by': current_user.display_name,
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating matching improvements: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

# ======= PHASE 2: TRUST & RELIABILITY ENDPOINTS =======

# Photo Verification Endpoints

@api_router.post("/jobs/{job_id}/photos")
async def submit_job_photos(job_id: str, request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Submit before, after, or progress photos for a job.
    Supports automatic AI analysis and quality assessment.
    """
    try:
        # Validate required fields
        photo_type = request.get('photo_type')  # 'before', 'after', 'progress'
        photos = request.get('photos', [])
        
        if not photo_type or photo_type not in ['before', 'after', 'progress']:
            raise HTTPException(status_code=400, detail="Invalid photo_type. Must be 'before', 'after', or 'progress'")
        
        if not photos or not isinstance(photos, list):
            raise HTTPException(status_code=400, detail="Photos array is required")
        
        # Submit photos
        result = photo_verification_service.submit_job_photos(
            db=db,
            job_id=job_id,
            photo_type=photo_type,
            photos=photos,
            submitted_by=current_user.id
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'message': result['message'],
            'data': {
                'verification_id': result['verification_id'],
                'photos_count': result['photos_count'],
                'total_size': result['total_size'],
                'status': result['status'],
                'is_new_record': result['is_new_record']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting job photos: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit photos: {str(e)}")

@api_router.get("/jobs/{job_id}/photo-verification")
async def get_job_photo_verification(job_id: str, db: Session = Depends(get_db)):
    """
    Get photo verification status and details for a job.
    """
    try:
        verification = photo_verification_service.get_job_photo_verification(db, job_id)
        
        if not verification:
            return {
                'success': True,
                'verification': None,
                'message': 'No photo verification found for this job'
            }
        
        return {
            'success': True,
            'verification': verification
        }
        
    except Exception as e:
        logger.error(f"Error getting photo verification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get photo verification: {str(e)}")

@api_router.get("/verification/{verification_id}/photos/{photo_type}")
async def get_verification_photos(verification_id: str, photo_type: str, db: Session = Depends(get_db)):
    """
    Get actual photo data for display (admin/authorized users only).
    """
    try:
        if photo_type not in ['before', 'after', 'progress']:
            raise HTTPException(status_code=400, detail="Invalid photo_type")
        
        photos = photo_verification_service.get_photo_data(db, verification_id, photo_type)
        
        if not photos:
            return {
                'success': True,
                'photos': [],
                'message': f'No {photo_type} photos found'
            }
        
        return {
            'success': True,
            'photos': photos,
            'count': len(photos)
        }
        
    except Exception as e:
        logger.error(f"Error getting verification photos: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get photos: {str(e)}")

@api_router.post("/admin/photo-verification/{verification_id}/verify")
async def admin_verify_photos(verification_id: str, request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Admin verification of job photos (Admin only).
    """
    # Check admin permissions
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        decision = request.get('decision')  # 'approved', 'rejected', 'needs_more'
        comments = request.get('comments', '')
        
        if decision not in ['approved', 'rejected', 'needs_more']:
            raise HTTPException(status_code=400, detail="Invalid decision. Must be 'approved', 'rejected', or 'needs_more'")
        
        result = photo_verification_service.admin_verify_photos(
            db=db,
            verification_id=verification_id,
            admin_id=current_user.id,
            decision=decision,
            comments=comments
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'message': result['message'],
            'verification_id': verification_id,
            'decision': decision,
            'verified_by': result['verified_by'],
            'verified_at': result['verified_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in admin photo verification: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

@api_router.get("/admin/photo-verifications/pending")
async def get_pending_photo_verifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get list of photo verifications pending admin review (Admin only).
    """
    # Check admin permissions
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        pending_verifications = photo_verification_service.get_pending_verifications(db)
        
        return {
            'success': True,
            'pending_verifications': pending_verifications,
            'count': len(pending_verifications)
        }
        
    except Exception as e:
        logger.error(f"Error getting pending photo verifications: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pending verifications: {str(e)}")

# Dispute Resolution Endpoints

@api_router.post("/jobs/{job_id}/dispute")
async def create_job_dispute(job_id: str, request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a dispute for a job.
    """
    try:
        # Validate required fields
        required_fields = ['dispute_type', 'description']
        for field in required_fields:
            if field not in request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        result = dispute_resolution_service.create_dispute(
            db=db,
            job_id=job_id,
            reporter_id=current_user.id,
            dispute_data=request
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'message': result['message'],
            'dispute_id': result['dispute_id'],
            'status': result['status'],
            'assigned_admin': result.get('assigned_admin'),
            'payment_hold': result.get('payment_hold', False)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating dispute: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create dispute: {str(e)}")

@api_router.post("/disputes/{dispute_id}/messages")
async def add_dispute_message(dispute_id: str, request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Add a message to an existing dispute.
    """
    try:
        if 'message' not in request:
            raise HTTPException(status_code=400, detail="Message is required")
        
        result = dispute_resolution_service.add_dispute_message(
            db=db,
            dispute_id=dispute_id,
            sender_id=current_user.id,
            message_data=request
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'message': result['message'],
            'message_id': result['message_id']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding dispute message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")

@api_router.get("/disputes/{dispute_id}")
async def get_dispute_details(dispute_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get complete dispute details including messages.
    """
    try:
        dispute = dispute_resolution_service.get_dispute_details(db, dispute_id)
        
        if not dispute:
            raise HTTPException(status_code=404, detail="Dispute not found")
        
        # Check permissions - only involved parties and admins can view
        is_authorized = (
            current_user.role in ['admin', 'super_admin'] or
            current_user.id == dispute['reporter']['id'] or
            current_user.id == dispute['job_details'].get('fixer_id')
        )
        
        if not is_authorized:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            'success': True,
            'dispute': dispute
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dispute details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dispute: {str(e)}")

@api_router.post("/admin/disputes/{dispute_id}/resolve")
async def resolve_dispute(dispute_id: str, request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Resolve a dispute with admin decision (Admin only).
    """
    # Check admin permissions
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        required_fields = ['resolution_action', 'resolution']
        for field in required_fields:
            if field not in request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        result = dispute_resolution_service.resolve_dispute(
            db=db,
            dispute_id=dispute_id,
            admin_id=current_user.id,
            resolution_data=request
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'message': result['message'],
            'dispute_id': dispute_id,
            'resolution_action': result['resolution_action'],
            'resolved_by': result['resolved_by'],
            'resolved_at': result['resolved_at']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving dispute: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve dispute: {str(e)}")

@api_router.get("/admin/disputes/pending")
async def get_pending_disputes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get list of pending disputes for admin review (Admin only).
    """
    # Check admin permissions
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        pending_disputes = dispute_resolution_service.get_pending_disputes(
            db=db,
            admin_id=current_user.id if current_user.role == 'admin' else None
        )
        
        return {
            'success': True,
            'pending_disputes': pending_disputes,
            'count': len(pending_disputes)
        }
        
    except Exception as e:
        logger.error(f"Error getting pending disputes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pending disputes: {str(e)}")

@api_router.post("/admin/disputes/auto-escalate")
async def auto_escalate_disputes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Auto-escalate disputes that have been open too long (Admin only).
    """
    # Check admin permissions
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = dispute_resolution_service.auto_escalate_disputes(db)
        
        return {
            'success': True,
            'message': result['message'],
            'escalated_count': result['escalated_count']
        }
        
    except Exception as e:
        logger.error(f"Error auto-escalating disputes: {e}")
        raise HTTPException(status_code=500, detail=f"Auto-escalation failed: {str(e)}")

# Job Completion with Photo Verification

@api_router.post("/jobs/{job_id}/complete-with-photos")
async def complete_job_with_photos(job_id: str, request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Complete a job with before/after photos (Fixer only).
    Combines job completion with photo verification process.
    """
    try:
        # Get the job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if current user is the assigned fixer
        if job.fixer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Only the assigned fixer can complete this job")
        
        # Check if job is in correct status
        if job.status not in ['assigned', 'in_progress']:
            raise HTTPException(status_code=400, detail=f"Cannot complete job with status: {job.status}")
        
        # Extract completion data
        before_photos = request.get('before_photos', [])
        after_photos = request.get('after_photos', [])
        completion_notes = request.get('completion_notes', '')
        final_price = request.get('final_price')
        
        # Submit before photos if provided
        if before_photos:
            before_result = photo_verification_service.submit_job_photos(
                db=db,
                job_id=job_id,
                photo_type='before',
                photos=before_photos,
                submitted_by=current_user.id
            )
            if not before_result['success']:
                raise HTTPException(status_code=400, detail=f"Before photos error: {before_result['error']}")
        
        # Submit after photos if provided
        if after_photos:
            after_result = photo_verification_service.submit_job_photos(
                db=db,
                job_id=job_id,
                photo_type='after',
                photos=after_photos,
                submitted_by=current_user.id
            )
            if not after_result['success']:
                raise HTTPException(status_code=400, detail=f"After photos error: {after_result['error']}")
        
        # Update job completion
        job.status = 'completed'
        job.job_completion_time = datetime.utcnow()
        
        if final_price:
            job.final_price = float(final_price)
        
        if completion_notes:
            # Add completion notes to job description or create a completion note field
            job.description += f"\n\nCompletion Notes: {completion_notes}"
        
        # Calculate actual duration if start time exists
        if job.job_start_time:
            duration = datetime.utcnow() - job.job_start_time
            job.actual_duration = int(duration.total_seconds() / 60)  # Duration in minutes
        
        job.updated_at = datetime.utcnow()
        
        try:
            db.commit()
            
            return {
                'success': True,
                'message': 'Job completed successfully with photo verification',
                'job_id': job_id,
                'status': job.status,
                'completion_time': job.job_completion_time.isoformat(),
                'final_price': job.final_price,
                'actual_duration': job.actual_duration,
                'photos_submitted': {
                    'before_count': len(before_photos),
                    'after_count': len(after_photos)
                }
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database error completing job with photos: {e}")
            raise HTTPException(status_code=500, detail="Database error occurred")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing job with photos: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete job: {str(e)}")

# ======= PHASE 3: AUTOMATION & ENGAGEMENT ENDPOINTS =======

# Real-Time Job Tracking Endpoints

@api_router.post("/jobs/{job_id}/tracking/start")
async def start_job_tracking(job_id: str, request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Start real-time tracking for a job (Fixer only).
    """
    try:
        # Find the fixer record associated with current user
        fixer = db.query(Fixer).filter(Fixer.user_id == current_user.id).first()
        if not fixer:
            raise HTTPException(status_code=403, detail="Access denied: User is not a registered fixer")
        
        departure_location = request.get('departure_location')  # {"lat": float, "lng": float}
        
        result = real_time_tracking_service.start_job_tracking(
            db=db,
            job_id=job_id,
            fixer_id=fixer.id,
            departure_location=departure_location
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'message': result['message'],
            'tracking_id': result['tracking_id'],
            'estimated_arrival': result.get('estimated_arrival'),
            'estimated_duration': result.get('estimated_duration')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting job tracking: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start tracking: {str(e)}")

@api_router.post("/jobs/{job_id}/tracking/location")
async def update_fixer_location(job_id: str, request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update fixer's current location and recalculate ETA (Fixer only).
    """
    try:
        # Find the fixer record associated with current user
        fixer = db.query(Fixer).filter(Fixer.user_id == current_user.id).first()
        if not fixer:
            raise HTTPException(status_code=403, detail="Access denied: User is not a registered fixer")
        
        location = request.get('location')  # {"lat": float, "lng": float}
        accuracy = request.get('accuracy')  # GPS accuracy in meters
        
        if not location or 'lat' not in location or 'lng' not in location:
            raise HTTPException(status_code=400, detail="Valid location with lat/lng is required")
        
        result = real_time_tracking_service.update_fixer_location(
            db=db,
            job_id=job_id,
            fixer_id=fixer.id,
            location=location,
            accuracy=accuracy
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'message': result['message'],
            'tracking_status': result['tracking_status'],
            'estimated_arrival': result.get('estimated_arrival'),
            'distance_to_job': result.get('distance_to_job'),
            'arrival_accuracy': result.get('arrival_accuracy')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating fixer location: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update location: {str(e)}")

@api_router.post("/jobs/{job_id}/tracking/complete")
async def complete_job_tracking(job_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Complete job tracking when work is finished (Fixer only).
    """
    try:
        # Find the fixer record associated with current user
        fixer = db.query(Fixer).filter(Fixer.user_id == current_user.id).first()
        if not fixer:
            raise HTTPException(status_code=403, detail="Access denied: User is not a registered fixer")
        
        result = real_time_tracking_service.complete_job_tracking(
            db=db,
            job_id=job_id,
            fixer_id=fixer.id
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'message': result['message'],
            'total_duration': result.get('total_duration'),
            'route_efficiency': result.get('route_efficiency')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing job tracking: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete tracking: {str(e)}")

@api_router.get("/jobs/{job_id}/tracking/status")
async def get_job_tracking_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get current tracking status for a job.
    """
    try:
        tracking_status = real_time_tracking_service.get_job_tracking_status(db, job_id)
        
        if not tracking_status:
            return {
                'success': True,
                'tracking': None,
                'message': 'No tracking information available for this job'
            }
        
        return {
            'success': True,
            'tracking': tracking_status
        }
        
    except Exception as e:
        logger.error(f"Error getting tracking status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tracking status: {str(e)}")

# Gamification & Reputation Endpoints

@api_router.get("/fixer/{fixer_id}/reputation")
async def get_fixer_reputation(fixer_id: str, db: Session = Depends(get_db)):
    """
    Get complete reputation and gamification information for a fixer.
    """
    try:
        reputation = gamification_service.get_fixer_reputation(db, fixer_id)
        
        if not reputation:
            return {
                'success': True,
                'reputation': None,
                'message': 'No reputation information found for this fixer'
            }
        
        return {
            'success': True,
            'reputation': reputation
        }
        
    except Exception as e:
        logger.error(f"Error getting fixer reputation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get reputation: {str(e)}")

@api_router.post("/fixer/{fixer_id}/reputation/initialize")
async def initialize_fixer_reputation(fixer_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Initialize reputation tier for a new fixer.
    """
    try:
        # Find the fixer record to check ownership
        fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
        if not fixer:
            raise HTTPException(status_code=404, detail="Fixer not found")
        
        # Check if current user owns this fixer record or is admin
        if current_user.id != fixer.user_id and current_user.role not in ['admin', 'super_admin']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        result = gamification_service.initialize_fixer_reputation(db, fixer_id)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'message': result['message'],
            'tier': result['tier'],
            'points': result['points']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing fixer reputation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize reputation: {str(e)}")

@api_router.post("/fixer/{fixer_id}/reputation/update")
async def update_fixer_performance(fixer_id: str, request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update fixer performance metrics (typically called after job completion).
    """
    try:
        # Find the fixer record to check ownership
        fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
        if not fixer:
            raise HTTPException(status_code=404, detail="Fixer not found")
        
        # Check permissions (fixer themselves or admin)
        if current_user.id != fixer.user_id and current_user.role not in ['admin', 'super_admin']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        job_completed = request.get('job_completed', True)
        
        result = gamification_service.update_fixer_performance(
            db=db,
            fixer_id=fixer_id,
            job_completed=job_completed
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'message': result['message'],
            'current_tier': result['current_tier'],
            'tier_points': result['tier_points'],
            'jobs_completed': result['jobs_completed'],
            'streak_count': result['streak_count'],
            'new_badges': result['new_badges'],
            'tier_changed': result['tier_changed'],
            'progress_to_next_tier': result['progress_to_next_tier']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating fixer performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update performance: {str(e)}")

# AI Multilingual Assistant Endpoints

@api_router.post("/ai-chat/start")
async def start_ai_conversation(request: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Start a new AI conversation session.
    """
    try:
        session_id = request.get('session_id')
        language = request.get('language', 'english')
        user_type = request.get('user_type', 'client')
        
        # Validate language
        if language not in ai_assistant.supported_languages:
            language = 'english'
        
        result = ai_assistant.start_conversation(
            db=db,
            user_id=current_user.id if current_user else None,
            session_id=session_id,
            language=language,
            user_type=user_type
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'conversation_id': result['conversation_id'],
            'session_id': result['session_id'],
            'welcome_message': result.get('welcome_message'),
            'supported_languages': result.get('supported_languages', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting AI conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start conversation: {str(e)}")

@api_router.post("/ai-chat/{session_id}/message")
async def send_ai_message(session_id: str, request: dict, db: Session = Depends(get_db)):
    """
    Send message to AI assistant and get response.
    """
    try:
        user_message = request.get('message')
        message_context = request.get('context', {})
        
        if not user_message or not user_message.strip():
            raise HTTPException(status_code=400, detail="Message is required")
        
        result = ai_assistant.process_user_message(
            db=db,
            session_id=session_id,
            user_message=user_message.strip(),
            message_context=message_context
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'message': result['message'],
            'intent': result.get('intent'),
            'confidence': result.get('confidence'),
            'actions': result.get('actions', []),
            'language': result.get('language'),
            'escalated': result.get('escalated', False),
            'total_messages': result.get('total_messages')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing AI message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@api_router.post("/ai-chat/{session_id}/end")
async def end_ai_conversation(session_id: str, request: dict, db: Session = Depends(get_db)):
    """
    End AI conversation and collect feedback.
    """
    try:
        satisfaction_rating = request.get('satisfaction_rating')  # 1-5
        resolved_query = request.get('resolved_query', False)
        
        if satisfaction_rating is not None:
            if not isinstance(satisfaction_rating, int) or satisfaction_rating < 1 or satisfaction_rating > 5:
                raise HTTPException(status_code=400, detail="Satisfaction rating must be between 1 and 5")
        
        result = ai_assistant.end_conversation(
            db=db,
            session_id=session_id,
            satisfaction_rating=satisfaction_rating,
            resolved_query=resolved_query
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'message': result['message'],
            'duration_minutes': result.get('duration_minutes'),
            'total_messages': result.get('total_messages'),
            'satisfaction_rating': satisfaction_rating
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending AI conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end conversation: {str(e)}")

@api_router.get("/ai-chat/{session_id}/history")
async def get_ai_conversation_history(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get conversation history and details.
    """
    try:
        history = ai_assistant.get_conversation_history(db, session_id)
        
        if not history:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Check permissions
        if history.get('user_id') and history['user_id'] != current_user.id and current_user.role not in ['admin', 'super_admin']:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            'success': True,
            'conversation': history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

# Anonymous AI Chat (for non-logged-in users)

@api_router.post("/ai-chat/anonymous/start")
async def start_anonymous_ai_conversation(request: dict, db: Session = Depends(get_db)):
    """
    Start anonymous AI conversation for non-logged-in users.
    """
    try:
        language = request.get('language', 'english')
        session_id = request.get('session_id')
        
        if language not in ai_assistant.supported_languages:
            language = 'english'
        
        result = ai_assistant.start_conversation(
            db=db,
            user_id=None,
            session_id=session_id,
            language=language,
            user_type='anonymous'
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return {
            'success': True,
            'conversation_id': result['conversation_id'],
            'session_id': result['session_id'],
            'welcome_message': result.get('welcome_message'),
            'supported_languages': result.get('supported_languages', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting anonymous AI conversation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start conversation: {str(e)}")

# Admin Analytics for Phase 3 Features

@api_router.get("/admin/gamification/stats")
async def get_gamification_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get gamification system statistics (Admin only).
    """
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from models import FixerReputationTier
        
        # Get tier distribution
        tier_stats = db.query(
            FixerReputationTier.current_tier,
            func.count(FixerReputationTier.id).label('count')
        ).group_by(FixerReputationTier.current_tier).all()
        
        # Get top performers
        top_performers = db.query(FixerReputationTier).order_by(
            FixerReputationTier.tier_points.desc()
        ).limit(10).all()
        
        # Calculate averages
        avg_stats = db.query(
            func.avg(FixerReputationTier.tier_points).label('avg_points'),
            func.avg(FixerReputationTier.client_satisfaction_avg).label('avg_satisfaction'),
            func.avg(FixerReputationTier.streak_count).label('avg_streak')
        ).first()
        
        return {
            'success': True,
            'tier_distribution': {tier: count for tier, count in tier_stats},
            'top_performers': [
                {
                    'fixer_id': performer.fixer_id,
                    'tier': performer.current_tier,
                    'points': performer.tier_points,
                    'jobs_completed': performer.jobs_completed,
                    'satisfaction': performer.client_satisfaction_avg
                }
                for performer in top_performers
            ],
            'averages': {
                'points': round(avg_stats.avg_points or 0, 1),
                'satisfaction': round(avg_stats.avg_satisfaction or 0, 2),
                'streak': round(avg_stats.avg_streak or 0, 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting gamification stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@api_router.get("/admin/ai-chat/analytics")
async def get_ai_chat_analytics(days: int = 7, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get AI chat analytics (Admin only).
    """
    if current_user.role not in ['admin', 'super_admin']:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from models import AIConversation
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get conversation stats
        conversations = db.query(AIConversation).filter(
            AIConversation.started_at >= cutoff_date
        ).all()
        
        total_conversations = len(conversations)
        completed_conversations = len([c for c in conversations if c.status == 'completed'])
        escalated_conversations = len([c for c in conversations if c.escalated_to_human])
        
        # Language distribution
        language_stats = {}
        for conv in conversations:
            lang = conv.language
            language_stats[lang] = language_stats.get(lang, 0) + 1
        
        # Average metrics
        total_messages = sum(c.total_messages for c in conversations)
        total_duration = sum(c.duration_minutes or 0 for c in conversations if c.duration_minutes)
        avg_satisfaction = sum(c.satisfaction_rating or 0 for c in conversations if c.satisfaction_rating) / max(1, len([c for c in conversations if c.satisfaction_rating]))
        
        return {
            'success': True,
            'period_days': days,
            'total_conversations': total_conversations,
            'completed_conversations': completed_conversations,
            'escalated_conversations': escalated_conversations,
            'completion_rate': round((completed_conversations / max(1, total_conversations)) * 100, 1),
            'escalation_rate': round((escalated_conversations / max(1, total_conversations)) * 100, 1),
            'language_distribution': language_stats,
            'averages': {
                'messages_per_conversation': round(total_messages / max(1, total_conversations), 1),
                'duration_minutes': round(total_duration / max(1, len([c for c in conversations if c.duration_minutes])), 1),
                'satisfaction_rating': round(avg_satisfaction, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting AI chat analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

# ======= PHASE 4: PUSH NOTIFICATION ENDPOINTS =======

@api_router.post("/push/subscribe")
async def subscribe_to_push(subscription_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Subscribe user to push notifications (PWA feature).
    """
    try:
        from services.push_notification_service import push_service, PushSubscriptionCreate
        
        # Validate subscription data
        required_fields = ['endpoint', 'keys']
        for field in required_fields:
            if field not in subscription_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create subscription
        subscription = PushSubscriptionCreate(
            endpoint=subscription_data['endpoint'],
            keys=subscription_data['keys'],
            user_agent=subscription_data.get('user_agent')
        )
        
        result = push_service.save_subscription(db, current_user.id, subscription)
        
        if result['success']:
            return {
                'success': True,
                'message': result['message'],
                'subscription_id': result['subscription_id']
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subscribing to push notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to subscribe: {str(e)}")

@api_router.get("/push/subscriptions")
async def get_push_subscriptions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get user's push notification subscriptions.
    """
    try:
        from services.push_notification_service import push_service
        
        subscriptions = push_service.get_user_subscriptions(db, current_user.id)
        
        return {
            'success': True,
            'subscriptions': subscriptions
        }
        
    except Exception as e:
        logger.error(f"Error getting push subscriptions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get subscriptions: {str(e)}")

@api_router.post("/push/send")
async def send_push_notification(notification_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Send push notification to user (Admin only or to self).
    """
    try:
        from services.push_notification_service import push_service, PushNotificationRequest
        
        # Validate required fields
        required_fields = ['title', 'body']
        for field in required_fields:
            if field not in notification_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        target_user_id = notification_data.get('user_id', current_user.id)
        
        # Check permissions
        if target_user_id != current_user.id and current_user.role not in ['admin', 'super_admin']:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Create notification
        notification = PushNotificationRequest(
            title=notification_data['title'],
            body=notification_data['body'],
            icon=notification_data.get('icon'),
            badge=notification_data.get('badge'),
            tag=notification_data.get('tag'),
            data=notification_data.get('data'),
            actions=notification_data.get('actions'),
            require_interaction=notification_data.get('require_interaction', False),
            silent=notification_data.get('silent', False),
            url=notification_data.get('url')
        )
        
        result = push_service.send_notification_to_user(db, target_user_id, notification)
        
        if result['success']:
            return {
                'success': True,
                'message': result['message'],
                'results': result.get('results', [])
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending push notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

@api_router.post("/push/send-to-role")
async def send_push_to_role(notification_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Send push notification to all users with specific role (Admin only).
    """
    try:
        from services.push_notification_service import push_service, PushNotificationRequest
        
        # Admin only
        if current_user.role not in ['admin', 'super_admin']:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Validate required fields
        required_fields = ['title', 'body', 'role']
        for field in required_fields:
            if field not in notification_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create notification
        notification = PushNotificationRequest(
            title=notification_data['title'],
            body=notification_data['body'],
            icon=notification_data.get('icon'),
            badge=notification_data.get('badge'),
            tag=notification_data.get('tag'),
            data=notification_data.get('data'),
            actions=notification_data.get('actions'),
            require_interaction=notification_data.get('require_interaction', False),
            silent=notification_data.get('silent', False),
            url=notification_data.get('url')
        )
        
        result = push_service.send_notification_to_role(db, notification_data['role'], notification)
        
        if result['success']:
            return {
                'success': True,
                'message': result['message'],
                'results': result.get('results', [])
            }
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending push notification to role: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

@api_router.get("/push/templates")
async def get_notification_templates(current_user: User = Depends(get_current_user)):
    """
    Get predefined notification templates.
    """
    try:
        from services.push_notification_service import push_service
        
        templates = push_service.get_notification_templates()
        
        return {
            'success': True,
            'templates': {
                name: {
                    'title': template.title,
                    'body': template.body,
                    'icon': template.icon,
                    'tag': template.tag,
                    'actions': template.actions,
                    'require_interaction': template.require_interaction
                }
                for name, template in templates.items()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting notification templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get templates: {str(e)}")

# ======= PWA SESSION TRACKING ENDPOINTS =======

@api_router.post("/pwa/session/start")
async def start_pwa_session(session_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Start PWA session tracking.
    """
    try:
        from models import AppSession
        
        # Create new session
        session = AppSession(
            user_id=current_user.id,
            session_id=session_data.get('session_id', str(uuid.uuid4())),
            user_agent=session_data.get('user_agent'),
            device_type=session_data.get('device_type'),
            platform=session_data.get('platform'),
            is_pwa=session_data.get('is_pwa', False),
            is_offline_capable=session_data.get('is_offline_capable', False),
            initial_load_time=session_data.get('initial_load_time')
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return {
            'success': True,
            'session_id': session.session_id,
            'message': 'Session started successfully'
        }
        
    except Exception as e:
        logger.error(f"Error starting PWA session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")

@api_router.post("/pwa/session/{session_id}/end")
async def end_pwa_session(session_id: str, session_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    End PWA session tracking.
    """
    try:
        from models import AppSession
        from datetime import datetime
        
        session = db.query(AppSession).filter(
            AppSession.session_id == session_id,
            AppSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update session end data
        session.session_end = datetime.utcnow()
        session.duration_seconds = session_data.get('duration_seconds')
        session.pages_visited = json.dumps(session_data.get('pages_visited', []))
        session.actions_performed = json.dumps(session_data.get('actions_performed', []))
        session.offline_actions_queued = session_data.get('offline_actions_queued', 0)
        session.cache_hits = session_data.get('cache_hits', 0)
        session.average_page_load_time = session_data.get('average_page_load_time')
        session.network_failures = session_data.get('network_failures', 0)
        
        db.commit()
        
        return {
            'success': True,
            'message': 'Session ended successfully',
            'duration_seconds': session.duration_seconds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending PWA session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")

@api_router.post("/pwa/offline-action")
async def queue_offline_action(action_data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Queue action for offline sync.
    """
    try:
        from models import OfflineAction
        from datetime import datetime, timedelta
        
        # Validate required fields
        required_fields = ['action_type', 'action_data', 'session_id']
        for field in required_fields:
            if field not in action_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Create offline action
        offline_action = OfflineAction(
            user_id=current_user.id,
            session_id=action_data['session_id'],
            action_type=action_data['action_type'],
            action_data=json.dumps(action_data['action_data']),
            priority=action_data.get('priority', 'normal'),
            created_offline_at=datetime.fromisoformat(action_data.get('created_offline_at', datetime.utcnow().isoformat())),
            expires_at=datetime.utcnow() + timedelta(days=7)  # Expire after 7 days
        )
        
        db.add(offline_action)
        db.commit()
        db.refresh(offline_action)
        
        return {
            'success': True,
            'action_id': offline_action.id,
            'message': 'Action queued for sync'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queuing offline action: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to queue action: {str(e)}")

@api_router.get("/pwa/offline-actions")
async def get_offline_actions(session_id: str = None, status: str = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get user's offline actions.
    """
    try:
        from models import OfflineAction
        
        query = db.query(OfflineAction).filter(OfflineAction.user_id == current_user.id)
        
        if session_id:
            query = query.filter(OfflineAction.session_id == session_id)
        if status:
            query = query.filter(OfflineAction.sync_status == status)
        
        actions = query.order_by(OfflineAction.created_offline_at.desc()).limit(100).all()
        
        return {
            'success': True,
            'actions': [
                {
                    'id': action.id,
                    'action_type': action.action_type,
                    'action_data': json.loads(action.action_data),
                    'priority': action.priority,
                    'sync_status': action.sync_status,
                    'sync_attempts': action.sync_attempts,
                    'created_offline_at': action.created_offline_at.isoformat(),
                    'synced_at': action.synced_at.isoformat() if action.synced_at else None
                }
                for action in actions
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting offline actions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get actions: {str(e)}")

# ======= END PHASE 4 ENDPOINTS =======

# Review endpoints
@api_router.post("/reviews", response_model=ReviewResponse)
async def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    # AI-powered sentiment analysis
    sentiment = ai_service.analyze_sentiment(review.comment or "")
    
    db_review = Review(**review.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # Update fixer rating
    fixer = db.query(Fixer).filter(Fixer.id == review.fixer_id).first()
    if fixer:
        reviews = db.query(Review).filter(Review.fixer_id == review.fixer_id).all()
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        fixer.rating = avg_rating
        db.commit()
    
    return db_review

@api_router.get("/reviews", response_model=List[ReviewResponse])
async def get_reviews(fixer_id: str = None, user_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    query = db.query(Review)
    
    if fixer_id:
        query = query.filter(Review.fixer_id == fixer_id)
    if user_id:
        query = query.filter(Review.user_id == user_id)
    
    reviews = query.offset(skip).limit(limit).all()
    return reviews

# Dashboard endpoints
@api_router.get("/dashboard/{user_id}")
async def get_dashboard(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's jobs
    jobs = db.query(Job).filter(Job.user_id == user_id).order_by(Job.created_at.desc()).limit(10).all()
    
    # Get recent fixers
    fixers = db.query(Fixer).filter(Fixer.is_active == True).order_by(Fixer.rating.desc()).limit(10).all()
    
    # Get stats
    total_jobs = db.query(Job).filter(Job.user_id == user_id).count()
    completed_jobs = db.query(Job).filter(Job.user_id == user_id, Job.status == "completed").count()
    
    # Generate AI business insight
    job_data = [{"id": job.id, "description": job.description, "service": job.service} for job in jobs]
    business_insight = ai_service.generate_business_insight(job_data)
    
    return {
        "user": user,
        "recent_jobs": jobs,
        "top_fixers": fixers,
        "stats": {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs
        },
        "business_insight": business_insight
    }

# Health check endpoint
@api_router.get("/")
async def root():
    return {"message": "FixMate-SA API is running"}

# PayFast payment endpoints
@api_router.post("/payfast/create-payment")
async def create_payfast_payment(
    job_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Create PayFast payment URL for a job.
    """
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        user = job.user
        
        # Prepare payment data
        payment_data = {
            'job_id': job.id,
            'client_name': user.full_name,
            'client_email': user.email or 'client@fixmate-sa.com',
            'client_phone': user.phone,
            'amount': str(job.estimated_price or 0.00),
            'service_type': job.service,
            'description': job.description,
            'user_id': user.id,
        }
        
        # Generate payment URL
        payment_url = payfast_service.generate_payment_url(payment_data)
        
        return {
            "success": True,
            "payment_url": payment_url,
            "job_id": job.id,
            "amount": payment_data['amount']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create payment: {str(e)}")

@api_router.post("/payfast/notify")
async def payfast_notification(request: dict, db: Session = Depends(get_db)):
    """
    Handle PayFast payment notifications.
    """
    try:
        # Process payment notification
        result = payfast_service.process_payment_notification(request)
        
        if result['status'] == 'error':
            logger.error(f"PayFast notification error: {result['message']}")
            return {"status": "error"}
        
        # Update job payment status
        job_id = result.get('job_id')
        if job_id:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                if result['payment_status'] == 'COMPLETE':
                    job.payment_status = 'paid'
                    job.final_price = float(result['amount_gross'])
                    
                    # Find and assign fixer if not already assigned
                    if not job.fixer_id:
                        matched_fixer = conversation_service.find_fixer_for_job(job, db)
                        if matched_fixer:
                            job.fixer_id = matched_fixer.id
                            job.status = 'assigned'
                            
                            # Send WhatsApp notification to fixer
                            job_data = {
                                'id': job.id,
                                'description': job.description,
                                'area': job.area,
                                'client_contact': job.client_contact_number
                            }
                            whatsapp_service.send_job_notification(matched_fixer.phone, job_data)
                        else:
                            job.status = 'paid_unassigned'
                    
                    db.commit()
                    
                    # Send confirmation to client
                    client_message = f"""✅ Payment confirmed! 

Job #{job.id} - {job.description}
Amount: R{result['amount_gross']}

We're finding the best fixer for you and will notify you once assigned.

Thank you for choosing FixMate-SA! 🔧"""
                    
                    whatsapp_service.send_whatsapp_message(job.user.phone, client_message)
                
                elif result['payment_status'] == 'FAILED':
                    job.payment_status = 'failed'
                    job.status = 'cancelled'
                    db.commit()
                    
                    # Notify client of failed payment
                    failure_message = f"""❌ Payment failed for Job #{job.id}

Please try again or contact support.

FixMate-SA Support"""
                    
                    whatsapp_service.send_whatsapp_message(job.user.phone, failure_message)
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"PayFast notification processing error: {e}")
        return {"status": "error", "error": str(e)}

@api_router.post("/payfast/fixer-payment")
async def create_fixer_payment(
    fixer_id: str = Form(...),
    payment_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Create PayFast payment URL for fixer service fee.
    """
    try:
        fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
        if not fixer:
            raise HTTPException(status_code=404, detail="Fixer not found")
        
        user = fixer.user
        
        # Prepare payment data
        payment_data = {
            'payment_id': payment_id,
            'fixer_name': fixer.name,
            'fixer_email': user.email or 'fixer@fixmate-sa.com',
            'fixer_phone': fixer.phone,
            'fixer_id': fixer.id,
        }
        
        # Generate payment URL
        payment_url = payfast_service.generate_fixer_payment_url(payment_data)
        
        return {
            "success": True,
            "payment_url": payment_url,
            "fixer_id": fixer.id,
            "amount": "20.00"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create fixer payment: {str(e)}")

@api_router.get("/payfast/payment-status/{job_id}")
async def get_payment_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get payment status for a job.
    """
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job.id,
            "payment_status": job.payment_status,
            "amount": job.final_price or job.estimated_price,
            "status": job.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get payment status: {str(e)}")

@api_router.post("/whatsapp/test")
async def test_whatsapp_api():
    """
    Test WhatsApp API connectivity and credentials.
    """
    try:
        result = whatsapp_service.send_whatsapp_message("27123456789", "Test message from FixMate-SA API")
        return {
            "status": "success" if result else "failed",
            "api_key_set": bool(whatsapp_service.api_key),
            "phone_number_id_set": bool(whatsapp_service.phone_number_id),
            "messages_url": whatsapp_service.messages_url,
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "api_key_set": bool(whatsapp_service.api_key),
            "phone_number_id_set": bool(whatsapp_service.phone_number_id),
            "messages_url": whatsapp_service.messages_url
        }

# Import the unified WhatsApp service
from services.unified_whatsapp_service import unified_whatsapp_service

# WhatsApp webhook endpoints - UNIFIED SYSTEM
@api_router.post("/whatsapp")
async def whatsapp_unified_webhook(request: dict, db: Session = Depends(get_db)):
    """
    Handle incoming WhatsApp messages using the unified system.
    This combines the proven working fixmate_whatsapp/run.py logic
    with the main FastAPI app's unified database models.
    
    Benefits:
    - Single database for all users (web + WhatsApp)
    - Unified models and relationships
    - Proven conversation logic from run.py
    - Complete data integration
    """
    try:
        print(f"🔄 Processing WhatsApp webhook with unified system")
        
        # Process webhook using the unified service
        result = unified_whatsapp_service.process_webhook(request, db)
        
        return result
        
    except Exception as e:
        logger.error(f"Unified WhatsApp webhook error: {e}")
        return {"status": "error", "error": str(e)}

@api_router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: dict, db: Session = Depends(get_db)):
    """
    Handle incoming WhatsApp messages from 360dialog.
    """
    try:
        # Process webhook message
        message_data = whatsapp_service.process_webhook_message(request)
        
        if message_data['status'] == 'ignored':
            return {"status": "ignored"}
        
        if message_data['status'] == 'error':
            logger.error(f"WhatsApp webhook error: {message_data.get('error')}")
            return {"status": "error"}
        
        # Process conversation
        from_number = message_data['from_number']
        content = message_data['content']
        msg_type = message_data['message_type']
        location_data = message_data.get('location')
        
        response_message = conversation_service.process_message(
            from_number, content, msg_type, location_data, db
        )
        
        # Send response
        if response_message:
            whatsapp_service.send_whatsapp_message(from_number, response_message)
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"WhatsApp webhook processing error: {e}")
        return {"status": "error", "error": str(e)}

@api_router.get("/whatsapp/webhook")
async def whatsapp_webhook_verify():
    """
    Verify WhatsApp webhook for 360dialog setup.
    """
    return {"status": "webhook verified"}

@api_router.post("/whatsapp/send-message")
async def send_whatsapp_message(
    to_number: str = Form(...),
    message: str = Form(...),
    media_url: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Send WhatsApp message manually (for testing/admin purposes).
    """
    try:
        success = whatsapp_service.send_whatsapp_message(to_number, message, media_url)
        return {"success": success, "message": "Message sent" if success else "Failed to send message"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@api_router.post("/whatsapp/send-job-notification")
async def send_job_notification(
    job_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Send job notification to fixer via WhatsApp.
    """
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if not job.fixer:
            raise HTTPException(status_code=400, detail="No fixer assigned to job")
        
        job_data = {
            'id': job.id,
            'description': job.description,
            'area': job.area,
            'client_contact': job.client_contact_number
        }
        
        success = whatsapp_service.send_job_notification(job.fixer.phone, job_data)
        return {"success": success, "message": "Notification sent" if success else "Failed to send notification"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

@api_router.post("/whatsapp/send-rating-request")
async def send_rating_request(
    job_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Send rating request to client via WhatsApp.
    """
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job_data = {
            'id': job.id,
            'description': job.description,
            'fixer_name': job.fixer.name if job.fixer else 'Unknown'
        }
        
        success = whatsapp_service.send_rating_request(job.user.phone, job_data)
        return {"success": success, "message": "Rating request sent" if success else "Failed to send request"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send rating request: {str(e)}")

@api_router.get("/whatsapp/insights")
async def get_business_insights(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get latest business insights generated by AI.
    """
    try:
        insights = db.query(DataInsight).filter(
            DataInsight.is_active == True
        ).order_by(DataInsight.created_at.desc()).limit(limit).all()
        
        return {
            "insights": [
                {
                    "id": insight.id,
                    "text": insight.insight_text,
                    "type": insight.insight_type,
                    "created_at": insight.created_at
                }
                for insight in insights
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@api_router.post("/whatsapp/generate-insight")
async def generate_business_insight(db: Session = Depends(get_db)):
    """
    Generate new business insight based on job data.
    """
    try:
        # Get completed jobs for analysis
        completed_jobs = db.query(Job).filter(Job.status == 'completed').all()
        
        if not completed_jobs:
            return {"message": "Not enough job data to generate insights"}
        
        # Prepare job data for AI analysis
        job_data = [
            {
                "description": job.description,
                "area": job.area,
                "service": job.service,
                "rating": job.rating
            }
            for job in completed_jobs
        ]
        
        # Generate insight using AI
        insight_text = ai_service.generate_business_insight(job_data)
        
        # Save insight to database
        insight = DataInsight(
            insight_text=insight_text,
            insight_type="business",
            generated_by="ai"
        )
        
        db.add(insight)
        db.commit()
        
        return {
            "success": True,
            "insight": insight_text,
            "generated_at": insight.created_at
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insight: {str(e)}")

# Business Compliance endpoints
@api_router.get("/compliance/categories")
async def get_compliance_categories():
    """Get all available business compliance categories"""
    return business_compliance_service.get_compliance_categories()

@api_router.post("/compliance/request")
async def submit_compliance_request(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a new business compliance assistance request"""
    try:
        result = business_compliance_service.create_compliance_request(
            db=db,
            user_id=current_user.id,
            category=request.get('category'),
            description=request.get('description'),
            urgency_level=request.get('urgency_level', 'normal'),
            contact_preference=request.get('contact_preference', 'whatsapp')
        )
        
        if result['success']:
            return {"success": True, "data": result}
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/compliance/requests")
async def get_user_compliance_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all compliance requests for the current user"""
    try:
        requests = business_compliance_service.get_user_requests(db, current_user.id)
        return {"success": True, "data": requests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/compliance/checklist/{category}")
async def get_compliance_checklist(category: str):
    """Get detailed compliance checklist for a specific category"""
    try:
        checklist = business_compliance_service.generate_compliance_checklist(category)
        if 'error' in checklist:
            raise HTTPException(status_code=400, detail=checklist['error'])
        return {"success": True, "data": checklist}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/compliance/admin/update/{request_id}")
async def update_compliance_request_status(
    request_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update compliance request status (Admin only)"""
    # Check if user is admin
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = business_compliance_service.update_request_status(
            db=db,
            request_id=request_id,
            status=update_data.get('status'),
            admin_notes=update_data.get('admin_notes'),
            estimated_cost=update_data.get('estimated_cost'),
            estimated_completion=update_data.get('estimated_completion')
        )
        
        if result['success']:
            return {"success": True, "message": result['message']}
        else:
            raise HTTPException(status_code=400, detail=result['error'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/compliance/admin/all-requests")
async def get_all_compliance_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all compliance requests (Admin only)"""
    # Check if user is admin
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        from models import BusinessComplianceRequest
        requests = db.query(BusinessComplianceRequest).order_by(
            BusinessComplianceRequest.created_at.desc()
        ).all()
        
        return {
            "success": True,
            "data": [
                {
                    'id': req.id,
                    'user_id': req.user_id,
                    'user_name': f"{req.user.first_name} {req.user.last_name}",
                    'user_phone': req.user.phone,
                    'category': req.category,
                    'category_name': business_compliance_service.COMPLIANCE_CATEGORIES.get(req.category, {}).get('name', req.category),
                    'description': req.description,
                    'status': req.status,
                    'urgency_level': req.urgency_level,
                    'contact_preference': req.contact_preference,
                    'created_at': req.created_at.isoformat(),
                    'updated_at': req.updated_at.isoformat() if req.updated_at else None,
                    'admin_notes': req.admin_notes,
                    'estimated_cost': req.estimated_cost,
                    'estimated_completion': req.estimated_completion.isoformat() if req.estimated_completion else None
                }
                for req in requests
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WhatsApp Business Integration (Updated for 0754466571)
@api_router.post("/whatsapp/business/webhook")
async def whatsapp_business_webhook(request: Request, db: Session = Depends(get_db)):
    """
    WhatsApp Business webhook for official FixMate-SA number (0754466571)
    """
    try:
        # Get request data
        webhook_data = await request.json()
        
        # Process the webhook message
        result = whatsapp_service.process_business_webhook(webhook_data, db)
        
        return {"success": True, "processed": result}
        
    except Exception as e:
        print(f"WhatsApp business webhook error: {e}")
        return {"success": False, "error": str(e)}

@api_router.get("/whatsapp/business/webhook")
async def whatsapp_business_webhook_verify(hub_challenge: str = None):
    """
    Verify WhatsApp Business webhook for 0754466571
    """
    # This is for webhook verification
    if hub_challenge:
        return Response(content=hub_challenge, media_type="text/plain")
    
    return {"success": True, "message": "FixMate-SA WhatsApp Business webhook active"}

# WhatsApp webhook endpoints WITHOUT /api prefix for Facebook integration
# Facebook/WhatsApp Business API expects the webhook at /whatsapp not /api/whatsapp

@app.get("/whatsapp")
async def whatsapp_webhook_verify(request: Request):
    """
    Verify WhatsApp webhook subscription from Facebook.
    Facebook sends GET request with verification parameters.
    """
    try:
        # Get query parameters from request
        hub_mode = request.query_params.get('hub.mode')
        hub_challenge = request.query_params.get('hub.challenge')
        hub_verify_token = request.query_params.get('hub.verify_token')
        
        print(f"🔐 WhatsApp webhook verification request: mode={hub_mode}, challenge={hub_challenge}")
        
        # For webhook verification, return the challenge
        if hub_mode == "subscribe" and hub_challenge:
            print("✅ WhatsApp webhook verification successful")
            return Response(content=hub_challenge, media_type="text/plain")
            
        return {"success": True, "message": "FixMate-SA WhatsApp webhook endpoint"}
        
    except Exception as e:
        print(f"❌ Error in WhatsApp webhook verification: {str(e)}")
        return {"success": False, "error": str(e)}

@app.post("/whatsapp")
async def whatsapp_webhook(request: dict, db: Session = Depends(get_db)):
    """
    Handle incoming WhatsApp messages from Facebook Business API.
    This endpoint is hit directly by Facebook at /whatsapp (no /api prefix).
    """
    try:
        print(f"🔄 Processing WhatsApp webhook from Facebook at /whatsapp")
        
        # Import the unified WhatsApp service
        from services.unified_whatsapp_service import unified_whatsapp_service
        
        # Process webhook using the unified service
        result = unified_whatsapp_service.process_webhook(request, db)
        
        return result
        
    except Exception as e:
        print(f"❌ Error processing WhatsApp webhook: {str(e)}")
        return {"success": False, "error": str(e)}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from React build if available
static_path = Path(__file__).parent.parent / "frontend" / "build"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path / "static")), name="static")
    
    # Serve React app for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Serve the React app for all non-API routes"""
        # Don't serve React app for API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Don't serve React app for WhatsApp webhook endpoints
        if full_path == "whatsapp":
            raise HTTPException(status_code=404, detail="WhatsApp endpoint not found")
        
        # Check if it's a static file request
        static_file_path = static_path / full_path
        if static_file_path.is_file():
            return FileResponse(static_file_path)
        
        # For all other routes, serve the React app
        index_path = static_path / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        else:
            return {"message": "FixMate-SA API is running", "status": "ok", "frontend": "not built"}

else:
    @app.get("/")
    async def root():
        return {"message": "FixMate-SA API is running", "status": "ok", "frontend": "not built"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
