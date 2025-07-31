import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import logging
import requests

from models import Job, JobTracking, User, Fixer, NotificationQueue
from services.ai_service import ai_service

logger = logging.getLogger(__name__)

class RealTimeTrackingService:
    """
    Service for managing real-time job tracking with GPS and ETA.
    Handles live location updates, arrival notifications, and route optimization.
    """
    
    def __init__(self):
        self.max_tracking_distance = 100  # km - maximum distance to track
        self.eta_update_interval = 300  # seconds - how often to update ETA
        self.location_accuracy_threshold = 100  # meters - minimum GPS accuracy
        self.arrival_threshold = 100  # meters - distance to consider "arrived"
        
        # Google Maps API (in production, use environment variable)
        self.google_maps_api_key = None  # Set via environment variable
        
    def start_job_tracking(
        self, 
        db: Session, 
        job_id: str, 
        fixer_id: str, 
        departure_location: Dict = None
    ) -> Dict:
        """
        Start real-time tracking for a job when fixer begins journey.
        
        Args:
            job_id: Job to track
            fixer_id: Fixer performing the job
            departure_location: Optional starting location {"lat": float, "lng": float}
        """
        try:
            # Validate job and fixer
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                return {'success': False, 'error': 'Job not found'}
            
            fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
            if not fixer:
                return {'success': False, 'error': 'Fixer not found'}
            
            if job.fixer_id != fixer_id:
                return {'success': False, 'error': 'Fixer not assigned to this job'}
            
            # Check if tracking already exists
            existing_tracking = db.query(JobTracking).filter(
                JobTracking.job_id == job_id,
                JobTracking.tracking_status != 'completed'
            ).first()
            
            if existing_tracking:
                return {'success': False, 'error': 'Tracking already active for this job'}
            
            # Create tracking record
            tracking = JobTracking(
                job_id=job_id,
                fixer_id=fixer_id,
                tracking_status='en_route',
                departure_time=datetime.utcnow(),
                last_status_update=datetime.utcnow()
            )
            
            # Set initial location if provided
            if departure_location:
                tracking.current_latitude = departure_location.get('lat')
                tracking.current_longitude = departure_location.get('lng')
                tracking.location_updated_at = datetime.utcnow()
                
                # Calculate initial ETA if job has coordinates
                if job.latitude and job.longitude:
                    eta_result = self._calculate_eta(
                        departure_location,
                        {'lat': job.latitude, 'lng': job.longitude}
                    )
                    
                    if eta_result['success']:
                        tracking.estimated_arrival = datetime.utcnow() + timedelta(minutes=eta_result['duration'])
                        tracking.estimated_distance = eta_result['distance']
                        tracking.estimated_duration = eta_result['duration']
                        tracking.route_data = json.dumps(eta_result.get('route_data', {}))
            
            # Update job status
            job.tracking_active = True
            job.fixer_departure_time = tracking.departure_time
            job.status = 'in_progress'
            job.updated_at = datetime.utcnow()
            
            db.add(tracking)
            
            try:
                db.commit()
                
                # Send notification to client
                self._notify_tracking_started(db, job, tracking)
                
                return {
                    'success': True,
                    'message': 'Job tracking started successfully',
                    'tracking_id': tracking.id,
                    'estimated_arrival': tracking.estimated_arrival.isoformat() if tracking.estimated_arrival else None,
                    'estimated_duration': tracking.estimated_duration
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error starting tracking: {e}")
                return {'success': False, 'error': 'Database error occurred'}
            
        except Exception as e:
            logger.error(f"Error starting job tracking: {e}")
            return {'success': False, 'error': f'Failed to start tracking: {str(e)}'}
    
    def update_fixer_location(
        self, 
        db: Session, 
        job_id: str, 
        fixer_id: str, 
        location: Dict,
        accuracy: float = None
    ) -> Dict:
        """
        Update fixer's current location and recalculate ETA.
        
        Args:
            location: {"lat": float, "lng": float}
            accuracy: GPS accuracy in meters
        """
        try:
            # Get active tracking
            tracking = db.query(JobTracking).filter(
                JobTracking.job_id == job_id,
                JobTracking.fixer_id == fixer_id,
                JobTracking.tracking_status.in_(['en_route', 'arrived'])
            ).first()
            
            if not tracking:
                return {'success': False, 'error': 'No active tracking found'}
            
            # Validate location accuracy
            if accuracy and accuracy > self.location_accuracy_threshold:
                logger.warning(f"Low GPS accuracy: {accuracy}m for job {job_id}")
            
            # Update location
            tracking.current_latitude = location['lat']
            tracking.current_longitude = location['lng']
            tracking.location_accuracy = accuracy
            tracking.location_updated_at = datetime.utcnow()
            tracking.updated_at = datetime.utcnow()
            
            # Get job details
            job = tracking.job
            if not job:
                return {'success': False, 'error': 'Associated job not found'}
            
            # Check if fixer has arrived
            if job.latitude and job.longitude:
                distance_to_job = self._calculate_distance(
                    location,
                    {'lat': job.latitude, 'lng': job.longitude}
                )
                
                # Update tracking distance
                tracking.estimated_distance = distance_to_job
                
                # Check for arrival
                if distance_to_job <= (self.arrival_threshold / 1000) and tracking.tracking_status != 'arrived':
                    tracking.tracking_status = 'arrived'
                    tracking.actual_arrival = datetime.utcnow()
                    job.fixer_arrival_time = tracking.actual_arrival
                    job.updated_at = datetime.utcnow()
                    
                    # Calculate arrival accuracy
                    if tracking.estimated_arrival:
                        time_diff = (tracking.actual_arrival - tracking.estimated_arrival).total_seconds() / 60
                        tracking.arrival_accuracy = abs(time_diff)
                    
                    # Notify client of arrival
                    self._notify_fixer_arrived(db, job, tracking)
                    
                    logger.info(f"Fixer arrived at job {job_id}")
                
                # Recalculate ETA if still en route
                elif tracking.tracking_status == 'en_route':
                    eta_result = self._calculate_eta(
                        location,
                        {'lat': job.latitude, 'lng': job.longitude}
                    )
                    
                    if eta_result['success']:
                        new_eta = datetime.utcnow() + timedelta(minutes=eta_result['duration'])
                        
                        # Only update if ETA changed significantly (>2 minutes)
                        if not tracking.estimated_arrival or abs(
                            (new_eta - tracking.estimated_arrival).total_seconds()
                        ) > 120:
                            tracking.estimated_arrival = new_eta
                            tracking.estimated_duration = eta_result['duration']
                            
                            # Notify client of ETA update
                            self._notify_eta_update(db, job, tracking)
            
            try:
                db.commit()
                
                return {
                    'success': True,
                    'message': 'Location updated successfully',
                    'tracking_status': tracking.tracking_status,
                    'estimated_arrival': tracking.estimated_arrival.isoformat() if tracking.estimated_arrival else None,
                    'distance_to_job': tracking.estimated_distance,
                    'arrival_accuracy': tracking.arrival_accuracy
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error updating location: {e}")
                return {'success': False, 'error': 'Database error occurred'}
            
        except Exception as e:
            logger.error(f"Error updating fixer location: {e}")
            return {'success': False, 'error': f'Failed to update location: {str(e)}'}
    
    def complete_job_tracking(
        self, 
        db: Session, 
        job_id: str, 
        fixer_id: str
    ) -> Dict:
        """
        Complete job tracking when work is finished.
        """
        try:
            # Get active tracking
            tracking = db.query(JobTracking).filter(
                JobTracking.job_id == job_id,
                JobTracking.fixer_id == fixer_id,
                JobTracking.tracking_status != 'completed'
            ).first()
            
            if not tracking:
                return {'success': False, 'error': 'No active tracking found'}
            
            # Update tracking status
            tracking.tracking_status = 'completed'
            tracking.updated_at = datetime.utcnow()
            
            # Update job
            job = tracking.job
            if job:
                job.tracking_active = False
                job.updated_at = datetime.utcnow()
            
            # Calculate route efficiency if we have route data
            if tracking.departure_time and tracking.actual_arrival:
                actual_duration = (tracking.actual_arrival - tracking.departure_time).total_seconds() / 60
                if tracking.estimated_duration:
                    efficiency = min(100, (tracking.estimated_duration / actual_duration) * 100)
                    tracking.route_efficiency = efficiency
            
            try:
                db.commit()
                
                return {
                    'success': True,
                    'message': 'Job tracking completed successfully',
                    'total_duration': actual_duration if 'actual_duration' in locals() else None,
                    'route_efficiency': tracking.route_efficiency
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error completing tracking: {e}")
                return {'success': False, 'error': 'Database error occurred'}
            
        except Exception as e:
            logger.error(f"Error completing job tracking: {e}")
            return {'success': False, 'error': f'Failed to complete tracking: {str(e)}'}
    
    def get_job_tracking_status(self, db: Session, job_id: str) -> Optional[Dict]:
        """
        Get current tracking status for a job.
        """
        try:
            tracking = db.query(JobTracking).filter(
                JobTracking.job_id == job_id
            ).order_by(desc(JobTracking.created_at)).first()
            
            if not tracking:
                return None
            
            return {
                'tracking_id': tracking.id,
                'job_id': tracking.job_id,
                'fixer_id': tracking.fixer_id,
                'fixer_name': tracking.fixer.name if tracking.fixer else 'Unknown',
                'status': tracking.tracking_status,
                'current_location': {
                    'lat': tracking.current_latitude,
                    'lng': tracking.current_longitude,
                    'accuracy': tracking.location_accuracy,
                    'updated_at': tracking.location_updated_at.isoformat() if tracking.location_updated_at else None
                } if tracking.current_latitude and tracking.current_longitude else None,
                'estimated_arrival': tracking.estimated_arrival.isoformat() if tracking.estimated_arrival else None,
                'actual_arrival': tracking.actual_arrival.isoformat() if tracking.actual_arrival else None,
                'estimated_distance': tracking.estimated_distance,
                'estimated_duration': tracking.estimated_duration,
                'departure_time': tracking.departure_time.isoformat() if tracking.departure_time else None,
                'arrival_accuracy': tracking.arrival_accuracy,
                'route_efficiency': tracking.route_efficiency,
                'last_update': tracking.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting tracking status: {e}")
            return None
    
    def _calculate_distance(self, point1: Dict, point2: Dict) -> float:
        """
        Calculate distance between two GPS coordinates using Haversine formula.
        Returns distance in kilometers.
        """
        try:
            lat1, lon1 = point1['lat'], point1['lng']
            lat2, lon2 = point2['lat'], point2['lng']
            
            # Haversine formula
            R = 6371  # Earth's radius in kilometers
            
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)
            
            a = (math.sin(delta_lat / 2) ** 2 +
                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            
            return R * c
            
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            return float('inf')
    
    def _calculate_eta(self, origin: Dict, destination: Dict) -> Dict:
        """
        Calculate ETA using route optimization.
        In production, this would use Google Maps API or similar service.
        """
        try:
            # For demo purposes, use simple distance/speed calculation
            distance = self._calculate_distance(origin, destination)
            
            # Assume average speed of 40 km/h in urban areas
            average_speed = 40  # km/h
            duration_hours = distance / average_speed
            duration_minutes = duration_hours * 60
            
            # Add buffer for traffic and stops
            buffer_minutes = max(5, duration_minutes * 0.2)
            total_duration = duration_minutes + buffer_minutes
            
            return {
                'success': True,
                'distance': distance,
                'duration': int(total_duration),
                'route_data': {
                    'average_speed_assumed': average_speed,
                    'buffer_added': buffer_minutes,
                    'calculation_method': 'haversine_estimate'
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating ETA: {e}")
            return {'success': False, 'error': str(e)}
    
    def _notify_tracking_started(self, db: Session, job: Job, tracking: JobTracking):
        """
        Send notification to client that tracking has started.
        """
        try:
            if not job.user:
                return
            
            eta_text = ''
            if tracking.estimated_arrival:
                eta_text = f" ETA: {tracking.estimated_arrival.strftime('%H:%M')}"
            
            notification = NotificationQueue(
                recipient_id=job.user.id,
                notification_type='whatsapp',  # or 'sms' based on user preference
                category='job_update',
                title='Fixer En Route',
                message=f'Your fixer {tracking.fixer.name} is on the way to your location.{eta_text}',
                related_job_id=job.id,
                context_data=json.dumps({
                    'tracking_id': tracking.id,
                    'fixer_name': tracking.fixer.name,
                    'estimated_arrival': tracking.estimated_arrival.isoformat() if tracking.estimated_arrival else None
                })
            )
            
            db.add(notification)
            logger.info(f"Queued tracking started notification for job {job.id}")
            
        except Exception as e:
            logger.error(f"Error queuing tracking notification: {e}")
    
    def _notify_eta_update(self, db: Session, job: Job, tracking: JobTracking):
        """
        Send ETA update notification to client.
        """
        try:
            if not job.user or not tracking.estimated_arrival:
                return
            
            notification = NotificationQueue(
                recipient_id=job.user.id,
                notification_type='whatsapp',
                category='eta_update',
                title='Updated Arrival Time',
                message=f'Updated ETA: Your fixer will arrive around {tracking.estimated_arrival.strftime("%H:%M")}',
                related_job_id=job.id,
                context_data=json.dumps({
                    'tracking_id': tracking.id,
                    'new_eta': tracking.estimated_arrival.isoformat()
                })
            )
            
            db.add(notification)
            logger.info(f"Queued ETA update notification for job {job.id}")
            
        except Exception as e:
            logger.error(f"Error queuing ETA notification: {e}")
    
    def _notify_fixer_arrived(self, db: Session, job: Job, tracking: JobTracking):
        """
        Send arrival notification to client.
        """
        try:
            if not job.user:
                return
            
            notification = NotificationQueue(
                recipient_id=job.user.id,
                notification_type='whatsapp',
                category='job_update',
                priority='high',
                title='Fixer Arrived',
                message=f'{tracking.fixer.name} has arrived at your location and is ready to start the work.',
                related_job_id=job.id,
                context_data=json.dumps({
                    'tracking_id': tracking.id,
                    'arrival_time': tracking.actual_arrival.isoformat()
                })
            )
            
            db.add(notification)
            logger.info(f"Queued arrival notification for job {job.id}")
            
        except Exception as e:
            logger.error(f"Error queuing arrival notification: {e}")

# Global instance
real_time_tracking_service = RealTimeTrackingService()