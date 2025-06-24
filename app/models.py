# app/models.py
from flask_sqlalchemy import SQLAlchemy

# Create a database instance. We will initialize it in our main app file.
db = SQLAlchemy()

class User(db.Model):
    """
    Represents a user (client) who interacts with the bot.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(30), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    
    # State management fields
    conversation_state = db.Column(db.String(50), nullable=True)
    service_request_cache = db.Column(db.String(255), nullable=True)
    latitude_cache = db.Column(db.Float, nullable=True)
    longitude_cache = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<User {self.phone_number}>'

# We will add Job and Fixer models here in the future.
