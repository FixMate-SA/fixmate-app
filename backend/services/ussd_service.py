from typing import Dict, Any
import json
from datetime import datetime
from models import User, Job, Fixer
from services.sms_service import sms_service
from services.ai_service import ai_service

class USSDService:
    def __init__(self):
        self.sessions = {}  # Store active USSD sessions
        self.menu_structure = self._build_menu_structure()
    
    def _build_menu_structure(self):
        """
        Build USSD menu structure for FixMate-SA
        """
        return {
            'main': {
                'title': 'Welcome to FixMate-SA',
                'options': {
                    '1': {'text': 'Request Service', 'action': 'request_service'},
                    '2': {'text': 'Check Job Status', 'action': 'check_status'},
                    '3': {'text': 'Find Fixers', 'action': 'find_fixers'},
                    '4': {'text': 'My Profile', 'action': 'profile'},
                    '5': {'text': 'Help & Support', 'action': 'help'},
                    '0': {'text': 'Exit', 'action': 'exit'}
                }
            },
            'request_service': {
                'title': 'Request Service',
                'options': {
                    '1': {'text': 'Plumbing', 'action': 'service_plumbing'},
                    '2': {'text': 'Electrical', 'action': 'service_electrical'},
                    '3': {'text': 'Carpentry', 'action': 'service_carpentry'},
                    '4': {'text': 'Painting', 'action': 'service_painting'},
                    '5': {'text': 'Cleaning', 'action': 'service_cleaning'},
                    '6': {'text': 'Gardening', 'action': 'service_gardening'},
                    '7': {'text': 'Other', 'action': 'service_other'},
                    '9': {'text': 'Back to Main Menu', 'action': 'main'},
                    '0': {'text': 'Exit', 'action': 'exit'}
                }
            },
            'find_fixers': {
                'title': 'Find Fixers',
                'options': {
                    '1': {'text': 'Top Rated Fixers', 'action': 'top_fixers'},
                    '2': {'text': 'Nearby Fixers', 'action': 'nearby_fixers'},
                    '3': {'text': 'By Service Type', 'action': 'fixers_by_service'},
                    '9': {'text': 'Back to Main Menu', 'action': 'main'},
                    '0': {'text': 'Exit', 'action': 'exit'}
                }
            },
            'help': {
                'title': 'Help & Support',
                'options': {
                    '1': {'text': 'How to Use', 'action': 'how_to_use'},
                    '2': {'text': 'Contact Support', 'action': 'contact_support'},
                    '3': {'text': 'Download App', 'action': 'download_app'},
                    '9': {'text': 'Back to Main Menu', 'action': 'main'},
                    '0': {'text': 'Exit', 'action': 'exit'}
                }
            }
        }
    
    def handle_ussd_request(self, phone_number: str, text: str, session_id: str) -> Dict[str, Any]:
        """
        Process USSD request and return response
        """
        try:
            # Clean phone number
            phone_number = self._clean_phone_number(phone_number)
            
            # Initialize or get existing session
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    'phone_number': phone_number,
                    'current_menu': 'main',
                    'history': [],
                    'data': {},
                    'created_at': datetime.now()
                }
            
            session = self.sessions[session_id]
            
            # Handle empty text (initial request)
            if not text:
                return self._generate_menu_response('main', session_id)
            
            # Parse user input
            user_input = text.strip()
            
            # Handle menu navigation
            if session['current_menu'] in self.menu_structure:
                return self._handle_menu_selection(user_input, session_id)
            else:
                # Handle data input (like entering job description)
                return self._handle_data_input(user_input, session_id)
                
        except Exception as e:
            return self._error_response(str(e))
    
    def _handle_menu_selection(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """
        Handle user menu selection
        """
        session = self.sessions[session_id]
        current_menu = session['current_menu']
        
        if current_menu not in self.menu_structure:
            return self._error_response("Invalid menu")
        
        menu = self.menu_structure[current_menu]
        
        if user_input in menu['options']:
            option = menu['options'][user_input]
            action = option['action']
            
            # Update session history
            session['history'].append({
                'menu': current_menu,
                'selection': user_input,
                'action': action,
                'timestamp': datetime.now()
            })
            
            # Process action
            return self._process_action(action, session_id)
        else:
            return self._error_response("Invalid selection. Please try again.")
    
    def _process_action(self, action: str, session_id: str) -> Dict[str, Any]:
        """
        Process the selected action
        """
        session = self.sessions[session_id]
        
        if action == 'exit':
            return self._end_session(session_id)
        elif action == 'main':
            return self._generate_menu_response('main', session_id)
        elif action.startswith('service_'):
            return self._handle_service_request(action, session_id)
        elif action == 'check_status':
            return self._check_job_status(session_id)
        elif action == 'top_fixers':
            return self._show_top_fixers(session_id)
        elif action == 'nearby_fixers':
            return self._show_nearby_fixers(session_id)
        elif action == 'profile':
            return self._show_profile(session_id)
        elif action == 'how_to_use':
            return self._show_how_to_use(session_id)
        elif action == 'contact_support':
            return self._show_contact_support(session_id)
        elif action == 'download_app':
            return self._show_download_app(session_id)
        else:
            # Navigate to submenu
            return self._generate_menu_response(action, session_id)
    
    def _handle_service_request(self, action: str, session_id: str) -> Dict[str, Any]:
        """
        Handle service request
        """
        session = self.sessions[session_id]
        service_type = action.replace('service_', '')
        
        session['data']['service_type'] = service_type
        session['current_menu'] = 'service_description'
        
        return {
            'response': f"CON You selected {service_type.title()} service.\n\nPlease describe what needs to be fixed:\n\n0. Exit\n9. Back to services",
            'continue': True
        }
    
    def _handle_data_input(self, user_input: str, session_id: str) -> Dict[str, Any]:
        """
        Handle data input from user
        """
        session = self.sessions[session_id]
        
        if user_input == '0':
            return self._end_session(session_id)
        elif user_input == '9':
            return self._generate_menu_response('request_service', session_id)
        
        if session['current_menu'] == 'service_description':
            return self._handle_service_description(user_input, session_id)
        elif session['current_menu'] == 'service_location':
            return self._handle_service_location(user_input, session_id)
        
        return self._error_response("Invalid input")
    
    def _handle_service_description(self, description: str, session_id: str) -> Dict[str, Any]:
        """
        Handle service description input
        """
        session = self.sessions[session_id]
        session['data']['description'] = description
        session['current_menu'] = 'service_location'
        
        return {
            'response': f"CON Service: {session['data']['service_type'].title()}\nDescription: {description}\n\nPlease enter your location/area:\n\n0. Exit\n9. Back",
            'continue': True
        }
    
    def _handle_service_location(self, location: str, session_id: str) -> Dict[str, Any]:
        """
        Handle service location input and create job
        """
        session = self.sessions[session_id]
        session['data']['location'] = location
        
        # Create job in database
        job_result = self._create_job_from_ussd(session)
        
        if job_result['success']:
            # Send SMS confirmation
            sms_service.send_sms(
                session['phone_number'],
                f"FixMate-SA: Job created successfully! Job ID: {job_result['job_id']}. A fixer will contact you shortly."
            )
            
            return {
                'response': f"END Job created successfully!\n\nJob ID: {job_result['job_id']}\nService: {session['data']['service_type'].title()}\nLocation: {location}\n\nYou'll receive SMS updates. Download our app for more features!",
                'continue': False
            }
        else:
            return {
                'response': f"END Error creating job: {job_result['error']}\n\nPlease try again or contact support at 087-123-4567",
                'continue': False
            }
    
    def _create_job_from_ussd(self, session: dict) -> Dict[str, Any]:
        """
        Create job from USSD session data
        """
        try:
            # Get or create user
            from database import SessionLocal
            db = SessionLocal()
            
            user = db.query(User).filter(User.phone == session['phone_number']).first()
            if not user:
                user = User(
                    phone=session['phone_number'],
                    name=f"User {session['phone_number']}"
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # Create job
            job = Job(
                user_id=user.id,
                service=session['data']['service_type'],
                description=session['data']['description'],
                location=session['data']['location'],
                status='pending'
            )
            
            db.add(job)
            db.commit()
            db.refresh(job)
            
            db.close()
            
            return {
                'success': True,
                'job_id': str(job.id)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _check_job_status(self, session_id: str) -> Dict[str, Any]:
        """
        Check job status for user
        """
        session = self.sessions[session_id]
        
        try:
            from database import SessionLocal
            db = SessionLocal()
            
            user = db.query(User).filter(User.phone == session['phone_number']).first()
            if not user:
                return {
                    'response': "END No jobs found for this number.\n\nCreate your first job by dialing *120*349*6283#",
                    'continue': False
                }
            
            jobs = db.query(Job).filter(Job.user_id == user.id).order_by(Job.created_at.desc()).limit(5).all()
            
            if not jobs:
                return {
                    'response': "END No jobs found.\n\nCreate your first job by dialing *120*349*6283#",
                    'continue': False
                }
            
            response = "END Your Recent Jobs:\n\n"
            for i, job in enumerate(jobs, 1):
                response += f"{i}. {job.service.title()}\n   Status: {job.status.title()}\n   Location: {job.location}\n\n"
            
            response += "For more details, download our app!"
            
            db.close()
            
            return {
                'response': response,
                'continue': False
            }
            
        except Exception as e:
            return self._error_response(str(e))
    
    def _show_top_fixers(self, session_id: str) -> Dict[str, Any]:
        """
        Show top rated fixers
        """
        try:
            from database import SessionLocal
            db = SessionLocal()
            
            fixers = db.query(Fixer).filter(Fixer.is_active == True).order_by(Fixer.rating.desc()).limit(5).all()
            
            if not fixers:
                return {
                    'response': "END No fixers available at the moment.\n\nPlease try again later.",
                    'continue': False
                }
            
            response = "END Top Rated Fixers:\n\n"
            for i, fixer in enumerate(fixers, 1):
                services = json.loads(fixer.services)[:2]  # Show first 2 services
                response += f"{i}. {fixer.name}\n   Rating: {fixer.rating:.1f}★\n   Services: {', '.join(services)}\n   Location: {fixer.location}\n\n"
            
            response += "Call 087-123-4567 to book or download our app!"
            
            db.close()
            
            return {
                'response': response,
                'continue': False
            }
            
        except Exception as e:
            return self._error_response(str(e))
    
    def _show_nearby_fixers(self, session_id: str) -> Dict[str, Any]:
        """
        Show nearby fixers (simplified - would need location services)
        """
        return {
            'response': "END Nearby Fixers:\n\n1. John Smith - Plumbing\n   Rating: 4.8★\n   Distance: 2km\n\n2. Sarah Johnson - Electrical\n   Rating: 4.9★\n   Distance: 3km\n\n3. Mike Brown - Carpentry\n   Rating: 4.7★\n   Distance: 4km\n\nCall 087-123-4567 to book or download our app for GPS location!",
            'continue': False
        }
    
    def _show_profile(self, session_id: str) -> Dict[str, Any]:
        """
        Show user profile
        """
        session = self.sessions[session_id]
        
        try:
            from database import SessionLocal
            db = SessionLocal()
            
            user = db.query(User).filter(User.phone == session['phone_number']).first()
            if not user:
                return {
                    'response': "END Profile not found.\n\nCreate account by requesting a service first.",
                    'continue': False
                }
            
            total_jobs = db.query(Job).filter(Job.user_id == user.id).count()
            completed_jobs = db.query(Job).filter(Job.user_id == user.id, Job.status == 'completed').count()
            
            response = f"END Your Profile:\n\nName: {user.name}\nPhone: {user.phone}\nTotal Jobs: {total_jobs}\nCompleted: {completed_jobs}\n\nDownload our app for full profile management!"
            
            db.close()
            
            return {
                'response': response,
                'continue': False
            }
            
        except Exception as e:
            return self._error_response(str(e))
    
    def _show_how_to_use(self, session_id: str) -> Dict[str, Any]:
        """
        Show how to use instructions
        """
        return {
            'response': "END How to Use FixMate-SA:\n\n1. Dial *120*349*6283#\n2. Select 'Request Service'\n3. Choose service type\n4. Describe your problem\n5. Enter your location\n6. Wait for fixer contact\n\nFor advanced features, download our app from Google Play Store!",
            'continue': False
        }
    
    def _show_contact_support(self, session_id: str) -> Dict[str, Any]:
        """
        Show contact support info
        """
        return {
            'response': "END FixMate-SA Support:\n\n📞 Call: 087-123-4567\n📱 WhatsApp: 082-349-6283\n📧 Email: support@fixmate.co.za\n🌐 Website: www.fixmate.co.za\n\nSupport Hours:\nMon-Fri: 8AM-6PM\nSat: 8AM-2PM\nSun: Closed",
            'continue': False
        }
    
    def _show_download_app(self, session_id: str) -> Dict[str, Any]:
        """
        Show app download info
        """
        return {
            'response': "END Download FixMate-SA App:\n\n📱 Android: Play Store\n🍎 iOS: App Store\n🌐 Web: www.fixmate.co.za\n\nApp Features:\n• Voice requests\n• Real-time tracking\n• Photo sharing\n• Payment options\n• Learning courses\n\nStay connected with FixMate-SA!",
            'continue': False
        }
    
    def _generate_menu_response(self, menu_name: str, session_id: str) -> Dict[str, Any]:
        """
        Generate menu response
        """
        session = self.sessions[session_id]
        session['current_menu'] = menu_name
        
        if menu_name not in self.menu_structure:
            return self._error_response("Invalid menu")
        
        menu = self.menu_structure[menu_name]
        response = f"CON {menu['title']}\n\n"
        
        for key, option in menu['options'].items():
            response += f"{key}. {option['text']}\n"
        
        return {
            'response': response,
            'continue': True
        }
    
    def _end_session(self, session_id: str) -> Dict[str, Any]:
        """
        End USSD session
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
        
        return {
            'response': "END Thank you for using FixMate-SA!\n\nFor more features, download our app or visit www.fixmate.co.za\n\nDial *120*349*6283# anytime for service!",
            'continue': False
        }
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """
        Generate error response
        """
        return {
            'response': f"END Error: {message}\n\nPlease try again or contact support at 087-123-4567",
            'continue': False
        }
    
    def _clean_phone_number(self, phone_number: str) -> str:
        """
        Clean and format phone number
        """
        # Remove all non-digit characters
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Add country code if missing
        if clean_number.startswith('0'):
            clean_number = '+27' + clean_number[1:]
        elif not clean_number.startswith('27'):
            clean_number = '+27' + clean_number
        else:
            clean_number = '+' + clean_number
        
        return clean_number
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get USSD session statistics
        """
        active_sessions = len(self.sessions)
        total_actions = sum(len(session.get('history', [])) for session in self.sessions.values())
        
        return {
            'active_sessions': active_sessions,
            'total_actions': total_actions,
            'menu_usage': self._get_menu_usage_stats()
        }
    
    def _get_menu_usage_stats(self) -> Dict[str, int]:
        """
        Get menu usage statistics
        """
        menu_usage = {}
        for session in self.sessions.values():
            for action in session.get('history', []):
                menu = action.get('menu', 'unknown')
                menu_usage[menu] = menu_usage.get(menu, 0) + 1
        
        return menu_usage

# Global instance
ussd_service = USSDService()