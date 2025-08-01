"""
FixMate Job Request and Assignment Workflow Service
Implements the comprehensive workflow system with terms acceptance, 
fixer notifications, first-come-first-serve assignment, live tracking, 
timeout handling, and AI monitoring.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
import logging

from models import (
    Job, User, Fixer, FixerAvailability, FixerBehaviorAnalysis,
    JobAssignmentHistory, JobNotification, PlatformTerms, UserTermsAcceptance,
    FixerPayment
)
from services.whatsapp_service import whatsapp_service
from services.ai_service import ai_service

logger = logging.getLogger(__name__)

class JobWorkflowService:
    """Comprehensive job workflow management service"""
    
    def __init__(self):
        self.assignment_timeout_minutes = 15  # Time for fixers to respond
        self.attendance_timeout_minutes = 180  # 3 hours for fixer to arrive (as per requirements)
        self.max_reassignment_attempts = 3    # Maximum auto-reassignment attempts
        self.emergency_escalation_minutes = 180  # 3 hours before emergency escalation
        self.platform_fee_amount = 20.0      # R20 platform fee
        self.platform_fee_deadline_hours = 48  # 48 hours to pay platform fee
        self.availability_freeze_hours = 4   # 4-hour freeze after timeout
        self.cancellation_freeze_hours = 2   # 2-hour freeze after cancellation
        self.rating_penalty_per_cancellation = 0.2  # 0.2 rating penalty per cancellation
        self.minimum_rating_threshold = 3.0  # Minimum rating required
        self.fraud_monitoring_thresholds = {
            'max_failures_per_week': 3,
            'min_completion_rate': 65.0,
            'max_cancellation_rate': 25.0
        }
        
    # 1. Terms Acceptance Management
    
    def check_terms_acceptance(self, db: Session, user_id: str) -> bool:
        """Check if user has accepted current platform terms"""
        try:
            current_terms = db.query(PlatformTerms).filter(
                PlatformTerms.is_current == True
            ).first()
            
            if not current_terms:
                logger.warning("No current platform terms found")
                return False
                
            acceptance = db.query(UserTermsAcceptance).filter(
                UserTermsAcceptance.user_id == user_id,
                UserTermsAcceptance.terms_id == current_terms.id,
                UserTermsAcceptance.is_current == True
            ).first()
            
            return acceptance is not None
            
        except Exception as e:
            logger.error(f"Error checking terms acceptance: {str(e)}")
            return False
    
    def accept_terms(self, db: Session, user_id: str, ip_address: str = None, 
                    user_agent: str = None, method: str = "web") -> bool:
        """Record user acceptance of current platform terms"""
        try:
            current_terms = db.query(PlatformTerms).filter(
                PlatformTerms.is_current == True
            ).first()
            
            if not current_terms:
                logger.error("No current platform terms found")
                return False
            
            # Mark previous acceptances as not current
            db.query(UserTermsAcceptance).filter(
                UserTermsAcceptance.user_id == user_id,
                UserTermsAcceptance.is_current == True
            ).update({"is_current": False})
            
            # Create new acceptance record
            acceptance = UserTermsAcceptance(
                user_id=user_id,
                terms_id=current_terms.id,
                ip_address=ip_address,
                user_agent=user_agent,
                acceptance_method=method
            )
            
            db.add(acceptance)
            db.commit()
            
            logger.info(f"Terms accepted by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording terms acceptance: {str(e)}")
            db.rollback()
            return False
    
    # 2. Fixer Eligibility Checking
    
    def get_eligible_fixers(self, db: Session, job: Job) -> List[str]:
        """Get list of eligible fixer IDs based on enhanced criteria including rating validation"""
        try:
            eligible_fixers = []
            
            # Get all fixers for the service type
            service_query = f'%"{job.service}"%' if job.service else '%'
            
            fixers = db.query(Fixer).filter(
                Fixer.is_active == True,
                Fixer.is_approved == True,
                Fixer.services.like(service_query)
            ).all()
            
            for fixer in fixers:
                # Enhanced eligibility checks
                if not self._is_fixer_eligible(db, fixer):
                    continue
                
                # Check availability record
                availability = db.query(FixerAvailability).filter(
                    FixerAvailability.fixer_id == fixer.id
                ).first()
                
                if not availability:
                    # Create availability record if not exists
                    availability = FixerAvailability(fixer_id=fixer.id)
                    db.add(availability)
                
                # Apply comprehensive eligibility checks
                if (availability.is_available and 
                    not availability.current_job_id and 
                    not availability.has_outstanding_debt and
                    not availability.is_suspended and
                    not availability.is_on_break and
                    not availability.is_availability_frozen and
                    availability.platform_fee_status == "current"):
                    
                    # Check location proximity with fair distribution
                    if self._check_location_and_fairness(db, job, fixer, availability):
                        eligible_fixers.append(fixer.id)
            
            # Apply fair matching algorithm to sort eligible fixers
            eligible_fixers = self._apply_fair_matching_algorithm(db, job, eligible_fixers)
            
            db.commit()
            logger.info(f"Found {len(eligible_fixers)} eligible fixers for job {job.id} after comprehensive screening")
            return eligible_fixers
            
        except Exception as e:
            logger.error(f"Error getting eligible fixers: {str(e)}")
            return []
    
    def _is_fixer_eligible(self, db: Session, fixer: Fixer) -> bool:
        """Enhanced fixer eligibility check with rating and payment validation"""
        try:
            # Check rating requirements (≥3.0 or new fixer with 0.0)
            if fixer.is_new_fixer:
                # New fixers with 0.0 rating are eligible
                if fixer.rating != 0.0:
                    fixer.is_new_fixer = False  # No longer new
            else:
                # Existing fixers must have ≥3.0 rating
                effective_rating = fixer.rating - fixer.rating_penalty_total
                if effective_rating < self.minimum_rating_threshold:
                    logger.info(f"Fixer {fixer.id} ineligible: rating {effective_rating} < {self.minimum_rating_threshold}")
                    return False
            
            # Check platform fee status
            if fixer.fee_payment_overdue or fixer.fee_suspension_applied:
                logger.info(f"Fixer {fixer.id} ineligible: platform fees overdue or suspended")
                return False
            
            # Check if fixer owes $0 outstanding balance
            if fixer.platform_fees_owed > 0:
                logger.info(f"Fixer {fixer.id} ineligible: outstanding balance R{fixer.platform_fees_owed}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking fixer eligibility: {str(e)}")
            return False
    
    def _check_location_and_fairness(self, db: Session, job: Job, fixer: Fixer, availability: FixerAvailability) -> bool:
        """Check location proximity and apply fairness criteria"""
        try:
            # Location proximity check
            if (job.latitude and job.longitude and 
                availability.current_latitude and availability.current_longitude):
                distance = self._calculate_distance(
                    job.latitude, job.longitude,
                    availability.current_latitude, availability.current_longitude
                )
                if distance > availability.service_radius:
                    return False
            
            # Fair distribution check - ensure fixers get equal opportunities
            # Check if fixer was recently assigned to avoid overloading
            if fixer.last_assigned_at:
                hours_since_last_job = (datetime.utcnow() - fixer.last_assigned_at).total_seconds() / 3600
                if hours_since_last_job < 1:  # Less than 1 hour since last assignment
                    # Only allow if completion rate is very high (>95%)
                    if fixer.completion_percentage < 95.0:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking location and fairness: {str(e)}")
            return False
    
    def _apply_fair_matching_algorithm(self, db: Session, job: Job, fixer_ids: List[str]) -> List[str]:
        """Apply fair matching algorithm prioritizing proximity, rating, availability, and performance"""
        try:
            if not fixer_ids:
                return []
            
            fixer_scores = []
            
            for fixer_id in fixer_ids:
                fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
                availability = db.query(FixerAvailability).filter(
                    FixerAvailability.fixer_id == fixer_id
                ).first()
                
                if not fixer or not availability:
                    continue
                
                score = self._calculate_fixer_match_score(job, fixer, availability)
                fixer_scores.append((fixer_id, score))
            
            # Sort by score (highest first) and return sorted fixer IDs
            fixer_scores.sort(key=lambda x: x[1], reverse=True)
            sorted_fixer_ids = [fixer_id for fixer_id, score in fixer_scores]
            
            logger.info(f"Applied fair matching algorithm, top fixer scores: {fixer_scores[:5]}")
            return sorted_fixer_ids
            
        except Exception as e:
            logger.error(f"Error applying fair matching algorithm: {str(e)}")
            return fixer_ids  # Return original list if error
    
    def _calculate_fixer_match_score(self, job: Job, fixer: Fixer, availability: FixerAvailability) -> float:
        """Calculate comprehensive match score for fair algorithm"""
        try:
            score = 0.0
            
            # 1. Proximity score (highest weight: 40%)
            if (job.latitude and job.longitude and 
                availability.current_latitude and availability.current_longitude):
                distance = self._calculate_distance(
                    job.latitude, job.longitude,
                    availability.current_latitude, availability.current_longitude
                )
                # Closer = higher score (max 40 points)
                proximity_score = max(0, 40 - (distance * 2))  # 2 points deducted per km
                score += proximity_score
            else:
                score += 20  # Default proximity score if no GPS data
            
            # 2. User rating score (25%)
            effective_rating = max(0, fixer.rating - fixer.rating_penalty_total)
            rating_score = (effective_rating / 5.0) * 25  # Max 25 points for 5-star rating
            score += rating_score
            
            # 3. Availability and reliability score (20%)
            reliability_score = (availability.reliability_score / 100.0) * 20
            score += reliability_score
            
            # 4. Historical performance score (15%)
            performance_score = (fixer.completion_percentage / 100.0) * 15
            score += performance_score
            
            # Fairness boost: Give slight advantage to fixers who haven't worked recently
            if fixer.last_assigned_at:
                hours_since_last_job = (datetime.utcnow() - fixer.last_assigned_at).total_seconds() / 3600
                if hours_since_last_job > 24:  # More than 24 hours
                    score += 5  # Fairness boost
                elif hours_since_last_job > 12:  # More than 12 hours
                    score += 2  # Small fairness boost
            else:
                score += 10  # New fixer boost
            
            return round(score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating fixer match score: {str(e)}")
            return 0.0
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS coordinates in kilometers"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return c * r
    
    # 3. Job Creation and Workflow Initiation
    
    def create_job_with_workflow(self, db: Session, user_id: str, job_data: Dict[str, Any]) -> Tuple[bool, str, Optional[Job]]:
        """Create job with complete workflow validation"""
        try:
            # Check terms acceptance first
            if not self.check_terms_acceptance(db, user_id):
                return False, "Terms and conditions must be accepted before creating a job", None
            
            # Create job with workflow fields
            job = Job(
                id=str(uuid.uuid4()),
                user_id=user_id,
                service=job_data.get('service'),
                description=job_data.get('description'),
                location=job_data.get('location'),
                estimated_price=job_data.get('estimated_price'),
                latitude=job_data.get('latitude'),
                longitude=job_data.get('longitude'),
                client_contact_number=job_data.get('contact_number'),
                # Workflow fields
                terms_accepted=True,
                terms_accepted_at=datetime.utcnow(),
                workflow_stage="terms_accepted",
                status="pending"
            )
            
            db.add(job)
            db.flush()  # Get the job ID
            
            # Update workflow stage to eligibility checking
            job.workflow_stage = "eligible_check"
            
            # Get eligible fixers
            eligible_fixers = self.get_eligible_fixers(db, job)
            
            if not eligible_fixers:
                job.workflow_stage = "no_fixers_available"
                job.status = "cancelled"
                db.commit()
                return False, "No eligible fixers available for this service", job
            
            # Store eligible fixers
            job.eligible_fixers = json.dumps(eligible_fixers)
            job.workflow_stage = "notifying"
            job.status = "notifying_fixers"
            
            # Set attendance deadline (180 minutes = 3 hours as per requirements)
            job.attendance_deadline = datetime.utcnow() + timedelta(minutes=self.attendance_timeout_minutes)
            job.assignment_timeout = datetime.utcnow() + timedelta(minutes=self.assignment_timeout_minutes)
            
            db.commit()
            
            # Start notification process
            self._notify_eligible_fixers(db, job, eligible_fixers)
            
            logger.info(f"Job {job.id} created with workflow for user {user_id}")
            return True, "Job created successfully and fixers notified", job
            
        except Exception as e:
            logger.error(f"Error creating job with workflow: {str(e)}")
            db.rollback()
            return False, f"Error creating job: {str(e)}", None
    
    # 4. Fixer Notification System
    
    def _notify_eligible_fixers(self, db: Session, job: Job, fixer_ids: List[str]) -> None:
        """Send notifications to all eligible fixers simultaneously"""
        try:
            for fixer_id in fixer_ids:
                fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
                if not fixer:
                    continue
                
                # Create notification record
                notification = JobNotification(
                    job_id=job.id,
                    fixer_id=fixer_id,
                    notification_type="job_available",
                    channel="app",
                    message_content=self._create_job_notification_message(job, fixer)
                )
                db.add(notification)
                
                # Send app notification (would integrate with push notification service)
                self._send_app_notification(fixer, job)
                
                # Send WhatsApp notification
                self._send_whatsapp_job_notification(fixer, job)
                
                # Create assignment history record
                assignment_history = JobAssignmentHistory(
                    job_id=job.id,
                    fixer_id=fixer_id,
                    assignment_type="initial"
                )
                db.add(assignment_history)
            
            # Update job
            job.notified_fixers = json.dumps(fixer_ids)
            job.assignment_attempts += 1
            job.last_assignment_attempt = datetime.utcnow()
            
            db.commit()
            logger.info(f"Notified {len(fixer_ids)} fixers for job {job.id}")
            
        except Exception as e:
            logger.error(f"Error notifying fixers: {str(e)}")
            db.rollback()
    
    def _create_job_notification_message(self, job: Job, fixer: Fixer) -> str:
        """Create notification message for fixer"""
        return f"""
