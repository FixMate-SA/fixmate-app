# app/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_login import UserMixin
from decimal import Decimal # <-- Add this import
import secrets # For generating secure tokens
import hashlib

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """Represents a client who interacts with the bot."""
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True)  # Updated to match FastAPI UUID
    phone = db.Column(db.String(30), unique=True, nullable=False)  # Changed from phone_number
    first_name = db.Column(db.String(120), nullable=False)  # Added first_name
    last_name = db.Column(db.String(120), nullable=False)   # Added last_name
    id_number = db.Column(db.String(20), unique=True, nullable=False)  # Added id_number
    town = db.Column(db.String(120), nullable=False)  # Added town
    email = db.Column(db.String(120), nullable=True)  # Added email
    address = db.Column(db.Text, nullable=True)  # Added address
    password_hash = db.Column(db.String(128), nullable=True)  # Added password_hash
    is_password_set = db.Column(db.Boolean, default=False)  # Added is_password_set
    role = db.Column(db.String(20), default="client")  # Changed from is_admin
    is_active = db.Column(db.Boolean, default=True)  # Added is_active
    last_login = db.Column(db.DateTime, nullable=True)  # Added last_login
    conversation_state = db.Column(db.String(50), nullable=True)  # Keep existing
    service_request_cache = db.Column(db.Text, nullable=True)  # Keep existing, changed to Text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Added created_at
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added updated_at
    
    # Legacy fields for backward compatibility (keep but don't use)
    api_key = db.Column(db.String(64), unique=True, nullable=True, index=True)
    otp_hash = db.Column(db.String(128), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    
    # Relationships - using the cascade delete behavior
    user_jobs = db.relationship(
        'Job',
        foreign_keys='Job.user_id',
        backref='user',
        lazy=True,
        cascade="all, delete-orphan",  # Automatically delete a user's jobs
        passive_deletes=True           # Ensures the database handles the deletion
    )

    def __repr__(self):
        return f'<User {self.phone}>'
    
    @property
    def full_name(self):
        """Get full name for display - for backward compatibility"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self):
        """Get display name (first name for welcome messages)"""
        return self.first_name
    
    @property
    def is_admin(self):
        """Backward compatibility property"""
        return self.role == "admin"
    
    @property
    def phone_number(self):
        """Backward compatibility property"""
        return self.phone
    
    @property
    def jobs(self):
        """Backward compatibility property"""
        return self.user_jobs
    
    def generate_api_key(self):
        self.api_key = secrets.token_hex(32)

    def set_otp(self, otp):
        self.otp_hash = hashlib.sha256(otp.encode('utf-8')).hexdigest()
        self.otp_expiry = datetime.now(timezone.utc) + timezone.timedelta(minutes=10)

    def verify_otp(self, otp):
        if self.otp_expiry and self.otp_expiry > datetime.now(timezone.utc):
            return self.otp_hash == hashlib.sha256(otp.encode('utf-8')).hexdigest()
        return False

class Fixer(db.Model, UserMixin):
    """Represents a service provider (fixer)."""
    __tablename__ = 'fixers'
    id = db.Column(db.String(36), primary_key=True)  # Updated to match FastAPI UUID
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)  # Link to user account
    application_id = db.Column(db.String(36), nullable=True)  # Link to approved application
    
    phone = db.Column(db.String(30), unique=True, nullable=False)  # Changed from phone_number
    name = db.Column(db.String(120), nullable=False)  # Changed from full_name
    email = db.Column(db.String(120), nullable=True)  # Added email
    services = db.Column(db.Text, nullable=False)  # JSON string of services
    location = db.Column(db.String(120), nullable=False)  # Added location
    rating = db.Column(db.Float, default=0.0)  # Added rating
    total_jobs = db.Column(db.Integer, default=0)  # Added total_jobs
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)  # Approval status from vetting process
    approval_date = db.Column(db.DateTime, nullable=True)  # When fixer was approved
    payment_status = db.Column(db.String(50), default="current")  # current, overdue, blocked
    
    # WhatsApp integration fields
    vetting_status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    skills = db.Column(db.Text, nullable=True)  # Skills for job matching
    current_latitude = db.Column(db.Float, nullable=True)  # Current GPS location
    current_longitude = db.Column(db.Float, nullable=True)
    last_assigned_at = db.Column(db.DateTime, nullable=True)  # For fair job distribution
    balance = db.Column(db.Numeric(10, 2), default=0.0)  # For fee management
    
    # Legacy fields for backward compatibility
    id_document_url = db.Column(db.String(255), nullable=True)
    vetting_notes = db.Column(db.Text, nullable=True)
    bank_account_holder = db.Column(db.String(150), nullable=True)
    bank_account_number = db.Column(db.String(50), nullable=True)
    bank_name = db.Column(db.String(100), nullable=True)
    api_key = db.Column(db.String(64), unique=True, nullable=True, index=True)
    otp_hash = db.Column(db.String(128), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fixer_jobs = db.relationship('Job', backref='fixer', lazy=True)

    def __repr__(self):
        return f'<Fixer {self.name}>'
    
    @property
    def full_name(self):
        """Backward compatibility property"""
        return self.name
    
    @property
    def phone_number(self):
        """Backward compatibility property"""
        return self.phone
    
    def generate_api_key(self):
        self.api_key = secrets.token_hex(32)

    def set_otp(self, otp):
        self.otp_hash = hashlib.sha256(otp.encode('utf-8')).hexdigest()
        self.otp_expiry = datetime.now(timezone.utc) + timezone.timedelta(minutes=10)

    def verify_otp(self, otp):
        if self.otp_expiry and self.otp_expiry > datetime.now(timezone.utc):
            return self.otp_hash == hashlib.sha256(otp.encode('utf-8')).hexdigest()
        return False

class Job(db.Model):
    """Represents a service request (a job)."""
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(36), primary_key=True)  # Updated to match FastAPI UUID
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)  # Updated FK
    fixer_id = db.Column(db.String(36), db.ForeignKey('fixers.id'), nullable=True)  # Updated FK
    service = db.Column(db.String(120), nullable=False)  # Added service field
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(120), nullable=False)  # Added location field
    status = db.Column(db.String(50), default='pending')  # pending, assigned, in_progress, completed, cancelled
    estimated_price = db.Column(db.Float, nullable=True)  # Added estimated_price
    final_price = db.Column(db.Float, nullable=True)  # Added final_price
    scheduled_at = db.Column(db.DateTime, nullable=True)  # Added scheduled_at
    
    # WhatsApp integration fields
    client_contact_number = db.Column(db.String(30), nullable=True)  # Contact number provided by client
    area = db.Column(db.String(100), nullable=True)  # Area derived from location
    latitude = db.Column(db.Float, nullable=True)  # GPS coordinates
    longitude = db.Column(db.Float, nullable=True)
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, failed
    rating = db.Column(db.Integer, nullable=True)  # 1-5 rating from client
    rating_comment = db.Column(db.Text, nullable=True)  # Client's review comment
    sentiment = db.Column(db.String(50), nullable=True)  # AI-analyzed sentiment of review
    
    # Legacy fields for backward compatibility
    amount = db.Column(db.Numeric(10, 2), nullable=True)  # Same as final_price
    fixer_fee_status = db.Column(db.String(50), default='unpaid')  # Fee status for fixer
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='user_jobs')
    assigned_fixer = db.relationship('Fixer', foreign_keys=[fixer_id], backref='fixer_jobs')

    def __repr__(self):
        return f'<Job {self.id}: {self.description[:50]}>'
    
    @property
    def client_id(self):
        """Backward compatibility property"""
        return self.user_id
    
    @property
    def client(self):
        """Backward compatibility property"""
        return self.user

class DataInsight(db.Model):
    """Stores the generated insights from our data analysis."""
    __tablename__ = 'data_insights'
    id = db.Column(db.String(36), primary_key=True)  # Updated to match FastAPI UUID
    insight_text = db.Column(db.Text, nullable=False)
    insight_type = db.Column(db.String(50), default='business')  # business, trend, market
    generated_by = db.Column(db.String(50), default='ai')  # ai, admin, system
    is_active = db.Column(db.Boolean, default=True)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)  # For backward compatibility
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<DataInsight {self.id}>'