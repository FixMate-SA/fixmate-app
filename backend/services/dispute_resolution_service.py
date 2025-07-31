import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
import logging

from models import Job, JobDispute, DisputeMessage, User, Fixer
from services.ai_service import ai_service

logger = logging.getLogger(__name__)

class DisputeResolutionService:
    """
    Service for managing job disputes and escalations.
    Handles formal dispute resolution with admin mediation.
    """
    
    def __init__(self):
        self.dispute_types = [
            'quality',      # Work quality issues
            'no_show',      # Fixer didn't show up
            'payment',      # Payment disputes
            'behavior',     # Unprofessional behavior
            'incomplete',   # Job not completed
            'damage',       # Property damage
            'timing',       # Scheduling issues
            'other'         # Other issues
        ]
        
        self.resolution_actions = [
            'refund',       # Full or partial refund
            'redo_job',     # Redo the job with same or different fixer
            'warning',      # Issue warning to fixer
            'suspension',   # Temporary suspension
            'mediation',    # Facilitate mediation between parties
            'no_action'     # No action required
        ]
        
        self.auto_escalation_hours = 24  # Auto-escalate disputes after 24 hours
        
    def create_dispute(
        self, 
        db: Session, 
        job_id: str, 
        reporter_id: str, 
        dispute_data: Dict
    ) -> Dict:
        """
        Create a new dispute for a job.
        """
        try:
            # Validate job exists
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return {'success': False, 'error': 'Job not found'}
            
            # Validate reporter
            reporter = db.query(User).filter(User.id == reporter_id).first()
            if not reporter:
                return {'success': False, 'error': 'Reporter not found'}
            
            # Determine reporter type
            reporter_type = 'client'
            if job.fixer_id and reporter_id == job.fixer_id:
                reporter_type = 'fixer'
            elif reporter.role in ['admin', 'super_admin']:
                reporter_type = 'admin'
            
            # Validate dispute type
            dispute_type = dispute_data.get('dispute_type')
            if dispute_type not in self.dispute_types:
                return {'success': False, 'error': f'Invalid dispute type: {dispute_type}'}
            
            # Check if dispute already exists for this job
            existing_dispute = db.query(JobDispute).filter(
                JobDispute.job_id == job_id,
                JobDispute.status.in_(['open', 'investigating'])
            ).first()
            
            if existing_dispute:
                return {'success': False, 'error': 'An active dispute already exists for this job'}
            
            # Create dispute
            dispute = JobDispute(
                job_id=job_id,
                reporter_id=reporter_id,
                reporter_type=reporter_type,
                dispute_type=dispute_type,
                description=dispute_data.get('description', ''),
                priority_level=dispute_data.get('priority_level', 'normal'),
                evidence_description=dispute_data.get('evidence_description'),
                evidence_photos=json.dumps(dispute_data.get('evidence_photos', [])) if dispute_data.get('evidence_photos') else None
            )
            
            # Auto-assign to admin if available
            available_admin = db.query(User).filter(
                User.role.in_(['admin', 'super_admin']),
                User.is_active == True
            ).first()
            
            if available_admin:
                dispute.assigned_admin_id = available_admin.id
                dispute.status = 'investigating'
            
            # Hold payment for high-priority disputes
            if dispute_data.get('priority_level') in ['high', 'urgent']:
                dispute.payment_hold = True
            
            db.add(dispute)
            db.flush()  # Flush to get the dispute ID
            
            # Create initial message
            initial_message = DisputeMessage(
                dispute_id=dispute.id,
                sender_id=reporter_id,
                sender_type=reporter_type,
                message=dispute_data.get('description', ''),
                message_type='text'
            )
            db.add(initial_message)
            
            try:
                db.commit()
                
                # Send notifications
                self._notify_dispute_created(db, dispute)
                
                return {
                    'success': True,
                    'message': 'Dispute created successfully',
                    'dispute_id': dispute.id,
                    'status': dispute.status,
                    'assigned_admin': available_admin.display_name if available_admin else None,
                    'payment_hold': dispute.payment_hold
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error creating dispute: {e}")
                return {'success': False, 'error': 'Database error occurred'}
            
        except Exception as e:
            logger.error(f"Error creating dispute: {e}")
            return {'success': False, 'error': f'Error creating dispute: {str(e)}'}
    
    def add_dispute_message(
        self, 
        db: Session, 
        dispute_id: str, 
        sender_id: str, 
        message_data: Dict
    ) -> Dict:
        """
        Add a message to an existing dispute.
        """
        try:
            # Validate dispute
            dispute = db.query(JobDispute).filter(
                JobDispute.id == dispute_id,
                JobDispute.status.in_(['open', 'investigating'])
            ).first()
            
            if not dispute:
                return {'success': False, 'error': 'Dispute not found or closed'}
            
            # Validate sender
            sender = db.query(User).filter(User.id == sender_id).first()
            if not sender:
                return {'success': False, 'error': 'Sender not found'}
            
            # Determine sender type
            sender_type = 'admin' if sender.role in ['admin', 'super_admin'] else 'client'
            if dispute.job.fixer_id == sender_id:
                sender_type = 'fixer'
            
            # Create message
            message = DisputeMessage(
                dispute_id=dispute_id,
                sender_id=sender_id,
                sender_type=sender_type,
                message=message_data.get('message', ''),
                message_type=message_data.get('message_type', 'text'),
                attachments=json.dumps(message_data.get('attachments', [])) if message_data.get('attachments') else None,
                is_internal=message_data.get('is_internal', False)
            )
            
            db.add(message)
            
            # Update dispute timestamp
            dispute.updated_at = datetime.utcnow()
            
            try:
                db.commit()
                
                return {
                    'success': True,
                    'message': 'Message added successfully',
                    'message_id': message.id,
                    'dispute_id': dispute_id
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error adding dispute message: {e}")
                return {'success': False, 'error': 'Database error occurred'}
            
        except Exception as e:
            logger.error(f"Error adding dispute message: {e}")
            return {'success': False, 'error': f'Error adding message: {str(e)}'}
    
    def resolve_dispute(
        self, 
        db: Session, 
        dispute_id: str, 
        admin_id: str, 
        resolution_data: Dict
    ) -> Dict:
        """
        Resolve a dispute with admin decision.
        """
        try:
            # Validate dispute
            dispute = db.query(JobDispute).filter(
                JobDispute.id == dispute_id,
                JobDispute.status.in_(['open', 'investigating'])
            ).first()
            
            if not dispute:
                return {'success': False, 'error': 'Dispute not found or already resolved'}
            
            # Validate admin
            admin = db.query(User).filter(
                User.id == admin_id,
                User.role.in_(['admin', 'super_admin'])
            ).first()
            
            if not admin:
                return {'success': False, 'error': 'Invalid admin user'}
            
            # Validate resolution action
            resolution_action = resolution_data.get('resolution_action')
            if resolution_action not in self.resolution_actions:
                return {'success': False, 'error': f'Invalid resolution action: {resolution_action}'}
            
            # Update dispute
            dispute.status = 'resolved'
            dispute.resolution = resolution_data.get('resolution', '')
            dispute.resolution_action = resolution_action
            dispute.assigned_admin_id = admin_id
            dispute.admin_notes = resolution_data.get('admin_notes', '')
            dispute.resolved_at = datetime.utcnow()
            dispute.updated_at = datetime.utcnow()
            
            # Handle payment actions
            if resolution_action == 'refund':
                dispute.payment_hold = True
                dispute.refund_amount = resolution_data.get('refund_amount')
            elif resolution_action in ['no_action', 'warning']:
                dispute.payment_hold = False
                dispute.payment_released = True
            
            # Add resolution message
            resolution_message = DisputeMessage(
                dispute_id=dispute_id,
                sender_id=admin_id,
                sender_type='admin',
                message=f"RESOLUTION: {resolution_data.get('resolution', '')}",
                message_type='status_update'
            )
            db.add(resolution_message)
            
            try:
                db.commit()
                
                # Send notifications
                self._notify_dispute_resolved(db, dispute, resolution_data)
                
                return {
                    'success': True,
                    'message': 'Dispute resolved successfully',
                    'dispute_id': dispute_id,
                    'resolution_action': resolution_action,
                    'resolved_by': admin.display_name,
                    'resolved_at': dispute.resolved_at.isoformat()
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error resolving dispute: {e}")
                return {'success': False, 'error': 'Database error occurred'}
            
        except Exception as e:
            logger.error(f"Error resolving dispute: {e}")
            return {'success': False, 'error': f'Error resolving dispute: {str(e)}'}
    
    def get_dispute_details(self, db: Session, dispute_id: str) -> Optional[Dict]:
        """
        Get complete dispute details including messages.
        """
        try:
            dispute = db.query(JobDispute).filter(JobDispute.id == dispute_id).first()
            if not dispute:
                return None
            
            # Get all messages
            messages = db.query(DisputeMessage).filter(
                DisputeMessage.dispute_id == dispute_id
            ).order_by(DisputeMessage.created_at.asc()).all()
            
            # Parse evidence photos
            evidence_photos = []
            if dispute.evidence_photos:
                try:
                    evidence_photos = json.loads(dispute.evidence_photos)
                except:
                    pass
            
            # Format messages
            formatted_messages = []
            for msg in messages:
                attachments = []
                if msg.attachments:
                    try:
                        attachments = json.loads(msg.attachments)
                    except:
                        pass
                
                formatted_messages.append({
                    'id': msg.id,
                    'sender_id': msg.sender_id,
                    'sender_name': msg.sender.display_name if msg.sender else 'Unknown',
                    'sender_type': msg.sender_type,
                    'message': msg.message,
                    'message_type': msg.message_type,
                    'attachments': attachments,
                    'is_internal': msg.is_internal,
                    'created_at': msg.created_at.isoformat()
                })
            
            return {
                'dispute_id': dispute.id,
                'job_id': dispute.job_id,
                'job_details': {
                    'service': dispute.job.service,
                    'description': dispute.job.description,
                    'location': dispute.job.location,
                    'final_price': dispute.job.final_price,
                    'status': dispute.job.status
                },
                'reporter': {
                    'id': dispute.reporter_id,
                    'name': dispute.reporter.display_name if dispute.reporter else 'Unknown',
                    'type': dispute.reporter_type
                },
                'dispute_type': dispute.dispute_type,
                'description': dispute.description,
                'priority_level': dispute.priority_level,
                'status': dispute.status,
                'evidence_photos': evidence_photos,
                'evidence_description': dispute.evidence_description,
                'resolution': dispute.resolution,
                'resolution_action': dispute.resolution_action,
                'assigned_admin': {
                    'id': dispute.assigned_admin_id,
                    'name': dispute.assigned_admin.display_name if dispute.assigned_admin else None
                } if dispute.assigned_admin_id else None,
                'admin_notes': dispute.admin_notes,
                'payment_hold': dispute.payment_hold,
                'payment_released': dispute.payment_released,
                'refund_amount': dispute.refund_amount,
                'messages': formatted_messages,
                'created_at': dispute.created_at.isoformat(),
                'updated_at': dispute.updated_at.isoformat(),
                'reviewed_at': dispute.reviewed_at.isoformat() if dispute.reviewed_at else None,
                'resolved_at': dispute.resolved_at.isoformat() if dispute.resolved_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting dispute details: {e}")
            return None
    
    def get_pending_disputes(self, db: Session, admin_id: str = None, limit: int = 50) -> List[Dict]:
        """
        Get list of pending disputes for admin review.
        """
        try:
            query = db.query(JobDispute).filter(
                JobDispute.status.in_(['open', 'investigating'])
            )
            
            # Filter by assigned admin if specified
            if admin_id:
                query = query.filter(JobDispute.assigned_admin_id == admin_id)
            
            disputes = query.order_by(
                JobDispute.priority_level.desc(),
                JobDispute.created_at.asc()
            ).limit(limit).all()
            
            results = []
            for dispute in disputes:
                # Get message count
                message_count = db.query(DisputeMessage).filter(
                    DisputeMessage.dispute_id == dispute.id
                ).count()
                
                # Calculate time since creation
                time_since_creation = datetime.utcnow() - dispute.created_at
                hours_open = int(time_since_creation.total_seconds() / 3600)
                
                results.append({
                    'dispute_id': dispute.id,
                    'job_id': dispute.job_id,
                    'dispute_type': dispute.dispute_type,
                    'priority_level': dispute.priority_level,
                    'status': dispute.status,
                    'reporter_name': dispute.reporter.display_name if dispute.reporter else 'Unknown',
                    'reporter_type': dispute.reporter_type,
                    'job_service': dispute.job.service,
                    'job_location': dispute.job.location,
                    'description_preview': dispute.description[:100] + '...' if len(dispute.description) > 100 else dispute.description,
                    'assigned_admin': dispute.assigned_admin.display_name if dispute.assigned_admin else None,
                    'message_count': message_count,
                    'hours_open': hours_open,
                    'payment_hold': dispute.payment_hold,
                    'created_at': dispute.created_at.isoformat(),
                    'updated_at': dispute.updated_at.isoformat()
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting pending disputes: {e}")
            return []
    
    def auto_escalate_disputes(self, db: Session) -> Dict:
        """
        Auto-escalate disputes that have been open too long.
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.auto_escalation_hours)
            
            # Find disputes that need escalation
            disputes_to_escalate = db.query(JobDispute).filter(
                JobDispute.status == 'open',
                JobDispute.created_at < cutoff_time,
                JobDispute.assigned_admin_id.is_(None)
            ).all()
            
            escalated_count = 0
            
            for dispute in disputes_to_escalate:
                # Assign to admin
                available_admin = db.query(User).filter(
                    User.role.in_(['admin', 'super_admin']),
                    User.is_active == True
                ).first()
                
                if available_admin:
                    dispute.status = 'escalated'
                    dispute.assigned_admin_id = available_admin.id
                    dispute.priority_level = 'high'
                    dispute.updated_at = datetime.utcnow()
                    
                    # Add escalation message
                    escalation_message = DisputeMessage(
                        dispute_id=dispute.id,
                        sender_id=available_admin.id,
                        sender_type='admin',
                        message=f"Dispute auto-escalated after {self.auto_escalation_hours} hours",
                        message_type='status_update',
                        is_internal=True
                    )
                    db.add(escalation_message)
                    
                    escalated_count += 1
            
            if escalated_count > 0:
                db.commit()
            
            return {
                'success': True,
                'escalated_count': escalated_count,
                'message': f'Auto-escalated {escalated_count} disputes'
            }
            
        except Exception as e:
            logger.error(f"Error auto-escalating disputes: {e}")
            return {'success': False, 'error': f'Auto-escalation error: {str(e)}'}
    
    def _notify_dispute_created(self, db: Session, dispute: JobDispute):
        """
        Send notifications when dispute is created.
        """
        try:
            # In a real implementation, this would send:
            # - Email/SMS to assigned admin
            # - In-app notification to relevant parties
            # - WhatsApp message if configured
            logger.info(f"Dispute {dispute.id} created - notifications would be sent here")
            
        except Exception as e:
            logger.error(f"Error sending dispute creation notifications: {e}")
    
    def _notify_dispute_resolved(self, db: Session, dispute: JobDispute, resolution_data: Dict):
        """
        Send notifications when dispute is resolved.
        """
        try:
            # In a real implementation, this would send:
            # - Resolution notification to reporter
            # - Status update to other party
            # - Payment team notification if refund needed
            logger.info(f"Dispute {dispute.id} resolved - notifications would be sent here")
            
        except Exception as e:
            logger.error(f"Error sending dispute resolution notifications: {e}")

# Global instance
dispute_resolution_service = DisputeResolutionService()