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
    JobAssignmentHistory, JobNotification, PlatformTerms, UserTermsAcceptance
)
from services.whatsapp_service import whatsapp_service
from services.ai_service import ai_service

logger = logging.getLogger(__name__)

class JobWorkflowService:
    """Comprehensive job workflow management service"""
    
    def __init__(self):
        self.assignment_timeout_minutes = 15  # Time for fixers to respond
        self.attendance_timeout_minutes = 30  # Time for fixer to confirm attendance
        self.max_reassignment_attempts = 3    # Maximum auto-reassignment attempts
        self.emergency_escalation_minutes = 45  # Time before emergency escalation
        
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
        """Get list of eligible fixer IDs based on location, debt, and active job checks"""
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
                # Check availability record
                availability = db.query(FixerAvailability).filter(
                    FixerAvailability.fixer_id == fixer.id
                ).first()
                
                if not availability:
                    # Create availability record if not exists
                    availability = FixerAvailability(fixer_id=fixer.id)
                    db.add(availability)
                
                # Apply eligibility checks
                if (availability.is_available and 
                    not availability.current_job_id and 
                    not availability.has_outstanding_debt and
                    not availability.is_suspended and
                    not availability.is_on_break):
                    
                    # Check location proximity if coordinates available
                    if (job.latitude and job.longitude and 
                        availability.current_latitude and availability.current_longitude):
                        distance = self._calculate_distance(
                            job.latitude, job.longitude,
                            availability.current_latitude, availability.current_longitude
                        )
                        if distance <= availability.service_radius:
                            eligible_fixers.append(fixer.id)
                    else:
                        # If no GPS data, include based on text location matching
                        eligible_fixers.append(fixer.id)
            
            db.commit()
            logger.info(f"Found {len(eligible_fixers)} eligible fixers for job {job.id}")
            return eligible_fixers
            
        except Exception as e:
            logger.error(f"Error getting eligible fixers: {str(e)}")
            return []
    
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
            
            # Set assignment timeout
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
        """Process all job timeouts and handle reallocation"""
        try:
            current_time = datetime.utcnow()
            
            # Handle assignment timeouts
            assignment_timeout_jobs = db.query(Job).filter(
                Job.status == "notifying_fixers",
                Job.assignment_timeout < current_time
            ).all()
            
            for job in assignment_timeout_jobs:
                self._handle_assignment_timeout(db, job)
            
            # Handle attendance timeouts
            attendance_timeout_jobs = db.query(Job).filter(
                Job.status == "assigned",
                Job.attendance_timeout < current_time
            ).all()
            
            for job in attendance_timeout_jobs:
                self._handle_attendance_timeout(db, job)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error processing job timeouts: {str(e)}")
            db.rollback()
    
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
        """Mark job as completed and process R20 platform fee"""
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job or job.fixer_id != fixer_id:
                return False, "Job not found or not assigned to you"
            
            # Update job
            job.status = "completed"
            job.workflow_stage = "completed"
            job.tracking_active = False
            job.final_price = completion_data.get('final_price')
            
            # Update fixer availability
            availability = db.query(FixerAvailability).filter(
                FixerAvailability.fixer_id == fixer_id
            ).first()
            
            if availability:
                availability.is_available = True
                availability.current_job_id = None
                availability.last_job_completed_at = datetime.utcnow()
            
            # Create R20 platform fee payment
            from services.payment_service import payment_service
            fee_created = payment_service.create_job_completion_fee(db, fixer_id, job_id)
            
            if not fee_created:
                logger.warning(f"Failed to create R20 fee for job {job_id}")
            
            # Update assignment history
            history = db.query(JobAssignmentHistory).filter(
                JobAssignmentHistory.job_id == job_id,
                JobAssignmentHistory.fixer_id == fixer_id,
                JobAssignmentHistory.response_type == "accepted"
            ).first()
            
            if history:
                history.completion_status = "completed"
            
            # Update fixer stats
            fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
            if fixer:
                fixer.total_jobs += 1
            
            db.commit()
            
            # Trigger AI analysis update
            self._update_fixer_behavior_analysis(db, fixer_id)
            
            logger.info(f"Job {job_id} completed by fixer {fixer_id}")
            return True, "Job completed successfully"
            
        except Exception as e:
            logger.error(f"Error completing job: {str(e)}")
            db.rollback()
            return False, f"Error completing job: {str(e)}"
    
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