import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

class SMSService:
    def __init__(self):
        self.client = None
        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
            self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """
        Send SMS using Twilio.
        """
        if not self.client or not TWILIO_PHONE_NUMBER:
            print("SMS service not configured. Please set Twilio credentials.")
            return False
        
        try:
            # Format phone number for South African numbers
            if to_number.startswith("0") and len(to_number) == 10:
                to_number = f"+27{to_number[1:]}"
            elif not to_number.startswith("+"):
                to_number = f"+27{to_number}"
            
            message_obj = self.client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=to_number
            )
            
            print(f"SMS sent successfully. SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
    
    def send_mms(self, to_number: str, message: str, media_url: str = None) -> bool:
        """
        Send MMS using Twilio.
        """
        if not self.client or not TWILIO_PHONE_NUMBER:
            print("MMS service not configured. Please set Twilio credentials.")
            return False
        
        try:
            # Format phone number for South African numbers
            if to_number.startswith("0") and len(to_number) == 10:
                to_number = f"+27{to_number[1:]}"
            elif not to_number.startswith("+"):
                to_number = f"+27{to_number}"
            
            message_params = {
                'body': message,
                'from_': TWILIO_PHONE_NUMBER,
                'to': to_number
            }
            
            if media_url:
                message_params['media_url'] = [media_url]
            
            message_obj = self.client.messages.create(**message_params)
            
            print(f"MMS sent successfully. SID: {message_obj.sid}")
            return True
            
        except Exception as e:
            print(f"Error sending MMS: {e}")
            return False
    
    def handle_incoming_sms(self, from_number: str, message_body: str) -> str:
        """
        Process incoming SMS and return response.
        """
        # Basic SMS conversation logic
        message_body = message_body.lower().strip()
        
        if any(greeting in message_body for greeting in ['hello', 'hi', 'help', 'start']):
            return self._get_welcome_message()
        elif 'service' in message_body or 'help' in message_body:
            return self._get_service_request_message()
        elif 'status' in message_body:
            return self._get_status_message(from_number)
        elif 'stop' in message_body:
            return "You have been unsubscribed from FixMate-SA SMS notifications. Reply START to resume."
        else:
            return self._get_help_message()
    
    def _get_welcome_message(self) -> str:
        return (
            "Welcome to FixMate-SA! 🔧\n\n"
            "Your reliable service provider via SMS.\n\n"
            "Reply:\n"
            "• SERVICE - to request a service\n"
            "• STATUS - to check job status\n"
            "• HELP - for more options\n\n"
            "Or visit our app: https://fixmate-sa.com"
        )
    
    def _get_service_request_message(self) -> str:
        return (
            "To request a service via SMS:\n\n"
            "1. Describe what you need (e.g., 'plumbing - leaking tap')\n"
            "2. Include your area (e.g., 'Johannesburg')\n"
            "3. Add your contact number\n\n"
            "Example: 'Electrical - broken light switch, Pretoria, 082 123 4567'\n\n"
            "Or use our app for better experience: https://fixmate-sa.com"
        )
    
    def _get_status_message(self, phone_number: str) -> str:
        # This would check the database for user's job status
        return (
            "To check your job status:\n\n"
            "• Visit our app: https://fixmate-sa.com\n"
            "• Call our support: 087 123 4567\n\n"
            "For real-time updates, download our app."
        )
    
    def _get_help_message(self) -> str:
        return (
            "FixMate-SA SMS Help 📱\n\n"
            "Commands:\n"
            "• SERVICE - request a service\n"
            "• STATUS - check job status\n"
            "• HELP - show this menu\n"
            "• STOP - unsubscribe\n\n"
            "Download our app for full features:\n"
            "https://fixmate-sa.com"
        )
    
    def send_job_notification(self, to_number: str, job_id: str, service_type: str, status: str) -> bool:
        """
        Send job status notification via SMS.
        """
        status_messages = {
            'created': f"Job #{job_id} created for {service_type}. We're finding a fixer for you.",
            'assigned': f"Job #{job_id} assigned! A fixer will contact you shortly.",
            'in_progress': f"Job #{job_id} is now in progress. Your fixer is on the way.",
            'completed': f"Job #{job_id} completed! Please rate your experience via our app.",
            'cancelled': f"Job #{job_id} has been cancelled. Contact support if needed."
        }
        
        message = status_messages.get(status, f"Job #{job_id} status updated to {status}.")
        message += f"\n\nTrack your job: https://fixmate-sa.com/jobs/{job_id}"
        
        return self.send_sms(to_number, message)
    
    def send_fixer_notification(self, to_number: str, job_id: str, service_type: str, client_area: str) -> bool:
        """
        Send new job notification to fixer via SMS.
        """
        message = (
            f"New FixMate-SA Job! 🔧\n\n"
            f"Job #{job_id}\n"
            f"Service: {service_type}\n"
            f"Area: {client_area}\n\n"
            f"Accept job: https://fixmate-sa.com/fixer/jobs/{job_id}\n\n"
            f"Or call: 087 123 4567"
        )
        
        return self.send_sms(to_number, message)

# Global instance
sms_service = SMSService()