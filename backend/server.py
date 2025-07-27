from fastapi import FastAPI, APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from typing import List, Optional
import json
from datetime import datetime

from database import get_db, create_tables
from models import User, Fixer, Job, Review
from schemas import (
    UserCreate, UserResponse, FixerCreate, FixerResponse,
    JobCreate, JobUpdate, JobResponse, ReviewCreate, ReviewResponse,
    LoginRequest, LoginResponse
)
from services.ai_service import ai_service
from services.sms_service import sms_service
from services.payment_service import payment_service
from services.ussd_service import ussd_service

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create tables
create_tables()

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

# SMS endpoints
@api_router.post("/sms/send")
async def send_sms(to_number: str = Form(...), message: str = Form(...)):
    """
    Send SMS to user.
    """
    try:
        success = sms_service.send_sms(to_number, message)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMS sending failed: {str(e)}")

@api_router.post("/sms/webhook")
async def sms_webhook(From: str = Form(...), Body: str = Form(...)):
    """
    Handle incoming SMS webhook from Twilio.
    """
    try:
        response_message = sms_service.handle_incoming_sms(From, Body)
        # Send response back
        sms_service.send_sms(From, response_message)
        return Response(content="OK", media_type="text/plain")
    except Exception as e:
        print(f"SMS webhook error: {e}")
        return Response(content="Error", media_type="text/plain")

# Authentication endpoints
@api_router.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == request.phone).first()
    
    if not user:
        # Create new user if doesn't exist
        user = User(phone=request.phone, name=f"User {request.phone}")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Simple token for now (in production, use JWT)
    token = f"token_{user.id}"
    
    return LoginResponse(user=user, token=token)

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
