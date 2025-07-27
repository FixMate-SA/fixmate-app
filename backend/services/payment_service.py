import os
import requests
import json
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class PaymentService:
    def __init__(self):
        self.payfast_merchant_id = os.getenv("PAYFAST_MERCHANT_ID")
        self.payfast_merchant_key = os.getenv("PAYFAST_MERCHANT_KEY")
        self.payfast_url = "https://sandbox.payfast.co.za/eng/process"  # Change to live for production
        
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