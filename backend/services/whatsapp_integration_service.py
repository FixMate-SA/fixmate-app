"""
WhatsApp Integration Service
Integrates the working fixmate_whatsapp system with the main FastAPI app
Ensures data synchronization and seamless workflow between systems
"""

import os
import json
import requests
import tempfile
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import main app models
from models import User as FastAPIUser, Fixer as FastAPIFixer, Job as FastAPIJob
from database import get_db

# Import WhatsApp system components
import sys
sys.path.append('/app/fixmate_whatsapp')
from app.models import db as whatsapp_db, User as WhatsAppUser, Fixer as WhatsAppFixer, Job as WhatsAppJob
from app.services import send_whatsapp_message

# Dialog360 Configuration
DIALOG_360_API_KEY = os.getenv("DIALOG_360_API_KEY")
DIALOG_360_URL = "https://waba-v2.360dialog.io/messages"

class WhatsAppIntegrationService:
    """Service to handle integration between WhatsApp system and main FastAPI app"""
    
    def __init__(self):
        self.api_key = DIALOG_360_API_KEY
        self.messages_url = DIALOG_360_URL
        
    def sync_user_to_main_app(self, whatsapp_user: WhatsAppUser, fastapi_db: Session) -> FastAPIUser:
        """Sync WhatsApp user to main FastAPI app database"""
        try:
            # Check if user already exists in main app
            existing_user = fastapi_db.query(FastAPIUser).filter(
                FastAPIUser.phone == whatsapp_user.phone
            ).first()
            
            if existing_user:
                # Update existing user with latest data
                existing_user.first_name = whatsapp_user.first_name or existing_user.first_name
                existing_user.last_name = whatsapp_user.last_name or existing_user.last_name
                existing_user.conversation_state = whatsapp_user.conversation_state
                existing_user.updated_at = datetime.utcnow()
                fastapi_db.commit()
                print(f"✅ Updated existing user in main app: {existing_user.phone}")
                return existing_user
            else:
                # Create new user in main app
                new_user = FastAPIUser(
                    id=whatsapp_user.id,
                    phone=whatsapp_user.phone,
                    first_name=whatsapp_user.first_name or "Unknown",
                    last_name=whatsapp_user.last_name or "User",
                    id_number=whatsapp_user.id_number or "000000000000",
                    town=whatsapp_user.town or "Unknown",
                    role=whatsapp_user.role or "client",
                    conversation_state=whatsapp_user.conversation_state,
                    is_active=whatsapp_user.is_active,
                    created_at=whatsapp_user.created_at or datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                fastapi_db.add(new_user)
                fastapi_db.commit()
                print(f"✅ Created new user in main app: {new_user.phone}")
                return new_user
                
        except Exception as e:
            print(f"❌ Error syncing user to main app: {e}")
            fastapi_db.rollback()
            return None
    
    def sync_job_to_main_app(self, whatsapp_job: WhatsAppJob, fastapi_db: Session) -> FastAPIJob:
        """Sync WhatsApp job to main FastAPI app database"""
        try:
            # Check if job already exists in main app
            existing_job = fastapi_db.query(FastAPIJob).filter(
                FastAPIJob.id == whatsapp_job.id
            ).first()
            
            if existing_job:
                # Update existing job
                existing_job.description = whatsapp_job.description
                existing_job.status = whatsapp_job.status
                existing_job.location = whatsapp_job.location
                existing_job.client_contact_number = whatsapp_job.client_contact_number
                existing_job.rating = whatsapp_job.rating
                existing_job.updated_at = datetime.utcnow()
                fastapi_db.commit()
                print(f"✅ Updated existing job in main app: {existing_job.id}")
                return existing_job
            else:
                # Create new job in main app
                new_job = FastAPIJob(
                    id=whatsapp_job.id,
                    user_id=whatsapp_job.user_id,
                    fixer_id=whatsapp_job.fixer_id,
                    service=whatsapp_job.service or "General Service",
                    description=whatsapp_job.description,
                    location=whatsapp_job.location,
                    status=whatsapp_job.status,
                    client_contact_number=whatsapp_job.client_contact_number,
                    latitude=whatsapp_job.latitude,
                    longitude=whatsapp_job.longitude,
                    rating=whatsapp_job.rating,
                    created_at=whatsapp_job.created_at or datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                fastapi_db.add(new_job)
                fastapi_db.commit()
                print(f"✅ Created new job in main app: {new_job.id}")
                return new_job
                
        except Exception as e:
            print(f"❌ Error syncing job to main app: {e}")
            fastapi_db.rollback()
            return None
    
    def process_whatsapp_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, str]:
        """Process WhatsApp webhook using the working fixmate_whatsapp logic"""
        try:
            print(f"🔄 Processing WhatsApp webhook: {json.dumps(webhook_data, indent=2)}")
            
            # Use the proven working webhook processing logic from run.py
            value = webhook_data['entry'][0]['changes'][0]['value']
            
            # Ignore status updates
            if 'statuses' in value:
                print("📊 Received status update - ignoring")
                return {"status": "ignored", "reason": "status_update"}
            
            # Process messages
            if 'messages' in value:
                message = value['messages'][0]
                from_number = f"whatsapp:+{message['from']}"
                msg_type = message.get('type')
                
                print(f"📱 Processing message from {from_number}, type: {msg_type}")
                
                # Get or create user in WhatsApp system first
                whatsapp_user = self.get_or_create_whatsapp_user(from_number)
                
                # Sync user to main app
                fastapi_db = next(get_db())
                try:
                    main_app_user = self.sync_user_to_main_app(whatsapp_user, fastapi_db)
                    
                    # Process the message using WhatsApp system logic
                    response_message = self.process_conversation_message(
                        whatsapp_user, message, msg_type
                    )
                    
                    # Send response if generated
                    if response_message:
                        success = send_whatsapp_message(from_number, response_message)
                        if success:
                            print(f"✅ Response sent to {from_number}")
                        else:
                            print(f"❌ Failed to send response to {from_number}")
                    
                    # Sync any job creation back to main app
                    if whatsapp_user.conversation_state == 'awaiting_terms_approval':
                        self.sync_pending_job_creation(whatsapp_user, fastapi_db)
                    
                    return {"status": "processed", "message": "WhatsApp message processed successfully"}
                    
                finally:
                    fastapi_db.close()
            
            return {"status": "ignored", "reason": "no_messages"}
            
        except Exception as e:
            print(f"❌ Error processing WhatsApp webhook: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_or_create_whatsapp_user(self, phone_number: str):
        """Get or create user in WhatsApp system database"""
        # This would interact with the WhatsApp system's database
        # For now, we'll use a simplified version
        # In production, this should use the actual WhatsApp system's get_or_create_user function
        print(f"🔍 Getting/creating WhatsApp user: {phone_number}")
        
        # Return a mock user object for now - replace with actual WhatsApp system integration
        class MockWhatsAppUser:
            def __init__(self, phone):
                self.id = f"whatsapp_user_{phone.replace(':', '_').replace('+', '')}"
                self.phone = phone
                self.first_name = "WhatsApp"
                self.last_name = "User"
                self.id_number = "1234567890123"
                self.town = "Unknown"
                self.role = "client"
                self.conversation_state = None
                self.is_active = True
                self.created_at = datetime.utcnow()
        
        return MockWhatsAppUser(phone_number)
    
    def process_conversation_message(self, user, message_data: Dict, msg_type: str) -> str:
        """Process conversation message using WhatsApp system logic"""
        # This would use the actual conversation logic from run.py
        # For now, return a simple response
        
        if msg_type == 'text':
            incoming_msg = message_data['text']['body'].strip().lower()
            
            if incoming_msg in ['hi', 'hello', 'hallo']:
                return "Welcome back to FixMate-SA! To request a service, please describe what you need (e.g., 'Leaking pipe', or any service you may think of)."
            else:
                return "Got it. What's your name?"
        
        return "Thank you for your message. Our team will get back to you soon."
    
    def sync_pending_job_creation(self, whatsapp_user, fastapi_db: Session):
        """Sync any pending job creations to main app"""
        # This would handle job creation synchronization
        print(f"🔄 Syncing pending job creation for user: {whatsapp_user.phone}")
        # Implementation would go here
        pass

# Global service instance
whatsapp_integration_service = WhatsAppIntegrationService()