from fastapi import FastAPI, APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import or_
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime

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
from services.conversation_service import conversation_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create tables
drop_and_recreate_tables()

# Create the main app without a prefix
app = FastAPI(title="FixMate-SA API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

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
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            or_(User.phone == request.phone, User.id_number == request.id_number)
        ).first()
        
        if existing_user:
            if existing_user.phone == request.phone:
                raise HTTPException(status_code=400, detail="Phone number already registered")
            else:
                raise HTTPException(status_code=400, detail="ID number already registered")
        
        # Create user data
        user_data = {
            "phone": request.phone,
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
        # Check if user exists
        user = db.query(User).filter(User.phone == request.phone).first()
        
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

# WhatsApp webhook endpoints
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

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
