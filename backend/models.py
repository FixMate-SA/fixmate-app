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
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    password_hash = Column(String, nullable=True)  # New: Password hash for security
    is_password_set = Column(Boolean, default=False)  # Track if password is set
    role = Column(String, default="client")  # client, fixer, admin, super_admin
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)  # Track last login
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = relationship("Job", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    emergency_alerts = relationship("EmergencyAlert", back_populates="user")
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
        self.is_password_set = True
    
    def check_password(self, password):
        """Check if password matches hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class Fixer(Base):
    __tablename__ = "fixers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    services = Column(Text, nullable=False)  # JSON string of services
    location = Column(String, nullable=False)
    rating = Column(Float, default=0.0)
    total_jobs = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    payment_status = Column(String, default="current")  # current, overdue, blocked
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    fixer = relationship("Fixer", back_populates="jobs")
    reviews = relationship("Review", back_populates="job")

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