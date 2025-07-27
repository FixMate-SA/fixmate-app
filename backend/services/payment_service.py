import os
import requests
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

load_dotenv()

class PaymentService:
    def __init__(self):
        self.payfast_merchant_id = os.getenv("PAYFAST_MERCHANT_ID", "test_merchant")
        self.payfast_merchant_key = os.getenv("PAYFAST_MERCHANT_KEY", "test_key")
        self.payfast_url = "https://sandbox.payfast.co.za/eng/process"  # Change to live for production
        self.fixer_service_fee = 20.00  # R20 service fee for fixers
        
    def check_fixer_payment_status(self, fixer_id: str, db: Session) -> Dict[str, Any]:
        """
        Check if fixer has outstanding payments and can receive job assignments
        """
        try:
            from models import Fixer, FixerPayment
            
            fixer = db.query(Fixer).filter(Fixer.id == fixer_id).first()
            if not fixer:
                return {"error": "Fixer not found", "can_receive_jobs": False}
            
            # Get outstanding payments
            outstanding_payments = db.query(FixerPayment).filter(
                and_(
                    FixerPayment.fixer_id == fixer_id,
                    or_(
                        FixerPayment.status == "pending",
                        FixerPayment.status == "overdue"
                    )
                )
            ).all()
            
            total_outstanding = sum([payment.amount for payment in outstanding_payments])
            overdue_count = len([p for p in outstanding_payments if p.status == "overdue"])
            
            # Determine if fixer can receive jobs
            can_receive_jobs = (
                fixer.payment_status == "current" and 
                total_outstanding < self.fixer_service_fee and
                overdue_count == 0
            )
            
            return {
                "fixer_id": fixer_id,
                "payment_status": fixer.payment_status,
                "total_outstanding": total_outstanding,
                "overdue_payments": overdue_count,
                "can_receive_jobs": can_receive_jobs,
                "outstanding_payments": [{
                    "id": p.id,
                    "amount": p.amount,
                    "status": p.status,
                    "due_date": p.due_date.isoformat() if p.due_date else None,
                    "description": p.description
                } for p in outstanding_payments]
            }
            
        except Exception as e:
            return {"error": str(e), "can_receive_jobs": False}
    
    def create_fixer_service_fee(self, fixer_id: str, description: str, db: Session) -> Dict[str, Any]:
        """
        Create R20 service fee for fixer when they get a job
        """
        try:
            from models import FixerPayment
            
            # Create new payment record
            payment = FixerPayment(
                fixer_id=fixer_id,
                amount=self.fixer_service_fee,
                payment_type="service_fee",
                payment_method="pending",
                status="pending",
                description=description,
                due_date=datetime.now() + timedelta(days=7)  # 7 days to pay
            )
            
            db.add(payment)
            db.commit()
            db.refresh(payment)
            
            return {
                "success": True,
                "payment_id": payment.id,
                "amount": payment.amount,
                "due_date": payment.due_date.isoformat(),
                "message": f"Service fee of R{self.fixer_service_fee:.2f} created for fixer"
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def update_fixer_payment_status(self, db: Session) -> Dict[str, Any]:
        """
        Update fixer payment statuses and block fixers with overdue payments
        """
        try:
            from models import Fixer, FixerPayment
            
            # Mark overdue payments
            overdue_payments = db.query(FixerPayment).filter(
                and_(
                    FixerPayment.status == "pending",
                    FixerPayment.due_date < datetime.now()
                )
            ).all()
            
            for payment in overdue_payments:
                payment.status = "overdue"
            
            # Update fixer statuses based on payments
            fixers = db.query(Fixer).all()
            for fixer in fixers:
                outstanding = db.query(FixerPayment).filter(
                    and_(
                        FixerPayment.fixer_id == fixer.id,
                        or_(
                            FixerPayment.status == "pending",
                            FixerPayment.status == "overdue"
                        )
                    )
                ).count()
                
                if outstanding > 0:
                    fixer.payment_status = "overdue"
                else:
                    fixer.payment_status = "current"
            
            db.commit()
            
            return {
                "success": True,
                "overdue_payments_updated": len(overdue_payments),
                "message": "Payment statuses updated successfully"
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def settle_payment(self, payment_id: str, payment_method: str, reference: str, db: Session) -> Dict[str, Any]:
        """
        Mark a payment as settled
        """
        try:
            from models import FixerPayment, Fixer
            
            payment = db.query(FixerPayment).filter(FixerPayment.id == payment_id).first()
            if not payment:
                return {"success": False, "error": "Payment not found"}
            
            payment.status = "paid"
            payment.payment_method = payment_method
            payment.payment_reference = reference
            payment.paid_date = datetime.now()
            
            # Update fixer status
            fixer = db.query(Fixer).filter(Fixer.id == payment.fixer_id).first()
            if fixer:
                # Check if fixer has any remaining outstanding payments
                remaining_outstanding = db.query(FixerPayment).filter(
                    and_(
                        FixerPayment.fixer_id == fixer.id,
                        or_(
                            FixerPayment.status == "pending",
                            FixerPayment.status == "overdue"
                        )
                    )
                ).count()
                
                if remaining_outstanding == 0:
                    fixer.payment_status = "current"
            
            db.commit()
            
            return {
                "success": True,
                "message": f"Payment of R{payment.amount:.2f} settled successfully",
                "payment_id": payment.id,
                "fixer_can_receive_jobs": fixer.payment_status == "current" if fixer else False
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
    
    def get_fixer_payment_history(self, fixer_id: str, db: Session) -> List[Dict[str, Any]]:
        """
        Get payment history for a fixer
        """
        try:
            from models import FixerPayment
            
            payments = db.query(FixerPayment).filter(
                FixerPayment.fixer_id == fixer_id
            ).order_by(FixerPayment.created_at.desc()).all()
            
            return [{
                "id": p.id,
                "amount": p.amount,
                "payment_type": p.payment_type,
                "payment_method": p.payment_method,
                "status": p.status,
                "description": p.description,
                "due_date": p.due_date.isoformat() if p.due_date else None,
                "paid_date": p.paid_date.isoformat() if p.paid_date else None,
                "created_at": p.created_at.isoformat()
            } for p in payments]
            
        except Exception as e:
            return []
        
    def create_payment_request(self, amount: float, description: str, user_email: str, user_name: str) -> Dict[str, Any]:
        """
        Create PayFast payment request for EFT and card payments
        """
        try:
            payment_data = {
                'merchant_id': self.payfast_merchant_id,
                'merchant_key': self.payfast_merchant_key,
                'return_url': f"{os.getenv('FRONTEND_URL')}/payment/success",
                'cancel_url': f"{os.getenv('FRONTEND_URL')}/payment/cancel",
                'notify_url': f"{os.getenv('BACKEND_URL')}/api/payment/notify",
                'name_first': user_name.split()[0] if user_name else "Customer",
                'name_last': user_name.split()[-1] if len(user_name.split()) > 1 else "Customer",
                'email_address': user_email,
                'amount': f"{amount:.2f}",
                'item_name': description,
                'item_description': description,
                'payment_method': 'eft',  # Support EFT payments
                'custom_str1': 'fixmate_payment',
                'custom_str2': f'job_payment_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            }
            
            return {
                'success': True,
                'payment_url': self.payfast_url,
                'payment_data': payment_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_airtime_payment(self, phone_number: str, amount: float, description: str) -> Dict[str, Any]:
        """
        Create airtime-based payment (South African innovation)
        """
        try:
            # This would integrate with airtime providers like MTN, Vodacom, Cell C
            # For now, we'll simulate the process
            
            payment_data = {
                'type': 'airtime',
                'phone_number': phone_number,
                'amount': amount,
                'description': description,
                'provider': self._detect_network_provider(phone_number),
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            return {
                'success': True,
                'payment_id': f"airtime_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'payment_data': payment_data,
                'instructions': f"Send airtime worth R{amount:.2f} to 082-FIXMATE (082-349-6283) with reference '{description}'"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_cash_collection_point(self, location: str, amount: float, description: str) -> Dict[str, Any]:
        """
        Create cash collection point payment (Shoprite, Pick n Pay, etc.)
        """
        try:
            collection_points = {
                'johannesburg': ['Shoprite Mayfair', 'Pick n Pay Randburg', 'Checkers Sandton'],
                'cape_town': ['Shoprite Bellville', 'Pick n Pay Canal Walk', 'Checkers V&A'],
                'durban': ['Shoprite Chatsworth', 'Pick n Pay Westville', 'Checkers Gateway'],
                'pretoria': ['Shoprite Centurion', 'Pick n Pay Menlyn', 'Checkers Brooklyn']
            }
            
            city = location.lower()
            available_points = collection_points.get(city, collection_points['johannesburg'])
            
            payment_data = {
                'type': 'cash_collection',
                'amount': amount,
                'description': description,
                'collection_points': available_points,
                'reference_number': f"FM{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'expires_at': (datetime.now()).isoformat(),
                'instructions': f"Visit any of these locations and pay R{amount:.2f} with reference FM{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            return {
                'success': True,
                'payment_id': f"cash_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'payment_data': payment_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_stokvel_payment(self, stokvel_name: str, amount: float, description: str) -> Dict[str, Any]:
        """
        Create stokvel (community savings group) payment
        """
        try:
            payment_data = {
                'type': 'stokvel',
                'stokvel_name': stokvel_name,
                'amount': amount,
                'description': description,
                'payment_id': f"stokvel_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'status': 'pending_approval',
                'instructions': f"Your stokvel '{stokvel_name}' will be contacted to approve payment of R{amount:.2f} for {description}"
            }
            
            return {
                'success': True,
                'payment_id': payment_data['payment_id'],
                'payment_data': payment_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_layby_payment(self, total_amount: float, deposit_amount: float, description: str, installments: int) -> Dict[str, Any]:
        """
        Create lay-by payment plan
        """
        try:
            monthly_payment = (total_amount - deposit_amount) / installments
            
            payment_data = {
                'type': 'layby',
                'total_amount': total_amount,
                'deposit_amount': deposit_amount,
                'monthly_payment': monthly_payment,
                'installments': installments,
                'description': description,
                'payment_id': f"layby_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'status': 'active',
                'next_payment_date': (datetime.now()).isoformat()
            }
            
            return {
                'success': True,
                'payment_id': payment_data['payment_id'],
                'payment_data': payment_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _detect_network_provider(self, phone_number: str) -> str:
        """
        Detect South African network provider from phone number
        """
        # Remove country code and spaces
        number = phone_number.replace('+27', '').replace(' ', '')
        
        # MTN prefixes
        mtn_prefixes = ['83', '63', '73', '74', '76', '77', '78', '79']
        # Vodacom prefixes  
        vodacom_prefixes = ['82', '72', '62', '71', '81', '84']
        # Cell C prefixes
        cellc_prefixes = ['84', '74', '64', '73', '76', '77', '78', '79']
        
        prefix = number[:2]
        
        if prefix in mtn_prefixes:
            return 'mtn'
        elif prefix in vodacom_prefixes:
            return 'vodacom'
        elif prefix in cellc_prefixes:
            return 'cellc'
        else:
            return 'unknown'
    
    def verify_payment(self, payment_id: str, payment_type: str) -> Dict[str, Any]:
        """
        Verify payment status
        """
        try:
            # This would integrate with actual payment providers
            # For now, we'll simulate verification
            
            return {
                'success': True,
                'payment_id': payment_id,
                'status': 'completed',
                'verified_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
payment_service = PaymentService()