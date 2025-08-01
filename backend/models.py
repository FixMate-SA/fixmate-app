from sqlalchemy import Column, String, DateTime, Integer, Text, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import bcrypt
import json

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)  # First name for personalized welcome
    last_name = Column(String, nullable=False)   # Last name for full identification
    id_number = Column(String, unique=True, nullable=False, index=True)  # SA ID number
    town = Column(String, nullable=False)        # Town/Local municipality
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)        # Detailed address (optional)
    password_hash = Column(String, nullable=True)
    is_password_set = Column(Boolean, default=False)
    role = Column(String, default="client")      # client, fixer, admin, super_admin
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    
    # WhatsApp conversation state management - UNIFIED FROM run.py
    conversation_state = Column(String, nullable=True)  # Current conversation state
    service_request_cache = Column(Text, nullable=True)  # Cached service request data (JSON)
    whatsapp_active = Column(Boolean, default=False)    # Whether user accessed via WhatsApp
    last_whatsapp_message = Column(DateTime, nullable=True)  # Last WhatsApp interaction
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = relationship("Job", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    compliance_requests = relationship("BusinessComplianceRequest", back_populates="user")
    emergency_alerts = relationship("EmergencyAlert", back_populates="user")
    fixer_applications = relationship("FixerApplication", back_populates="user")
    terms_acceptances = relationship("UserTermsAcceptance", back_populates="user")
    
    # Phase 4: PWA & Mobile Relationships
    push_subscriptions = relationship("PushSubscription", back_populates="user")
    app_sessions = relationship("AppSession", back_populates="user")
    offline_actions = relationship("OfflineAction", back_populates="user")
    
    def set_password(self, password):
        """Set password hash using bcrypt"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.is_password_set = True
    
    def check_password(self, password):
        """Check if password matches hash"""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    # WhatsApp conversation management methods - FROM run.py integration
    def set_conversation_cache(self, data):
        """Set conversation cache data"""
        self.service_request_cache = json.dumps(data) if data else None
    
    def get_conversation_cache(self):
        """Get conversation cache data"""
        if self.service_request_cache:
            try:
                return json.loads(self.service_request_cache)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def clear_conversation_cache(self):
        """Clear conversation cache and state"""
        self.service_request_cache = None
        self.conversation_state = None
    
    def update_whatsapp_activity(self):
        """Update WhatsApp activity timestamp"""
        self.whatsapp_active = True
        self.last_whatsapp_message = datetime.utcnow()
    
    @property
    def full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property 
    def display_name(self):
        """Get display name based on role and context"""
        if self.role == 'admin' or self.role == 'super_admin':
            return f"Admin {self.first_name}"
        elif self.role == 'fixer':
            return f"Fixer {self.first_name}"
        else:
            return self.first_name
    
    def __repr__(self):
        return f'<User {self.phone}>'
    
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
    
    # Enhanced rating and performance tracking
    base_rating = Column(Float, default=0.0)  # Base rating before penalties
    rating_penalty_total = Column(Float, default=0.0)  # Total rating penalties applied
    minimum_rating_threshold = Column(Float, default=3.0)  # Minimum rating required for jobs
    is_new_fixer = Column(Boolean, default=True)  # If fixer is new (0.0 rating acceptable)
    
    # Job completion tracking
    jobs_completed = Column(Integer, default=0)
    jobs_cancelled = Column(Integer, default=0)
    jobs_incomplete = Column(Integer, default=0)
    jobs_no_show = Column(Integer, default=0)
    completion_percentage = Column(Float, default=100.0)  # Calculated completion rate
    
    # Cancellation and penalty tracking
    cancellation_penalty_count = Column(Integer, default=0)
    last_cancellation_penalty = Column(DateTime, nullable=True)
    availability_freeze_count = Column(Integer, default=0)  # Number of times frozen
    total_freeze_hours = Column(Integer, default=0)  # Total hours frozen
    
    # Platform fee management
    platform_fees_owed = Column(Float, default=0.0)  # Total platform fees owed
    platform_fees_paid = Column(Float, default=0.0)  # Total platform fees paid
    fee_payment_overdue = Column(Boolean, default=False)  # If fees are overdue > 48 hours
    fee_suspension_applied = Column(Boolean, default=False)  # If suspended due to unpaid fees
    
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
    # New workflow relationships
    availability = relationship("FixerAvailability", back_populates="fixer", uselist=False)
    behavior_analysis = relationship("FixerBehaviorAnalysis", back_populates="fixer")
    assignment_history = relationship("JobAssignmentHistory", back_populates="fixer")
    notifications = relationship("JobNotification", back_populates="fixer")

# New models for enhanced job workflow system

class JobAssignmentHistory(Base):
    """Track all assignment attempts and fixer responses"""
    __tablename__ = "job_assignment_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=False)
    
    # Assignment details
    assignment_type = Column(String, nullable=False)  # initial, reassignment, escalation
    notified_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)
    response_type = Column(String, nullable=True)  # accepted, declined, timeout, cancelled
    response_reason = Column(Text, nullable=True)  # Reason for decline/cancellation
    
    # Tracking
    accepted_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    completion_status = Column(String, nullable=True)  # completed, incomplete, cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="assignment_history")
    fixer = relationship("Fixer", back_populates="assignment_history")

class JobNotification(Base):
    """Track all notifications sent to fixers"""
    __tablename__ = "job_notifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=False)
    
    # Notification details
    notification_type = Column(String, nullable=False)  # job_available, assignment, reminder, escalation
    channel = Column(String, nullable=False)  # app, whatsapp, sms
    message_content = Column(Text, nullable=False)
    
    # Status tracking
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    responded_at = Column(DateTime, nullable=True)
    status = Column(String, default="pending")  # pending, sent, delivered, read, failed
    
    # Response tracking
    response_action = Column(String, nullable=True)  # accept, decline, ignore
    response_data = Column(Text, nullable=True)  # JSON response data
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="notifications")
    fixer = relationship("Fixer", back_populates="notifications")

class FixerAvailability(Base):
    """Track fixer availability and current job status"""
    __tablename__ = "fixer_availability"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=False, unique=True)
    
    # Availability status
    is_available = Column(Boolean, default=True)  # Overall availability
    current_job_id = Column(String, ForeignKey("jobs.id"), nullable=True)  # Current active job
    is_on_break = Column(Boolean, default=False)  # Manual break status
    break_until = Column(DateTime, nullable=True)  # When break ends
    
    # Location for proximity matching
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    location_updated_at = Column(DateTime, nullable=True)
    service_radius = Column(Integer, default=20)  # Service radius in km
    
    # Performance metrics for AI matching
    average_response_time = Column(Integer, nullable=True)  # Minutes
    completion_rate = Column(Float, default=100.0)  # Percentage
    reliability_score = Column(Float, default=100.0)  # AI-calculated reliability
    last_job_completed_at = Column(DateTime, nullable=True)
    
    # Restriction tracking
    has_outstanding_debt = Column(Boolean, default=False)
    debt_amount = Column(Float, default=0.0)
    is_suspended = Column(Boolean, default=False)  # Admin suspension
    suspension_reason = Column(Text, nullable=True)
    suspension_until = Column(DateTime, nullable=True)
    
    # Enhanced workflow restrictions
    is_availability_frozen = Column(Boolean, default=False)  # Temporary freeze after cancellation
    availability_frozen_until = Column(DateTime, nullable=True)  # When freeze expires
    freeze_reason = Column(String, nullable=True)  # Reason for freeze (timeout, cancellation, etc.)
    
    # Rating and performance thresholds
    minimum_rating_met = Column(Boolean, default=True)  # If meets minimum 3.0 rating requirement
    rating_penalty_applied = Column(Float, default=0.0)  # Accumulated rating penalties
    cancellation_penalty_count = Column(Integer, default=0)  # Number of cancellation penalties
    
    # Payment status tracking
    platform_fee_status = Column(String, default="current")  # current, overdue, blocked
    platform_fee_overdue_since = Column(DateTime, nullable=True)  # When fees became overdue
    platform_fee_amount_due = Column(Float, default=0.0)  # Amount currently due
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    fixer = relationship("Fixer", back_populates="availability")
    current_job = relationship("Job", foreign_keys=[current_job_id])

class FixerBehaviorAnalysis(Base):
    """AI monitoring and behavior analysis for fixers"""
    __tablename__ = "fixer_behavior_analysis"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=False)
    
    # Behavior patterns
    analysis_period = Column(String, default="30_days")  # 7_days, 30_days, 90_days, all_time
    total_jobs_assigned = Column(Integer, default=0)
    total_jobs_completed = Column(Integer, default=0)
    total_jobs_cancelled = Column(Integer, default=0)
    total_jobs_incomplete = Column(Integer, default=0)
    
    # Performance metrics
    completion_rate = Column(Float, default=0.0)  # Percentage
    cancellation_rate = Column(Float, default=0.0)  # Percentage
    average_response_time = Column(Integer, default=0)  # Minutes
    average_job_duration = Column(Integer, default=0)  # Minutes
    client_satisfaction_avg = Column(Float, default=0.0)  # Average rating
    
    # AI flags and alerts
    reliability_score = Column(Float, default=100.0)  # AI-calculated score
    risk_level = Column(String, default="low")  # low, medium, high, critical
    behavior_flags = Column(Text, nullable=True)  # JSON array of behavior flags
    ai_recommendations = Column(Text, nullable=True)  # AI-generated recommendations
    admin_attention_required = Column(Boolean, default=False)
    
    # Pattern detection
    frequent_cancellation_pattern = Column(Boolean, default=False)
    dishonesty_indicators = Column(Text, nullable=True)  # JSON array of indicators
    quality_decline_trend = Column(Boolean, default=False)
    improvement_trend = Column(Boolean, default=False)
    
    # Analysis metadata
    last_analyzed_at = Column(DateTime, default=datetime.utcnow)
    next_analysis_due = Column(DateTime, nullable=True)
    analysis_version = Column(String, default="1.0")  # AI model version used
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fixer = relationship("Fixer", back_populates="behavior_analysis")

class PlatformTerms(Base):
    """Track platform terms and client acceptance"""
    __tablename__ = "platform_terms"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    version = Column(String, nullable=False)  # Terms version (e.g., "1.0", "2.1")
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # Full terms content
    effective_date = Column(DateTime, nullable=False)
    is_current = Column(Boolean, default=True)  # If this is the current version
    
    # Usage tracking
    acceptance_count = Column(Integer, default=0)  # How many users accepted
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=True)  # Admin who created/updated
    
    # Relationships
    user_acceptances = relationship("UserTermsAcceptance", back_populates="terms")

class UserTermsAcceptance(Base):
    """Track individual user acceptance of platform terms"""
    __tablename__ = "user_terms_acceptance"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    terms_id = Column(String, ForeignKey("platform_terms.id"), nullable=False)
    
    # Acceptance details
    accepted_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)  # For record keeping
    user_agent = Column(Text, nullable=True)  # Browser/app info
    acceptance_method = Column(String, nullable=False)  # web, app, whatsapp
    
    # Status
    is_current = Column(Boolean, default=True)  # If this is current acceptance
    revoked_at = Column(DateTime, nullable=True)  # If user revoked acceptance
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="terms_acceptances")
    terms = relationship("PlatformTerms", back_populates="user_acceptances")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=True)
    service = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, notifying_fixers, assigned, in_progress, completed, cancelled, escalated, timeout
    estimated_price = Column(Float, nullable=True)
    final_price = Column(Float, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    
    # Enhanced Workflow Fields
    terms_accepted = Column(Boolean, default=False, nullable=False)  # Mandatory terms acceptance
    terms_accepted_at = Column(DateTime, nullable=True)  # When terms were accepted
    workflow_stage = Column(String, default="terms_pending")  # terms_pending, eligible_check, notifying, waiting_assignment, assigned, tracking, completed
    notified_fixers = Column(Text, nullable=True)  # JSON array of fixer IDs notified
    eligible_fixers = Column(Text, nullable=True)  # JSON array of eligible fixer IDs
    assignment_timeout = Column(DateTime, nullable=True)  # When assignment expires
    attendance_timeout = Column(DateTime, nullable=True)  # When fixer must confirm attendance
    is_emergency_escalated = Column(Boolean, default=False)  # If job was escalated due to timeout
    priority_level = Column(String, default="normal")  # normal, urgent, emergency
    
    # Live Tracking Fields
    fixer_location_lat = Column(Float, nullable=True)  # Current fixer GPS latitude
    fixer_location_lng = Column(Float, nullable=True)  # Current fixer GPS longitude
    fixer_location_updated = Column(DateTime, nullable=True)  # Last location update
    estimated_arrival = Column(DateTime, nullable=True)  # Estimated arrival time
    tracking_active = Column(Boolean, default=False)  # If live tracking is active
    
    # WhatsApp integration fields
    client_contact_number = Column(String, nullable=True)  # Contact number provided by client
    area = Column(String, nullable=True)  # Area derived from location
    latitude = Column(Float, nullable=True)  # GPS coordinates
    longitude = Column(Float, nullable=True)
    payment_status = Column(String, default="pending")  # pending, paid, failed
    rating = Column(Integer, nullable=True)  # 1-5 rating from client
    rating_comment = Column(Text, nullable=True)  # Client's review comment
    sentiment = Column(String, nullable=True)  # AI-analyzed sentiment of review
    
    # Assignment tracking
    assignment_attempts = Column(Integer, default=0)  # Number of assignment attempts
    last_assignment_attempt = Column(DateTime, nullable=True)  # Last assignment attempt time
    auto_reassignment_count = Column(Integer, default=0)  # How many times auto-reassigned
    
    # Enhanced timeout and penalty system
    fixer_timeout_count = Column(Integer, default=0)  # How many fixers timed out
    emergency_escalation_reason = Column(String, nullable=True)  # Why escalated (timeout, no_fixers, emergency)
    attendance_deadline = Column(DateTime, nullable=True)  # 180-minute attendance deadline
    fixer_freeze_applied = Column(Boolean, default=False)  # If fixer was frozen due to timeout
    
    # Cancellation tracking
    client_cancelled = Column(Boolean, default=False)  # If client cancelled
    client_cancellation_reason = Column(Text, nullable=True)  # Client's reason for cancellation
    fixer_cancelled = Column(Boolean, default=False)  # If fixer cancelled
    fixer_cancellation_reason = Column(Text, nullable=True)  # Fixer's reason for cancellation
    cancellation_penalties_applied = Column(Text, nullable=True)  # JSON of penalties applied
    
    # Payment and fee tracking
    platform_fee_due = Column(Float, default=20.0)  # R20 platform fee
    platform_fee_status = Column(String, default="pending")  # pending, paid, overdue, waived
    platform_fee_deadline = Column(DateTime, nullable=True)  # 48-hour payment deadline
    platform_fee_paid_at = Column(DateTime, nullable=True)  # When fee was paid
    
    # AI fraud monitoring
    fraud_risk_score = Column(Float, default=0.0)  # AI-calculated fraud risk (0-100)
    fraud_indicators = Column(Text, nullable=True)  # JSON array of detected indicators
    ai_monitoring_active = Column(Boolean, default=True)  # If AI is monitoring this job
    admin_attention_flagged = Column(Boolean, default=False)  # If flagged for admin attention
    
    # Photo Verification Fields - Phase 2 Enhancement
    before_photos = Column(Text, nullable=True)  # JSON array of base64 before photos
    after_photos = Column(Text, nullable=True)   # JSON array of base64 after photos
    photo_verification_status = Column(String, default="not_required")  # not_required, pending, verified, rejected
    photo_verified_at = Column(DateTime, nullable=True)  # When photos were verified
    photo_verified_by = Column(String, nullable=True)   # Admin ID who verified
    photo_rejection_reason = Column(Text, nullable=True)  # Reason for photo rejection
    requires_photo_verification = Column(Boolean, default=False)  # If this job type requires photos
    
    # ETA and Live Tracking Fields - Phase 2 Enhancement  
    fixer_departure_time = Column(DateTime, nullable=True)  # When fixer left for job
    fixer_arrival_time = Column(DateTime, nullable=True)    # When fixer arrived at job
    job_start_time = Column(DateTime, nullable=True)        # When work actually started
    job_completion_time = Column(DateTime, nullable=True)   # When work was completed
    estimated_duration = Column(Integer, nullable=True)     # Estimated job duration in minutes
    actual_duration = Column(Integer, nullable=True)        # Actual job duration in minutes
    live_tracking_enabled = Column(Boolean, default=False)  # If client enabled live tracking
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    fixer = relationship("Fixer", back_populates="jobs")
    reviews = relationship("Review", back_populates="job")
    emergency_alerts = relationship("EmergencyAlert", back_populates="job")
    assignment_history = relationship("JobAssignmentHistory", back_populates="job")
    notifications = relationship("JobNotification", back_populates="job")
    disputes = relationship("JobDispute", back_populates="job")  # New relationship

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

# ======= PHASE 2 ENHANCEMENTS: TRUST & RELIABILITY MODELS =======

class JobDispute(Base):
    """
    Model for handling job disputes and escalations.
    Supports formal dispute resolution with admin mediation.
    """
    __tablename__ = "job_disputes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    reporter_id = Column(String, ForeignKey("users.id"), nullable=False)  # Who reported the dispute
    reporter_type = Column(String, nullable=False)  # 'client' or 'fixer'
    
    # Dispute Details
    dispute_type = Column(String, nullable=False)  # 'quality', 'no_show', 'payment', 'behavior', 'other'
    description = Column(Text, nullable=False)  # Detailed description of the issue
    priority_level = Column(String, default='normal')  # 'low', 'normal', 'high', 'urgent'
    
    # Evidence
    evidence_photos = Column(Text, nullable=True)  # JSON array of base64 photos
    evidence_description = Column(Text, nullable=True)  # Description of evidence
    chat_logs = Column(Text, nullable=True)  # Relevant chat/communication logs
    
    # Status and Resolution
    status = Column(String, default='open')  # 'open', 'investigating', 'resolved', 'escalated', 'closed'
    resolution = Column(Text, nullable=True)  # Admin's resolution decision
    resolution_action = Column(String, nullable=True)  # 'refund', 'redo_job', 'warning', 'suspension', 'no_action'
    
    # Admin Management
    assigned_admin_id = Column(String, ForeignKey("users.id"), nullable=True)
    admin_notes = Column(Text, nullable=True)  # Internal admin notes
    reviewed_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Payment Management
    payment_hold = Column(Boolean, default=False)  # If payment is on hold
    payment_released = Column(Boolean, default=False)  # If payment was released
    refund_amount = Column(Float, nullable=True)  # Partial or full refund amount
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="disputes")
    reporter = relationship("User", foreign_keys=[reporter_id])
    assigned_admin = relationship("User", foreign_keys=[assigned_admin_id])
    
    def __repr__(self):
        return f"<JobDispute(id='{self.id}', type='{self.dispute_type}', status='{self.status}')>"

class JobPhotoVerification(Base):
    """
    Model for managing job photo verification process.
    Stores before/after photos and verification status.
    """
    __tablename__ = "job_photo_verifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    
    # Photo Data (stored as base64 strings)
    before_photos = Column(Text, nullable=True)  # JSON array of base64 images
    after_photos = Column(Text, nullable=True)   # JSON array of base64 images
    work_progress_photos = Column(Text, nullable=True)  # JSON array of progress photos
    
    # Verification Process
    verification_status = Column(String, default='pending')  # 'pending', 'approved', 'rejected', 'needs_more'
    verified_by = Column(String, ForeignKey("users.id"), nullable=True)  # Admin who verified
    verified_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Photo Quality Assessment
    photo_quality_score = Column(Float, nullable=True)  # AI-assessed photo quality (0-100)
    has_clear_before_after = Column(Boolean, default=False)  # If before/after comparison is clear
    shows_completed_work = Column(Boolean, default=False)  # If after photos show completed work
    
    # Requirements
    is_required = Column(Boolean, default=False)  # If photos are mandatory for this job
    requirement_reason = Column(String, nullable=True)  # 'high_value', 'dispute_history', 'job_type'
    
    # AI Analysis
    ai_analysis = Column(Text, nullable=True)  # JSON with AI analysis results
    ai_confidence = Column(Float, nullable=True)  # AI confidence in verification (0-100)
    flagged_issues = Column(Text, nullable=True)  # JSON array of potential issues found
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job")
    verifier = relationship("User", foreign_keys=[verified_by])
    
    def __repr__(self):
        return f"<JobPhotoVerification(id='{self.id}', job_id='{self.job_id}', status='{self.verification_status}')>"

class JobTracking(Base):
    """
    Model for real-time job tracking and ETA management.
    Tracks fixer location and provides arrival estimates.
    """
    __tablename__ = "job_tracking"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=False)
    
    # Live Location Data
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    location_updated_at = Column(DateTime, nullable=True)
    location_accuracy = Column(Float, nullable=True)  # GPS accuracy in meters
    
    # Journey Tracking
    departure_time = Column(DateTime, nullable=True)  # When fixer left for job
    estimated_arrival = Column(DateTime, nullable=True)  # Current ETA
    actual_arrival = Column(DateTime, nullable=True)  # When fixer actually arrived
    
    # Status Updates
    tracking_status = Column(String, default='inactive')  # 'inactive', 'en_route', 'arrived', 'completed'
    last_status_update = Column(DateTime, nullable=True)
    client_notified = Column(Boolean, default=False)  # If client was notified of updates
    
    # Route Information  
    estimated_distance = Column(Float, nullable=True)  # Distance to job in km
    estimated_duration = Column(Integer, nullable=True)  # Estimated travel time in minutes
    route_data = Column(Text, nullable=True)  # JSON with route information
    traffic_conditions = Column(String, nullable=True)  # 'light', 'moderate', 'heavy'
    
    # Efficiency Metrics
    arrival_accuracy = Column(Float, nullable=True)  # How accurate was the ETA (minutes difference)
    route_efficiency = Column(Float, nullable=True)  # How efficient was the route taken
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job = relationship("Job")
    fixer = relationship("Fixer")
    
    def __repr__(self):
        return f"<JobTracking(id='{self.id}', job_id='{self.job_id}', status='{self.tracking_status}')>"

class DisputeMessage(Base):
    """
    Model for managing communication within dispute resolution.
    Tracks messages between all parties during dispute resolution.
    """
    __tablename__ = "dispute_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dispute_id = Column(String, ForeignKey("job_disputes.id"), nullable=False)
    sender_id = Column(String, ForeignKey("users.id"), nullable=False)
    sender_type = Column(String, nullable=False)  # 'client', 'fixer', 'admin'
    
    # Message Content
    message = Column(Text, nullable=False)
    message_type = Column(String, default='text')  # 'text', 'photo', 'document', 'status_update'
    attachments = Column(Text, nullable=True)  # JSON array of attachments (base64 or URLs)
    
    # Message Status
    is_internal = Column(Boolean, default=False)  # If this is an internal admin note
    read_by_client = Column(Boolean, default=False)
    read_by_fixer = Column(Boolean, default=False) 
    read_by_admin = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    dispute = relationship("JobDispute")
    sender = relationship("User")
    
    def __repr__(self):
        return f"<DisputeMessage(id='{self.id}', dispute_id='{self.dispute_id}', sender_type='{self.sender_type}')>"

class AdminOverrideLog(Base):
    """Track all admin override actions for audit purposes"""
    __tablename__ = "admin_override_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    admin_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    target_type = Column(String, nullable=False)  # fixer, job, user
    target_id = Column(String, nullable=False)  # ID of affected entity
    
    # Override details
    override_type = Column(String, nullable=False)  # bypass_restrictions, reset_status, adjust_rating, emergency_intervention
    override_reason = Column(Text, nullable=False)  # Admin's reason for override
    previous_values = Column(Text, nullable=True)  # JSON of previous values
    new_values = Column(Text, nullable=True)  # JSON of new values
    
    # Context
    related_job_id = Column(String, ForeignKey("jobs.id"), nullable=True)
    emergency_flag = Column(Boolean, default=False)  # If this was an emergency override
    client_complaint = Column(Boolean, default=False)  # If related to client complaint
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relationships
    admin_user = relationship("User", foreign_keys=[admin_user_id])
    related_job = relationship("Job", foreign_keys=[related_job_id])

class FraudAlertLog(Base):
    """Track AI-detected fraud patterns and admin responses"""
    __tablename__ = "fraud_alert_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=False)
    
    # Alert details
    alert_type = Column(String, nullable=False)  # high_cancellation, low_completion, no_show_pattern, suspicious_behavior
    alert_severity = Column(String, default="medium")  # low, medium, high, critical
    description = Column(Text, nullable=False)
    ai_confidence = Column(Float, default=0.0)  # AI confidence in detection (0-100)
    
    # Pattern data
    pattern_data = Column(Text, nullable=True)  # JSON with detected patterns
    metrics = Column(Text, nullable=True)  # JSON with supporting metrics
    timeframe = Column(String, default="30_days")  # Analysis timeframe
    
    # Status and response
    status = Column(String, default="pending")  # pending, reviewed, dismissed, action_taken
    admin_response = Column(Text, nullable=True)  # Admin notes/response
    action_taken = Column(String, nullable=True)  # warning, suspension, no_action
    reviewed_by = Column(String, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Auto-resolution
    auto_escalated = Column(Boolean, default=False)  # If automatically escalated
    escalation_threshold_met = Column(Boolean, default=False)  # If critical thresholds were met
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fixer = relationship("Fixer")
    reviewer = relationship("User", foreign_keys=[reviewed_by])

# ======= PHASE 4: MOBILE & PWA MODELS =======

class PushSubscription(Base):
    """
    Model for managing push notification subscriptions for PWA functionality.
    Stores device subscription information for real-time notifications.
    """
    __tablename__ = "push_subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Push Subscription Details
    endpoint = Column(String, nullable=False)  # Push service endpoint URL
    keys = Column(Text, nullable=False)  # JSON string containing p256dh and auth keys
    user_agent = Column(String, nullable=True)  # Device/browser info
    
    # Subscription Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)  # Last successful notification
    
    # Notification Preferences
    enable_job_notifications = Column(Boolean, default=True)
    enable_payment_notifications = Column(Boolean, default=True)
    enable_system_notifications = Column(Boolean, default=True)
    enable_marketing_notifications = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="push_subscriptions")
    
    def __repr__(self):
        return f"<PushSubscription(id='{self.id}', user_id='{self.user_id}', active='{self.is_active}')>"

class AppSession(Base):
    """
    Model for tracking PWA app sessions and usage analytics.
    Helps understand user engagement and offline usage patterns.
    """
    __tablename__ = "app_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous sessions
    
    # Session Details
    session_id = Column(String, nullable=False, unique=True)  # Frontend-generated session ID
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Device and Environment
    user_agent = Column(String, nullable=True)
    device_type = Column(String, nullable=True)  # 'mobile', 'tablet', 'desktop'
    platform = Column(String, nullable=True)  # 'android', 'ios', 'windows', etc.
    is_pwa = Column(Boolean, default=False)  # If accessed as installed PWA
    is_offline_capable = Column(Boolean, default=False)  # If service worker is active
    
    # Usage Analytics
    pages_visited = Column(Text, nullable=True)  # JSON array of page routes
    actions_performed = Column(Text, nullable=True)  # JSON array of key actions
    offline_actions_queued = Column(Integer, default=0)  # Number of actions queued offline
    cache_hits = Column(Integer, default=0)  # Number of successful cache responses
    
    # Performance Metrics
    initial_load_time = Column(Float, nullable=True)  # Initial app load time in seconds
    average_page_load_time = Column(Float, nullable=True)  # Average page load time
    network_failures = Column(Integer, default=0)  # Network request failures during session
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="app_sessions")
    
    def __repr__(self):
        return f"<AppSession(id='{self.id}', user_id='{self.user_id}', is_pwa='{self.is_pwa}')>"

class OfflineAction(Base):
    """
    Model for tracking actions performed while offline that need to be synced.
    Ensures data consistency when users work offline.
    """
    __tablename__ = "offline_actions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_id = Column(String, nullable=False)  # Links to AppSession
    
    # Action Details
    action_type = Column(String, nullable=False)  # 'create_job', 'update_profile', 'submit_review', etc.
    action_data = Column(Text, nullable=False)  # JSON data for the action
    priority = Column(String, default='normal')  # 'high', 'normal', 'low'
    
    # Sync Status
    sync_status = Column(String, default='pending')  # 'pending', 'synced', 'failed', 'cancelled'
    sync_attempts = Column(Integer, default=0)
    last_sync_attempt = Column(DateTime, nullable=True)
    sync_error = Column(Text, nullable=True)  # Error message if sync failed
    
    # Timestamps
    created_offline_at = Column(DateTime, nullable=False)  # When action was performed offline
    synced_at = Column(DateTime, nullable=True)  # When successfully synced
    expires_at = Column(DateTime, nullable=True)  # When to give up syncing
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="offline_actions")
    
    def __repr__(self):
        return f"<OfflineAction(id='{self.id}', action_type='{self.action_type}', sync_status='{self.sync_status}')>"

# ======= PHASE 3 ENHANCEMENTS: AUTOMATION & ENGAGEMENT MODELS =======

class FixerReputationTier(Base):
    """
    Model for fixer reputation tiers and gamification system.
    Manages badges, levels, and performance-based incentives.
    """
    __tablename__ = "fixer_reputation_tiers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fixer_id = Column(String, ForeignKey("fixers.id"), nullable=False, unique=True)
    
    # Current Tier Status
    current_tier = Column(String, default='apprentice')  # 'apprentice', 'skilled', 'expert', 'master', 'legend'
    tier_points = Column(Integer, default=0)  # Total points accumulated
    tier_level = Column(Integer, default=1)  # Numeric level within tier
    
    # Performance Metrics
    jobs_completed = Column(Integer, default=0)
    client_satisfaction_avg = Column(Float, default=0.0)
    response_time_avg = Column(Float, default=0.0)  # Average response time in minutes
    completion_rate = Column(Float, default=100.0)  # Percentage of jobs completed
    reliability_score = Column(Float, default=100.0)  # Overall reliability
    
    # Achievements & Badges
    badges_earned = Column(Text, nullable=True)  # JSON array of badge IDs
    achievements = Column(Text, nullable=True)  # JSON array of achievement data
    milestones_reached = Column(Text, nullable=True)  # JSON array of milestone data
    
    # Tier Benefits
    priority_access = Column(Boolean, default=False)  # Early access to high-value jobs
    lower_platform_fees = Column(Float, default=0.0)  # Percentage fee reduction
    verified_status = Column(Boolean, default=False)  # Verified professional status
    featured_listing = Column(Boolean, default=False)  # Featured in search results
    
    # Gamification Elements
    streak_count = Column(Integer, default=0)  # Current success streak
    best_streak = Column(Integer, default=0)  # Best streak achieved
    monthly_goals = Column(Text, nullable=True)  # JSON with monthly targets
    rewards_claimed = Column(Text, nullable=True)  # JSON array of claimed rewards
    
    # Progress Tracking
    last_tier_promotion = Column(DateTime, nullable=True)
    next_tier_requirements = Column(Text, nullable=True)  # JSON with requirements
    progress_to_next_tier = Column(Float, default=0.0)  # Percentage progress
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fixer = relationship("Fixer")
    
    def __repr__(self):
        return f"<FixerReputationTier(fixer_id='{self.fixer_id}', tier='{self.current_tier}', level={self.tier_level})>"

class BadgeDefinition(Base):
    """
    Model for defining available badges and achievements.
    Centralizes badge criteria and rewards.
    """
    __tablename__ = "badge_definitions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Badge Information
    badge_code = Column(String, unique=True, nullable=False)  # Unique identifier
    name = Column(String, nullable=False)  # Display name
    description = Column(Text, nullable=False)  # Badge description
    icon = Column(String, nullable=True)  # Emoji or icon code
    category = Column(String, nullable=False)  # 'performance', 'milestone', 'special', 'seasonal'
    
    # Requirements
    criteria = Column(Text, nullable=False)  # JSON with badge criteria
    difficulty = Column(String, default='easy')  # 'easy', 'medium', 'hard', 'legendary'
    
    # Rewards
    points_reward = Column(Integer, default=0)  # Points awarded
    tier_boost = Column(Float, default=0.0)  # Tier progress boost
    special_benefits = Column(Text, nullable=True)  # JSON with special benefits
    
    # Status
    is_active = Column(Boolean, default=True)
    is_visible = Column(Boolean, default=True)  # If visible to fixers
    launch_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=True)  # For seasonal badges
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<BadgeDefinition(code='{self.badge_code}', name='{self.name}', category='{self.category}')>"

class AIConversation(Base):
    """
    Model for tracking AI chat assistant conversations.
    Supports multilingual conversations and context tracking.
    """
    __tablename__ = "ai_conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous chats
    session_id = Column(String, nullable=False)  # Session identifier
    
    # Conversation Details
    language = Column(String, default='english')  # Conversation language
    user_type = Column(String, nullable=False)  # 'client', 'fixer', 'anonymous'
    conversation_context = Column(Text, nullable=True)  # JSON with conversation context
    
    # Message Content
    messages = Column(Text, nullable=True)  # JSON array of conversation messages
    total_messages = Column(Integer, default=0)
    user_messages = Column(Integer, default=0)
    ai_responses = Column(Integer, default=0)
    
    # Conversation Status
    status = Column(String, default='active')  # 'active', 'completed', 'escalated', 'abandoned'
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 rating from user
    resolved_query = Column(Boolean, default=False)  # If user's query was resolved
    escalated_to_human = Column(Boolean, default=False)  # If escalated to human support
    
    # AI Performance
    avg_response_confidence = Column(Float, default=0.0)  # Average AI confidence
    topics_discussed = Column(Text, nullable=True)  # JSON array of topics
    actions_performed = Column(Text, nullable=True)  # JSON array of actions taken
    
    # Session Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<AIConversation(id='{self.id}', user_type='{self.user_type}', language='{self.language}', status='{self.status}')>"

class NotificationQueue(Base):
    """
    Model for managing automated notifications and updates.
    Handles SMS, WhatsApp, and in-app notifications.
    """
    __tablename__ = "notification_queue"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    recipient_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Notification Details
    notification_type = Column(String, nullable=False)  # 'sms', 'whatsapp', 'in_app', 'email'
    category = Column(String, nullable=False)  # 'job_update', 'eta_update', 'promotion', 'achievement'
    priority = Column(String, default='normal')  # 'low', 'normal', 'high', 'urgent'
    
    # Content
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    action_url = Column(String, nullable=True)  # Deep link or URL
    action_label = Column(String, nullable=True)  # Button text
    
    # Delivery
    scheduled_for = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    delivery_status = Column(String, default='pending')  # 'pending', 'sent', 'delivered', 'failed', 'cancelled'
    delivery_attempts = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Tracking
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    
    # Context
    related_job_id = Column(String, ForeignKey("jobs.id"), nullable=True)
    context_data = Column(Text, nullable=True)  # JSON with additional data
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recipient = relationship("User")
    related_job = relationship("Job")
    
    def __repr__(self):
        return f"<NotificationQueue(id='{self.id}', type='{self.notification_type}', status='{self.delivery_status}')>"