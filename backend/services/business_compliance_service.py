import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from models import BusinessComplianceRequest, User
from services.whatsapp_service import WhatsAppService
from services.sms_service import sms_service
from services.ai_service import ai_service

class BusinessComplianceService:
    """
    Service for handling business compliance assistance requests
    """
    
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        
        # Business compliance categories
        self.COMPLIANCE_CATEGORIES = {
            'company_registration': {
                'name': 'Company Registration',
                'description': 'Assistance with registering new companies (Pty Ltd, CC, etc.)',
                'typical_docs': ['ID copies', 'Proof of address', 'Company name reservations'],
                'processing_time': '10-15 business days',
                'cost_range': 'R1,500 - R3,500'
            },
            'sars_registration': {
                'name': 'SARS Registration & Tax Compliance',
                'description': 'VAT registration, PAYE, UIF, SDL registration and compliance',
                'typical_docs': ['Company registration documents', 'Banking details', 'Director details'],
                'processing_time': '5-10 business days',
                'cost_range': 'R800 - R2,500'
            },
            'labour_compliance': {
                'name': 'Labour Law Compliance',
                'description': 'Employment contracts, labour law compliance, CCMA assistance',
                'typical_docs': ['Employee details', 'Existing contracts', 'Company policies'],
                'processing_time': '3-7 business days',
                'cost_range': 'R1,000 - R2,000'
            },
            'bbbee_certification': {
                'name': 'B-BBEE Certification',
                'description': 'B-BBEE certificate applications and compliance management',
                'typical_docs': ['Financial statements', 'Ownership details', 'Skills development records'],
                'processing_time': '15-30 business days',
                'cost_range': 'R3,000 - R8,000'
            },
            'licensing_permits': {
                'name': 'Licensing & Permits',
                'description': 'Trading licenses, municipal permits, industry-specific licenses',
                'typical_docs': ['Zoning certificates', 'Health certificates', 'Fire certificates'],
                'processing_time': '10-20 business days',
                'cost_range': 'R500 - R3,000'
            },
            'financial_compliance': {
                'name': 'Financial Compliance',
                'description': 'Annual returns, financial statements, audit compliance',
                'typical_docs': ['Bank statements', 'Trial balance', 'Supporting documents'],
                'processing_time': '5-15 business days',
                'cost_range': 'R2,000 - R5,000'
            }
        }
    
    def create_compliance_request(self, db: Session, user_id: str, category: str, 
                                description: str, urgency_level: str = 'normal', 
                                contact_preference: str = 'whatsapp') -> Dict[str, Any]:
        """
        Create a new business compliance assistance request
        """
        try:
            # Validate category
            if category not in self.COMPLIANCE_CATEGORIES:
                raise ValueError(f"Invalid compliance category: {category}")
            
            # Get user details
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Create compliance request
            compliance_request = BusinessComplianceRequest(
                id=str(uuid.uuid4()),
                user_id=user_id,
                category=category,
                description=description,
                urgency_level=urgency_level,
                contact_preference=contact_preference,
                status='submitted',
                created_at=datetime.utcnow()
            )
            
            db.add(compliance_request)
            db.commit()
            db.refresh(compliance_request)
            
            # Send confirmation message
            self._send_confirmation_message(user, compliance_request)
            
            # Send internal notification
            self._notify_compliance_team(compliance_request, user)
            
            return {
                'success': True,
                'request_id': compliance_request.id,
                'message': 'Compliance assistance request submitted successfully',
                'estimated_response_time': self.COMPLIANCE_CATEGORIES[category]['processing_time'],
                'cost_estimate': self.COMPLIANCE_CATEGORIES[category]['cost_range']
            }
            
        except Exception as e:
            db.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to submit compliance request'
            }
    
    def get_compliance_categories(self) -> Dict[str, Any]:
        """
        Get all available compliance categories with descriptions
        """
        return self.COMPLIANCE_CATEGORIES
    
    def get_user_requests(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all compliance requests for a specific user
        """
        try:
            requests = db.query(BusinessComplianceRequest).filter(
                BusinessComplianceRequest.user_id == user_id
            ).order_by(BusinessComplianceRequest.created_at.desc()).all()
            
            return [
                {
                    'id': req.id,
                    'category': req.category,
                    'category_name': self.COMPLIANCE_CATEGORIES.get(req.category, {}).get('name', req.category),
                    'description': req.description,
                    'status': req.status,
                    'urgency_level': req.urgency_level,
                    'created_at': req.created_at.isoformat(),
                    'updated_at': req.updated_at.isoformat() if req.updated_at else None,
                    'admin_notes': req.admin_notes,
                    'estimated_cost': req.estimated_cost,
                    'estimated_completion': req.estimated_completion.isoformat() if req.estimated_completion else None
                }
                for req in requests
            ]
            
        except Exception as e:
            print(f"Error getting user requests: {e}")
            return []
    
    def update_request_status(self, db: Session, request_id: str, status: str, 
                            admin_notes: str = None, estimated_cost: float = None,
                            estimated_completion: datetime = None) -> Dict[str, Any]:
        """
        Update compliance request status (Admin function)
        """
        try:
            request = db.query(BusinessComplianceRequest).filter(
                BusinessComplianceRequest.id == request_id
            ).first()
            
            if not request:
                return {'success': False, 'error': 'Request not found'}
            
            old_status = request.status
            request.status = status
            request.updated_at = datetime.utcnow()
            
            if admin_notes:
                request.admin_notes = admin_notes
            if estimated_cost:
                request.estimated_cost = estimated_cost
            if estimated_completion:
                request.estimated_completion = estimated_completion
            
            db.commit()
            
            # Notify user of status change
            user = db.query(User).filter(User.id == request.user_id).first()
            if user:
                self._send_status_update_message(user, request, old_status)
            
            return {
                'success': True,
                'message': f'Request status updated to {status}'
            }
            
        except Exception as e:
            db.rollback()
            return {'success': False, 'error': str(e)}
    
    def _send_confirmation_message(self, user: User, request: BusinessComplianceRequest):
        """
        Send confirmation message to user
        """
        try:
            category_info = self.COMPLIANCE_CATEGORIES[request.category]
            
            message = f"""🏢 FixMate-SA Business Compliance Assistant

Thank you {user.first_name}! We've received your request for:

📋 Service: {category_info['name']}
🆔 Request ID: {request.id[:8]}...
⏱️ Processing Time: {category_info['processing_time']}
💰 Cost Estimate: {category_info['cost_range']}

Our compliance experts will review your request and contact you within 24 hours with:
• Detailed requirements list
• Exact pricing quote
• Timeline confirmation

You can track your request status in the FixMate-SA app under 'Business Compliance'.

Questions? Reply to this message or call us directly.

Best regards,
FixMate-SA Compliance Team"""

            # Send via WhatsApp or SMS based on preference
            if request.contact_preference == 'whatsapp' and user.phone.startswith('whatsapp:'):
                self.whatsapp_service.send_whatsapp_message(user.phone, message)
            else:
                sms_service.send_sms(user.phone, message)
                
        except Exception as e:
            print(f"Error sending confirmation message: {e}")
    
    def _notify_compliance_team(self, request: BusinessComplianceRequest, user: User):
        """
        Notify internal compliance team of new request
        """
        try:
            category_info = self.COMPLIANCE_CATEGORIES[request.category]
            
            # Format internal notification
            internal_message = f"""🚨 NEW COMPLIANCE REQUEST

Client: {user.first_name} {user.last_name}
Phone: {user.phone}
Role: {user.role.title()}
Town: {user.town}

Service: {category_info['name']}
Urgency: {request.urgency_level.title()}
Request ID: {request.id}

Description:
{request.description}

Contact Preference: {request.contact_preference.title()}
Submitted: {request.created_at.strftime('%Y-%m-%d %H:%M')}

Please assign to compliance specialist and respond within 24 hours."""
            
            # Send to compliance team (using FixMate business WhatsApp)
            compliance_phone = "27754466571"  # Your business number
            self.whatsapp_service.send_whatsapp_message(
                f"whatsapp:+{compliance_phone}", 
                internal_message
            )
            
        except Exception as e:
            print(f"Error notifying compliance team: {e}")
    
    def _send_status_update_message(self, user: User, request: BusinessComplianceRequest, old_status: str):
        """
        Send status update message to user
        """
        try:
            status_messages = {
                'in_review': '🔍 Your compliance request is now under review by our experts.',
                'quote_sent': '💰 We\'ve prepared a detailed quote for your compliance needs.',
                'in_progress': '⚡ Work has begun on your compliance request!',
                'completed': '✅ Your compliance request has been completed successfully!',
                'on_hold': '⏸️ Your request is temporarily on hold - we\'ll contact you soon.',
                'cancelled': '❌ Your compliance request has been cancelled.'
            }
            
            message = f"""🏢 FixMate-SA Compliance Update

Request ID: {request.id[:8]}...
Status Update: {old_status.title()} → {request.status.title()}

{status_messages.get(request.status, 'Your request status has been updated.')}"""
            
            if request.admin_notes:
                message += f"\n\nNotes: {request.admin_notes}"
            
            if request.estimated_cost:
                message += f"\n💰 Estimated Cost: R{request.estimated_cost:,.2f}"
            
            if request.estimated_completion:
                message += f"\n📅 Estimated Completion: {request.estimated_completion.strftime('%Y-%m-%d')}"
            
            message += "\n\nView full details in the FixMate-SA app under 'Business Compliance'."
            
            # Send via preferred contact method
            if request.contact_preference == 'whatsapp' and user.phone.startswith('whatsapp:'):
                self.whatsapp_service.send_whatsapp_message(user.phone, message)
            else:
                sms_service.send_sms(user.phone, message)
                
        except Exception as e:
            print(f"Error sending status update: {e}")
    
    def generate_compliance_checklist(self, category: str) -> Dict[str, Any]:
        """
        Generate a detailed checklist for a specific compliance category
        """
        if category not in self.COMPLIANCE_CATEGORIES:
            return {'error': 'Invalid category'}
        
        category_info = self.COMPLIANCE_CATEGORIES[category]
        
        # Use AI to generate detailed checklist
        try:
            prompt = f"""Generate a detailed compliance checklist for {category_info['name']} in South Africa. 
            Include:
            1. Required documents
            2. Step-by-step process
            3. Government departments involved
            4. Common pitfalls to avoid
            5. Timeline expectations
            
            Format as a structured, actionable checklist."""
            
            checklist = ai_service.generate_content(prompt)
            
            return {
                'category': category,
                'name': category_info['name'],
                'checklist': checklist,
                'typical_docs': category_info['typical_docs'],
                'processing_time': category_info['processing_time'],
                'cost_range': category_info['cost_range']
            }
            
        except Exception as e:
            print(f"Error generating checklist: {e}")
            return {
                'category': category,
                'name': category_info['name'],
                'basic_info': category_info,
                'error': 'Could not generate detailed checklist'
            }

# Create global instance
business_compliance_service = BusinessComplianceService()