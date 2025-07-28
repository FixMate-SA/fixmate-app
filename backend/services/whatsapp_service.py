import os
import json
import requests
import tempfile
from datetime import datetime
from typing import Dict, Optional, Any
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

class WhatsAppService:
    def __init__(self):
        self.api_key = DIALOG_360_API_KEY
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
    
    def send_rating_request(self, phone_number: str, job_data: Dict[str, Any]) -> bool:
        """
        Send rating request to client via WhatsApp.
        """
        message = f"""
✅ Your FixMate-SA job has been completed!

📋 Job #{job_data.get('id', 'N/A')}
🔨 Service: {job_data.get('description', 'N/A')}
👷 Fixer: {job_data.get('fixer_name', 'N/A')}

How would you rate this service?
Please reply with a number from 1 (poor) to 5 (excellent).

Your feedback helps us improve our service quality.

FixMate-SA Team 🔧
        """.strip()
        
        return self.send_whatsapp_message(phone_number, message)
    
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