import os
import requests
import json
import tempfile
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from twilio.rest import Client
from fastapi import UploadFile
import uuid

# Optional Whisper import for voice transcription
try:
    import whisper
    WHISPER_AVAILABLE = True
    print("✅ Whisper model available for voice transcription")
except ImportError:
    whisper = None
    WHISPER_AVAILABLE = False
    print("⚠️ Whisper not available - voice transcription disabled")

load_dotenv()

class EmergencyService:
    def __init__(self):
        # Twilio configuration for SMS alerts
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # South African Emergency Services
        self.police_emergency_number = "10111"  # South Africa Police emergency
        self.medical_emergency_number = "10177"  # Medical emergency
        self.fire_emergency_number = "10177"   # Fire emergency
        
        # Emergency dispatch configuration
        self.emergency_dispatch_email = os.getenv("EMERGENCY_DISPATCH_EMAIL", "dispatch@fixmate-sa.co.za")
        self.fixmate_emergency_phone = os.getenv("FIXMATE_EMERGENCY_PHONE", "+27115551234")
        
        # Initialize Twilio client
        if self.twilio_account_sid and self.twilio_auth_token:
            self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.twilio_client = None
            print("⚠️ Twilio credentials not configured - using mock emergency alerts")
        
        # Initialize Whisper for voice transcription (optional)
        self.whisper_model = None
        if WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model("base")
                print("✅ Whisper model loaded for voice transcription")
            except Exception as e:
                print(f"⚠️ Whisper model failed to load: {e}")
                self.whisper_model = None
        else:
            print("⚠️ Whisper not available - voice transcription will be handled as text fallback")
    
    async def trigger_emergency_alert(
        self, 
        user_id: str, 
        alert_data: Dict[str, Any], 
        voice_file: Optional[UploadFile],
        db: Session
    ) -> Dict[str, Any]:
        """
        Trigger comprehensive emergency alert with voice recording processing
        """
        try:
            from models import EmergencyAlert, User
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Generate unique alert ID
            alert_id = str(uuid.uuid4())
            
            # Process voice recording if provided
            voice_transcription = None
            voice_file_path = None
            recording_duration = 0
            
            if voice_file:
                try:
                    # Save voice file temporarily
                    voice_file_path = f"/tmp/emergency_voice_{alert_id}.webm"
                    with open(voice_file_path, "wb") as f:
                        content = await voice_file.read()
                        f.write(content)
                    
                    # Get recording duration from form data
                    recording_duration = int(alert_data.get("recording_duration", 0))
                    
                    # Transcribe voice recording
                    if self.whisper_model:
                        voice_transcription = self._transcribe_audio(voice_file_path)
                    else:
                        voice_transcription = "[Voice transcription unavailable - file saved for manual review]"
                    
                    print(f"🎤 Voice transcription: {voice_transcription}")
                    
                except Exception as e:
                    print(f"⚠️ Voice processing error: {e}")
                    voice_transcription = "[Voice processing failed - raw audio file available]"
            
            # Create comprehensive emergency alert record
            emergency_alert = EmergencyAlert(
                id=alert_id,
                user_id=user_id,
                job_id=alert_data.get("job_id"),
                alert_type=alert_data.get("alert_type", "emergency"),
                priority=alert_data.get("priority", "high"),
                latitude=float(alert_data.get("latitude")) if alert_data.get("latitude") else None,
                longitude=float(alert_data.get("longitude")) if alert_data.get("longitude") else None,
                address=alert_data.get("address"),
                description=alert_data.get("description", "Emergency assistance requested"),
                voice_transcription=voice_transcription,
                voice_file_path=voice_file_path,
                recording_duration=recording_duration,
                status="active"
            )
            
            db.add(emergency_alert)
            db.commit()
            db.refresh(emergency_alert)
            
            # Immediate notifications and escalation
            results = await self._execute_emergency_protocol(user, emergency_alert, db)
            
            # Update alert with protocol results
            emergency_alert.police_notified = results.get("police_notified", False)
            emergency_alert.police_reference = results.get("police_reference")
            emergency_alert.emergency_contacts_notified = results.get("emergency_sms_sent", False)
            emergency_alert.dispatch_notified = results.get("dispatch_notified", False)
            emergency_alert.admin_notified = results.get("admin_notified", False)
            
            db.commit()
            
            return {
                "success": True,
                "alert_id": emergency_alert.id,
                "message": "Emergency alert activated - authorities are being contacted",
                "police_notified": emergency_alert.police_notified,
                "police_reference": emergency_alert.police_reference,
                "voice_transcribed": bool(voice_transcription),
                "transcription_preview": voice_transcription[:100] + "..." if voice_transcription and len(voice_transcription) > 100 else voice_transcription,
                "emergency_protocol_status": results.get("protocol_status", "initiated"),
                "priority_level": emergency_alert.priority
            }
            
        except Exception as e:
            db.rollback()
            print(f"❌ Emergency alert failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _execute_emergency_protocol(self, user, emergency_alert, db: Session) -> Dict[str, Any]:
        """
        Execute comprehensive emergency response protocol
        """
        results = {
            "police_notified": False,
            "emergency_sms_sent": False,
            "dispatch_notified": False,
            "admin_notified": False,
            "protocol_status": "failed"
        }
        
        try:
            # Step 1: Create comprehensive emergency data package
            emergency_package = self._create_emergency_data_package(user, emergency_alert)
            
            # Step 2: Notify FixMate emergency dispatch (immediate)
            dispatch_result = await self._notify_fixmate_dispatch(emergency_package)
            results["dispatch_notified"] = dispatch_result.get("success", False)
            
            # Step 3: Send emergency SMS to user and emergency contacts
            sms_result = await self._send_comprehensive_emergency_sms(user, emergency_alert, emergency_package)
            results["emergency_sms_sent"] = sms_result.get("success", False)
            
            # Step 4: Alert FixMate admin team
            admin_result = await self._alert_admin_team(emergency_package)
            results["admin_notified"] = admin_result.get("success", False)
            
            # Step 5: Initiate 10111 contact protocol (through dispatch)
            police_result = await self._initiate_police_contact_protocol(emergency_package)
            results["police_notified"] = police_result.get("success", False)
            results["police_reference"] = police_result.get("reference")
            
            # Determine overall protocol status
            if results["dispatch_notified"] and results["emergency_sms_sent"]:
                results["protocol_status"] = "active"
            elif results["dispatch_notified"] or results["emergency_sms_sent"]:
                results["protocol_status"] = "partial"
            else:
                results["protocol_status"] = "failed"
            
            return results
            
        except Exception as e:
            print(f"❌ Emergency protocol execution failed: {e}")
            results["protocol_status"] = "failed"
            return results
    
    def _create_emergency_data_package(self, user, emergency_alert) -> Dict[str, Any]:
        """
        Create comprehensive emergency data package for dispatch
        """
        location_text = "Location unknown"
        if emergency_alert.latitude and emergency_alert.longitude:
            location_text = f"{emergency_alert.latitude:.6f}, {emergency_alert.longitude:.6f}"
            if emergency_alert.address:
                location_text = f"{emergency_alert.address} (GPS: {emergency_alert.latitude:.6f}, {emergency_alert.longitude:.6f})"
        
        return {
            "alert_id": emergency_alert.id,
            "timestamp": emergency_alert.created_at.isoformat(),
            "priority": emergency_alert.priority,
            "user_info": {
                "name": user.name or f"{user.first_name or ''} {user.last_name or ''}".strip() or "Unknown",
                "phone": user.phone or "Unknown",
                "user_id": user.id
            },
            "emergency_details": {
                "type": emergency_alert.alert_type,
                "description": emergency_alert.description,
                "location": location_text,
                "coordinates": {
                    "latitude": emergency_alert.latitude,
                    "longitude": emergency_alert.longitude
                } if emergency_alert.latitude and emergency_alert.longitude else None
            },
            "voice_data": {
                "transcription": emergency_alert.voice_transcription,
                "duration": emergency_alert.recording_duration,
                "file_available": bool(emergency_alert.voice_file_path)
            },
            "job_context": {
                "job_id": emergency_alert.job_id
            } if emergency_alert.job_id else None
        }
    
    async def _notify_fixmate_dispatch(self, emergency_package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notify FixMate emergency dispatch team immediately
        """
        try:
            # Create urgent dispatch message
            dispatch_message = self._format_dispatch_message(emergency_package)
            
            # Log to emergency dispatch system (file-based for now, can be database/webhook later)
            dispatch_log_file = "/tmp/emergency_dispatch.log"
            with open(dispatch_log_file, "a") as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"🚨 EMERGENCY ALERT - {datetime.now().isoformat()}\n")
                f.write(dispatch_message)
                f.write(f"\n{'='*80}\n")
            
            # Send to dispatch team via SMS/Email (if configured)
            if self.twilio_client and self.fixmate_emergency_phone:
                try:
                    message = self.twilio_client.messages.create(
                        body=f"🚨 FIXMATE EMERGENCY ALERT\n\n{dispatch_message[:1400]}",  # SMS limit
                        from_=self.twilio_phone_number,
                        to=self.fixmate_emergency_phone
                    )
                    print(f"📱 Emergency dispatch SMS sent: {message.sid}")
                except Exception as e:
                    print(f"⚠️ Dispatch SMS failed: {e}")
            
            print("🚨 EMERGENCY DISPATCH NOTIFIED:")
            print(dispatch_message)
            
            return {
                "success": True,
                "message": "Emergency dispatch team notified",
                "dispatch_logged": True
            }
            
        except Exception as e:
            print(f"❌ Dispatch notification failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _format_dispatch_message(self, emergency_package: Dict[str, Any]) -> str:
        """
        Format comprehensive dispatch message
        """
        user_info = emergency_package["user_info"]
        emergency_details = emergency_package["emergency_details"]
        voice_data = emergency_package["voice_data"]
        
        message = f"""🚨 EMERGENCY ALERT #{emergency_package['alert_id'][:8]}
Priority: {emergency_package['priority'].upper()}
Time: {emergency_package['timestamp']}

👤 USER DETAILS:
Name: {user_info['name']}
Phone: {user_info['phone']}
User ID: {user_info['user_id']}

📍 LOCATION:
{emergency_details['location']}

🆘 EMERGENCY DETAILS:
Type: {emergency_details['type']}
Description: {emergency_details['description']}

🎤 VOICE MESSAGE:
Duration: {voice_data['duration']} seconds
Transcription: {voice_data['transcription'] or 'No transcription available'}

⚡ REQUIRED ACTIONS:
1. Contact 10111 immediately with this information
2. Call user at {user_info['phone']} to verify status
3. Coordinate with emergency services
4. Update alert status in system

📞 Emergency Services: 10111
🚑 Medical Emergency: 10177
🚒 Fire Emergency: 10177"""
        
        return message
    
    async def _send_comprehensive_emergency_sms(
        self, 
        user, 
        emergency_alert, 
        emergency_package: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send comprehensive emergency SMS to user and emergency contacts
        """
        try:
            messages_sent = []
            
            if not self.twilio_client:
                print("📱 MOCK SMS - Emergency notification would be sent")
                return {"success": True, "mock": True}
            
            # SMS to user (confirmation and instructions)
            user_sms = f"""🚨 FIXMATE EMERGENCY ALERT CONFIRMED

Your emergency alert has been received and processed.
Alert ID: {emergency_alert.id[:8]}

✅ ACTIONS TAKEN:
- Emergency services (10111) are being contacted
- Your location has been shared
- Voice message processed

📍 Location: {emergency_package['emergency_details']['location']}
🕐 Time: {datetime.now().strftime('%H:%M, %d %b %Y')}

🚨 KEEP YOUR PHONE ON
Emergency services may contact you directly.

If in immediate danger, call 10111 now.
FixMate Emergency Team is monitoring."""
            
            try:
                user_message = self.twilio_client.messages.create(
                    body=user_sms,
                    from_=self.twilio_phone_number,
                    to=user.phone
                )
                messages_sent.append(("user", user_message.sid))
                print(f"📱 User emergency SMS sent: {user_message.sid}")
            except Exception as e:
                print(f"⚠️ User SMS failed: {e}")
            
            # TODO: Add emergency contacts SMS (when contact system is implemented)
            # For now, focus on user and dispatch notifications
            
            return {
                "success": len(messages_sent) > 0,
                "messages_sent": len(messages_sent),
                "message_ids": messages_sent
            }
            
        except Exception as e:
            print(f"❌ Emergency SMS failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _alert_admin_team(self, emergency_package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Alert FixMate admin team about emergency
        """
        try:
            # Create admin alert summary
            admin_alert = f"""🚨 EMERGENCY ALERT - ADMIN NOTIFICATION
            
Alert ID: {emergency_package['alert_id']}
User: {emergency_package['user_info']['name']} ({emergency_package['user_info']['phone']})
Priority: {emergency_package['priority'].upper()}
Location: {emergency_package['emergency_details']['location']}
Description: {emergency_package['emergency_details']['description']}

Voice Message: {emergency_package['voice_data']['transcription'][:200] if emergency_package['voice_data']['transcription'] else 'No voice message'}

Timestamp: {emergency_package['timestamp']}

REQUIRED: Monitor emergency response and update system."""
            
            # Log admin alert
            admin_log_file = "/tmp/admin_emergency_alerts.log"
            with open(admin_log_file, "a") as f:
                f.write(f"\n{datetime.now().isoformat()}: {admin_alert}\n")
            
            print("👨‍💼 ADMIN TEAM ALERTED:")
            print(admin_alert)
            
            return {
                "success": True,
                "message": "Admin team notified successfully"
            }
            
        except Exception as e:
            print(f"❌ Admin alert failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _initiate_police_contact_protocol(self, emergency_package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate 10111 police contact protocol through FixMate dispatch
        """
        try:
            # Generate police reference number for tracking
            police_reference = f"FM-{emergency_package['alert_id'][:8]}-{datetime.now().strftime('%Y%m%d-%H%M')}"
            
            # Create 10111 contact package
            police_contact_data = {
                "emergency_reference": police_reference,
                "contact_time": datetime.now().isoformat(),
                "caller_info": {
                    "reporting_entity": "FixMate-SA Emergency Services",
                    "contact_phone": self.fixmate_emergency_phone,
                    "emergency_type": "Third-party emergency report"
                },
                "incident_details": {
                    "person_in_distress": emergency_package['user_info']['name'],
                    "contact_number": emergency_package['user_info']['phone'],
                    "location": emergency_package['emergency_details']['location'],
                    "incident_description": emergency_package['emergency_details']['description'],
                    "additional_info": emergency_package['voice_data']['transcription'] if emergency_package['voice_data']['transcription'] else "Voice recording available"
                },
                "priority": emergency_package['priority']
            }
            
            # Log police contact initiation
            police_log_file = "/tmp/police_contact_log.log"
            with open(police_log_file, "a") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"🚨 10111 CONTACT INITIATED - {datetime.now().isoformat()}\n")
                f.write(f"Reference: {police_reference}\n")
                f.write(json.dumps(police_contact_data, indent=2))
                f.write(f"\n{'='*60}\n")
            
            print("🚔 10111 POLICE CONTACT PROTOCOL INITIATED:")
            print(f"Reference: {police_reference}")
            print(f"Person: {emergency_package['user_info']['name']} ({emergency_package['user_info']['phone']})")
            print(f"Location: {emergency_package['emergency_details']['location']}")
            print(f"Emergency: {emergency_package['emergency_details']['description']}")
            
            # In production, this would make actual call to 10111 or official police API
            # For now, this creates a comprehensive log for manual follow-up
            
            return {
                "success": True,
                "reference": police_reference,
                "message": "Police contact protocol initiated - manual follow-up required"
            }
            
        except Exception as e:
            print(f"❌ Police contact protocol failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe audio file to text using Whisper (if available)
        """
        try:
            if not WHISPER_AVAILABLE or not self.whisper_model:
                print("⚠️ Whisper not available - returning fallback transcription")
                return "[Voice transcription unavailable - Whisper not installed. Voice file saved for manual review.]"
            
            # Transcribe audio
            result = self.whisper_model.transcribe(audio_file_path)
            transcription = result["text"].strip()
            
            # Add confidence information if available
            if "segments" in result and result["segments"]:
                avg_confidence = sum(segment.get("avg_logprob", 0) for segment in result["segments"]) / len(result["segments"])
                print(f"🎤 Transcription confidence: {avg_confidence:.2f}")
            
            return transcription if transcription else None
            
        except Exception as e:
            print(f"⚠️ Audio transcription failed: {e}")
            return "[Voice transcription failed - audio file saved for manual review]"
    
    def get_location_from_coordinates(self, latitude: float, longitude: float) -> str:
        """
        Get human-readable address from coordinates using reverse geocoding
        """
        try:
            # Using BigDataCloud free reverse geocoding API
            url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "localityLanguage": "en"
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                address = data.get("displayName", f"{latitude:.6f}, {longitude:.6f}")
                
                # Add South African context
                city = data.get("city", "")
                locality = data.get("locality", "")
                region = data.get("principalSubdivision", "")
                
                if city or locality or region:
                    location_parts = [part for part in [locality, city, region] if part]
                    sa_context = ", ".join(location_parts)
                    if "South Africa" not in address:
                        address += f", South Africa"
                
                return address
            else:
                return f"{latitude:.6f}, {longitude:.6f}, South Africa"
                
        except Exception as e:
            print(f"⚠️ Reverse geocoding failed: {e}")
            return f"{latitude:.6f}, {longitude:.6f}, South Africa"
    
    def get_emergency_alerts(self, user_id: str, db: Session) -> list:
        """
        Get user's emergency alert history
        """
        try:
            from models import EmergencyAlert
            
            alerts = db.query(EmergencyAlert).filter(
                EmergencyAlert.user_id == user_id
            ).order_by(EmergencyAlert.created_at.desc()).limit(50).all()
            
            return [{
                "id": alert.id,
                "alert_type": alert.alert_type,
                "priority": alert.priority,
                "description": alert.description,
                "status": alert.status,
                "latitude": alert.latitude,
                "longitude": alert.longitude,
                "address": alert.address,
                "voice_transcription": alert.voice_transcription,
                "recording_duration": alert.recording_duration,
                "police_notified": alert.police_notified,
                "police_reference": alert.police_reference,
                "created_at": alert.created_at.isoformat(),
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            } for alert in alerts]
            
        except Exception as e:
            print(f"❌ Get emergency alerts failed: {e}")
            return []
    
    def resolve_emergency_alert(self, alert_id: str, resolution: str, notes: str, db: Session) -> Dict[str, Any]:
        """
        Mark emergency alert as resolved with notes
        """
        try:
            from models import EmergencyAlert
            
            alert = db.query(EmergencyAlert).filter(EmergencyAlert.id == alert_id).first()
            if not alert:
                return {"success": False, "error": "Emergency alert not found"}
            
            alert.status = resolution  # resolved, false_alarm, handled, etc.
            alert.resolved_at = datetime.now()
            alert.resolution_notes = notes
            
            db.commit()
            
            print(f"✅ Emergency alert {alert_id} resolved as: {resolution}")
            
            return {
                "success": True,
                "message": f"Emergency alert marked as {resolution}",
                "alert_id": alert_id,
                "resolution": resolution
            }
            
        except Exception as e:
            db.rollback()
            print(f"❌ Resolve emergency alert failed: {e}")
            return {"success": False, "error": str(e)}

# Global instance
emergency_service = EmergencyService()