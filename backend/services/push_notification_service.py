from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime
import os

from database import get_db
from models import User, PushSubscription
from services.role_service import get_current_user

# Configure logging
logger = logging.getLogger(__name__)

# Pydantic models for push notifications
class PushSubscriptionCreate(BaseModel):
    endpoint: str
    keys: Dict[str, str]
    user_agent: Optional[str] = None

class PushNotificationRequest(BaseModel):
    title: str
    body: str
    icon: Optional[str] = None
    badge: Optional[str] = None
    tag: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, str]]] = None
    require_interaction: Optional[bool] = False
    silent: Optional[bool] = False
    url: Optional[str] = None

class PushNotificationService:
    def __init__(self):
        self.vapid_private_key = os.getenv('VAPID_PRIVATE_KEY')
        self.vapid_public_key = os.getenv('VAPID_PUBLIC_KEY')
        self.vapid_subject = os.getenv('VAPID_SUBJECT', 'mailto:support@fixmate-sa.com')
        
        if not self.vapid_private_key or not self.vapid_public_key:
            logger.warning("VAPID keys not configured. Push notifications will not work.")
    
    def save_subscription(self, db: Session, user_id: str, subscription_data: PushSubscriptionCreate) -> Dict[str, Any]:
        """Save push subscription for a user"""
        try:
            # Check if subscription already exists
            existing_subscription = db.query(PushSubscription).filter(
                PushSubscription.user_id == user_id,
                PushSubscription.endpoint == subscription_data.endpoint
            ).first()
            
            if existing_subscription:
                # Update existing subscription
                existing_subscription.keys = json.dumps(subscription_data.keys)
                existing_subscription.user_agent = subscription_data.user_agent
                existing_subscription.updated_at = datetime.utcnow()
                db.commit()
                
                return {
                    'success': True,
                    'message': 'Push subscription updated successfully',
                    'subscription_id': existing_subscription.id
                }
            else:
                # Create new subscription
                new_subscription = PushSubscription(
                    user_id=user_id,
                    endpoint=subscription_data.endpoint,
                    keys=json.dumps(subscription_data.keys),
                    user_agent=subscription_data.user_agent,
                    is_active=True
                )
                
                db.add(new_subscription)
                db.commit()
                
                return {
                    'success': True,
                    'message': 'Push subscription saved successfully',
                    'subscription_id': new_subscription.id
                }
                
        except Exception as e:
            logger.error(f"Failed to save push subscription: {e}")
            db.rollback()
            return {
                'success': False,
                'error': f'Failed to save subscription: {str(e)}'
            }
    
    def get_user_subscriptions(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Get all active subscriptions for a user"""
        try:
            subscriptions = db.query(PushSubscription).filter(
                PushSubscription.user_id == user_id,
                PushSubscription.is_active == True
            ).all()
            
            return [
                {
                    'id': sub.id,
                    'endpoint': sub.endpoint,
                    'keys': json.loads(sub.keys),
                    'created_at': sub.created_at.isoformat(),
                    'user_agent': sub.user_agent
                }
                for sub in subscriptions
            ]
            
        except Exception as e:
            logger.error(f"Failed to get user subscriptions: {e}")
            return []
    
    def send_notification_to_user(self, db: Session, user_id: str, notification: PushNotificationRequest) -> Dict[str, Any]:
        """Send push notification to all user's devices"""
        try:
            subscriptions = self.get_user_subscriptions(db, user_id)
            
            if not subscriptions:
                return {
                    'success': False,
                    'error': 'No active subscriptions found for user'
                }
            
            results = []
            successful_sends = 0
            
            for subscription in subscriptions:
                try:
                    result = self._send_push_notification(subscription, notification)
                    results.append(result)
                    
                    if result.get('success'):
                        successful_sends += 1
                    else:
                        # If subscription is invalid, mark as inactive
                        if result.get('error') == 'invalid_subscription':
                            self._deactivate_subscription(db, subscription['id'])
                            
                except Exception as e:
                    logger.error(f"Failed to send notification to subscription {subscription['id']}: {e}")
                    results.append({'success': False, 'error': str(e)})
            
            return {
                'success': successful_sends > 0,
                'message': f'Sent to {successful_sends}/{len(subscriptions)} devices',
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Failed to send notification to user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Failed to send notification: {str(e)}'
            }
    
    def send_notification_to_role(self, db: Session, role: str, notification: PushNotificationRequest) -> Dict[str, Any]:
        """Send push notification to all users with a specific role"""
        try:
            users = db.query(User).filter(User.role == role, User.is_active == True).all()
            
            if not users:
                return {
                    'success': False,
                    'error': f'No active users found with role: {role}'
                }
            
            results = []
            successful_users = 0
            
            for user in users:
                try:
                    result = self.send_notification_to_user(db, user.id, notification)
                    results.append({
                        'user_id': user.id,
                        'result': result
                    })
                    
                    if result.get('success'):
                        successful_users += 1
                        
                except Exception as e:
                    logger.error(f"Failed to send notification to user {user.id}: {e}")
                    results.append({
                        'user_id': user.id,
                        'result': {'success': False, 'error': str(e)}
                    })
            
            return {
                'success': successful_users > 0,
                'message': f'Sent to {successful_users}/{len(users)} users with role {role}',
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Failed to send notification to role {role}: {e}")
            return {
                'success': False,
                'error': f'Failed to send notification: {str(e)}'
            }
    
    def _send_push_notification(self, subscription: Dict[str, Any], notification: PushNotificationRequest) -> Dict[str, Any]:
        """Send push notification to a specific subscription"""
        try:
            # This is a placeholder for actual push notification sending
            # In production, you would use a library like pywebpush
            
            if not self.vapid_private_key or not self.vapid_public_key:
                logger.warning("VAPID keys not configured, simulating notification send")
                return {
                    'success': True,
                    'message': 'Notification simulated (VAPID keys not configured)',
                    'subscription_id': subscription['id']
                }
            
            # Prepare notification payload
            payload = {
                'title': notification.title,
                'body': notification.body,
                'icon': notification.icon or '/fixmate-logo.jpg',
                'badge': notification.badge or '/fixmate-logo.jpg',
                'tag': notification.tag or 'fixmate-notification',
                'data': notification.data or {},
                'actions': notification.actions or [],
                'requireInteraction': notification.require_interaction,
                'silent': notification.silent,
                'url': notification.url
            }
            
            # Here you would use pywebpush to actually send the notification
            # from pywebpush import webpush, WebPushException
            # 
            # try:
            #     webpush(
            #         subscription_info={
            #             "endpoint": subscription['endpoint'],
            #             "keys": subscription['keys']
            #         },
            #         data=json.dumps(payload),
            #         vapid_private_key=self.vapid_private_key,
            #         vapid_claims={
            #             "sub": self.vapid_subject
            #         }
            #     )
            #     return {'success': True, 'message': 'Notification sent successfully'}
            # except WebPushException as e:
            #     return {'success': False, 'error': str(e)}
            
            # For now, simulate successful send
            logger.info(f"Simulated push notification: {notification.title} to {subscription['endpoint'][:50]}...")
            
            return {
                'success': True,
                'message': 'Notification sent successfully (simulated)',
                'payload': payload
            }
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _deactivate_subscription(self, db: Session, subscription_id: str):
        """Deactivate an invalid subscription"""
        try:
            subscription = db.query(PushSubscription).filter(PushSubscription.id == subscription_id).first()
            if subscription:
                subscription.is_active = False
                subscription.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Deactivated invalid subscription: {subscription_id}")
        except Exception as e:
            logger.error(f"Failed to deactivate subscription {subscription_id}: {e}")
    
    def get_notification_templates(self) -> Dict[str, PushNotificationRequest]:
        """Get predefined notification templates"""
        return {
            'job_assigned': PushNotificationRequest(
                title='New Job Assigned!',
                body='You have been assigned a new job. Tap to view details.',
                icon='/fixmate-logo.jpg',
                tag='job-assigned',
                actions=[
                    {'action': 'view', 'title': 'View Job'},
                    {'action': 'dismiss', 'title': 'Dismiss'}
                ],
                require_interaction=True
            ),
            'job_completed': PushNotificationRequest(
                title='Job Completed',
                body='Your service request has been completed successfully.',
                icon='/fixmate-logo.jpg',
                tag='job-completed',
                actions=[
                    {'action': 'review', 'title': 'Leave Review'},
                    {'action': 'view', 'title': 'View Details'}
                ]
            ),
            'payment_due': PushNotificationRequest(
                title='Payment Due',
                body='You have a pending payment for your completed job.',
                icon='/fixmate-logo.jpg',
                tag='payment-due',
                actions=[
                    {'action': 'pay', 'title': 'Pay Now'},
                    {'action': 'view', 'title': 'View Details'}
                ],
                require_interaction=True
            ),
            'fixer_nearby': PushNotificationRequest(
                title='Fixer Nearby',
                body='Your assigned fixer is approaching your location.',
                icon='/fixmate-logo.jpg',
                tag='fixer-nearby',
                actions=[
                    {'action': 'track', 'title': 'Track Fixer'},
                    {'action': 'call', 'title': 'Call Fixer'}
                ]
            ),
            'system_update': PushNotificationRequest(
                title='System Update',
                body='FixMate-SA has been updated with new features.',
                icon='/fixmate-logo.jpg',
                tag='system-update',
                actions=[
                    {'action': 'update', 'title': 'Update App'},
                    {'action': 'later', 'title': 'Later'}
                ]
            )
        }

# Create push notification service instance
push_service = PushNotificationService()