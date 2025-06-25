# app/models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """Represents a client who interacts with the bot."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(30), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    
    conversation_state = db.Column(db.String(50), nullable=True)
    service_request_cache = db.Column(db.String(255), nullable=True)
    latitude_cache = db.Column(db.Float, nullable=True)
    longitude_cache = db.Column(db.Float, nullable=True)
    
    jobs = db.relationship('Job', backref='client', lazy=True)

    def __repr__(self):
        return f'<User {self.phone_number}>'

# --- UPDATED: Fixer model now includes UserMixin ---
class Fixer(db.Model, UserMixin):
    """Represents a service provider (fixer)."""
    __tablename__ = 'fixers'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone_number = db.Column(db.String(30), unique=True, nullable=False)
    skills = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    jobs = db.relationship('Job', backref='assigned_fixer', lazy=True)

    def __repr__(self):
        return f'<Fixer {self.full_name}>'

class Job(db.Model):
    """Represents a service request (a job)."""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='pending', nullable=False)
    
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    client_contact_number = db.Column(db.String(30), nullable=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fixer_id = db.Column(db.Integer, db.ForeignKey('fixers.id'), nullable=True)

    def __repr__(self):
        return f'<Job {self.id} - {self.description[:20]}>'
