import json
import base64
import io
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import logging

from models import Job, JobPhotoVerification, User, Fixer
from services.ai_service import ai_service

logger = logging.getLogger(__name__)

class PhotoVerificationService:
    """
    Service for managing job photo verification process.
    Handles before/after photos, AI analysis, and admin verification.
    """
    
    def __init__(self):
        self.max_photo_size = 5 * 1024 * 1024  # 5MB per photo
        self.max_photos_per_stage = 5  # Max photos per before/after/progress
        self.required_job_types = ['plumbing', 'electrical', 'painting', 'carpentry']  # Job types requiring photos
        self.high_value_threshold = 1000.0  # Jobs above this amount require photos
        
    def is_photo_verification_required(self, job: Job) -> Tuple[bool, str]:
        """
        Determine if photo verification is required for a job.
        
        Returns:
            Tuple of (is_required: bool, reason: str)
        """
        reasons = []
        
        # High-value jobs require photos
        if job.final_price and job.final_price >= self.high_value_threshold:
            reasons.append('high_value')
        
        # Specific job types require photos
        if job.service and job.service.lower() in self.required_job_types:
            reasons.append('job_type')
        
        # Jobs with dispute history require photos
        if hasattr(job, 'disputes') and job.disputes:
            reasons.append('dispute_history')
        
        # Fixer with low reliability requires photos
        if job.fixer and hasattr(job.fixer, 'reliability_score'):
            reliability = getattr(job.fixer, 'reliability_score', 100.0)
            if reliability < 80.0:
                reasons.append('fixer_reliability')
        
        is_required = len(reasons) > 0
        reason = ', '.join(reasons) if reasons else 'not_required'
        
        return is_required, reason
    
    def validate_photo_data(self, photo_base64: str) -> Dict:
        """
        Validate a base64 photo for size and format.
        """
        try:
            # Remove data URL prefix if present
            if photo_base64.startswith('data:image/'):
                photo_base64 = photo_base64.split(',')[1]
            
            # Decode and check size
            photo_data = base64.b64decode(photo_base64)
            if len(photo_data) > self.max_photo_size:
                return {
                    'valid': False,
                    'error': f'Photo size ({len(photo_data)} bytes) exceeds maximum allowed ({self.max_photo_size} bytes)'
                }
            
            # Basic image validation (check for common image headers)
            image_headers = [
                b'\xff\xd8\xff',  # JPEG
                b'\x89PNG\r\n\x1a\n',  # PNG
                b'GIF87a',  # GIF87a
                b'GIF89a',  # GIF89a
            ]
            
            is_valid_image = any(photo_data.startswith(header) for header in image_headers)
            
            if not is_valid_image:
                return {
                    'valid': False,
                    'error': 'Invalid image format. Only JPEG, PNG, and GIF are supported'
                }
            
            return {
                'valid': True,
                'size': len(photo_data),
                'format': 'jpeg' if photo_data.startswith(b'\xff\xd8\xff') else 'png' if photo_data.startswith(b'\x89PNG') else 'gif'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f'Error validating photo: {str(e)}'
            }
    
    def submit_job_photos(
        self, 
        db: Session, 
        job_id: str, 
        photo_type: str,  # 'before', 'after', 'progress'
        photos: List[str],  # List of base64 photo strings
        submitted_by: str  # User ID who submitted
    ) -> Dict:
        """
        Submit photos for a job (before, after, or progress photos).
        """
        try:
            # Get the job
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return {'success': False, 'error': 'Job not found'}
            
            # Validate photo count
            if len(photos) > self.max_photos_per_stage:
                return {
                    'success': False, 
                    'error': f'Maximum {self.max_photos_per_stage} photos allowed per stage'
                }
            
            # Validate each photo
            validated_photos = []
            total_size = 0
            
            for i, photo in enumerate(photos):
                validation = self.validate_photo_data(photo)
                if not validation['valid']:
                    return {
                        'success': False,
                        'error': f'Photo {i+1}: {validation["error"]}'
                    }
                
                validated_photos.append(photo)
                total_size += validation['size']
            
            # Get or create photo verification record
            verification = db.query(JobPhotoVerification).filter(
                JobPhotoVerification.job_id == job_id
            ).first()
            
            is_new_record = False
            if not verification:
                is_new_record = True
                # Check if photos are required
                is_required, reason = self.is_photo_verification_required(job)
                
                verification = JobPhotoVerification(
                    job_id=job_id,
                    is_required=is_required,
                    requirement_reason=reason,
                    verification_status='pending'
                )
                db.add(verification)
            
            # Store photos based on type
            photos_json = json.dumps(validated_photos)
            
            if photo_type == 'before':
                verification.before_photos = photos_json
            elif photo_type == 'after':
                verification.after_photos = photos_json
            elif photo_type == 'progress':
                verification.work_progress_photos = photos_json
            else:
                return {'success': False, 'error': 'Invalid photo type'}
            
            # Update verification status
            if photo_type == 'after' and verification.before_photos:
                # If we have both before and after, trigger AI analysis
                verification.verification_status = 'pending'
                self._analyze_photos_with_ai(verification, job)
            
            verification.updated_at = datetime.utcnow()
            
            try:
                db.commit()
                
                return {
                    'success': True,
                    'message': f'{photo_type.title()} photos submitted successfully',
                    'verification_id': verification.id,
                    'photos_count': len(validated_photos),
                    'total_size': total_size,
                    'status': verification.verification_status,
                    'is_new_record': is_new_record
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error submitting photos: {e}")
                return {'success': False, 'error': 'Database error occurred'}
            
        except Exception as e:
            logger.error(f"Error submitting job photos: {e}")
            return {'success': False, 'error': f'Error submitting photos: {str(e)}'}
    
    def _analyze_photos_with_ai(self, verification: JobPhotoVerification, job: Job):
        """
        Analyze photos using AI to assess quality and completion.
        """
        try:
            if not ai_service.model or not verification.before_photos or not verification.after_photos:
                return
            
            # Prepare analysis prompt
            analysis_prompt = f"""
            Analyze these before and after photos for a {job.service} job.
            Job Description: {job.description}
            
            Please assess:
            1. Photo quality (clarity, lighting, framing) - score 0-100
            2. Clear before/after comparison visible - true/false  
            3. Work appears completed based on description - true/false
            4. Any quality concerns or red flags
            5. Confidence level in assessment - score 0-100
            
            Respond in JSON format:
            {{
                "photo_quality_score": 85,
                "has_clear_before_after": true,
                "shows_completed_work": true,
                "concerns": ["concern1", "concern2"],
                "confidence": 90,
                "recommendation": "approved/needs_review/rejected"
            }}
            """
            
            try:
                response = ai_service.model.generate_content(analysis_prompt)
                analysis_text = response.text.strip()
                
                # Try to parse JSON response
                if analysis_text.startswith('{') and analysis_text.endswith('}'):
                    analysis_data = json.loads(analysis_text)
                    
                    verification.ai_analysis = json.dumps(analysis_data)
                    verification.ai_confidence = analysis_data.get('confidence', 0)
                    verification.photo_quality_score = analysis_data.get('photo_quality_score', 0)
                    verification.has_clear_before_after = analysis_data.get('has_clear_before_after', False)
                    verification.shows_completed_work = analysis_data.get('shows_completed_work', False)
                    
                    # Set flagged issues
                    concerns = analysis_data.get('concerns', [])
                    if concerns:
                        verification.flagged_issues = json.dumps(concerns)
                    
                    # Auto-approve if AI is confident and quality is good
                    if (analysis_data.get('confidence', 0) >= 85 and 
                        analysis_data.get('photo_quality_score', 0) >= 75 and
                        analysis_data.get('shows_completed_work', False) and
                        len(concerns) == 0):
                        verification.verification_status = 'approved'
                        verification.verified_at = datetime.utcnow()
                    
            except json.JSONDecodeError:
                # If AI doesn't return valid JSON, store raw response
                verification.ai_analysis = json.dumps({
                    'raw_response': analysis_text,
                    'parsing_error': True
                })
                
        except Exception as e:
            logger.error(f"Error in AI photo analysis: {e}")
            verification.ai_analysis = json.dumps({
                'error': str(e),
                'analysis_failed': True
            })
    
    def get_job_photo_verification(self, db: Session, job_id: str) -> Optional[Dict]:
        """
        Get photo verification status and data for a job.
        """
        try:
            verification = db.query(JobPhotoVerification).filter(
                JobPhotoVerification.job_id == job_id
            ).first()
            
            if not verification:
                return None
            
            # Parse photos (but don't return full base64 data for efficiency)
            before_count = 0
            after_count = 0
            progress_count = 0
            
            if verification.before_photos:
                before_photos = json.loads(verification.before_photos)
                before_count = len(before_photos)
            
            if verification.after_photos:
                after_photos = json.loads(verification.after_photos)
                after_count = len(after_photos)
                
            if verification.work_progress_photos:
                progress_photos = json.loads(verification.work_progress_photos)
                progress_count = len(progress_photos)
            
            # Parse AI analysis
            ai_analysis = {}
            if verification.ai_analysis:
                try:
                    ai_analysis = json.loads(verification.ai_analysis)
                except:
                    ai_analysis = {'parsing_error': True}
            
            # Parse flagged issues
            flagged_issues = []
            if verification.flagged_issues:
                try:
                    flagged_issues = json.loads(verification.flagged_issues)
                except:
                    flagged_issues = []
            
            return {
                'verification_id': verification.id,
                'job_id': verification.job_id,
                'status': verification.verification_status,
                'is_required': verification.is_required,
                'requirement_reason': verification.requirement_reason,
                'photo_counts': {
                    'before': before_count,
                    'after': after_count,
                    'progress': progress_count
                },
                'quality_assessment': {
                    'photo_quality_score': verification.photo_quality_score,
                    'has_clear_before_after': verification.has_clear_before_after,
                    'shows_completed_work': verification.shows_completed_work,
                    'ai_confidence': verification.ai_confidence
                },
                'ai_analysis': ai_analysis,
                'flagged_issues': flagged_issues,
                'verified_by': verification.verified_by,
                'verified_at': verification.verified_at.isoformat() if verification.verified_at else None,
                'rejection_reason': verification.rejection_reason,
                'created_at': verification.created_at.isoformat(),
                'updated_at': verification.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting photo verification: {e}")
            return None
    
    def admin_verify_photos(
        self, 
        db: Session, 
        verification_id: str, 
        admin_id: str, 
        decision: str,  # 'approved', 'rejected', 'needs_more'
        comments: str = None
    ) -> Dict:
        """
        Admin verification of job photos.
        """
        try:
            verification = db.query(JobPhotoVerification).filter(
                JobPhotoVerification.id == verification_id
            ).first()
            
            if not verification:
                return {'success': False, 'error': 'Verification record not found'}
            
            # Validate admin
            admin = db.query(User).filter(
                User.id == admin_id,
                User.role.in_(['admin', 'super_admin'])
            ).first()
            
            if not admin:
                return {'success': False, 'error': 'Invalid admin user'}
            
            # Update verification
            verification.verification_status = decision
            verification.verified_by = admin_id
            verification.verified_at = datetime.utcnow()
            
            if decision == 'rejected' and comments:
                verification.rejection_reason = comments
            
            verification.updated_at = datetime.utcnow()
            
            try:
                db.commit()
                
                return {
                    'success': True,
                    'message': f'Photos {decision} successfully',
                    'verification_id': verification_id,
                    'decision': decision,
                    'verified_by': admin.display_name,
                    'verified_at': verification.verified_at.isoformat()
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error in admin verification: {e}")
                return {'success': False, 'error': 'Database error occurred'}
            
        except Exception as e:
            logger.error(f"Error in admin photo verification: {e}")
            return {'success': False, 'error': f'Verification error: {str(e)}'}
    
    def get_pending_verifications(self, db: Session, limit: int = 50) -> List[Dict]:
        """
        Get list of photo verifications pending admin review.
        """
        try:
            pending_verifications = db.query(JobPhotoVerification).filter(
                JobPhotoVerification.verification_status == 'pending',
                JobPhotoVerification.after_photos.isnot(None)  # Only show if after photos exist
            ).order_by(JobPhotoVerification.created_at.desc()).limit(limit).all()
            
            results = []
            for verification in pending_verifications:
                # Get job details
                job = db.query(Job).filter(Job.id == verification.job_id).first()
                
                if job:
                    verification_data = self.get_job_photo_verification(db, verification.job_id)
                    if verification_data:
                        verification_data.update({
                            'job_details': {
                                'id': job.id,
                                'service': job.service,
                                'description': job.description,
                                'location': job.location,
                                'final_price': job.final_price,
                                'client_name': job.user.display_name if job.user else 'Unknown',
                                'fixer_name': job.fixer.name if job.fixer else 'Unknown'
                            }
                        })
                        results.append(verification_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting pending verifications: {e}")
            return []
    
    def get_photo_data(self, db: Session, verification_id: str, photo_type: str) -> Optional[List[str]]:
        """
        Get actual photo data (base64) for display purposes.
        Use with caution as this returns large data.
        """
        try:
            verification = db.query(JobPhotoVerification).filter(
                JobPhotoVerification.id == verification_id
            ).first()
            
            if not verification:
                return None
            
            if photo_type == 'before' and verification.before_photos:
                return json.loads(verification.before_photos)
            elif photo_type == 'after' and verification.after_photos:
                return json.loads(verification.after_photos)
            elif photo_type == 'progress' and verification.work_progress_photos:
                return json.loads(verification.work_progress_photos)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting photo data: {e}")
            return None

# Global instance
photo_verification_service = PhotoVerificationService()