import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from models import User, Fixer, Job, DataInsight
from .whatsapp_service import whatsapp_service
from .ai_service import ai_service
from .sms_service import sms_service

class ConversationService:
    def __init__(self):
        self.states = {
            'AWAITING_SERVICE_REQUEST': 'awaiting_service_request',
            'AWAITING_NAME': 'awaiting_name',
            'AWAITING_LOCATION': 'awaiting_location',
            'AWAITING_CONTACT_NUMBER': 'awaiting_contact_number',
            'AWAITING_TERMS_APPROVAL': 'awaiting_terms_approval',
            'AWAITING_RATING': 'awaiting_rating',
            'AWAITING_RATING_COMMENT': 'awaiting_rating_comment'
        }
    
    def get_or_create_user(self, phone_number: str, db: Session) -> User:
        """Get or create user from WhatsApp phone number."""
        # Ensure proper WhatsApp format
        if not phone_number.startswith("whatsapp:"):
            phone_number = f"whatsapp:{phone_number}"
        
        user = db.query(User).filter(User.phone == phone_number).first()
        if not user:
            # Create new user with default values
            user = User(
                phone=phone_number,
                first_name="Unknown",
                last_name="User",
                id_number="",
                town="Unknown"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
    
    def set_user_state(self, user: User, new_state: str, data: Dict[str, Any] = None, db: Session = None):
        """Set user conversation state with optional data."""
        cached_data = json.loads(user.service_request_cache) if user.service_request_cache else {}
        
        if data:
            cached_data.update(data)
        
        user.conversation_state = new_state
        user.service_request_cache = json.dumps(cached_data)
        
        if db:
            db.commit()
        
        print(f"State for {user.phone} set to {new_state} with data: {cached_data}")
    
    def get_user_cache(self, user: User) -> Dict[str, Any]:
        """Get cached conversation data for user."""
        if user.service_request_cache:
            return json.loads(user.service_request_cache)
        return {}
    
    def clear_user_state(self, user: User, db: Session = None):
        """Clear user conversation state."""
        user.conversation_state = None
        user.service_request_cache = None
        
        if db:
            db.commit()
        
        print(f"State for {user.phone} cleared.")
    
    def find_fixer_for_job(self, job: Job, db: Session) -> Optional[Fixer]:
        """Find the best fixer for a job using AI classification and scoring."""
        # Classify service request
        skill_needed = ai_service.classify_service_request(job.description)
        
        # Get eligible fixers
        eligible_fixers = db.query(Fixer).filter(
            Fixer.is_active == True,
            Fixer.vetting_status == 'approved',
            Fixer.skills.ilike(f'%{skill_needed}%')
        ).all()
        
        if not eligible_fixers:
            # Fallback to general fixers
            eligible_fixers = db.query(Fixer).filter(
                Fixer.is_active == True,
                Fixer.vetting_status == 'approved',
                Fixer.skills.ilike('%general%')
            ).all()
        
        if not eligible_fixers:
            return None
        
        # Score fixers based on multiple criteria
        scored_fixers = []
        for fixer in eligible_fixers:
            score = 0
            
            # Location proximity (if both job and fixer have coordinates)
            if (fixer.current_latitude and fixer.current_longitude and 
                job.latitude and job.longitude):
                from geopy.distance import geodesic
                client_location = (job.latitude, job.longitude)
                fixer_location = (fixer.current_latitude, fixer.current_longitude)
                distance_km = geodesic(client_location, fixer_location).km
                proximity_score = max(0, 50 - (distance_km * 2))
                score += proximity_score
            
            # Rating score (30% weight)
            avg_rating = db.query(db.func.avg(Job.rating)).filter(
                Job.fixer_id == fixer.id,
                Job.rating != None
            ).scalar() or 3.5
            score += (avg_rating / 5) * 30
            
            # Fairness score (time since last assignment)
            if fixer.last_assigned_at:
                hours_since_last = (datetime.now() - fixer.last_assigned_at).total_seconds() / 3600
                score += min(20, hours_since_last)
            else:
                score += 20  # New fixer bonus
            
            scored_fixers.append({'fixer': fixer, 'score': score})
        
        if not scored_fixers:
            return None
        
        # Select best fixer
        best_fixer_data = max(scored_fixers, key=lambda x: x['score'])
        best_fixer = best_fixer_data['fixer']
        
        # Update assignment time
        best_fixer.last_assigned_at = datetime.now()
        db.commit()
        
        return best_fixer
    
    def create_job_from_cache(self, user: User, job_data: Dict[str, Any], db: Session) -> Tuple[str, bool]:
        """Create job from cached conversation data."""
        # Create job object
        job = Job(
            user_id=user.id,
            service=ai_service.classify_service_request(job_data.get('service', '')),
            description=job_data.get('service', ''),
            location=job_data.get('area', 'Unknown'),
            client_contact_number=job_data.get('contact', ''),
            latitude=float(job_data.get('latitude', 0)) if job_data.get('latitude') else None,
            longitude=float(job_data.get('longitude', 0)) if job_data.get('longitude') else None,
            area=job_data.get('area', 'Unknown'),
            status='pending'
        )
        
        # Find and assign fixer
        matched_fixer = self.find_fixer_for_job(job, db)
        
        if matched_fixer:
            job.fixer_id = matched_fixer.id
            job.status = 'assigned'
            
            # Send notification to fixer
            fixer_message = f"""
🔧 New FixMate-SA Job Alert!

📋 Job #{job.id}
🔨 Service: {job.description}
📍 Area: {job.area}
📞 Client Contact: {job.client_contact_number}

Please log in to your Fixer Portal to accept this job.
            """.strip()
            
            whatsapp_service.send_whatsapp_message(
                matched_fixer.phone,
                fixer_message
            )
        else:
            job.status = 'unassigned'
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return job.id, matched_fixer is not None
    
    def process_message(self, from_number: str, message_content: str, message_type: str, 
                       location_data: Dict[str, Any] = None, db: Session = None) -> str:
        """Process WhatsApp message and return response."""
        user = self.get_or_create_user(from_number, db)
        current_state = user.conversation_state
        
        # Handle different message types
        if message_type == 'location' and current_state == self.states['AWAITING_LOCATION']:
            return self._handle_location_message(user, location_data, db)
        
        if message_type == 'text' and message_content:
            return self._handle_text_message(user, message_content, current_state, db)
        
        if message_type == 'audio' and message_content:
            return self._handle_audio_message(user, message_content, current_state, db)
        
        return self._get_help_message(user)
    
    def _handle_location_text(self, user: User, message: str, db: Session) -> str:
        """Handle location provided as text."""
        location_text = message.strip()
        
        user_name = user.first_name if user.first_name != "Unknown" else ""
        greeting = f"Thanks, {user_name}! " if user_name else "Thanks! "
        
        response = f"{greeting}I've got your location. Lastly, what's the best contact number for the fixer to use?"
        
        self.set_user_state(user, self.states['AWAITING_CONTACT_NUMBER'], {
            'area': location_text,
            'location_text': location_text
        }, db)
        
        return response

    def _handle_location_message(self, user: User, location_data: Dict[str, Any], db: Session) -> str:
        """Handle location sharing."""
        latitude = location_data.get('latitude')
        longitude = location_data.get('longitude')
        
        if not latitude or not longitude:
            return "Could not get your location. Please try sharing it again."
        
        # Get area from coordinates
        area = whatsapp_service.get_location_from_coords(latitude, longitude)
        
        user_name = user.first_name if user.first_name != "Unknown" else ""
        greeting = f"Thanks, {user_name}! " if user_name else "Thanks! "
        
        response = f"{greeting}I've got your location in {area}. What's the best contact number for the fixer to reach you?"
        
        self.set_user_state(user, self.states['AWAITING_CONTACT_NUMBER'], {
            'latitude': str(latitude),
            'longitude': str(longitude),
            'area': area
        }, db)
        
        return response
    
    def _handle_text_message(self, user: User, message: str, current_state: str, db: Session) -> str:
        """Handle text message based on conversation state."""
        message = message.strip()
        
        # Post-job states (rating & feedback)
        if current_state == self.states['AWAITING_RATING']:
            return self._handle_rating_message(user, message, db)
        
        elif current_state == self.states['AWAITING_RATING_COMMENT']:
            return self._handle_rating_comment(user, message, db)
        
        # Job request states
        elif current_state == self.states['AWAITING_SERVICE_REQUEST']:
            return self._handle_service_request(user, message, db)
        
        elif current_state == self.states['AWAITING_NAME']:
            return self._handle_name_message(user, message, db)
        
        elif current_state == self.states['AWAITING_LOCATION']:
            return self._handle_location_text(user, message, db)
        
        elif current_state == self.states['AWAITING_CONTACT_NUMBER']:
            return self._handle_contact_number(user, message, db)
        
        elif current_state == self.states['AWAITING_TERMS_APPROVAL']:
            return self._handle_terms_approval(user, message, db)
        
        else:
            # Default/new conversation
            return self._handle_initial_message(user, message, db)
    
    def _handle_audio_message(self, user: User, transcribed_text: str, current_state: str, db: Session) -> str:
        """Handle transcribed audio message."""
        if not transcribed_text or "error" in transcribed_text.lower():
            return "I couldn't understand your voice message. Please try again or send a text message."
        
        # Process transcribed audio as text
        return self._handle_text_message(user, transcribed_text, current_state, db)
    
    def _handle_rating_message(self, user: User, message: str, db: Session) -> str:
        """Handle rating message."""
        cache_data = self.get_user_cache(user)
        job_id = cache_data.get('job_id')
        
        if not job_id:
            self.clear_user_state(user, db)
            return "Sorry, I couldn't find the job to rate. Please try again."
        
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            self.clear_user_state(user, db)
            return "Sorry, I couldn't find the job to rate."
        
        if message.isdigit() and 1 <= int(message) <= 5:
            job.rating = int(message)
            db.commit()
            
            response = "Thank you for the rating! Could you please share a brief comment about your experience?"
            self.set_user_state(user, self.states['AWAITING_RATING_COMMENT'], 
                               {'job_id': job_id}, db)
            return response
        else:
            return "Please provide a rating from 1 (poor) to 5 (excellent)."
    
    def _handle_rating_comment(self, user: User, message: str, db: Session) -> str:
        """Handle rating comment."""
        cache_data = self.get_user_cache(user)
        job_id = cache_data.get('job_id')
        
        if not job_id:
            self.clear_user_state(user, db)
            return "Thank you for your feedback!"
        
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.rating_comment = message
            job.sentiment = ai_service.analyze_sentiment(message)
            db.commit()
        
        self.clear_user_state(user, db)
        return "Your feedback has been recorded. We appreciate you helping us improve FixMate-SA!"
    
    def _handle_service_request(self, user: User, message: str, db: Session) -> str:
        """Handle service request message."""
        response = "Got it. What's your name?"
        self.set_user_state(user, self.states['AWAITING_NAME'], {'service': message}, db)
        return response
    
    def _handle_name_message(self, user: User, message: str, db: Session) -> str:
        """Handle name message."""
        # Update user name
        names = message.strip().split()
        if len(names) >= 2:
            user.first_name = names[0]
            user.last_name = " ".join(names[1:])
        else:
            user.first_name = names[0] if names else "Unknown"
            user.last_name = "User"
        
        db.commit()
        
        response = f'Thanks, {user.first_name}. To help us find the nearest fixer, please share your location address: "Town/Village/township name and house number."'
        
        self.set_user_state(user, self.states['AWAITING_LOCATION'], db=db)
        return response
    
    def _handle_contact_number(self, user: User, message: str, db: Session) -> str:
        """Handle contact number message."""
        if any(char.isdigit() for char in message) and len(message) >= 10:
            response = """Great! We have all the details.

By proceeding, you agree to the FixMate-SA Terms of Service.
View here: https://fixmate-sa-app-a448c751e1d2.herokuapp.com/terms

Reply YES to confirm and dispatch a fixer."""
            
            self.set_user_state(user, self.states['AWAITING_TERMS_APPROVAL'], 
                               {'contact': message}, db)
            return response
        else:
            return "That doesn't seem to be a valid phone number. Please try again."
    
    def _handle_terms_approval(self, user: User, message: str, db: Session) -> str:
        """Handle terms approval message."""
        if 'yes' in message.lower():
            job_data = self.get_user_cache(user)
            job_id, fixer_found = self.create_job_from_cache(user, job_data, db)
            
            if fixer_found:
                response = f"""Perfect! We have logged your request (Job #{job_id}) and have notified a nearby fixer. 

They will contact you shortly."""
            else:
                response = f"""Thank you. We have logged your request (Job #{job_id}), but all our fixers for this service are currently busy. 

We will notify you as soon as one becomes available."""
            
            self.clear_user_state(user, db)
            return response
        else:
            self.clear_user_state(user, db)
            return "Job request cancelled. Please say 'hello' to start a new request."
    
    def _handle_initial_message(self, user: User, message: str, db: Session) -> str:
        """Handle initial/greeting message."""
        self.clear_user_state(user, db)
        
        first_name = user.first_name if user.first_name != "Unknown" else ""
        greeting = f"Welcome back to FixMate-SA!" if first_name else "Welcome back to FixMate-SA!"
        
        greetings = ['hi', 'hello', 'hallo', 'dumela', 'sawubona', 'molo', 'avuxeni', 'ndaa']
        
        if message.lower() in greetings:
            response = f"""{greeting} To request a service, please describe what you need (e.g., 'Leaking pipe', or any service you may think of)."""
            
            self.set_user_state(user, self.states['AWAITING_SERVICE_REQUEST'], db=db)
            return response
        else:
            # Treat as service request
            response = f"""{greeting} To request a service, please describe what you need (e.g., 'Leaking pipe', or any service you may think of)."""
            
            self.set_user_state(user, self.states['AWAITING_SERVICE_REQUEST'], db=db)
            return response
    
    def _get_help_message(self, user: User) -> str:
        """Get help message for user."""
        return """Welcome to FixMate-SA! 🔧

To request a service:
1. Describe what you need (e.g., "leaking tap")
2. Or send a voice note
3. Or say "hello" to start

We support all South African languages!"""

# Global instance
conversation_service = ConversationService()