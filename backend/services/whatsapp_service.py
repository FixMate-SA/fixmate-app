import os
import json
import requests
import tempfile
from datetime import datetime
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from .ai_service import ai_service
from .sms_service import sms_service

load_dotenv()

# WhatsApp API Configuration
DIALOG_360_API_KEY = os.getenv("DIALOG_360_API_KEY")
DIALOG_360_URL = "https://waba-v2.360dialog.io"
DIALOG_360_MESSAGES_URL = f"{DIALOG_360_URL}/messages"
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# Official FixMate-SA WhatsApp Business Number
FIXMATE_WHATSAPP_BUSINESS_NUMBER = "27754466571"  # Official business number without +

class WhatsAppService:
    def __init__(self):
        self.api_key = DIALOG_360_API_KEY
        self.phone_number_id = PHONE_NUMBER_ID
        self.base_url = DIALOG_360_URL
        self.messages_url = DIALOG_360_MESSAGES_URL
        self.geocoder = Nominatim(user_agent="FixMate-SA")
        
        # Conversation states
        self.STATES = {
            'AWAITING_SERVICE_REQUEST': 'awaiting_service_request',
            'AWAITING_NAME': 'awaiting_name', 
            'AWAITING_LOCATION': 'awaiting_location',
            'AWAITING_CONTACT_NUMBER': 'awaiting_contact_number',
            'AWAITING_TERMS_APPROVAL': 'awaiting_terms_approval',
            'AWAITING_RATING': 'awaiting_rating',
            'AWAITING_RATING_COMMENT': 'awaiting_rating_comment'
        }
    
    def send_whatsapp_message(self, to_number: str, message_body: str, media_url: str = None) -> bool:
        """
        Send WhatsApp message via 360dialog API.
        """
        if not self.api_key:
            print("WhatsApp service not configured. Please set DIALOG_360_API_KEY.")
            return False
        
        try:
            # Format phone number (remove whatsapp: prefix if present)
            if to_number.startswith("whatsapp:"):
                to_number = to_number.replace("whatsapp:", "")
            
            # Remove + prefix for 360dialog
            if to_number.startswith("+"):
                to_number = to_number[1:]
            
            headers = {
                'D360-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Create message payload
            payload = {
                "to": to_number,
                "type": "text",
                "text": {
                    "body": message_body
                }
            }
            
            # Add phone number ID if available
            if self.phone_number_id:
                payload["from"] = self.phone_number_id
            
            # Add media if provided
            if media_url:
                payload["type"] = "image"
                payload["image"] = {
                    "link": media_url,
                    "caption": message_body
                }
                del payload["text"]
            
            response = requests.post(
                self.messages_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"WhatsApp message sent successfully to {to_number}")
                return True
            else:
                print(f"Failed to send WhatsApp message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False
    
    def download_media(self, media_id: str) -> bytes:
        """
        Download media from WhatsApp using 360dialog API.
        """
        if not self.api_key:
            print("WhatsApp service not configured.")
            return None
        
        try:
            headers = {'D360-API-KEY': self.api_key}
            media_url = f"{self.base_url}/{media_id}"
            
            response = requests.get(media_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to download media: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error downloading media: {e}")
            return None
    
    def transcribe_whatsapp_audio(self, media_id: str) -> str:
        """
        Download and transcribe audio from WhatsApp.
        """
        try:
            # Download audio content
            audio_content = self.download_media(media_id)
            if not audio_content:
                return "Could not download audio."
            
            # Transcribe using AI service
            transcription = ai_service.transcribe_audio(audio_content)
            return transcription
            
        except Exception as e:
            print(f"Error transcribing WhatsApp audio: {e}")
            return "Error processing audio message."
    
    def get_location_from_coords(self, latitude: float, longitude: float) -> str:
        """
        Get area name from coordinates using reverse geocoding.
        """
        try:
            location = self.geocoder.reverse(f"{latitude}, {longitude}")
            if location and location.address:
                # Extract area/suburb/city from address
                address_parts = location.address.split(', ')
                for part in address_parts:
                    if any(keyword in part.lower() for keyword in ['suburb', 'city', 'town']):
                        return part
                # Fallback to first meaningful part
                return address_parts[0] if address_parts else "Unknown Area"
            return "Unknown Area"
            
        except Exception as e:
            print(f"Error in reverse geocoding: {e}")
            return "Unknown Area"
    
    def format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number to WhatsApp format.
        """
        if not phone_number.startswith("whatsapp:"):
            if phone_number.startswith("0") and len(phone_number) == 10:
                phone_number = f"+27{phone_number[1:]}"
            elif not phone_number.startswith("+"):
                phone_number = f"+27{phone_number}"
            phone_number = f"whatsapp:{phone_number}"
        return phone_number
    
    def process_webhook_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming WhatsApp webhook message.
        """
        try:
            # Extract message data from webhook
            entry = webhook_data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            # Handle status updates (ignore them)
            if 'statuses' in value:
                return {"status": "ignored", "type": "status_update"}
            
            # Process messages
            if 'messages' in value:
                message = value['messages'][0]
                from_number = f"whatsapp:+{message['from']}"
                msg_type = message.get('type')
                
                result = {
                    "status": "processed",
                    "from_number": from_number,
                    "message_type": msg_type,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Extract message content based on type
                if msg_type == 'text':
                    result["content"] = message['text']['body'].strip()
                elif msg_type == 'audio':
                    audio_id = message['audio']['id']
                    result["content"] = self.transcribe_whatsapp_audio(audio_id)
                    result["media_id"] = audio_id
                elif msg_type == 'location':
                    location = message['location']
                    result["content"] = "Location shared"
                    result["location"] = {
                        "latitude": location.get('latitude'),
                        "longitude": location.get('longitude'),
                        "address": location.get('address', '')
                    }
                elif msg_type == 'image':
                    result["content"] = message.get('image', {}).get('caption', 'Image received')
                    result["media_id"] = message.get('image', {}).get('id')
                else:
                    result["content"] = f"Unsupported message type: {msg_type}"
                
                return result
            
            return {"status": "ignored", "type": "unknown"}
            
        except Exception as e:
            print(f"Error processing webhook message: {e}")
            return {"status": "error", "error": str(e)}
    
    def send_job_notification(self, phone_number: str, job_data: Dict[str, Any]) -> bool:
        """
        Send job notification via WhatsApp.
        """
        message = f"""
🔧 New FixMate-SA Job Alert!

📋 Job #{job_data.get('id', 'N/A')}
🔨 Service: {job_data.get('description', 'N/A')}
📍 Area: {job_data.get('area', 'N/A')}
📞 Client Contact: {job_data.get('client_contact', 'N/A')}

Please log in to your Fixer Portal to accept this job:
https://fixmate-sa.com/fixer/login

FixMate-SA Team
        """.strip()
        
        return self.send_whatsapp_message(phone_number, message)
    
    def send_client_confirmation(self, phone_number: str, job_data: Dict[str, Any]) -> bool:
        """
        Send job confirmation to client via WhatsApp.
        """
        message = f"""
✅ Your FixMate-SA service request has been logged!

📋 Job #{job_data.get('id', 'N/A')}
🔨 Service: {job_data.get('description', 'N/A')}
📍 Area: {job_data.get('area', 'N/A')}

We're finding the best fixer for you and will notify you once assigned.

Track your job: https://fixmate-sa.com/jobs/{job_data.get('id', '')}

Thank you for choosing FixMate-SA! 🔧
        """.strip()
        
        return self.send_whatsapp_message(phone_number, message)
    
    def process_business_webhook(self, webhook_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Process WhatsApp Business webhook for official FixMate-SA number (0754466571)
        """
        try:
            # Extract webhook data
            entry = webhook_data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            # Check if it's a message
            messages = value.get('messages', [])
            if not messages:
                return {'processed': False, 'reason': 'No messages found'}
            
            for message in messages:
                from_number = message.get('from')
                message_type = message.get('type')
                message_id = message.get('id')
                timestamp = message.get('timestamp')
                
                # Format phone number
                if not from_number.startswith('+'):
                    from_number = f"+{from_number}"
                
                # Process different message types
                if message_type == 'text':
                    text_body = message.get('text', {}).get('body', '')
                    self._process_business_text_message(from_number, text_body, db)
                    
                elif message_type == 'audio':
                    audio_id = message.get('audio', {}).get('id')
                    self._process_business_audio_message(from_number, audio_id, db)
                    
                elif message_type == 'location':
                    location = message.get('location', {})
                    latitude = location.get('latitude')
                    longitude = location.get('longitude')
                    self._process_business_location_message(from_number, latitude, longitude, db)
                
                # Log the message
                print(f"Business WhatsApp message processed: {from_number} - {message_type}")
            
            return {'processed': True, 'messages_count': len(messages)}
            
        except Exception as e:
            print(f"Error processing business webhook: {e}")
            return {'processed': False, 'error': str(e)}
    
    def _process_business_text_message(self, from_number: str, text: str, db: Session):
        """Process text message from business WhatsApp"""
        try:
            from ..models import User
            
            # Check for business compliance keywords
            compliance_keywords = [
                'company registration', 'sars', 'tax', 'compliance', 'license', 
                'registration', 'business help', 'company help', 'b-bbee', 
                'labour law', 'permits', 'audit', 'financial compliance'
            ]
            
            text_lower = text.lower()
            is_compliance_inquiry = any(keyword in text_lower for keyword in compliance_keywords)
            
            if is_compliance_inquiry:
                # Send business compliance information
                response_message = """🏢 FixMate-SA Business Compliance Services

I can help you with:
• Company Registrations (Pty Ltd, CC, etc.)
• SARS Registration & Tax Compliance
• Labour Law Compliance
• B-BBEE Certification
• Licensing & Permits
• Financial Compliance & Audits

📱 Visit our app at https://fixmate-sa-app-a448c751e1d2.herokuapp.com
📋 Or type "COMPLIANCE MENU" for detailed options

Our compliance experts are ready to assist you!
Reply with your specific needs for a personalized quote."""
                
                self.send_whatsapp_message(f"whatsapp:{from_number}", response_message)
            
            elif 'compliance menu' in text_lower:
                # Send detailed compliance menu
                self._send_compliance_menu(from_number)
            
            else:
                # Regular FixMate service inquiry
                response_message = f"""👋 Hello! Welcome to FixMate-SA!

I can help you with:
🔧 Home & Office Repairs
🏢 Business Compliance Services
📱 Emergency Services

Type:
• "REPAIRS" for fixing services
• "COMPLIANCE" for business help
• "EMERGENCY" for urgent assistance

Or visit our app: https://fixmate-sa-app-a448c751e1d2.herokuapp.com"""
                
                self.send_whatsapp_message(f"whatsapp:{from_number}", response_message)
        
        except Exception as e:
            print(f"Error processing business text message: {e}")
    
    def _send_compliance_menu(self, from_number: str):
        """Send detailed compliance services menu"""
        try:
            from .business_compliance_service import business_compliance_service
            
            categories = business_compliance_service.get_compliance_categories()
            
            menu_message = """🏢 FixMate-SA Business Compliance Services

Choose a service:

1️⃣ Company Registration (R1,500-R3,500)
   • Pty Ltd, CC, NPO registrations
   • CIPC submissions & approvals

2️⃣ SARS & Tax Compliance (R800-R2,500)
   • VAT, PAYE, UIF, SDL registration
   • Tax returns & compliance

3️⃣ Labour Law Compliance (R1,000-R2,000)
   • Employment contracts
   • CCMA assistance

4️⃣ B-BBEE Certification (R3,000-R8,000)
   • B-BBEE certificates
   • Compliance management

5️⃣ Licensing & Permits (R500-R3,000)
   • Trading licenses
   • Municipal permits

6️⃣ Financial Compliance (R2,000-R5,000)
   • Annual returns
   • Audit compliance

📱 Visit our app for detailed quotes: https://fixmate-sa-app-a448c751e1d2.herokuapp.com/business-compliance

Reply with the service number or describe your needs for a personalized quote!"""
            
            self.send_whatsapp_message(f"whatsapp:{from_number}", menu_message)
            
        except Exception as e:
            print(f"Error sending compliance menu: {e}")
    
    def _process_business_audio_message(self, from_number: str, audio_id: str, db: Session):
        """Process audio message from business WhatsApp"""
        try:
            # Transcribe audio using existing transcription service
            transcription = ai_service.transcribe_audio(audio_id)
            
            if transcription:
                # Process the transcribed text
                self._process_business_text_message(from_number, transcription, db)
                
                # Send confirmation
                response = f"🎙️ I heard: \"{transcription}\"\n\nLet me help you with that..."
                self.send_whatsapp_message(f"whatsapp:{from_number}", response)
            else:
                error_message = "Sorry, I couldn't understand the audio. Please try typing your message or call us directly."
                self.send_whatsapp_message(f"whatsapp:{from_number}", error_message)
                
        except Exception as e:
            print(f"Error processing business audio message: {e}")
    
    def _process_business_location_message(self, from_number: str, latitude: float, longitude: float, db: Session):
        """Process location message from business WhatsApp"""
        try:
            # Get area from coordinates
            area = self._get_area_from_coords(latitude, longitude)
            
            response_message = f"""📍 Location received: {area}

I can connect you with fixers and compliance experts in your area.

Services available in {area}:
🔧 Home & Office Repairs
🏢 Business Compliance Services
🚨 Emergency Assistance

What do you need help with today?"""
            
            self.send_whatsapp_message(f"whatsapp:{from_number}", response_message)
            
        except Exception as e:
            print(f"Error processing business location message: {e}")
    
    def _get_area_from_coords(self, latitude: float, longitude: float) -> str:
        """Get area name from coordinates using reverse geocoding"""
        try:
            location = self.geocoder.reverse((latitude, longitude), timeout=10)
            if location and location.address:
                # Extract suburb/city from address
                address_components = location.raw.get('address', {})
                area = (address_components.get('suburb') or 
                       address_components.get('city') or 
                       address_components.get('town') or 
                       'Unknown Area')
                return area
            return 'Unknown Area'
        except Exception as e:
            print(f"Error in reverse geocoding: {e}")
            return 'Unknown Area'
    
    def send_welcome_message(self, phone_number: str, user_name: str = None) -> bool:
        """
        Send welcome message to new or returning user.
        """
        greeting = f"Welcome back {user_name.split()[0]}!" if user_name else "Welcome to FixMate-SA!"
        
        message = f"""
🔧 {greeting}

Your reliable service provider in South Africa.

To request a service, please:
1. Describe what you need (e.g., "leaking tap", "broken light")
2. Or send a voice note with your request
3. Or say "hello" to start the conversation

We support all South African languages!

Visit our app: https://fixmate-sa.com
        """.strip()
        
        return self.send_whatsapp_message(phone_number, message)
    
    def handle_admin_command(self, command: str, from_number: str) -> str:
        """
        Handle admin commands sent via WhatsApp.
        """
        # This would check if the sender is an admin and process commands
        # For now, return a simple message
        return "Admin commands are not supported via WhatsApp yet. Please use the web interface."

# Global instance
whatsapp_service = WhatsAppService()