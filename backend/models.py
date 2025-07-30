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
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    fixer = relationship("Fixer", back_populates="jobs")
    reviews = relationship("Review", back_populates="job")
    emergency_alerts = relationship("EmergencyAlert", back_populates="job")
    assignment_history = relationship("JobAssignmentHistory", back_populates="job")
    notifications = relationship("JobNotification", back_populates="job")

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