from sqlalchemy import Column, String, DateTime, Integer, Text, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)  # NEW: First name for personalized welcome
    last_name = Column(String, nullable=False)   # NEW: Last name for full identification
    id_number = Column(String, unique=True, nullable=False, index=True)  # NEW: SA ID number
    town = Column(String, nullable=False)        # NEW: Town/Local municipality
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)        # Detailed address (optional)
    password_hash = Column(String, nullable=True)
    is_password_set = Column(Boolean, default=False)
    role = Column(String, default="client")      # client, fixer, admin, super_admin
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    
    # WhatsApp conversation state management
    conversation_state = Column(String, nullable=True)  # Current conversation state
    service_request_cache = Column(Text, nullable=True)  # Cached service request data (JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = relationship("Job", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    emergency_alerts = relationship("EmergencyAlert", back_populates="user")
    fixer_applications = relationship("FixerApplication", back_populates="user")
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
        self.is_password_set = True
    
    def check_password(self, password):
        """Check if password matches hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Get full name for display"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self):
        """Get display name (first name for welcome messages)"""
        return self.first_name

class FixerApplication(Base):
    __tablename__ = "fixer_applications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Application details
    services_offered = Column(Text, nullable=False)  # JSON string of services
    experience_years = Column(Integer, nullable=False)
    qualifications = Column(Text, nullable=True)  # Educational/professional qualifications
    previous_work = Column(Text, nullable=True)   # Previous work experience
    why_fixer = Column(Text, nullable=False)      # Why they want to be a fixer
    
    # Documents (stored as base64 or file paths)
    id_document = Column(Text, nullable=False)    # ID document image
    proof_of_address = Column(Text, nullable=True) # Proof of address
    qualifications_cert = Column(Text, nullable=True) # Qualification certificates
    criminal_clearance = Column(Text, nullable=True)  # Criminal clearance certificate
    
    # Application status and review
    status = Column(String, default="pending")    # pending, under_review, approved, rejected, needs_documents
    admin_notes = Column(Text, nullable=True)     # Admin review notes
    rejection_reason = Column(Text, nullable=True) # Reason for rejection if applicable
    reviewed_by = Column(String, nullable=True)   # Admin ID who reviewed
    reviewed_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Application dates
    submitted_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="fixer_applications")

class Fixer(Base):
    __tablename__ = "fixers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)  # Link to user account
    application_id = Column(String, ForeignKey("fixer_applications.id"), nullable=True)  # Link to approved application
    
    phone = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    services = Column(Text, nullable=False)  # JSON string of services
    location = Column(String, nullable=False)
    rating = Column(Float, default=0.0)
    total_jobs = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)  # NEW: Approval status from vetting process
    approval_date = Column(DateTime, nullable=True)  # When fixer was approved
    payment_status = Column(String, default="current")  # current, overdue, blocked
    
    # WhatsApp integration fields
    vetting_status = Column(String, default="pending")  # pending, approved, rejected
    skills = Column(Text, nullable=True)  # Skills for job matching
    current_latitude = Column(Float, nullable=True)  # Current GPS location
    current_longitude = Column(Float, nullable=True)
    last_assigned_at = Column(DateTime, nullable=True)  # For fair job distribution
    balance = Column(Float, default=0.0)  # For fee management
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    application = relationship("FixerApplication", foreign_keys=[application_id])
    jobs = relationship("Job", back_populates="fixer")
    reviews = relationship("Review", back_populates="fixer")
    payments = relationship("FixerPayment", back_populates="fixer")
    verification = relationship("FixerVerification", back_populates="fixer", uselist=False)

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=True)
    service = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, assigned, in_progress, completed, cancelled
    estimated_price = Column(Float, nullable=True)
    final_price = Column(Float, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    
    # WhatsApp integration fields
    client_contact_number = Column(String, nullable=True)  # Contact number provided by client
    area = Column(String, nullable=True)  # Area derived from location
    latitude = Column(Float, nullable=True)  # GPS coordinates
    longitude = Column(Float, nullable=True)
    payment_status = Column(String, default="pending")  # pending, paid, failed
    rating = Column(Integer, nullable=True)  # 1-5 rating from client
    rating_comment = Column(Text, nullable=True)  # Client's review comment
    sentiment = Column(String, nullable=True)  # AI-analyzed sentiment of review
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    fixer = relationship("Fixer", back_populates="jobs")
    reviews = relationship("Review", back_populates="job")
    emergency_alerts = relationship("EmergencyAlert", back_populates="job")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 rating
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
    fixer = relationship("Fixer", back_populates="reviews")

class FixerPayment(Base):
    __tablename__ = "fixer_payments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=False)
    amount = Column(Float, nullable=False)  # R20.00 service fee
    payment_type = Column(String, nullable=False)  # eft, airtime, cash, etc.
    payment_method = Column(String, nullable=True)  # card, bank_transfer, etc.
    payment_reference = Column(String, nullable=True)  # transaction reference
    status = Column(String, default="pending")  # pending, paid, overdue, settled
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fixer = relationship("Fixer", back_populates="payments")

class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=True)  # Optional if during a job
    alert_type = Column(String, default="emergency")  # emergency, panic, safety
    latitude = Column(Float, nullable=True)  # User's location
    longitude = Column(Float, nullable=True)
    address = Column(Text, nullable=True)  # Human readable address
    description = Column(Text, nullable=True)  # User's description of emergency
    status = Column(String, default="active")  # active, resolved, false_alarm
    police_notified = Column(Boolean, default=False)  # Track if police contacted
    police_reference = Column(String, nullable=True)  # Police case number if available
    emergency_contacts_notified = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emergency_alerts")
    job = relationship("Job", back_populates="emergency_alerts")

class FixerVerification(Base):
    __tablename__ = "fixer_verifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=False)
    id_document_url = Column(String, nullable=True)  # Base64 or file path
    verification_status = Column(String, default="pending")  # pending, verified, rejected
    admin_notes = Column(Text, nullable=True)
    verified_by = Column(String, nullable=True)  # Admin ID who verified
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fixer = relationship("Fixer", back_populates="verification")

class DataInsight(Base):
    __tablename__ = "data_insights"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    insight_text = Column(Text, nullable=False)
    insight_type = Column(String, default="business")  # business, trend, market
    generated_by = Column(String, default="ai")  # ai, admin, system
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DataInsight(id='{self.id}', insight='{self.insight_text[:50]}...')>"

class BusinessComplianceRequest(Base):
    __tablename__ = "business_compliance_requests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    category = Column(String(100), nullable=False)  # company_registration, sars_registration, etc.
    description = Column(Text, nullable=False)
    urgency_level = Column(String(20), default='normal')  # low, normal, high, urgent
    contact_preference = Column(String(20), default='whatsapp')  # whatsapp, sms, phone, email
    status = Column(String(50), default='submitted')  # submitted, in_review, quote_sent, in_progress, completed, cancelled
    admin_notes = Column(Text)
    estimated_cost = Column(Float)
    estimated_completion = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="compliance_requests")
    
    def __repr__(self):
        return f"<BusinessComplianceRequest(id='{self.id}', category='{self.category}', status='{self.status}')>"