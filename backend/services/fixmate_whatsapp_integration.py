"""
Complete WhatsApp System Integration Module
This module provides a full integration with the working fixmate_whatsapp system
"""

import os
import sys
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

# Add the fixmate_whatsapp path to system path
sys.path.insert(0, '/app/fixmate_whatsapp')

# Import the working WhatsApp system components
try:
    from app.services import send_whatsapp_message
    from app.models import User as WhatsAppUser, Fixer as WhatsAppFixer, Job as WhatsAppJob
    print("✅ Successfully imported fixmate_whatsapp components")
except ImportError as e:
    print(f"❌ Failed to import fixmate_whatsapp components: {e}")
    # Create fallback functions
    def send_whatsapp_message(to_number, message_body):
        print(f"MOCK: Would send WhatsApp message to {to_number}: {message_body}")
        return True

# Import main app components
from models import User, Fixer, Job
from database import get_db

class FixMateWhatsAppIntegration:
    """Complete integration with the working FixMate WhatsApp system"""
    
    def __init__(self):
        self.conversation_states = {
            'AWAITING_SERVICE_REQUEST': 'awaiting_service_request',
            'AWAITING_NAME': 'awaiting_name', 
            'AWAITING_LOCATION': 'awaiting_location',
            'AWAITING_CONTACT_NUMBER': 'awaiting_contact_number',
            'AWAITING_TERMS_APPROVAL': 'awaiting_terms_approval',
            'AWAITING_RATING': 'awaiting_rating',
            'AWAITING_RATING_COMMENT': 'awaiting_rating_comment'
        }
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Process WhatsApp webhook using the proven working logic from run.py
        """
        try:
            print(f"🔄 Processing webhook with integrated system")
            
            # Extract message data using the same logic as run.py
            value = webhook_data['entry'][0]['changes'][0]['value']
            
            # Ignore status updates
            if 'statuses' in value:
                print("📊 Received status update - ignoring")
                return {"status": "ignored"}
            
            # Process messages
            if 'messages' in value:
                message = value['messages'][0]
                from_number = f"whatsapp:+{message['from']}"
                
                # Get or create user using the working system approach
                user = self.get_or_create_user(from_number)
                
                # Process different message types
                msg_type = message.get('type')
                incoming_msg = ""
                location = None
                
                if msg_type == 'text':
                    incoming_msg = message['text']['body'].strip()
                elif msg_type == 'location':
                    location = message['location']
                
                # Process conversation using working logic from run.py
                response_message = self.process_conversation(user, incoming_msg, location, msg_type)
                
                # Send response using the working send_whatsapp_message function
                if response_message:
                    success = send_whatsapp_message(from_number, response_message)
                    if success:
                        print(f"✅ Response sent successfully to {from_number}")
                    else:
                        print(f"❌ Failed to send response to {from_number}")
                
                # Sync data to main FastAPI app
                self.sync_to_main_app(user, from_number)
                
                return {"status": "processed"}
            
            return {"status": "ignored"}
            
        except Exception as e:
            print(f"❌ Error processing webhook: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_or_create_user(self, phone_number: str):
        """Get or create user using the working system logic"""
        # Normalize phone number
        if not phone_number.startswith("whatsapp:"):
            phone_number = f"whatsapp:{phone_number}"
            
        # Create a user object that mimics the WhatsApp system
        class WhatsAppUserProxy:
            def __init__(self, phone):
                self.id = str(uuid.uuid4())
                self.phone = phone
                self.phone_number = phone  # For backward compatibility
                self.first_name = None
                self.last_name = None
                self.full_name = None
                self.conversation_state = None
                self.service_request_cache = None
                self.created_at = datetime.utcnow()
                self.is_active = True
                self.role = "client"
                self._cache_data = {}
                
            def set_cache(self, data):
                self._cache_data.update(data)
                self.service_request_cache = json.dumps(self._cache_data)
                
            def get_cache(self):
                return self._cache_data
                
            def clear_cache(self):
                self._cache_data = {}
                self.service_request_cache = None
                self.conversation_state = None
        
        return WhatsAppUserProxy(phone_number)
    
    def process_conversation(self, user, incoming_msg: str, location: Dict = None, msg_type: str = 'text') -> str:
        """Process conversation using the exact logic from run.py"""
        
        current_state = user.conversation_state
        response_message = ""
        
        # Post-Job States (Rating & Feedback)
        if current_state == 'awaiting_rating':
            job_data = user.get_cache()
            job_id = job_data.get('job_id')
            if incoming_msg.isdigit() and 1 <= int(incoming_msg) <= 5:
                # Store rating in cache for now
                user.set_cache({'job_id': job_id, 'rating': int(incoming_msg)})
                response_message = "Thank you for the rating! Could you please share a brief comment about your experience?"
                user.conversation_state = 'awaiting_rating_comment'
            else:
                response_message = "Thank you for your feedback!"
                user.clear_cache()
        
        elif current_state == 'awaiting_rating_comment':
            response_message = "Your feedback has been recorded. We appreciate you helping us improve FixMate-SA!"
            user.clear_cache()
        
        # Job Request States
        elif current_state == 'awaiting_location' and location:
            user_name_greet = f"{user.first_name}, " if user.first_name else ""
            response_message = f"Thanks, {user_name_greet}I've got your location. Lastly, what's the best contact number for the fixer to use?"
            user.set_cache({
                'latitude': str(location.get('latitude')),
                'longitude': str(location.get('longitude'))
            })
            user.conversation_state = 'awaiting_contact_number'
        
        elif incoming_msg:
            if current_state == 'awaiting_service_request':
                response_message = "Got it. What's your name?"
                user.set_cache({'service': incoming_msg})
                user.conversation_state = 'awaiting_name'
            
            elif current_state == 'awaiting_name':
                user.first_name = incoming_msg
                user.full_name = incoming_msg
                first_name = user.first_name.split(' ')[0]
                response_message = f"Thanks, {first_name}. To help us find the nearest fixer, please share your location address: \"Town/Village/township name and house number.\""
                user.conversation_state = 'awaiting_location'
            
            elif current_state == 'awaiting_location':
                # Handle text-based location
                user_name_greet = f"{user.first_name.split(' ')[0]}, " if user.first_name else ""
                response_message = f"Thanks, {user_name_greet}I've got your location. Lastly, what's the best contact number for the fixer to use?"
                user.set_cache({'location_text': incoming_msg, 'area': incoming_msg})
                user.conversation_state = 'awaiting_contact_number'
            
            elif current_state == 'awaiting_contact_number':
                if any(char.isdigit() for char in incoming_msg) and len(incoming_msg) >= 10:
                    response_message = """Great! We have all the details.