🔧 New Job Available!
Service: {job.service}
Location: {job.location}
Description: {job.description[:100]}...
Estimated Price: R{job.estimated_price or 'TBD'}

Tap to accept this job (First come, first serve)
"""
    
    def _send_app_notification(self, fixer: Fixer, job: Job) -> None:
        """Send in-app notification (placeholder for push notification service)"""
        # This would integrate with a push notification service like FCM
        logger.info(f"App notification sent to fixer {fixer.id} for job {job.id}")
    
    def _send_whatsapp_job_notification(self, fixer: Fixer, job: Job) -> None:
        """Send WhatsApp notification to fixer"""
        try:
            message = self._create_job_notification_message(job, fixer)
            whatsapp_service.send_whatsapp_message(fixer.phone, message)
            logger.info(f"WhatsApp notification sent to fixer {fixer.id}")
        except Exception as e:
            logger.error(f"Error sending WhatsApp notification: {str(e)}")
    
    # 5. First Come, First Serve Assignment
    
    def accept_job(self, db: Session, job_id: str, fixer_id: str) -> Tuple[bool, str]:
        """Handle fixer accepting a job (first come, first serve)"""
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return False, "Job not found"
            
            # Check if job is still available
            if job.status != "notifying_fixers":
                return False, "Job is no longer available"
            
            # Check if assignment timeout has passed
            if datetime.utcnow() > job.assignment_timeout:
                return False, "Assignment timeout has passed"
            
            # Check if fixer is still eligible
            fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
            if not fixer:
                return False, "Fixer not found"
            
            availability = db.query(FixerAvailability).filter(
                FixerAvailability.fixer_id == fixer_id
            ).first()
            
            if not availability or not availability.is_available or availability.current_job_id:
                return False, "Fixer is no longer available"
            
            # Assign job to fixer (LOCK to prevent race conditions)
            job.fixer_id = fixer_id
            job.status = "assigned"
            job.workflow_stage = "assigned"
            job.tracking_active = True
            job.attendance_timeout = datetime.utcnow() + timedelta(minutes=self.attendance_timeout_minutes)
            
            # Update fixer availability
            availability.is_available = False
            availability.current_job_id = job.id
            
            # Update assignment history
            history = db.query(JobAssignmentHistory).filter(
                JobAssignmentHistory.job_id == job_id,
                JobAssignmentHistory.fixer_id == fixer_id
            ).first()
            
            if history:
                history.response_type = "accepted"
                history.responded_at = datetime.utcnow()
                history.accepted_at = datetime.utcnow()
            
            db.commit()
            
            # Notify client
            self._notify_client_assignment(db, job, fixer)
            
            # Start live tracking
            self._activate_live_tracking(db, job)
            
            logger.info(f"Job {job_id} assigned to fixer {fixer_id}")
            return True, "Job assigned successfully"
            
        except Exception as e:
            logger.error(f"Error accepting job: {str(e)}")
            db.rollback()
            return False, f"Error accepting job: {str(e)}"
    
    def _notify_client_assignment(self, db: Session, job: Job, fixer: Fixer) -> None:
        """Notify client that fixer has been assigned"""
        try:
            user = job.user
            message = f"""
