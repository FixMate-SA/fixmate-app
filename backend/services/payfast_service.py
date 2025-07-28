import os
import hashlib
from urllib.parse import urlencode
from typing import Dict, Any
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# PayFast Configuration
PAYFAST_MERCHANT_ID = os.getenv('PAYFAST_MERCHANT_ID')
PAYFAST_MERCHANT_KEY = os.getenv('PAYFAST_MERCHANT_KEY')
PAYFAST_PASSPHRASE = os.getenv('PAYFAST_PASSPHRASE', '')
PAYFAST_SANDBOX = os.getenv('PAYFAST_SANDBOX', 'true').lower() == 'true'

if PAYFAST_SANDBOX:
    PAYFAST_URL = 'https://sandbox.payfast.co.za/eng/process'
else:
    PAYFAST_URL = 'https://www.payfast.co.za/eng/process'

class PayFastService:
    def __init__(self):
        self.merchant_id = PAYFAST_MERCHANT_ID
        self.merchant_key = PAYFAST_MERCHANT_KEY
        self.passphrase = PAYFAST_PASSPHRASE
        self.sandbox = PAYFAST_SANDBOX
        self.url = PAYFAST_URL
    
    def generate_payment_url(self, job_data: Dict[str, Any]) -> str:
        """
        Generate PayFast payment URL for a job.
        """
        if not self.merchant_id or not self.merchant_key:
            raise ValueError("PayFast credentials not configured")
        
        # Payment data
        payment_data = {
            'merchant_id': self.merchant_id,
            'merchant_key': self.merchant_key,
            'return_url': f"https://fixmate-sa.com/payment/success?job_id={job_data['job_id']}",
            'cancel_url': f"https://fixmate-sa.com/payment/cancel?job_id={job_data['job_id']}",
            'notify_url': "https://fixmate-sa.com/api/payfast/notify",
            'name_first': job_data.get('client_name', '').split()[0] if job_data.get('client_name') else 'Client',
            'name_last': job_data.get('client_name', '').split()[-1] if job_data.get('client_name') else 'User',
            'email_address': job_data.get('client_email', 'client@fixmate-sa.com'),
            'cell_number': job_data.get('client_phone', ''),
            'amount': str(job_data.get('amount', '0.00')),
            'item_name': f"FixMate-SA Service - {job_data.get('service_type', 'General Service')}",
            'item_description': job_data.get('description', 'Service request'),
            'custom_int1': job_data.get('job_id', ''),
            'custom_str1': job_data.get('user_id', ''),
            'custom_str2': job_data.get('service_type', ''),
        }
        
        # Generate signature
        signature = self._generate_signature(payment_data)
        payment_data['signature'] = signature
        
        # Generate URL
        query_string = urlencode(payment_data)
        return f"{self.url}?{query_string}"
    
    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """
        Generate PayFast signature for payment data.
        """
        # Sort data by key
        sorted_data = sorted(data.items())
        
        # Create query string
        query_string = urlencode(sorted_data)
        
        # Add passphrase if provided
        if self.passphrase:
            query_string += f"&passphrase={self.passphrase}"
        
        # Generate MD5 hash
        return hashlib.md5(query_string.encode()).hexdigest()
    
    def verify_payment_signature(self, payment_data: Dict[str, Any]) -> bool:
        """
        Verify PayFast payment signature.
        """
        if not payment_data.get('signature'):
            return False
        
        # Remove signature from data
        signature = payment_data.pop('signature')
        
        # Generate expected signature
        expected_signature = self._generate_signature(payment_data)
        
        return signature == expected_signature
    
    def process_payment_notification(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process PayFast payment notification.
        """
        try:
            # Verify signature
            if not self.verify_payment_signature(payment_data.copy()):
                return {"status": "error", "message": "Invalid signature"}
            
            # Extract payment information
            payment_status = payment_data.get('payment_status')
            amount_gross = payment_data.get('amount_gross')
            amount_fee = payment_data.get('amount_fee')
            amount_net = payment_data.get('amount_net')
            
            # Extract custom fields
            job_id = payment_data.get('custom_int1')
            user_id = payment_data.get('custom_str1')
            service_type = payment_data.get('custom_str2')
            
            result = {
                "status": "success",
                "payment_status": payment_status,
                "job_id": job_id,
                "user_id": user_id,
                "service_type": service_type,
                "amount_gross": amount_gross,
                "amount_fee": amount_fee,
                "amount_net": amount_net,
                "payment_id": payment_data.get('pf_payment_id'),
                "transaction_id": payment_data.get('m_payment_id')
            }
            
            return result
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment status from PayFast (if API is available).
        """
        # PayFast doesn't have a direct API for payment status
        # This would need to be tracked in the database
        return {"status": "unknown", "message": "Payment status tracking not implemented"}
    
    def create_subscription(self, subscription_data: Dict[str, Any]) -> str:
        """
        Create PayFast subscription (for recurring payments).
        """
        if not self.merchant_id or not self.merchant_key:
            raise ValueError("PayFast credentials not configured")
        
        # Subscription data
        payment_data = {
            'merchant_id': self.merchant_id,
            'merchant_key': self.merchant_key,
            'return_url': subscription_data.get('return_url', 'https://fixmate-sa.com/payment/success'),
            'cancel_url': subscription_data.get('cancel_url', 'https://fixmate-sa.com/payment/cancel'),
            'notify_url': subscription_data.get('notify_url', 'https://fixmate-sa.com/api/payfast/notify'),
            'name_first': subscription_data.get('first_name', 'Client'),
            'name_last': subscription_data.get('last_name', 'User'),
            'email_address': subscription_data.get('email', 'client@fixmate-sa.com'),
            'cell_number': subscription_data.get('phone', ''),
            'amount': str(subscription_data.get('amount', '20.00')),
            'item_name': subscription_data.get('item_name', 'FixMate-SA Subscription'),
            'item_description': subscription_data.get('description', 'Monthly subscription'),
            'subscription_type': '1',  # Monthly subscription
            'billing_date': subscription_data.get('billing_date', '2024-01-01'),
            'recurring_amount': str(subscription_data.get('recurring_amount', '20.00')),
            'frequency': subscription_data.get('frequency', '3'),  # Monthly
            'cycles': subscription_data.get('cycles', '0'),  # Indefinite
        }
        
        # Generate signature
        signature = self._generate_signature(payment_data)
        payment_data['signature'] = signature
        
        # Generate URL
        query_string = urlencode(payment_data)
        return f"{self.url}?{query_string}"
    
    def calculate_fixer_fee(self, job_amount: Decimal) -> Decimal:
        """
        Calculate fixer service fee (R20 flat fee).
        """
        return Decimal('20.00')
    
    def generate_fixer_payment_url(self, fixer_data: Dict[str, Any]) -> str:
        """
        Generate payment URL for fixer service fee.
        """
        job_data = {
            'job_id': fixer_data.get('payment_id', ''),
            'client_name': fixer_data.get('fixer_name', 'Fixer'),
            'client_email': fixer_data.get('fixer_email', 'fixer@fixmate-sa.com'),
            'client_phone': fixer_data.get('fixer_phone', ''),
            'amount': '20.00',
            'service_type': 'Service Fee',
            'description': 'FixMate-SA Service Fee - R20.00',
            'user_id': fixer_data.get('fixer_id', ''),
        }
        
        return self.generate_payment_url(job_data)

# Global instance
payfast_service = PayFastService()