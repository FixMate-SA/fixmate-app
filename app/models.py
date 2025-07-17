# app/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_login import UserMixin
from decimal import Decimal # <-- Add this import

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """Represents a client who interacts with the bot."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(30), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    conversation_state = db.Column(db.String(50), nullable=True)
    service_request_cache = db.Column(db.String(255), nullable=True)
    jobs = db.relationship('Job', backref='client', lazy=True)

    def __repr__(self):
        return f'<User {self.phone_number}>'

    # === FIX: ADDED CASCADE DELETE BEHAVIOR HERE ===
    jobs = db.relationship(
        'Job',
        backref='client',
        lazy=True,
        cascade="all, delete-orphan",  # Automatically delete a user's jobs
        passive_deletes=True           # Ensures the database handles the deletion
    )

class Fixer(db.Model, UserMixin):
    """Represents a service provider (fixer)."""
    __tablename__ = 'fixers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(30), unique=True, nullable=False)
    skills = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    current_latitude = db.Column(db.Float, nullable=True)
    current_longitude = db.Column(db.Float, nullable=True)
    vetting_status = db.Column(db.String(50), nullable=False, default='pending_review', server_default='pending_review')
    id_document_url = db.Column(db.String(255), nullable=True)
    vetting_notes = db.Column(db.Text, nullable=True)
    jobs = db.relationship('Job', backref='assigned_fixer', lazy=True)

    def __repr__(self):
        return f'<Fixer {self.full_name}>'

    # === NEWLY ADDED COLUMNS (Corrected) ===
    balance = db.Column(db.Numeric(10, 2), nullable=False, server_default='0.00')
    bank_account_holder = db.Column(db.String(150), nullable=True)
    bank_account_number = db.Column(db.String(50), nullable=True)
    bank_name = db.Column(db.String(100), nullable=True)

    # --- NEW: Timestamp for fairness algorithm ---
    last_assigned_at = db.Column(db.DateTime, nullable=True)

    jobs = db.relationship('Job', backref='assigned_fixer', lazy=True)

class Job(db.Model):
    """Represents a service request (a job)."""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='awaiting_payment', nullable=False)
    
    # MODIFIED: Removed the default='Pretoria' value.
    area = db.Column(db.String(100), nullable=True)
    
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    client_contact_number = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    client_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    fixer_id = db.Column(db.Integer, db.ForeignKey('fixers.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    rating_comment = db.Column(db.Text, nullable=True)
    sentiment = db.Column(db.String(50), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=True)
    payment_status = db.Column(db.String(50), default='unpaid', nullable=False)
    fixer_fee_status = db.Column(db.String(50), default='unpaid', nullable=False)

    def __repr__(self):
        return f'<Job {self.id} - {self.description[:20]}>'

class DataInsight(db.Model):
    """Stores the generated insights from our data analysis."""
    __tablename__ = 'data_insights'
    id = db.Column(db.Integer, primary_key=True)
    insight_text = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<DataInsight {self.id}>'