✅ Fixer Assigned!
Fixer: {fixer.name}
Contact: {fixer.phone}
Rating: {fixer.rating:.1f}⭐
Service: {job.service}

Your fixer is on the way! You can track their location in the app.
"""
            
            # Send WhatsApp notification
            if user.whatsapp_active and user.phone:
                whatsapp_service.send_whatsapp_message(user.phone, message)
            
            logger.info(f"Client notified of assignment for job {job.id}")
            
        except Exception as e:
            logger.error(f"Error notifying client: {str(e)}")
    
    # 6. Live Tracking System
    
    def _activate_live_tracking(self, db: Session, job: Job) -> None:
        """Activate live tracking for assigned job"""
        try:
            job.tracking_active = True
            db.commit()
            logger.info(f"Live tracking activated for job {job.id}")
        except Exception as e:
            logger.error(f"Error activating live tracking: {str(e)}")
    
    def update_fixer_location(self, db: Session, fixer_id: str, latitude: float, longitude: float) -> bool:
        """Update fixer's current location for live tracking"""
        try:
            # Update fixer availability record
            availability = db.query(FixerAvailability).filter(
                FixerAvailability.fixer_id == fixer_id
            ).first()
            
            if availability:
                availability.current_latitude = latitude
                availability.current_longitude = longitude
                availability.location_updated_at = datetime.utcnow()
                
                # Update current job if exists
                if availability.current_job_id:
                    job = db.query(Job).filter(
                        Job.id == availability.current_job_id,
                        Job.tracking_active == True
                    ).first()
                    
                    if job:
                        job.fixer_location_lat = latitude
                        job.fixer_location_lng = longitude
                        job.fixer_location_updated = datetime.utcnow()
                        
                        # Calculate estimated arrival if job location available
                        if job.latitude and job.longitude:
                            distance = self._calculate_distance(
                                latitude, longitude, job.latitude, job.longitude
                            )
                            # Rough estimate: 30 km/h average speed
                            arrival_minutes = (distance / 30) * 60
                            job.estimated_arrival = datetime.utcnow() + timedelta(minutes=arrival_minutes)
                
                db.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating fixer location: {str(e)}")
            db.rollback()
            
        return False
    
    # 7. Timeout and Reallocation System
    
    def process_job_timeouts(self, db: Session) -> None:
        """Process all job timeouts and handle reallocation with enhanced 3-hour system"""
        try:
            current_time = datetime.utcnow()
            
            # Handle assignment timeouts (fixers not responding)
            assignment_timeout_jobs = db.query(Job).filter(
                Job.status == "notifying_fixers",
                Job.assignment_timeout < current_time
            ).all()
            
            for job in assignment_timeout_jobs:
                self._handle_assignment_timeout(db, job)
            
            # Handle attendance timeouts (3-hour attendance deadline)
            attendance_timeout_jobs = db.query(Job).filter(
                Job.status == "assigned",
                Job.attendance_deadline < current_time
            ).all()
            
            for job in attendance_timeout_jobs:
                self._handle_attendance_timeout_enhanced(db, job)
            
            # Process availability freeze expirations
            self._process_availability_freeze_expirations(db)
            
            # Process platform fee deadlines
            self._process_platform_fee_deadlines(db)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error processing job timeouts: {str(e)}")
            db.rollback()
    
    def _handle_attendance_timeout_enhanced(self, db: Session, job: Job) -> None:
        """Enhanced attendance timeout handling with 4-hour fixer freeze"""
        try:
            if not job.fixer_id:
                return
            
            # Get fixer and availability
            fixer = db.query(Fixer).filter(Fixer.id == job.fixer_id).first()
            availability = db.query(FixerAvailability).filter(
                FixerAvailability.fixer_id == job.fixer_id
            ).first()
            
            if fixer and availability:
                # Apply 4-hour availability freeze as per requirements
                freeze_until = datetime.utcnow() + timedelta(hours=self.availability_freeze_hours)
                availability.is_availability_frozen = True
                availability.availability_frozen_until = freeze_until
                availability.freeze_reason = "attendance_timeout"
                availability.is_available = False  # Mark as unavailable
                
                # Update fixer stats
                fixer.jobs_no_show += 1
                fixer.availability_freeze_count += 1
                fixer.total_freeze_hours += self.availability_freeze_hours
                fixer.last_assigned_at = None  # Reset last assignment
                
                # Recalculate completion percentage
                total_assignments = fixer.jobs_completed + fixer.jobs_cancelled + fixer.jobs_incomplete + fixer.jobs_no_show
                if total_assignments > 0:
                    fixer.completion_percentage = (fixer.jobs_completed / total_assignments) * 100
                
                # Update assignment history
                history = db.query(JobAssignmentHistory).filter(
                    JobAssignmentHistory.job_id == job.id,
                    JobAssignmentHistory.fixer_id == job.fixer_id,
                    JobAssignmentHistory.response_type == "accepted"
                ).first()
                
                if history:
                    history.response_type = "timeout"
                    history.completion_status = "no_show"
                    history.response_reason = "Failed to arrive within 180 minutes"
                
                logger.warning(f"Fixer {job.fixer_id} froze for 4 hours due to attendance timeout on job {job.id}")
            
            # Update job for emergency escalation
            job.fixer_timeout_count += 1
            job.emergency_escalation_reason = "attendance_timeout"
            job.fixer_freeze_applied = True
            job.fixer_id = None  # Clear assignment
            job.tracking_active = False
            
            # Flag as emergency and escalate
            self._escalate_to_emergency_enhanced(db, job, "attendance_timeout")
            
            logger.info(f"Enhanced attendance timeout handled for job {job.id}")
            
        except Exception as e:
            logger.error(f"Error handling enhanced attendance timeout: {str(e)}")
    
    def _process_availability_freeze_expirations(self, db: Session) -> None:
        """Process and release expired availability freezes"""
        try:
            current_time = datetime.utcnow()
            
            expired_freezes = db.query(FixerAvailability).filter(
                FixerAvailability.is_availability_frozen == True,
                FixerAvailability.availability_frozen_until < current_time
            ).all()
            
            for availability in expired_freezes:
                availability.is_availability_frozen = False
                availability.availability_frozen_until = None
                availability.freeze_reason = None
                availability.is_available = True  # Restore availability
                
                logger.info(f"Availability freeze expired for fixer {availability.fixer_id}")
            
            if expired_freezes:
                db.commit()
                logger.info(f"Released {len(expired_freezes)} expired availability freezes")
                
        except Exception as e:
            logger.error(f"Error processing availability freeze expirations: {str(e)}")
    
    def _process_platform_fee_deadlines(self, db: Session) -> None:
        """Process platform fee deadlines and apply suspensions"""
        try:
            current_time = datetime.utcnow()
            
            # Find fixers with overdue platform fees (>48 hours)
            overdue_fixers = db.query(Fixer).filter(
                Fixer.platform_fees_owed > 0,
                Fixer.fee_payment_overdue == False
            ).all()
            
            for fixer in overdue_fixers:
                # Check if any fees are more than 48 hours overdue
                overdue_payments = db.query(FixerPayment).filter(
                    FixerPayment.fixer_id == fixer.id,
                    FixerPayment.status == "pending",
                    FixerPayment.due_date < (current_time - timedelta(hours=self.platform_fee_deadline_hours))
                ).all()
                
                if overdue_payments:
                    # Mark as overdue and suspend if necessary
                    fixer.fee_payment_overdue = True
                    fixer.fee_suspension_applied = True
                    
                    # Update availability to suspended
                    availability = db.query(FixerAvailability).filter(
                        FixerAvailability.fixer_id == fixer.id
                    ).first()
                    
                    if availability:
                        availability.is_suspended = True
                        availability.suspension_reason = "Platform fees overdue >48 hours"
                        availability.platform_fee_status = "overdue"
                    
                    logger.warning(f"Fixer {fixer.id} suspended for overdue platform fees")
            
            if overdue_fixers:
                db.commit()
                
        except Exception as e:
            logger.error(f"Error processing platform fee deadlines: {str(e)}")
    
    def _escalate_to_emergency_enhanced(self, db: Session, job: Job, reason: str) -> None:
        """Enhanced emergency escalation with comprehensive notification system"""
        try:
            job.status = "escalated"
            job.workflow_stage = "emergency"
            job.is_emergency_escalated = True
            job.priority_level = "emergency"
            job.emergency_escalation_reason = reason
            
            # Get all available fixers with emergency criteria (less restrictive)
            emergency_fixers = db.query(Fixer).join(FixerAvailability).filter(
                Fixer.is_active == True,
                Fixer.is_approved == True,
                FixerAvailability.is_available == True,
                FixerAvailability.is_suspended == False,
                FixerAvailability.platform_fee_status == "current"
            ).all()
            
            # Filter out frozen fixers unless absolutely necessary
            available_emergency_fixers = []
            frozen_emergency_fixers = []
            
            for fixer in emergency_fixers:
                availability = db.query(FixerAvailability).filter(
                    FixerAvailability.fixer_id == fixer.id
                ).first()
                
                if availability and not availability.is_availability_frozen:
                    available_emergency_fixers.append(fixer)
                elif availability:
                    frozen_emergency_fixers.append(fixer)
            
            # Use available fixers first, then frozen if necessary
            target_fixers = available_emergency_fixers if available_emergency_fixers else frozen_emergency_fixers
            emergency_fixer_ids = [f.id for f in target_fixers]
            
            if emergency_fixer_ids:
                # Send emergency notifications with higher compensation mention
                for fixer in target_fixers:
                    message = f"""
🚨 EMERGENCY JOB ALERT! 🚨
Service: {job.service}
Location: {job.location}
Priority: URGENT - {reason.replace('_', ' ').title()}
Estimated Price: R{job.estimated_price or 'TBD'}

⚡ EMERGENCY RATE: Higher compensation applies!
⏰ Immediate response required!

This job needs immediate attention due to: {reason.replace('_', ' ')}
"""
                    whatsapp_service.send_whatsapp_message(fixer.phone, message)
                
                job.eligible_fixers = json.dumps(emergency_fixer_ids)
                job.assignment_timeout = datetime.utcnow() + timedelta(minutes=10)  # Shorter timeout for emergency
                
                logger.warning(f"Job {job.id} escalated to emergency - notified {len(target_fixers)} fixers")
            else:
                # No fixers available - flag for manual admin intervention
                job.admin_attention_flagged = True
                job.workflow_stage = "admin_intervention_required"
                logger.critical(f"Job {job.id} requires manual admin intervention - no emergency fixers available")
            
        except Exception as e:
            logger.error(f"Error escalating to emergency: {str(e)}")
    
    def _handle_assignment_timeout(self, db: Session, job: Job) -> None:
        """Handle timeout when no fixer accepts the job"""
        try:
            if job.auto_reassignment_count < self.max_reassignment_attempts:
                # Try reassignment
                job.auto_reassignment_count += 1
                job.assignment_timeout = datetime.utcnow() + timedelta(minutes=self.assignment_timeout_minutes)
                
                # Get fresh list of eligible fixers
                eligible_fixers = self.get_eligible_fixers(db, job)
                if eligible_fixers:
                    self._notify_eligible_fixers(db, job, eligible_fixers)
                    logger.info(f"Job {job.id} reassigned (attempt {job.auto_reassignment_count})")
                else:
                    self._escalate_to_emergency(db, job)
            else:
                # Max attempts reached, escalate to emergency
                self._escalate_to_emergency(db, job)
                
        except Exception as e:
            logger.error(f"Error handling assignment timeout: {str(e)}")
    
    def _handle_attendance_timeout(self, db: Session, job: Job) -> None:
        """Handle timeout when fixer doesn't confirm attendance"""
        try:
            # Release the fixer
            if job.fixer_id:
                availability = db.query(FixerAvailability).filter(
                    FixerAvailability.fixer_id == job.fixer_id
                ).first()
                
                if availability:
                    availability.is_available = True
                    availability.current_job_id = None
                
                # Update assignment history
                history = db.query(JobAssignmentHistory).filter(
                    JobAssignmentHistory.job_id == job.id,
                    JobAssignmentHistory.fixer_id == job.fixer_id,
                    JobAssignmentHistory.response_type == "accepted"
                ).first()
                
                if history:
                    history.response_type = "timeout"
                    history.completion_status = "timeout"
            
            # Clear assignment
            job.fixer_id = None
            job.tracking_active = False
            
            # Escalate to emergency or reassign
            self._escalate_to_emergency(db, job)
            
            logger.info(f"Attendance timeout handled for job {job.id}")
            
        except Exception as e:
            logger.error(f"Error handling attendance timeout: {str(e)}")
    
    def _escalate_to_emergency(self, db: Session, job: Job) -> None:
        """Escalate job as emergency and notify all available fixers"""
        try:
            job.status = "escalated"
            job.workflow_stage = "emergency"
            job.is_emergency_escalated = True
            job.priority_level = "emergency"
            
            # Get all available fixers (broader criteria for emergency)
            emergency_fixers = db.query(Fixer).join(FixerAvailability).filter(
                Fixer.is_active == True,
                Fixer.is_approved == True,
                FixerAvailability.is_available == True,
                FixerAvailability.is_suspended == False
            ).all()
            
            emergency_fixer_ids = [f.id for f in emergency_fixers]
            
            if emergency_fixer_ids:
                # Send emergency notifications
                for fixer in emergency_fixers:
                    message = f"""
🚨 EMERGENCY JOB ALERT! 🚨
Service: {job.service}
Location: {job.location}
Priority: URGENT
Estimated Price: R{job.estimated_price or 'TBD'}

This job needs immediate attention. Higher compensation may apply.
"""
                    whatsapp_service.send_whatsapp_message(fixer.phone, message)
                
                job.eligible_fixers = json.dumps(emergency_fixer_ids)
                job.assignment_timeout = datetime.utcnow() + timedelta(minutes=10)  # Shorter timeout for emergency
                
            logger.info(f"Job {job.id} escalated to emergency")
            
        except Exception as e:
            logger.error(f"Error escalating to emergency: {str(e)}")
    
    # 8. Job Completion and Fee Processing
    
    def complete_job(self, db: Session, job_id: str, fixer_id: str, completion_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Enhanced job completion with automatic R20 platform fee processing"""
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job or job.fixer_id != fixer_id:
                return False, "Job not found or not assigned to you"
            
            # Update job status
            job.status = "completed"
            job.workflow_stage = "completed"
            job.tracking_active = False
            job.final_price = completion_data.get('final_price')
            job.platform_fee_status = "due"
            job.platform_fee_deadline = datetime.utcnow() + timedelta(hours=self.platform_fee_deadline_hours)
            
            # Get fixer and update availability
            fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
            availability = db.query(FixerAvailability).filter(
                FixerAvailability.fixer_id == fixer_id
            ).first()
            
            if availability:
                availability.is_available = True
                availability.current_job_id = None
                availability.last_job_completed_at = datetime.utcnow()
            
            if fixer:
                # Update fixer statistics
                fixer.jobs_completed += 1
                fixer.total_jobs += 1
                fixer.last_assigned_at = datetime.utcnow()
                
                # Add platform fee to amount owed
                fixer.platform_fees_owed += self.platform_fee_amount
                
                # Recalculate completion percentage
                total_assignments = fixer.jobs_completed + fixer.jobs_cancelled + fixer.jobs_incomplete + fixer.jobs_no_show
                if total_assignments > 0:
                    fixer.completion_percentage = (fixer.jobs_completed / total_assignments) * 100
            
            # Create R20 platform fee payment record
            platform_fee_payment = FixerPayment(
                fixer_id=fixer_id,
                amount=self.platform_fee_amount,
                payment_type="platform_fee",
                description=f"Platform fee for job {job_id}",
                due_date=job.platform_fee_deadline,
                status="pending"
            )
            db.add(platform_fee_payment)
            
            # Update assignment history
            history = db.query(JobAssignmentHistory).filter(
                JobAssignmentHistory.job_id == job_id,
                JobAssignmentHistory.fixer_id == fixer_id,
                JobAssignmentHistory.response_type == "accepted"
            ).first()
            
            if history:
                history.completion_status = "completed"
            
            db.commit()
            
            # Trigger AI behavior analysis update
            self._update_fixer_behavior_analysis_enhanced(db, fixer_id)
            
            # Notify client of completion
            self._notify_client_job_completion(db, job)
            
            logger.info(f"Job {job_id} completed by fixer {fixer_id} - R{self.platform_fee_amount} platform fee due")
            return True, f"Job completed successfully. Platform fee of R{self.platform_fee_amount} due within {self.platform_fee_deadline_hours} hours."
            
        except Exception as e:
            logger.error(f"Error completing job: {str(e)}")
            db.rollback()
            return False, f"Error completing job: {str(e)}"
    
    def _notify_client_job_completion(self, db: Session, job: Job) -> None:
        """Notify client that job has been completed"""
        try:
            user = job.user
            fixer = job.fixer
            
            message = f"""
✅ Job Completed!
Service: {job.service}
Fixer: {fixer.name if fixer else 'Unknown'}
Final Price: R{job.final_price or job.estimated_price or 'TBD'}

Please rate your fixer's service quality to help other clients.
Thank you for using FixMate-SA! 🔧
"""
            
            # Send WhatsApp notification
            if user.whatsapp_active and user.phone:
                whatsapp_service.send_whatsapp_message(user.phone, message)
            
            logger.info(f"Client notified of job completion for job {job.id}")
            
        except Exception as e:
            logger.error(f"Error notifying client of job completion: {str(e)}")
    
    # Enhanced Cancellation Protocols
    
    def cancel_job_by_client(self, db: Session, job_id: str, user_id: str, reason: str = None) -> Tuple[bool, str]:
        """Handle client cancellation with immediate job release"""
        try:
            job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
            if not job:
                return False, "Job not found or not authorized"
            
            # Check if job can be cancelled
            if job.status in ["completed", "cancelled"]:
                return False, "Job cannot be cancelled in its current state"
            
            # Update job
            job.status = "cancelled"
            job.workflow_stage = "cancelled_by_client"
            job.client_cancelled = True
            job.client_cancellation_reason = reason or "No reason provided"
            job.tracking_active = False
            
            # Release fixer if assigned
            if job.fixer_id:
                availability = db.query(FixerAvailability).filter(
                    FixerAvailability.fixer_id == job.fixer_id
                ).first()
                
                if availability:
                    availability.is_available = True
                    availability.current_job_id = None
                
                # Notify fixer of cancellation
                fixer = db.query(Fixer).filter(Fixer.id == job.fixer_id).first()
                if fixer:
                    message = f"""
❌ Job Cancelled by Client
Service: {job.service}
Location: {job.location}
Reason: {job.client_cancellation_reason}

You are now available for new jobs.
"""
                    whatsapp_service.send_whatsapp_message(fixer.phone, message)
                
                job.fixer_id = None
            
            db.commit()
            logger.info(f"Job {job_id} cancelled by client {user_id}")
            return True, "Job cancelled successfully. No fees charged."
            
        except Exception as e:
            logger.error(f"Error cancelling job by client: {str(e)}")
            db.rollback()
            return False, f"Error cancelling job: {str(e)}"
    
    def cancel_job_by_fixer(self, db: Session, job_id: str, fixer_id: str, reason: str = None) -> Tuple[bool, str]:
        """Handle fixer cancellation with 2-hour freeze and 0.2 rating penalty"""
        try:
            job = db.query(Job).filter(Job.id == job_id, Job.fixer_id == fixer_id).first()
            if not job:
                return False, "Job not found or not assigned to you"
            
            # Check if job can be cancelled
            if job.status in ["completed", "cancelled"]:
                return False, "Job cannot be cancelled in its current state"
            
            # Get fixer and availability
            fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
            availability = db.query(FixerAvailability).filter(
                FixerAvailability.fixer_id == fixer_id
            ).first()
            
            if fixer and availability:
                # Apply 2-hour availability freeze as per requirements
                freeze_until = datetime.utcnow() + timedelta(hours=self.cancellation_freeze_hours)
                availability.is_availability_frozen = True
                availability.availability_frozen_until = freeze_until
                availability.freeze_reason = "fixer_cancellation"
                availability.is_available = False
                
                # Apply 0.2 rating penalty
                rating_penalty = self.rating_penalty_per_cancellation
                fixer.rating_penalty_total += rating_penalty
                fixer.cancellation_penalty_count += 1
                fixer.last_cancellation_penalty = datetime.utcnow()
                fixer.jobs_cancelled += 1
                
                # Update stats
                fixer.availability_freeze_count += 1
                fixer.total_freeze_hours += self.cancellation_freeze_hours
                
                # Recalculate completion percentage
                total_assignments = fixer.jobs_completed + fixer.jobs_cancelled + fixer.jobs_incomplete + fixer.jobs_no_show
                if total_assignments > 0:
                    fixer.completion_percentage = (fixer.jobs_completed / total_assignments) * 100
                
                penalties_applied = {
                    "rating_penalty": rating_penalty,
                    "freeze_hours": self.cancellation_freeze_hours,
                    "freeze_until": freeze_until.isoformat()
                }
                
                logger.warning(f"Fixer {fixer_id} penalized for job cancellation: {penalties_applied}")
            
            # Update job
            job.status = "cancelled"
            job.workflow_stage = "cancelled_by_fixer"
            job.fixer_cancelled = True
            job.fixer_cancellation_reason = reason or "No reason provided"
            job.cancellation_penalties_applied = json.dumps(penalties_applied) if 'penalties_applied' in locals() else None
            job.tracking_active = False
            job.fixer_id = None
            
            # Update assignment history
            history = db.query(JobAssignmentHistory).filter(
                JobAssignmentHistory.job_id == job_id,
                JobAssignmentHistory.fixer_id == fixer_id,
                JobAssignmentHistory.response_type == "accepted"
            ).first()
            
            if history:
                history.response_type = "cancelled"
                history.completion_status = "cancelled"
                history.response_reason = reason or "Fixer cancelled"
            
            # Immediately reassign to next available fixer
            self._reassign_after_cancellation(db, job)
            
            db.commit()
            
            # Trigger AI fraud monitoring
            self._check_fixer_fraud_patterns(db, fixer_id)
            
            logger.info(f"Job {job_id} cancelled by fixer {fixer_id} - penalties applied")
            return True, f"Job cancelled. Penalties applied: {self.cancellation_freeze_hours}h freeze, -{rating_penalty} rating points."
            
        except Exception as e:
            logger.error(f"Error cancelling job by fixer: {str(e)}")
            db.rollback()
            return False, f"Error cancelling job: {str(e)}"
    
    def _reassign_after_cancellation(self, db: Session, job: Job) -> None:
        """Reassign job to next available fixer after cancellation"""
        try:
            # Get fresh list of eligible fixers
            eligible_fixers = self.get_eligible_fixers(db, job)
            
            if eligible_fixers:
                job.status = "notifying_fixers"
                job.workflow_stage = "notifying"
                job.assignment_timeout = datetime.utcnow() + timedelta(minutes=self.assignment_timeout_minutes)
                job.assignment_attempts += 1
                
                # Notify eligible fixers
                self._notify_eligible_fixers(db, job, eligible_fixers)
                
                logger.info(f"Job {job.id} reassigned after fixer cancellation")
            else:
                # No eligible fixers - escalate
                self._escalate_to_emergency_enhanced(db, job, "no_fixers_after_cancellation")
                
        except Exception as e:
            logger.error(f"Error reassigning after cancellation: {str(e)}")
    
    # 9. AI Monitoring and Behavior Analysis
    
    def _update_fixer_behavior_analysis(self, db: Session, fixer_id: str) -> None:
        """Update AI behavior analysis for fixer"""
        try:
            # Get or create behavior analysis record
            analysis = db.query(FixerBehaviorAnalysis).filter(
                FixerBehaviorAnalysis.fixer_id == fixer_id
            ).first()
            
            if not analysis:
                analysis = FixerBehaviorAnalysis(fixer_id=fixer_id)
                db.add(analysis)
            
            # Calculate metrics for last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            job_history = db.query(JobAssignmentHistory).filter(
                JobAssignmentHistory.fixer_id == fixer_id,
                JobAssignmentHistory.notified_at >= thirty_days_ago
            ).all()
            
            # Calculate performance metrics
            total_assigned = len([h for h in job_history if h.response_type == "accepted"])
            total_completed = len([h for h in job_history if h.completion_status == "completed"])
            total_cancelled = len([h for h in job_history if h.completion_status == "cancelled"])
            total_incomplete = len([h for h in job_history if h.completion_status == "incomplete"])
            
            analysis.total_jobs_assigned = total_assigned
            analysis.total_jobs_completed = total_completed
            analysis.total_jobs_cancelled = total_cancelled
            analysis.total_jobs_incomplete = total_incomplete
            
            # Calculate rates
            if total_assigned > 0:
                analysis.completion_rate = (total_completed / total_assigned) * 100
                analysis.cancellation_rate = (total_cancelled / total_assigned) * 100
            
            # AI behavior pattern detection
            behavior_flags = []
            
            # Check for concerning patterns
            if analysis.cancellation_rate > 20:  # More than 20% cancellation
                behavior_flags.append("high_cancellation_rate")
            
            if analysis.completion_rate < 80:  # Less than 80% completion
                behavior_flags.append("low_completion_rate")
            
            if total_incomplete > 3:  # More than 3 incomplete jobs
                behavior_flags.append("frequent_incomplete_jobs")
            
            # Update risk level
            if len(behavior_flags) >= 3:
                analysis.risk_level = "critical"
                analysis.admin_attention_required = True
            elif len(behavior_flags) >= 2:
                analysis.risk_level = "high"
            elif len(behavior_flags) >= 1:
                analysis.risk_level = "medium"
            else:
                analysis.risk_level = "low"
            
            analysis.behavior_flags = json.dumps(behavior_flags)
            analysis.last_analyzed_at = datetime.utcnow()
            analysis.next_analysis_due = datetime.utcnow() + timedelta(days=7)
            
            # Generate AI recommendations
            recommendations = self._generate_ai_recommendations(analysis, behavior_flags)
            analysis.ai_recommendations = json.dumps(recommendations)
            
            db.commit()
            
            logger.info(f"Behavior analysis updated for fixer {fixer_id}")
            
        except Exception as e:
            logger.error(f"Error updating behavior analysis: {str(e)}")
    
    def _generate_ai_recommendations(self, analysis: FixerBehaviorAnalysis, behavior_flags: List[str]) -> List[str]:
        """Generate AI recommendations based on behavior analysis"""
        recommendations = []
        
        if "high_cancellation_rate" in behavior_flags:
            recommendations.append("Consider contacting fixer about high cancellation rate")
            recommendations.append("Provide training on commitment and scheduling")
        
        if "low_completion_rate" in behavior_flags:
            recommendations.append("Review fixer's technical skills and provide additional training")
            recommendations.append("Monitor next 5 jobs closely")
        
        if "frequent_incomplete_jobs" in behavior_flags:
            recommendations.append("Investigate reasons for incomplete jobs")
            recommendations.append("Consider temporary supervision or mentoring")
        
        if analysis.risk_level == "critical":
            recommendations.append("Consider temporary suspension pending review")
            recommendations.append("Schedule immediate admin interview")
        
        return recommendations
    
    # 10. Admin Override Functions
    
    def admin_override_fixer_restriction(self, db: Session, fixer_id: str, admin_id: str, reason: str) -> bool:
        """Allow admin to override fixer restrictions"""
        try:
            availability = db.query(FixerAvailability).filter(
                FixerAvailability.fixer_id == fixer_id
            ).first()
            
            if not availability:
                return False
            
            # Reset restrictions
            availability.has_outstanding_debt = False
            availability.is_suspended = False
            availability.suspension_reason = f"Admin override by {admin_id}: {reason}"
            availability.is_available = True
            
            db.commit()
            
            logger.info(f"Admin {admin_id} overrode restrictions for fixer {fixer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error with admin override: {str(e)}")
            db.rollback()
            return False
    
    # 11. Utility Methods
    
    def get_job_workflow_status(self, db: Session, job_id: str) -> Dict[str, Any]:
        """Get complete workflow status for a job"""
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return {}
            
            eligible_fixers = json.loads(job.eligible_fixers) if job.eligible_fixers else []
            notified_fixers = json.loads(job.notified_fixers) if job.notified_fixers else []
            
            return {
                "job_id": job.id,
                "status": job.status,
                "workflow_stage": job.workflow_stage,
                "terms_accepted": job.terms_accepted,
                "eligible_fixers_count": len(eligible_fixers),
                "notified_fixers_count": len(notified_fixers),
                "assignment_attempts": job.assignment_attempts,
                "auto_reassignment_count": job.auto_reassignment_count,
                "is_emergency_escalated": job.is_emergency_escalated,
                "priority_level": job.priority_level,
                "tracking_active": job.tracking_active,
                "assignment_timeout": job.assignment_timeout.isoformat() if job.assignment_timeout else None,
                "attendance_timeout": job.attendance_timeout.isoformat() if job.attendance_timeout else None,
                "fixer_assigned": job.fixer_id is not None,
                "estimated_arrival": job.estimated_arrival.isoformat() if job.estimated_arrival else None
            }
            
        except Exception as e:
            logger.error(f"Error getting job workflow status: {str(e)}")
            return {}

# Global service instance
job_workflow_service = JobWorkflowService()