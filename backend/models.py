from sqlalchemy import Column, String, DateTime, Integer, Text, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    role = Column(String, default="client")  # client, fixer, admin, super_admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = relationship("Job", back_populates="user")
    reviews = relationship("Review", back_populates="user")

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