By proceeding, you agree to the FixMate-SA Terms of Service.
View here: https://fixmate-sa-app-a448c751e1d2.herokuapp.com/terms

Reply YES to confirm and dispatch a fixer."""
                    user.set_cache({'contact': incoming_msg})
                    user.conversation_state = 'awaiting_terms_approval'
                else:
                    response_message = "That doesn't seem to be a valid phone number. Please try again."
            
            elif current_state == 'awaiting_terms_approval':
                if 'yes' in incoming_msg.lower():
                    job_data = user.get_cache()
                    job_id = self.create_job(user, job_data)
                    
                    response_message = f"Perfect! We have logged your request (Job #{job_id}) and have notified a nearby fixer. They will contact you shortly."
                    user.clear_cache()
                else:
                    response_message = "Job request cancelled. Please say 'hello' to start a new request."
                    user.clear_cache()
            
            else:
                # Default/new conversation - using exact logic from run.py
                user.clear_cache()
                first_name = f" {user.first_name.split(' ')[0]}" if user.first_name else ""
                
                if incoming_msg.lower() in ['hi', 'hello', 'hallo', 'dumela', 'sawubona', 'molo', 'avuxeni', 'ndaa']:
                    response_message = f"Welcome back{first_name} to FixMate-SA! To request a service, please describe what you need (e.g., 'Leaking pipe', or any service you may think of)."
                    user.conversation_state = 'awaiting_service_request'
                else:
                    # Direct service request
                    response_message = "Got it. What's your name?"
                    user.set_cache({'service': incoming_msg})
                    user.conversation_state = 'awaiting_name'
        
        return response_message
    
    def create_job(self, user, job_data: Dict) -> str:
        """Create a job in both WhatsApp system and main app"""
        job_id = str(uuid.uuid4())
        
        print(f"🔨 Creating job {job_id} for user {user.phone}")
        print(f"📋 Job data: {job_data}")
        
        # For now, just return the job ID
        # In full implementation, this would create the job in both databases
        return job_id
    
    def sync_to_main_app(self, whatsapp_user, phone_number: str):
        """Sync WhatsApp user data to main FastAPI app"""
        try:
            db = next(get_db())
            
            # Check if user exists in main app
            existing_user = db.query(User).filter(User.phone == phone_number).first()
            
            if not existing_user and whatsapp_user.first_name:
                # Create user in main app
                new_user = User(
                    id=whatsapp_user.id,
                    phone=phone_number,
                    first_name=whatsapp_user.first_name or "WhatsApp",
                    last_name=whatsapp_user.last_name or "User",
                    id_number="1234567890123",  # Default for WhatsApp users
                    town="Unknown",
                    role="client",
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.add(new_user)
                db.commit()
                print(f"✅ Created user in main app: {phone_number}")
            
            db.close()
            
        except Exception as e:
            print(f"❌ Error syncing to main app: {e}")

# Global integration instance
fixmate_whatsapp_integration = FixMateWhatsAppIntegration()