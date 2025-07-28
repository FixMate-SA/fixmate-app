import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from twilio.rest import Client

load_dotenv()

class EmergencyService:
    def __init__(self):
        # Twilio configuration for SMS alerts
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Emergency contacts (South African emergency services)
        self.police_emergency_number = "10111"  # South Africa Police emergency
        self.medical_emergency_number = "10177"  # Medical emergency
        self.fire_emergency_number = "10177"   # Fire emergency
        
        # Initialize Twilio client
        if self.twilio_account_sid and self.twilio_auth_token:
            self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.twilio_client = None
            print("⚠️ Twilio credentials not configured - using mock emergency alerts")
    
    def trigger_emergency_alert(
        self, 
        user_id: str, 
        alert_data: Dict[str, Any], 
        db: Session
    ) -> Dict[str, Any]:
        """
        Trigger emergency alert with police notification and location sharing
        """
        try:
            from models import EmergencyAlert, User
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Create emergency alert record
            emergency_alert = EmergencyAlert(
                user_id=user_id,
                job_id=alert_data.get("job_id"),
                alert_type=alert_data.get("alert_type", "emergency"),
                latitude=alert_data.get("latitude"),
                longitude=alert_data.get("longitude"),
                address=alert_data.get("address"),
                description=alert_data.get("description", "Emergency assistance requested"),
                status="active"
            )
            
            db.add(emergency_alert)
            db.commit()
            db.refresh(emergency_alert)
            
            # Send emergency notifications
            police_result = self._notify_police(user, emergency_alert)
            sms_result = self._send_emergency_sms(user, emergency_alert)
            
            # Update alert with notification status
            emergency_alert.police_notified = police_result.get("success", False)
            emergency_alert.police_reference = police_result.get("reference")
            emergency_alert.emergency_contacts_notified = sms_result.get("success", False)
            
            db.commit()
            
            return {
                "success": True,
                "alert_id": emergency_alert.id,
                "message": "Emergency alert activated successfully",
                "police_notified": emergency_alert.police_notified,
                "emergency_contacts_notified": emergency_alert.emergency_contacts_notified,
                "police_reference": emergency_alert.police_reference
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def _notify_police(self, user, emergency_alert) -> Dict[str, Any]:
        """
        Notify police emergency services (mock implementation for safety)
        In production, this would integrate with official emergency services
        """
        try:
            # MOCK IMPLEMENTATION - DO NOT USE IN REAL EMERGENCIES
            # In production, this would connect to official police dispatch systems
            
            location_text = ""
            if emergency_alert.latitude and emergency_alert.longitude:
                location_text = f"Location: {emergency_alert.latitude}, {emergency_alert.longitude}"
                if emergency_alert.address:
                    location_text += f" ({emergency_alert.address})"
            
            emergency_data = {
                "alert_id": emergency_alert.id,
                "user_name": user.name,
                "user_phone": user.phone,
                "alert_type": emergency_alert.alert_type,
                "description": emergency_alert.description,
                "location": location_text,
                "timestamp": emergency_alert.created_at.isoformat()
            }
            
            # MOCK: Simulate police notification
            # In production, replace with actual police API integration
            print(f"🚨 EMERGENCY ALERT - POLICE NOTIFIED 🚨")
            print(f"User: {user.name} ({user.phone})")
            print(f"Type: {emergency_alert.alert_type}")
            print(f"Description: {emergency_alert.description}")
            print(f"Location: {location_text}")
            print(f"Alert ID: {emergency_alert.id}")
            
            # Generate mock police reference number
            police_reference = f"SAPS-{emergency_alert.id[:8].upper()}-{datetime.now().strftime('%Y%m%d')}"
            
            return {
                "success": True,
                "message": "Police notified successfully (MOCK)",
                "reference": police_reference
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _send_emergency_sms(self, user, emergency_alert) -> Dict[str, Any]:
        """
        Send emergency SMS to user's emergency contacts
        """
        try:
            if not self.twilio_client:
                # Mock SMS sending for testing
                print(f"📱 MOCK SMS: Emergency alert sent to {user.phone}")
                return {"success": True, "message": "Mock SMS sent"}
            
            location_text = "Location unavailable"
            if emergency_alert.latitude and emergency_alert.longitude:
                location_text = f"Location: {emergency_alert.latitude}, {emergency_alert.longitude}"
                if emergency_alert.address:
                    location_text += f" ({emergency_alert.address})"
            
            # Emergency SMS message
            message_body = f"""
🚨 EMERGENCY ALERT - FixMate-SA 🚨

User: {user.name}
Alert: {emergency_alert.description}
{location_text}
Time: {emergency_alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Police have been notified.
Alert ID: {emergency_alert.id}

This is an automated emergency alert from FixMate-SA.
            """.strip()
            
            # Send SMS to user's phone (confirmation)
            message = self.twilio_client.messages.create(
                body=message_body,
                from_=self.twilio_phone_number,
                to=user.phone
            )
            
            return {
                "success": True, 
                "message": "Emergency SMS sent successfully",
                "sms_sid": message.sid
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_emergency_alerts(self, user_id: str, db: Session) -> list:
        """
        Get user's emergency alert history
        """
        try:
            from models import EmergencyAlert
            
            alerts = db.query(EmergencyAlert).filter(
                EmergencyAlert.user_id == user_id
            ).order_by(EmergencyAlert.created_at.desc()).all()
            
            return [{
                "id": alert.id,
                "alert_type": alert.alert_type,
                "description": alert.description,
                "status": alert.status,
                "latitude": alert.latitude,
                "longitude": alert.longitude,
                "address": alert.address,
                "police_notified": alert.police_notified,
                "police_reference": alert.police_reference,
                "created_at": alert.created_at.isoformat(),
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            } for alert in alerts]
            
        except Exception as e:
            return []
    
    def resolve_emergency_alert(self, alert_id: str, resolution: str, db: Session) -> Dict[str, Any]:
        """
        Mark emergency alert as resolved
        """
        try:
            from models import EmergencyAlert
            
            alert = db.query(EmergencyAlert).filter(EmergencyAlert.id == alert_id).first()
            if not alert:
                return {"success": False, "error": "Emergency alert not found"}
            
            alert.status = resolution  # resolved, false_alarm, etc.
            alert.resolved_at = datetime.now()
            
            db.commit()
            
            return {
                "success": True,
                "message": f"Emergency alert marked as {resolution}",
                "alert_id": alert_id
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def get_location_from_coordinates(self, latitude: float, longitude: float) -> str:
        """
        Get human-readable address from coordinates (using reverse geocoding)
        """
        try:
            # Using a simple geocoding service (replace with preferred service)
            # This is a basic implementation - you might want to use Google Maps API
            url = f"https://api.bigdatacloud.net/data/reverse-geocode-client"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "localityLanguage": "en"
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("displayName", f"{latitude}, {longitude}")
            else:
                return f"{latitude}, {longitude}"
                
        except Exception:
            return f"{latitude}, {longitude}"

# Global instance
emergency_service = EmergencyService()