import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import logging

from models import Fixer, FixerReputationTier, BadgeDefinition, Job, NotificationQueue
from services.ai_service import ai_service

logger = logging.getLogger(__name__)

class GamificationService:
    """
    Service for managing fixer gamification, reputation tiers, and achievements.
    Handles badges, levels, rewards, and performance-based incentives.
    """
    
    def __init__(self):
        self.tier_thresholds = {
            'apprentice': {'min_points': 0, 'min_jobs': 0, 'min_rating': 0.0},
            'skilled': {'min_points': 100, 'min_jobs': 10, 'min_rating': 4.0},
            'expert': {'min_points': 500, 'min_jobs': 50, 'min_rating': 4.3},
            'master': {'min_points': 1500, 'min_jobs': 150, 'min_rating': 4.5},
            'legend': {'min_points': 5000, 'min_jobs': 500, 'min_rating': 4.7}
        }
        
        self.tier_benefits = {
            'apprentice': {'fee_reduction': 0.0, 'priority_access': False},
            'skilled': {'fee_reduction': 0.05, 'priority_access': False},  # 5% fee reduction
            'expert': {'fee_reduction': 0.10, 'priority_access': True},   # 10% fee reduction + priority
            'master': {'fee_reduction': 0.15, 'priority_access': True},   # 15% fee reduction + priority
            'legend': {'fee_reduction': 0.20, 'priority_access': True}    # 20% fee reduction + priority
        }
        
        # Initialize badge definitions if not already done
        self._initialize_badges()
    
    def _initialize_badges(self):
        """Initialize default badge definitions (run once on startup)"""
        self.default_badges = [
            {
                'badge_code': 'first_job',
                'name': 'First Job Completed',
                'description': 'Complete your first job on FixMate-SA',
                'icon': '🎯',
                'category': 'milestone',
                'criteria': {'jobs_completed': 1},
                'points_reward': 50,
                'difficulty': 'easy'
            },
            {
                'badge_code': 'ten_jobs',
                'name': 'Rising Star',
                'description': 'Complete 10 jobs successfully',
                'icon': '⭐',
                'category': 'milestone',
                'criteria': {'jobs_completed': 10},
                'points_reward': 100,
                'difficulty': 'easy'
            },
            {
                'badge_code': 'fifty_jobs',
                'name': 'Reliable Professional',
                'description': 'Complete 50 jobs with excellence',
                'icon': '🏆',
                'category': 'milestone',
                'criteria': {'jobs_completed': 50},
                'points_reward': 300,
                'difficulty': 'medium'
            },
            {
                'badge_code': 'hundred_jobs',
                'name': 'Master Craftsman',
                'description': 'Complete 100 jobs - true dedication!',
                'icon': '👑',
                'category': 'milestone',
                'criteria': {'jobs_completed': 100},
                'points_reward': 500,
                'difficulty': 'hard'
            },
            {
                'badge_code': 'perfect_rating',
                'name': 'Perfect Record',
                'description': 'Maintain 5.0 rating with 20+ jobs',
                'icon': '💎',
                'category': 'performance',
                'criteria': {'min_rating': 5.0, 'min_jobs': 20},
                'points_reward': 400,
                'difficulty': 'hard'
            },
            {
                'badge_code': 'speed_demon',
                'name': 'Speed Demon',
                'description': 'Average response time under 5 minutes',
                'icon': '⚡',
                'category': 'performance',
                'criteria': {'max_response_time': 5.0, 'min_jobs': 15},
                'points_reward': 200,
                'difficulty': 'medium'
            },
            {
                'badge_code': 'no_show_hero',
                'name': 'Always Shows Up',
                'description': 'Zero no-shows in 50+ jobs',
                'icon': '🎖️',
                'category': 'performance',
                'criteria': {'max_no_shows': 0, 'min_jobs': 50},
                'points_reward': 350,
                'difficulty': 'hard'
            },
            {
                'badge_code': 'early_bird',
                'name': 'Early Bird',
                'description': 'Always arrive early or on time',
                'icon': '🌅',
                'category': 'performance',
                'criteria': {'punctuality_rate': 100.0, 'min_jobs': 25},
                'points_reward': 250,
                'difficulty': 'medium'
            },
            {
                'badge_code': 'streak_master',
                'name': 'Streak Master',
                'description': 'Complete 20 jobs in a row successfully',
                'icon': '🔥',
                'category': 'special',
                'criteria': {'success_streak': 20},
                'points_reward': 300,
                'difficulty': 'medium'
            },
            {
                'badge_code': 'customer_favorite',
                'name': 'Customer Favorite',
                'description': 'Receive 50+ positive reviews',
                'icon': '❤️',
                'category': 'performance',
                'criteria': {'positive_reviews': 50},
                'points_reward': 200,
                'difficulty': 'medium'
            }
        ]
    
    def initialize_fixer_reputation(self, db: Session, fixer_id: str) -> Dict:
        """
        Initialize reputation tier for a new fixer.
        """
        try:
            # Check if reputation already exists
            existing = db.query(FixerReputationTier).filter(
                FixerReputationTier.fixer_id == fixer_id
            ).first()
            
            if existing:
                return {'success': False, 'error': 'Reputation tier already exists'}
            
            # Create initial reputation tier
            reputation = FixerReputationTier(
                fixer_id=fixer_id,
                current_tier='apprentice',
                tier_points=0,
                tier_level=1,
                badges_earned=json.dumps([]),
                achievements=json.dumps([]),
                milestones_reached=json.dumps([]),
                monthly_goals=json.dumps({
                    'jobs_target': 5,
                    'rating_target': 4.0,
                    'response_time_target': 30.0
                }),
                rewards_claimed=json.dumps([])
            )
            
            db.add(reputation)
            
            try:
                db.commit()
                return {
                    'success': True,
                    'message': 'Fixer reputation initialized',
                    'tier': 'apprentice',
                    'points': 0
                }
            except Exception as e:
                db.rollback()
                logger.error(f"Database error initializing reputation: {e}")
                return {'success': False, 'error': 'Database error occurred'}
                
        except Exception as e:
            logger.error(f"Error initializing fixer reputation: {e}")
            return {'success': False, 'error': f'Failed to initialize: {str(e)}'}
    
    def update_fixer_performance(self, db: Session, fixer_id: str, job_completed: bool = True) -> Dict:
        """
        Update fixer performance metrics after job completion.
        Triggers badge checks and tier progression.
        """
        try:
            # Get fixer and reputation
            fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
            if not fixer:
                return {'success': False, 'error': 'Fixer not found'}
            
            reputation = db.query(FixerReputationTier).filter(
                FixerReputationTier.fixer_id == fixer_id
            ).first()
            
            if not reputation:
                # Initialize if doesn't exist
                init_result = self.initialize_fixer_reputation(db, fixer_id)
                if not init_result['success']:
                    return init_result
                
                reputation = db.query(FixerReputationTier).filter(
                    FixerReputationTier.fixer_id == fixer_id
                ).first()
            
            # Update performance metrics
            if job_completed:
                reputation.jobs_completed += 1
                reputation.tier_points += 10  # Base points per job
                
                # Update streak
                reputation.streak_count += 1
                if reputation.streak_count > reputation.best_streak:
                    reputation.best_streak = reputation.streak_count
            else:
                # Job not completed successfully - reset streak
                reputation.streak_count = 0
            
            # Update other metrics from fixer data
            reputation.client_satisfaction_avg = fixer.rating
            reputation.response_time_avg = getattr(fixer, 'avg_response_time', 30.0)
            reputation.completion_rate = self._calculate_completion_rate(db, fixer_id)
            reputation.reliability_score = self._calculate_reliability_score(db, fixer_id)
            
            reputation.updated_at = datetime.utcnow()
            
            # Check for new badges
            new_badges = self._check_badge_eligibility(db, fixer, reputation)
            awarded_badges = []
            
            for badge in new_badges:
                badge_result = self._award_badge(db, reputation, badge)
                if badge_result['success']:
                    awarded_badges.append(badge)
            
            # Check for tier progression
            tier_change = self._check_tier_progression(db, reputation)
            
            # Calculate progress to next tier
            next_tier_progress = self._calculate_next_tier_progress(reputation)
            reputation.progress_to_next_tier = next_tier_progress['percentage']
            reputation.next_tier_requirements = json.dumps(next_tier_progress['requirements'])
            
            try:
                db.commit()
                
                result = {
                    'success': True,
                    'message': 'Performance updated successfully',
                    'current_tier': reputation.current_tier,
                    'tier_points': reputation.tier_points,
                    'jobs_completed': reputation.jobs_completed,
                    'streak_count': reputation.streak_count,
                    'new_badges': [badge['name'] for badge in awarded_badges],
                    'tier_changed': tier_change['changed'],
                    'progress_to_next_tier': next_tier_progress
                }
                
                # Send congratulations if tier changed or badges earned
                if tier_change['changed'] or awarded_badges:
                    self._send_achievement_notification(db, fixer, reputation, tier_change, awarded_badges)
                
                return result
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error updating performance: {e}")
                return {'success': False, 'error': 'Database error occurred'}
                
        except Exception as e:
            logger.error(f"Error updating fixer performance: {e}")
            return {'success': False, 'error': f'Failed to update performance: {str(e)}'}
    
    def get_fixer_reputation(self, db: Session, fixer_id: str) -> Optional[Dict]:
        """
        Get complete reputation information for a fixer.
        """
        try:
            reputation = db.query(FixerReputationTier).filter(
                FixerReputationTier.fixer_id == fixer_id
            ).first()
            
            if not reputation:
                return None
            
            # Parse JSON fields
            badges_earned = json.loads(reputation.badges_earned) if reputation.badges_earned else []
            achievements = json.loads(reputation.achievements) if reputation.achievements else []
            monthly_goals = json.loads(reputation.monthly_goals) if reputation.monthly_goals else {}
            
            # Get badge details
            badge_definitions = db.query(BadgeDefinition).filter(
                BadgeDefinition.badge_code.in_([badge['code'] for badge in badges_earned])
            ).all()
            
            detailed_badges = []
            for badge in badges_earned:
                badge_def = next((b for b in badge_definitions if b.badge_code == badge['code']), None)
                if badge_def:
                    detailed_badges.append({
                        'code': badge['code'],
                        'name': badge_def.name,
                        'description': badge_def.description,
                        'icon': badge_def.icon,
                        'category': badge_def.category,
                        'earned_at': badge['earned_at'],
                        'points_earned': badge.get('points_earned', 0)
                    })
            
            # Calculate tier benefits
            tier_benefits = self.tier_benefits.get(reputation.current_tier, {})
            
            return {
                'fixer_id': reputation.fixer_id,
                'current_tier': reputation.current_tier,
                'tier_level': reputation.tier_level,
                'tier_points': reputation.tier_points,
                'performance_metrics': {
                    'jobs_completed': reputation.jobs_completed,
                    'client_satisfaction_avg': reputation.client_satisfaction_avg,
                    'response_time_avg': reputation.response_time_avg,
                    'completion_rate': reputation.completion_rate,
                    'reliability_score': reputation.reliability_score
                },
                'gamification': {
                    'streak_count': reputation.streak_count,
                    'best_streak': reputation.best_streak,
                    'badges_count': len(detailed_badges),
                    'achievements_count': len(achievements)
                },
                'tier_benefits': {
                    'fee_reduction_percentage': tier_benefits.get('fee_reduction', 0) * 100,
                    'priority_access': tier_benefits.get('priority_access', False),
                    'verified_status': reputation.verified_status,
                    'featured_listing': reputation.featured_listing
                },
                'badges': detailed_badges,
                'achievements': achievements,
                'monthly_goals': monthly_goals,
                'progress_to_next_tier': reputation.progress_to_next_tier,
                'next_tier_requirements': json.loads(reputation.next_tier_requirements) if reputation.next_tier_requirements else {},
                'last_tier_promotion': reputation.last_tier_promotion.isoformat() if reputation.last_tier_promotion else None,
                'updated_at': reputation.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting fixer reputation: {e}")
            return None
    
    def _check_badge_eligibility(self, db: Session, fixer: Fixer, reputation: FixerReputationTier) -> List[Dict]:
        """
        Check which badges the fixer is now eligible for.
        """
        try:
            # Get already earned badges
            earned_badges = json.loads(reputation.badges_earned) if reputation.badges_earned else []
            earned_codes = [badge['code'] for badge in earned_badges]
            
            eligible_badges = []
            
            for badge_def in self.default_badges:
                badge_code = badge_def['badge_code']
                
                # Skip if already earned
                if badge_code in earned_codes:
                    continue
                
                # Check criteria
                criteria = badge_def['criteria']
                eligible = True
                
                if 'jobs_completed' in criteria:
                    if reputation.jobs_completed < criteria['jobs_completed']:
                        eligible = False
                
                if 'min_rating' in criteria:
                    if reputation.client_satisfaction_avg < criteria['min_rating']:
                        eligible = False
                
                if 'min_jobs' in criteria:
                    if reputation.jobs_completed < criteria['min_jobs']:
                        eligible = False
                
                if 'max_response_time' in criteria:
                    if reputation.response_time_avg > criteria['max_response_time']:
                        eligible = False
                
                if 'success_streak' in criteria:
                    if reputation.streak_count < criteria['success_streak']:
                        eligible = False
                
                if 'punctuality_rate' in criteria:
                    # Would need to calculate punctuality rate
                    # For demo, assume 95% if completion rate is high
                    punctuality = 95.0 if reputation.completion_rate >= 90 else 80.0
                    if punctuality < criteria['punctuality_rate']:
                        eligible = False
                
                if eligible:
                    eligible_badges.append(badge_def)
            
            return eligible_badges
            
        except Exception as e:
            logger.error(f"Error checking badge eligibility: {e}")
            return []
    
    def _award_badge(self, db: Session, reputation: FixerReputationTier, badge_def: Dict) -> Dict:
        """
        Award a badge to a fixer.
        """
        try:
            # Parse current badges
            badges_earned = json.loads(reputation.badges_earned) if reputation.badges_earned else []
            
            # Add new badge
            new_badge = {
                'code': badge_def['badge_code'],
                'earned_at': datetime.utcnow().isoformat(),
                'points_earned': badge_def.get('points_reward', 0)
            }
            
            badges_earned.append(new_badge)
            
            # Update reputation
            reputation.badges_earned = json.dumps(badges_earned)
            reputation.tier_points += badge_def.get('points_reward', 0)
            
            return {'success': True, 'badge': badge_def}
            
        except Exception as e:
            logger.error(f"Error awarding badge: {e}")
            return {'success': False, 'error': str(e)}
    
    def _check_tier_progression(self, db: Session, reputation: FixerReputationTier) -> Dict:
        """
        Check if fixer should be promoted to a higher tier.
        """
        try:
            current_tier = reputation.current_tier
            next_tiers = ['skilled', 'expert', 'master', 'legend']
            
            if current_tier == 'legend':
                return {'changed': False, 'new_tier': current_tier}
            
            # Find next tier
            current_index = list(self.tier_thresholds.keys()).index(current_tier)
            tier_names = list(self.tier_thresholds.keys())
            
            for i in range(current_index + 1, len(tier_names)):
                next_tier = tier_names[i]
                thresholds = self.tier_thresholds[next_tier]
                
                # Check if qualifies for this tier
                if (reputation.tier_points >= thresholds['min_points'] and
                    reputation.jobs_completed >= thresholds['min_jobs'] and
                    reputation.client_satisfaction_avg >= thresholds['min_rating']):
                    
                    # Promote to this tier
                    reputation.current_tier = next_tier
                    reputation.last_tier_promotion = datetime.utcnow()
                    
                    # Apply tier benefits
                    benefits = self.tier_benefits[next_tier]
                    reputation.lower_platform_fees = benefits['fee_reduction']
                    reputation.priority_access = benefits['priority_access']
                    
                    if next_tier in ['expert', 'master', 'legend']:
                        reputation.verified_status = True
                    
                    if next_tier in ['master', 'legend']:
                        reputation.featured_listing = True
                    
                    return {'changed': True, 'new_tier': next_tier, 'old_tier': current_tier}
            
            return {'changed': False, 'new_tier': current_tier}
            
        except Exception as e:
            logger.error(f"Error checking tier progression: {e}")
            return {'changed': False, 'new_tier': current_tier}
    
    def _calculate_next_tier_progress(self, reputation: FixerReputationTier) -> Dict:
        """
        Calculate progress towards next tier.
        """
        try:
            current_tier = reputation.current_tier
            tier_names = list(self.tier_thresholds.keys())
            
            if current_tier == 'legend':
                return {
                    'percentage': 100.0,
                    'requirements': {},
                    'next_tier': None
                }
            
            current_index = tier_names.index(current_tier)
            next_tier = tier_names[current_index + 1]
            next_thresholds = self.tier_thresholds[next_tier]
            
            # Calculate progress for each requirement
            points_progress = min(100, (reputation.tier_points / next_thresholds['min_points']) * 100)
            jobs_progress = min(100, (reputation.jobs_completed / next_thresholds['min_jobs']) * 100)
            rating_progress = min(100, (reputation.client_satisfaction_avg / next_thresholds['min_rating']) * 100)
            
            # Overall progress is the minimum of all requirements
            overall_progress = min(points_progress, jobs_progress, rating_progress)
            
            return {
                'percentage': round(overall_progress, 1),
                'next_tier': next_tier,
                'requirements': {
                    'points': {
                        'current': reputation.tier_points,
                        'required': next_thresholds['min_points'],
                        'progress': round(points_progress, 1)
                    },
                    'jobs': {
                        'current': reputation.jobs_completed,
                        'required': next_thresholds['min_jobs'],
                        'progress': round(jobs_progress, 1)
                    },
                    'rating': {
                        'current': round(reputation.client_satisfaction_avg, 2),
                        'required': next_thresholds['min_rating'],
                        'progress': round(rating_progress, 1)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating next tier progress: {e}")
            return {'percentage': 0.0, 'requirements': {}, 'next_tier': None}
    
    def _calculate_completion_rate(self, db: Session, fixer_id: str) -> float:
        """
        Calculate job completion rate for fixer.
        """
        try:
            total_jobs = db.query(Job).filter(Job.fixer_id == fixer_id).count()
            completed_jobs = db.query(Job).filter(
                Job.fixer_id == fixer_id,
                Job.status == 'completed'
            ).count()
            
            if total_jobs == 0:
                return 100.0
            
            return (completed_jobs / total_jobs) * 100
            
        except Exception as e:
            logger.error(f"Error calculating completion rate: {e}")
            return 0.0
    
    def _calculate_reliability_score(self, db: Session, fixer_id: str) -> float:
        """
        Calculate overall reliability score.
        """
        try:
            # Simple reliability calculation based on completion rate and response time
            completion_rate = self._calculate_completion_rate(db, fixer_id)
            
            # Get average response time (assume good if under 30 minutes)
            reputation = db.query(FixerReputationTier).filter(
                FixerReputationTier.fixer_id == fixer_id
            ).first()
            
            response_score = 100
            if reputation and reputation.response_time_avg:
                if reputation.response_time_avg <= 15:
                    response_score = 100
                elif reputation.response_time_avg <= 30:
                    response_score = 90
                elif reputation.response_time_avg <= 60:
                    response_score = 80
                else:
                    response_score = 70
            
            # Combine completion rate and response score
            reliability = (completion_rate * 0.7) + (response_score * 0.3)
            return min(100.0, reliability)
            
        except Exception as e:
            logger.error(f"Error calculating reliability score: {e}")
            return 100.0
    
    def _send_achievement_notification(
        self, 
        db: Session, 
        fixer: Fixer, 
        reputation: FixerReputationTier, 
        tier_change: Dict, 
        new_badges: List[Dict]
    ):
        """
        Send congratulations notification for achievements.
        """
        try:
            messages = []
            
            if tier_change['changed']:
                tier_benefits = self.tier_benefits.get(tier_change['new_tier'], {})
                fee_reduction = tier_benefits.get('fee_reduction', 0) * 100
                
                messages.append(f"🎉 Congratulations! You've been promoted to {tier_change['new_tier'].title()} tier!")
                if fee_reduction > 0:
                    messages.append(f"💰 You now get {fee_reduction:.0f}% platform fee reduction!")
                if tier_benefits.get('priority_access'):
                    messages.append("⚡ You now have priority access to high-value jobs!")
            
            if new_badges:
                for badge in new_badges:
                    messages.append(f"{badge['icon']} New badge earned: {badge['name']}!")
            
            if messages:
                notification = NotificationQueue(
                    recipient_id=fixer.id,
                    notification_type='whatsapp',
                    category='achievement',
                    priority='normal',
                    title='Achievement Unlocked!',
                    message='\n'.join(messages),
                    context_data=json.dumps({
                        'tier_change': tier_change,
                        'new_badges': [badge['badge_code'] for badge in new_badges],
                        'current_tier': reputation.current_tier,
                        'tier_points': reputation.tier_points
                    })
                )
                
                db.add(notification)
                logger.info(f"Queued achievement notification for fixer {fixer.id}")
                
        except Exception as e:
            logger.error(f"Error sending achievement notification: {e}")

# Global instance
gamification_service = GamificationService()