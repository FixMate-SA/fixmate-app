from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
import math
from geopy.distance import geodesic
import logging

from models import Job, Fixer, User, FixerAvailability, FixerBehaviorAnalysis, JobAssignmentHistory
from services.ai_service import ai_service

logger = logging.getLogger(__name__)

class SmartMatchingService:
    """
    Advanced AI-powered matching service for FixMate-SA.
    Implements fair, efficient, and intelligent job-to-fixer matching.
    """
    
    def __init__(self):
        self.max_search_radius = 50  # km
        self.default_search_radius = 20  # km
        self.min_match_threshold = 30  # minimum score for consideration
        
    def find_best_fixers_for_job(self, db: Session, job: Job, limit: int = 10) -> List[Dict]:
        """
        Find and rank the best fixers for a specific job using AI-powered matching.
        
        Args:
            db: Database session
            job: Job object to match fixers for
            limit: Maximum number of fixers to return
            
        Returns:
            List of ranked fixer matches with scores and explanations
        """
        try:
            logger.info(f"Starting smart matching for job {job.id}")
            
            # Step 1: Get eligible fixers (basic filtering)
            eligible_fixers = self._get_eligible_fixers(db, job)
            
            if not eligible_fixers:
                logger.warning(f"No eligible fixers found for job {job.id}")
                return []
            
            logger.info(f"Found {len(eligible_fixers)} eligible fixers for job {job.id}")
            
            # Step 2: Prepare job data for AI matching
            job_data = self._prepare_job_data(job)
            
            # Step 3: Prepare fixer data with enriched information
            enriched_fixers = []
            for fixer in eligible_fixers:
                fixer_data = self._enrich_fixer_data(db, fixer, job)
                enriched_fixers.append(fixer_data)
            
            # Step 4: Use AI to rank fixers
            ranked_matches = ai_service.rank_fixers_for_job(enriched_fixers, job_data)
            
            # Step 5: Filter by minimum threshold and limit results
            quality_matches = [
                match for match in ranked_matches 
                if match['match_score'] >= self.min_match_threshold
            ]
            
            # Step 6: Apply fair distribution adjustments
            fair_matches = self._apply_fair_distribution(db, quality_matches, job)
            
            # Step 7: Generate matching insights
            insights = ai_service.generate_matching_insights(job_data, fair_matches)
            
            logger.info(f"Smart matching completed for job {job.id}: {len(fair_matches)} quality matches")
            
            # Return top matches with insights
            result = fair_matches[:limit]
            if result:
                result[0]['matching_insights'] = insights
            
            return result
            
        except Exception as e:
            logger.error(f"Error in smart matching for job {job.id}: {e}")
            return []
    
    def _get_eligible_fixers(self, db: Session, job: Job) -> List[Fixer]:
        """
        Get fixers eligible for the job based on basic criteria.
        """
        # Extract coordinates if available
        job_lat = job.latitude
        job_lng = job.longitude
        
        # Base query for active, approved fixers
        query = db.query(Fixer).filter(
            Fixer.is_active == True,
            Fixer.is_approved == True,
            Fixer.vetting_status == 'approved'
        )
        
        # Service filtering - check if fixer offers the required service
        if job.service:
            query = query.filter(
                or_(
                    Fixer.services.contains(job.service),
                    Fixer.services.contains(job.service.lower()),
                    Fixer.services.contains(job.service.title())
                )
            )
        
        all_fixers = query.all()
        
        # If no coordinates, return all eligible fixers
        if not job_lat or not job_lng:
            return all_fixers
        
        # Filter by distance
        nearby_fixers = []
        for fixer in all_fixers:
            if fixer.current_latitude and fixer.current_longitude:
                try:
                    distance = geodesic(
                        (job_lat, job_lng),
                        (fixer.current_latitude, fixer.current_longitude)
                    ).kilometers
                    
                    if distance <= self.max_search_radius:
                        nearby_fixers.append(fixer)
                        
                except Exception as e:
                    logger.warning(f"Error calculating distance for fixer {fixer.id}: {e}")
                    # Include fixer if distance calculation fails
                    nearby_fixers.append(fixer)
        
        return nearby_fixers if nearby_fixers else all_fixers[:20]  # Fallback to first 20
    
    def _prepare_job_data(self, job: Job) -> Dict:
        """
        Prepare job data for AI matching.
        """
        return {
            'id': job.id,
            'service': job.service,
            'description': job.description,
            'location': job.location,
            'latitude': job.latitude,
            'longitude': job.longitude,
            'estimated_price': job.estimated_price,
            'priority_level': job.priority_level,
            'is_emergency': job.is_emergency_escalated,
            'client_language': getattr(job.user, 'preferred_language', 'english') if job.user else 'english',
            'created_at': job.created_at.isoformat(),
            'scheduled_at': job.scheduled_at.isoformat() if job.scheduled_at else None
        }
    
    def _enrich_fixer_data(self, db: Session, fixer: Fixer, job: Job) -> Dict:
        """
        Enrich fixer data with all relevant information for AI matching.
        """
        # Calculate distance
        distance_km = float('inf')
        if job.latitude and job.longitude and fixer.current_latitude and fixer.current_longitude:
            try:
                distance_km = geodesic(
                    (job.latitude, job.longitude),
                    (fixer.current_latitude, fixer.current_longitude)
                ).kilometers
            except:
                pass
        
        # Get availability information
        availability = db.query(FixerAvailability).filter(
            FixerAvailability.fixer_id == fixer.id
        ).first()
        
        # Get behavior analysis
        behavior = db.query(FixerBehaviorAnalysis).filter(
            FixerBehaviorAnalysis.fixer_id == fixer.id
        ).first()
        
        # Calculate hours since last job
        hours_since_last_job = 0
        if fixer.last_assigned_at:
            hours_since_last_job = (datetime.utcnow() - fixer.last_assigned_at).total_seconds() / 3600
        else:
            hours_since_last_job = 168  # Default to 1 week if never assigned
        
        # Count current jobs
        current_jobs = db.query(Job).filter(
            Job.fixer_id == fixer.id,
            Job.status.in_(['assigned', 'in_progress'])
        ).count()
        
        # Get recent assignment history
        recent_assignments = db.query(JobAssignmentHistory).filter(
            JobAssignmentHistory.fixer_id == fixer.id,
            JobAssignmentHistory.notified_at >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        return {
            'id': fixer.id,
            'name': fixer.name,
            'phone': fixer.phone,
            'services': fixer.services,
            'rating': fixer.rating,
            'total_jobs': fixer.total_jobs,
            'location': fixer.location,
            'distance_km': distance_km,
            'is_available': availability.is_available if availability else True,
            'current_jobs': current_jobs,
            'completion_rate': behavior.completion_rate if behavior else 100.0,
            'avg_response_time': availability.average_response_time if availability else 30,
            'reliability_score': availability.reliability_score if availability else 100.0,
            'hours_since_last_job': hours_since_last_job,
            'languages': ['english', 'afrikaans'],  # Default languages, can be enhanced
            'recent_assignments': recent_assignments,
            'is_suspended': availability.is_suspended if availability else False,
            'has_outstanding_debt': availability.has_outstanding_debt if availability else False,
            'risk_level': behavior.risk_level if behavior else 'low',
            'last_assigned_at': fixer.last_assigned_at.isoformat() if fixer.last_assigned_at else None
        }
    
    def _apply_fair_distribution(self, db: Session, matches: List[Dict], job: Job) -> List[Dict]:
        """
        Apply fair distribution adjustments to ensure equal opportunities.
        """
        if not matches:
            return matches
        
        # Sort by fairness boost first, then by match score
        def fair_sort_key(match):
            fairness_boost = match['factors'].get('fairness_boost', 0)
            match_score = match['match_score']
            
            # Prioritize matches with high fairness boost
            if fairness_boost >= 6:
                return (1, match_score)  # High priority
            else:
                return (0, match_score)  # Normal priority
        
        matches.sort(key=fair_sort_key, reverse=True)
        
        return matches
    
    def notify_selected_fixers(self, db: Session, job: Job, selected_matches: List[Dict]) -> Dict:
        """
        Notify selected fixers about the job opportunity.
        """
        try:
            from services.job_workflow_service import job_workflow_service
            
            # Extract fixer IDs
            fixer_ids = [match['fixer_id'] for match in selected_matches]
            
            # Use the job workflow service to handle notifications
            result = job_workflow_service.notify_eligible_fixers(db, job.id, fixer_ids)
            
            # Add matching insights to the result
            if selected_matches:
                insights = selected_matches[0].get('matching_insights', {})
                result['matching_insights'] = insights
            
            return result
            
        except Exception as e:
            logger.error(f"Error notifying fixers for job {job.id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_fixer_match_history(self, db: Session, fixer_id: str, days: int = 30) -> Dict:
        """
        Get matching performance history for a fixer.
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get assignment history
            assignments = db.query(JobAssignmentHistory).filter(
                JobAssignmentHistory.fixer_id == fixer_id,
                JobAssignmentHistory.notified_at >= cutoff_date
            ).all()
            
            total_notifications = len(assignments)
            accepted = sum(1 for a in assignments if a.response_type == 'accepted')
            declined = sum(1 for a in assignments if a.response_type == 'declined')
            timeouts = sum(1 for a in assignments if a.response_type == 'timeout')
            
            acceptance_rate = (accepted / total_notifications * 100) if total_notifications > 0 else 0
            
            # Get behavior analysis
            behavior = db.query(FixerBehaviorAnalysis).filter(
                FixerBehaviorAnalysis.fixer_id == fixer_id
            ).first()
            
            return {
                'fixer_id': fixer_id,
                'period_days': days,
                'total_notifications': total_notifications,
                'accepted': accepted,
                'declined': declined,
                'timeouts': timeouts,
                'acceptance_rate': round(acceptance_rate, 1),
                'completion_rate': behavior.completion_rate if behavior else None,
                'reliability_score': behavior.reliability_score if behavior else None,
                'risk_level': behavior.risk_level if behavior else 'unknown'
            }
            
        except Exception as e:
            logger.error(f"Error getting match history for fixer {fixer_id}: {e}")
            return {'error': str(e)}
    
    def analyze_matching_performance(self, db: Session, days: int = 7) -> Dict:
        """
        Analyze overall matching performance for the platform.
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get recent jobs with matching data
            recent_jobs = db.query(Job).filter(
                Job.created_at >= cutoff_date,
                Job.workflow_stage != 'terms_pending'
            ).all()
            
            total_jobs = len(recent_jobs)
            successfully_assigned = sum(1 for job in recent_jobs if job.fixer_id is not None)
            completion_rate = sum(1 for job in recent_jobs if job.status == 'completed')
            
            assignment_rate = (successfully_assigned / total_jobs * 100) if total_jobs > 0 else 0
            job_completion_rate = (completion_rate / total_jobs * 100) if total_jobs > 0 else 0
            
            # Average time to assignment
            assigned_jobs = [job for job in recent_jobs if job.fixer_id and job.assignment_history]
            avg_assignment_time = 0
            if assigned_jobs:
                assignment_times = []
                for job in assigned_jobs:
                    for history in job.assignment_history:
                        if history.accepted_at:
                            time_diff = (history.accepted_at - job.created_at).total_seconds() / 60
                            assignment_times.append(time_diff)
                            break
                
                if assignment_times:
                    avg_assignment_time = sum(assignment_times) / len(assignment_times)
            
            return {
                'period_days': days,
                'total_jobs': total_jobs,
                'successfully_assigned': successfully_assigned,
                'assignment_rate': round(assignment_rate, 1),
                'completion_rate': round(job_completion_rate, 1),
                'avg_assignment_time_minutes': round(avg_assignment_time, 1),
                'performance_rating': self._calculate_performance_rating(assignment_rate, job_completion_rate, avg_assignment_time)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing matching performance: {e}")
            return {'error': str(e)}
    
    def _calculate_performance_rating(self, assignment_rate: float, completion_rate: float, avg_time: float) -> str:
        """Calculate overall performance rating"""
        score = 0
        
        # Assignment rate scoring
        if assignment_rate >= 90:
            score += 40
        elif assignment_rate >= 75:
            score += 30
        elif assignment_rate >= 60:
            score += 20
        else:
            score += 10
        
        # Completion rate scoring
        if completion_rate >= 85:
            score += 30
        elif completion_rate >= 70:
            score += 20
        elif completion_rate >= 55:
            score += 10
        
        # Time to assignment scoring
        if avg_time <= 15:
            score += 30
        elif avg_time <= 30:
            score += 20
        elif avg_time <= 60:
            score += 10
        
        if score >= 85:
            return 'excellent'
        elif score >= 65:
            return 'good'
        elif score >= 45:
            return 'fair'
        else:
            return 'needs_improvement'

# Global instance
smart_matching_service = SmartMatchingService()