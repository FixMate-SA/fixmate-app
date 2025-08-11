from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum, JSON, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    client = "client"
    fixer = "fixer"  
    admin = "admin"

class JobStatus(enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class JobPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class EmergencyStatus(enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"
    HANDLED = "handled"

# Existing Models
class User(Base):
    __tablename__ = "users"
    
    # Only include columns that actually exist in the database
    id = Column(String, primary_key=True)
    phone = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    id_number = Column(String)
    town = Column(String)
    email = Column(String, unique=True, index=True)
    address = Column(Text)
    password_hash = Column(String)
    is_password_set = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.client)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    money_spent = Column(Float, default=0.0)
    conversation_state = Column(String)
    service_request_cache = Column(Text)
    whatsapp_active = Column(Boolean, default=False)
    last_whatsapp_message = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    password_reset_code = Column(Text)
    password_reset_expires = Column(DateTime)
    
    # Relationships
    jobs_created = relationship("Job", foreign_keys="Job.client_id", back_populates="client")
    jobs_assigned = relationship("Job", foreign_keys="Job.fixer_id", back_populates="fixer")
    emergency_alerts = relationship("EmergencyAlert", back_populates="user")
    
    # Properties for backward compatibility
    @property
    def name(self):
        """Computed name property for backward compatibility"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return "Unknown User"
    
    @property
    def full_name(self):
        """Full name property"""
        return self.name
    
    @property 
    def display_name(self):
        """Display name property"""
        return self.first_name or "User"
        
    # Default properties for fields that don't exist in DB but are expected by services
    @property
    def profile_picture(self):
        return None
        
    @property
    def bio(self):
        return None
        
    @property
    def location(self):
        return None
        
    @property
    def is_verified(self):
        return False
        
    @property
    def skills(self):
        return []
        
    @property
    def experience_years(self):
        return 0
        
    @property
    def hourly_rate(self):
        return 0.0
        
    @property
    def availability_status(self):
        return "available"
        
    @property
    def average_rating(self):
        return 0.0
        
    @property
    def total_ratings(self):
        return 0
        
    @property
    def total_jobs_completed(self):
        return 0

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    
    # Location information
    location = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Pricing
    estimated_price = Column(Float)
    agreed_price = Column(Float)
    
    # Status and priority
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    priority = Column(Enum(JobPriority), default=JobPriority.MEDIUM)
    urgency = Column(String)  # low, medium, high, urgent
    
    # Dates
    preferred_date = Column(DateTime)
    preferred_time = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    client_id = Column(String, ForeignKey("users.id"), nullable=False)
    fixer_id = Column(String, ForeignKey("users.id"))
    
    client = relationship("User", foreign_keys=[client_id], back_populates="jobs_created")
    fixer = relationship("User", foreign_keys=[fixer_id], back_populates="jobs_assigned")
    
    # Job images (stored as JSON array of URLs)
    images = Column(JSON)
    
    # Voice recording for job description
    voice_description_url = Column(String)
    voice_description_transcription = Column(Text)
    
    # Rating and feedback
    client_rating = Column(Integer)  # 1-5 stars from client
    fixer_rating = Column(Integer)   # 1-5 stars from fixer
    client_feedback = Column(Text)
    fixer_feedback = Column(Text)

# New Emergency Alert System
class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"
    __table_args__ = {'extend_existing': True}
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=True)  # Optional job context
    
    # Alert details
    alert_type = Column(String, default="emergency")  # emergency, medical, fire, security
    priority = Column(String, default="high")  # low, medium, high, critical
    status = Column(Enum(EmergencyStatus), default=EmergencyStatus.ACTIVE)
    
    # Location information
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(Text)
    
    # Emergency details
    description = Column(Text)
    voice_transcription = Column(Text)  # Transcribed voice message
    voice_file_path = Column(String)    # Path to voice recording file
    recording_duration = Column(Integer, default=0)  # Duration in seconds
    
    # Response tracking
    police_notified = Column(Boolean, default=False)
    police_reference = Column(String)  # Police case reference number
    emergency_contacts_notified = Column(Boolean, default=False)
    dispatch_notified = Column(Boolean, default=False)
    admin_notified = Column(Boolean, default=False)
    
    # Resolution
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emergency_alerts")

# Existing Models (keeping for compatibility)
class WhatsAppStatistics(Base):
    __tablename__ = "whatsapp_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    total_messages = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    successful_jobs = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Announcement(Base):
    __tablename__ = "announcements"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    target_audience = Column(String, default="all")  # all, clients, fixers
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=False)  # admin user id
    chat_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AnnouncementChat(Base):
    __tablename__ = "announcement_chats"  
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    announcement_id = Column(Integer, ForeignKey("announcements.id"))
    user_id = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    user_role = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)