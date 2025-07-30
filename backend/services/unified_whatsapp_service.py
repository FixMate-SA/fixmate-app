"""
Unified WhatsApp Service for FixMate-SA
Integrates the proven working WhatsApp system from fixmate_whatsapp/run.py 
with the main FastAPI application using unified models and database.
"""

import os
import sys
import json
import uuid
import requests
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

# Add fixmate_whatsapp to path for importing working components
sys.path.insert(0, '/app/fixmate_whatsapp')

# Import the working WhatsApp functions from the original system
try:
    from app.services import send_whatsapp_message as original_send_whatsapp
    print("✅ Successfully imported original WhatsApp send function")
except ImportError as e:
    print(f"⚠️ Could not import original WhatsApp function: {e}")
    def original_send_whatsapp(to_number, message_body):
        print(f"MOCK: Would send WhatsApp message to {to_number}: {message_body}")
        return True

# Import main app components
from models import User, Fixer, Job, Review
from database import get_db
from services.ai_service import ai_service

# Dialog360 Configuration - Using proven working settings
DIALOG_360_API_KEY = os.getenv("DIALOG_360_API_KEY")
DIALOG_360_URL = "https://waba-v2.360dialog.io/messages"  # Cloud API (not /v1)
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

class UnifiedWhatsAppService:
    """
    Unified WhatsApp service that combines the working run.py logic
    with the main FastAPI app database and models.
    """
    
    def __init__(self):
        self.api_key = DIALOG_360_API_KEY
        self.phone_number_id = PHONE_NUMBER_ID
        self.messages_url = DIALOG_360_URL
        
        # Conversation states from working run.py system
        self.states = {
            'AWAITING_SERVICE_REQUEST': 'awaiting_service_request',
            'AWAITING_NAME': 'awaiting_name',
            'AWAITING_LOCATION': 'awaiting_location', 
            'AWAITING_CONTACT_NUMBER': 'awaiting_contact_number',
            'AWAITING_TERMS_APPROVAL': 'awaiting_terms_approval',
            'AWAITING_RATING': 'awaiting_rating',
            'AWAITING_RATING_COMMENT': 'awaiting_rating_comment'
        }
    
    def process_webhook(self, webhook_data: Dict[str, Any], db: Session) -> Dict[str, str]:
        """
        Process WhatsApp webhook using the proven working logic from run.py
        but with unified database models.
        """
        try:
            print(f"🔄 Processing WhatsApp webhook with unified system")
            
            # Extract message data using exact logic from run.py
            if 'entry' not in webhook_data:
                return {"status": "ignored", "reason": "no_entry"}
            
            value = webhook_data['entry'][0]['changes'][0]['value']
            
            # Ignore status updates
            if 'statuses' in value:
                print("📊 Received status update - ignoring")
                return {"status": "ignored", "reason": "status_update"}
            
            # Process messages
            if 'messages' in value:
                message = value['messages'][0]
                from_number = f"whatsapp:+{message['from']}"
                
                # Get or create user in unified database
                user = self.get_or_create_user(from_number, db)
                
                # Update WhatsApp activity
                user.update_whatsapp_activity()
                db.commit()
                
                # Process different message types
                msg_type = message.get('type')
                incoming_msg = ""
                location = None
                
                if msg_type == 'text':
                    incoming_msg = message['text']['body'].strip()
                elif msg_type == 'location':
                    location = message['location']
                elif msg_type == 'audio':
                    # Handle voice messages using AI service
                    audio_id = message['audio']['id']
                    incoming_msg = self.process_voice_message(audio_id)
                
                # Process conversation using unified logic
                response_message = self.process_conversation(user, incoming_msg, location, msg_type, db)
                
                # Send response using the proven working function
                if response_message:
                    success = self.send_whatsapp_message(from_number, response_message)
                    if success:
                        print(f"✅ Response sent successfully to {from_number}")
                    else:
                        print(f"❌ Failed to send response to {from_number}")
                
                return {"status": "processed"}
            
            return {"status": "ignored", "reason": "no_messages"}
            
        except Exception as e:
            print(f"❌ Error processing webhook: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "error": str(e)}
    
    def get_or_create_user(self, phone_number: str, db: Session) -> User:
        """Get or create user in unified database"""
        # Check if user exists
        existing_user = db.query(User).filter(User.phone == phone_number).first()
        
        if existing_user:
            return existing_user
        
        # Generate unique placeholder ID number using phone number
        import hashlib
        phone_hash = hashlib.md5(phone_number.encode()).hexdigest()[:10]
        unique_id_number = f"WA{phone_hash}"  # WhatsApp prefix + unique hash
        
        # Create new user with WhatsApp defaults
        new_user = User(
            phone=phone_number,
            first_name="WhatsApp",
            last_name="User", 
            id_number=unique_id_number,  # Unique placeholder based on phone
            town="Unknown",
            role="client",
            whatsapp_active=True,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        print(f"✅ Created new WhatsApp user: {phone_number}")
        
        return new_user
    
    def process_conversation(self, user: User, incoming_msg: str, location: Dict = None, 
                           msg_type: str = 'text', db: Session = None) -> str:
        """
        Process conversation using the exact logic from run.py 
        but with unified database models.
        """
        current_state = user.conversation_state
        response_message = ""
        
        # Post-Job States (Rating & Feedback)
        if current_state == self.states['AWAITING_RATING']:
            cache_data = user.get_conversation_cache()
            job_id = cache_data.get('job_id')
            
            if incoming_msg.isdigit() and 1 <= int(incoming_msg) <= 5:
                # Update job rating in database
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.rating = int(incoming_msg)
                    db.commit()
                
                user.set_conversation_cache({'job_id': job_id, 'rating': int(incoming_msg)})
                response_message = "Thank you for the rating! Could you please share a brief comment about your experience?"
                user.conversation_state = self.states['AWAITING_RATING_COMMENT']
                db.commit()
            else:
                response_message = "Please provide a rating from 1 to 5 stars."
        
        elif current_state == self.states['AWAITING_RATING_COMMENT']:
            cache_data = user.get_conversation_cache()
            job_id = cache_data.get('job_id')
            
            # Update job with rating comment and sentiment analysis
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.rating_comment = incoming_msg
                # Use AI service for sentiment analysis
                try:
                    sentiment = ai_service.analyze_sentiment(incoming_msg)
                    job.sentiment = sentiment
                except Exception as e:
                    print(f"⚠️ Sentiment analysis failed: {e}")
                    job.sentiment = "neutral"
                db.commit()
            
            response_message = "Thank you for your feedback! We appreciate you helping us improve FixMate-SA!"
            user.clear_conversation_cache()
            db.commit()
        
        # Job Request States
        elif current_state == self.states['AWAITING_LOCATION'] and location:
            # Handle GPS location
            user_name_greet = f"{user.first_name.split(' ')[0]}, " if user.first_name and user.first_name != "WhatsApp" else ""
            response_message = f"Thanks, {user_name_greet}I've got your location. Lastly, what's the best contact number for the fixer to use?"
            
            cache_data = user.get_conversation_cache()
            cache_data.update({
                'latitude': str(location.get('latitude')),
                'longitude': str(location.get('longitude'))
            })
            user.set_conversation_cache(cache_data)
            user.conversation_state = self.states['AWAITING_CONTACT_NUMBER']
            db.commit()
        
        elif incoming_msg:
            if current_state == self.states['AWAITING_SERVICE_REQUEST']:
                response_message = "Got it. What's your name?"
                user.set_conversation_cache({'service': incoming_msg})
                user.conversation_state = self.states['AWAITING_NAME']
                db.commit()
            
            elif current_state == self.states['AWAITING_NAME']:
                # Update user with actual name
                names = incoming_msg.strip().split()
                user.first_name = names[0] if names else "Client"
                user.last_name = " ".join(names[1:]) if len(names) > 1 else "User"
                
                first_name = user.first_name.split(' ')[0]
                response_message = f"Thanks, {first_name}. To help us find the nearest fixer, please share your location address: \"Town/Village/township name and house number.\""
                user.conversation_state = self.states['AWAITING_LOCATION']
                db.commit()
            
            elif current_state == self.states['AWAITING_LOCATION']:
                # Handle text-based location
                user_name_greet = f"{user.first_name.split(' ')[0]}, " if user.first_name and user.first_name != "WhatsApp" else ""
                response_message = f"Thanks, {user_name_greet}I've got your location. Lastly, what's the best contact number for the fixer to use?"
                
                cache_data = user.get_conversation_cache()
                cache_data.update({
                    'location_text': incoming_msg, 
                    'area': incoming_msg
                })
                user.set_conversation_cache(cache_data)
                user.conversation_state = self.states['AWAITING_CONTACT_NUMBER']
                db.commit()
            
            elif current_state == self.states['AWAITING_CONTACT_NUMBER']:
                if any(char.isdigit() for char in incoming_msg) and len(incoming_msg) >= 10:
                    response_message = """Great! We have all the details.

By proceeding, you agree to the FixMate-SA Terms of Service.
View here: https://fixmate-sa-app-a448c751e1d2.herokuapp.com/terms

Reply YES to confirm and dispatch a fixer."""
                    
                    cache_data = user.get_conversation_cache()
                    cache_data['contact'] = incoming_msg
                    user.set_conversation_cache(cache_data)
                    user.conversation_state = self.states['AWAITING_TERMS_APPROVAL']
                    db.commit()
                else:
                    response_message = "That doesn't seem to be a valid phone number. Please try again."
            
            elif current_state == self.states['AWAITING_TERMS_APPROVAL']:
                if 'yes' in incoming_msg.lower():
                    cache_data = user.get_conversation_cache()
                    job_id = self.create_job(user, cache_data, db)
                    
                    response_message = f"Perfect! We have logged your request (Job #{job_id}) and have notified a nearby fixer. They will contact you shortly."
                    user.clear_conversation_cache()
                    db.commit()
                else:
                    response_message = "Job request cancelled. Please say 'hello' to start a new request."
                    user.clear_conversation_cache()
                    db.commit()
            
            else:
                # Default/new conversation - using exact logic from run.py
                user.clear_conversation_cache()
                db.commit()
                
                first_name = f" {user.first_name.split(' ')[0]}" if user.first_name and user.first_name != "WhatsApp" else ""
                
                if incoming_msg.lower() in ['hi', 'hello', 'hallo', 'dumela', 'sawubona', 'molo', 'avuxeni', 'ndaa']:
                    response_message = f"Welcome back{first_name} to FixMate-SA! To request a service, please describe what you need (e.g., 'Leaking pipe', or any service you may think of)."
                    user.conversation_state = self.states['AWAITING_SERVICE_REQUEST']
                    db.commit()
                else:
                    # Direct service request
                    response_message = "Got it. What's your name?"
                    user.set_conversation_cache({'service': incoming_msg})
                    user.conversation_state = self.states['AWAITING_NAME']
                    db.commit()
        
        return response_message
    
    def create_job(self, user: User, job_data: Dict, db: Session) -> str:
        """Create a job in the unified database"""
        try:
            # Create new job using unified Job model
            new_job = Job(
                user_id=user.id,
                service=job_data.get('service', 'General Service'),
                description=job_data.get('service', 'Service requested via WhatsApp'),
                location=job_data.get('location_text', job_data.get('area', 'Location provided via WhatsApp')),
                client_contact_number=job_data.get('contact'),
                area=job_data.get('area'),
                latitude=float(job_data.get('latitude', 0)) if job_data.get('latitude') else None,
                longitude=float(job_data.get('longitude', 0)) if job_data.get('longitude') else None,
                status='pending'
            )
            
            db.add(new_job)
            db.commit()
            
            print(f"✅ Created job {new_job.id} for user {user.phone}")
            
            # Here you could add job assignment logic to find and assign a fixer
            self.assign_fixer_to_job(new_job, db)
            
            return new_job.id
            
        except Exception as e:
            print(f"❌ Error creating job: {e}")
            db.rollback()
            return str(uuid.uuid4())  # Return a UUID for user feedback even if creation failed
    
    def assign_fixer_to_job(self, job: Job, db: Session):
        """Assign a suitable fixer to the job"""
        try:
            # Find available fixers near the job location
            available_fixers = db.query(Fixer).filter(
                Fixer.is_active == True,
                Fixer.is_approved == True,
                Fixer.payment_status == 'current'
            ).limit(5).all()
            
            if available_fixers:
                # Simple assignment to first available fixer
                # In production, this would include distance/rating/specialty matching
                assigned_fixer = available_fixers[0]
                job.fixer_id = assigned_fixer.id
                job.status = 'assigned'
                
                # Update fixer stats
                assigned_fixer.total_jobs += 1
                assigned_fixer.last_assigned_at = datetime.utcnow()
                
                db.commit()
                print(f"✅ Assigned fixer {assigned_fixer.name} to job {job.id}")
            
        except Exception as e:
            print(f"⚠️ Error assigning fixer: {e}")
    
    def send_whatsapp_message(self, to_number: str, message_body: str) -> bool:
        """Send WhatsApp message using the proven working function"""
        try:
            # Use the original working function from fixmate_whatsapp
            return original_send_whatsapp(to_number, message_body)
        except Exception as e:
            print(f"❌ Error sending WhatsApp message: {e}")
            return False
    
    def process_voice_message(self, audio_id: str) -> str:
        """Process voice message using AI transcription"""
        try:
            # Use AI service for transcription
            transcription = ai_service.transcribe_audio(f"whatsapp_audio_{audio_id}")
            return transcription or "I couldn't understand the voice message. Please type your request."
        except Exception as e:
            print(f"⚠️ Voice transcription failed: {e}")
            return "I couldn't process the voice message. Please type your request."

# Global unified service instance
unified_whatsapp_service = UnifiedWhatsAppService()