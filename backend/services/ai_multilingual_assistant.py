import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import logging

from models import AIConversation, User, Job, Fixer, NotificationQueue
from services.ai_service import ai_service

logger = logging.getLogger(__name__)

class AIMultilingualAssistant:
    """
    AI-powered multilingual chat assistant for FixMate-SA.
    Provides 24/7 automated support in all 11 South African languages.
    """
    
    def __init__(self):
        self.supported_languages = {
            'english': 'English',
            'afrikaans': 'Afrikaans', 
            'zulu': 'isiZulu',
            'xhosa': 'isiXhosa',
            'sotho': 'Sesotho',
            'tswana': 'Setswana',
            'pedi': 'Sepedi',
            'venda': 'Tshivenda',
            'tsonga': 'Xitsonga',
            'ndebele': 'isiNdebele',
            'swati': 'siSwati'
        }
        
        self.conversation_timeout = 30  # minutes
        self.max_conversation_length = 50  # messages
        
        # Common intents and responses
        self.intent_patterns = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'sawubona', 'dumela', 'hola'],
            'help': ['help', 'assist', 'support', 'problem', 'issue', 'lusizo', 'thuso'],
            'job_status': ['job', 'work', 'status', 'progress', 'fixer', 'when', 'umsebenzi', 'mosebetsi'],
            'pricing': ['price', 'cost', 'how much', 'expensive', 'intengo', 'tlhwatlhwa'],
            'booking': ['book', 'schedule', 'appointment', 'when can', 'available', 'beha'],
            'complaint': ['complaint', 'problem', 'unhappy', 'bad', 'terrible', 'isikhalo'],
            'compliment': ['thank', 'good', 'excellent', 'happy', 'great', 'siyabonga', 'ke a leboga']
        }
        
        self.escalation_triggers = [
            'speak to human', 'talk to person', 'manager', 'supervisor', 'not helping',
            'useless', 'terrible', 'worst', 'cancel everything', 'delete account'
        ]
    
    def start_conversation(
        self, 
        db: Session, 
        user_id: str = None, 
        session_id: str = None,
        language: str = 'english',
        user_type: str = 'client'
    ) -> Dict:
        """
        Start a new AI conversation session.
        """
        try:
            if not session_id:
                session_id = f"ai_chat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id or 'anon'}"
            
            # Check for existing active conversation
            existing = db.query(AIConversation).filter(
                AIConversation.session_id == session_id,
                AIConversation.status == 'active'
            ).first()
            
            if existing:
                return {
                    'success': True,
                    'conversation_id': existing.id,
                    'session_id': session_id,
                    'message': 'Resumed existing conversation'
                }
            
            # Create new conversation
            conversation = AIConversation(
                user_id=user_id,
                session_id=session_id,
                language=language,
                user_type=user_type,
                messages=json.dumps([]),
                conversation_context=json.dumps({
                    'user_preferences': {},
                    'mentioned_jobs': [],
                    'topics_discussed': [],
                    'language_detected': language
                })
            )
            
            db.add(conversation)
            
            try:
                db.commit()
                
                # Send welcome message
                welcome_response = self._generate_welcome_message(language, user_type)
                
                return {
                    'success': True,
                    'conversation_id': conversation.id,
                    'session_id': session_id,
                    'welcome_message': welcome_response,
                    'supported_languages': list(self.supported_languages.keys())
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error starting conversation: {e}")
                return {'success': False, 'error': 'Database error occurred'}
                
        except Exception as e:
            logger.error(f"Error starting AI conversation: {e}")
            return {'success': False, 'error': f'Failed to start conversation: {str(e)}'}
    
    def process_user_message(
        self, 
        db: Session, 
        session_id: str, 
        user_message: str,
        message_context: Dict = None
    ) -> Dict:
        """
        Process user message and generate AI response.
        """
        try:
            # Get conversation
            conversation = db.query(AIConversation).filter(
                AIConversation.session_id == session_id,
                AIConversation.status == 'active'
            ).first()
            
            if not conversation:
                return {'success': False, 'error': 'Conversation not found or ended'}
            
            # Check conversation timeout
            if self._is_conversation_expired(conversation):
                conversation.status = 'abandoned'
                conversation.ended_at = datetime.utcnow()
                db.commit()
                return {'success': False, 'error': 'Conversation expired. Please start a new one.'}
            
            # Load existing messages
            messages = json.loads(conversation.messages) if conversation.messages else []
            
            # Check message limit
            if len(messages) >= self.max_conversation_length:
                return self._escalate_conversation(db, conversation, 'Message limit reached')
            
            # Add user message
            user_msg = {
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.utcnow().isoformat(),
                'context': message_context or {}
            }
            messages.append(user_msg)
            
            # Update conversation stats
            conversation.user_messages += 1
            conversation.total_messages += 1
            conversation.last_message_at = datetime.utcnow()
            
            # Check for escalation triggers
            if self._should_escalate(user_message):
                return self._escalate_conversation(db, conversation, 'User requested human assistance')
            
            # Detect language if needed
            detected_language = self._detect_language(user_message, conversation.language)
            if detected_language != conversation.language:
                conversation.language = detected_language
            
            # Generate AI response
            ai_response = self._generate_ai_response(db, conversation, user_message, messages)
            
            # Add AI response to messages
            ai_msg = {
                'role': 'assistant',
                'content': ai_response['message'],
                'timestamp': datetime.utcnow().isoformat(),
                'confidence': ai_response.get('confidence', 0.8),
                'intent': ai_response.get('intent', 'general'),
                'actions': ai_response.get('actions', [])
            }
            messages.append(ai_msg)
            
            # Update conversation
            conversation.messages = json.dumps(messages)
            conversation.ai_responses += 1
            conversation.total_messages += 1
            
            # Update context
            context = json.loads(conversation.conversation_context) if conversation.conversation_context else {}
            context['last_intent'] = ai_response.get('intent', 'general')
            context['topics_discussed'] = list(set(context.get('topics_discussed', []) + [ai_response.get('intent', 'general')]))
            conversation.conversation_context = json.dumps(context)
            
            # Update confidence average
            if conversation.avg_response_confidence == 0:
                conversation.avg_response_confidence = ai_response.get('confidence', 0.8)
            else:
                conversation.avg_response_confidence = (
                    (conversation.avg_response_confidence + ai_response.get('confidence', 0.8)) / 2
                )
            
            try:
                db.commit()
                
                return {
                    'success': True,
                    'message': ai_response['message'],
                    'intent': ai_response.get('intent', 'general'),
                    'confidence': ai_response.get('confidence', 0.8),
                    'actions': ai_response.get('actions', []),
                    'conversation_id': conversation.id,
                    'language': conversation.language,
                    'total_messages': conversation.total_messages
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error processing message: {e}")
                return {'success': False, 'error': 'Database error occurred'}
                
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            return {'success': False, 'error': f'Failed to process message: {str(e)}'}
    
    def end_conversation(
        self, 
        db: Session, 
        session_id: str, 
        satisfaction_rating: int = None,
        resolved_query: bool = False
    ) -> Dict:
        """
        End conversation and collect feedback.
        """
        try:
            conversation = db.query(AIConversation).filter(
                AIConversation.session_id == session_id,
                AIConversation.status == 'active'
            ).first()
            
            if not conversation:
                return {'success': False, 'error': 'Conversation not found'}
            
            # Update conversation status
            conversation.status = 'completed'
            conversation.ended_at = datetime.utcnow()
            conversation.satisfaction_rating = satisfaction_rating
            conversation.resolved_query = resolved_query
            
            # Calculate duration
            if conversation.started_at:
                duration = (conversation.ended_at - conversation.started_at).total_seconds() / 60
                conversation.duration_minutes = duration
            
            try:
                db.commit()
                
                return {
                    'success': True,
                    'message': 'Conversation ended successfully',
                    'duration_minutes': conversation.duration_minutes,
                    'total_messages': conversation.total_messages,
                    'satisfaction_rating': satisfaction_rating
                }
                
            except Exception as e:
                db.rollback()
                logger.error(f"Database error ending conversation: {e}")
                return {'success': False, 'error': 'Database error occurred'}
                
        except Exception as e:
            logger.error(f"Error ending conversation: {e}")
            return {'success': False, 'error': f'Failed to end conversation: {str(e)}'}
    
    def get_conversation_history(self, db: Session, session_id: str) -> Optional[Dict]:
        """
        Get conversation history and details.
        """
        try:
            conversation = db.query(AIConversation).filter(
                AIConversation.session_id == session_id
            ).first()
            
            if not conversation:
                return None
            
            messages = json.loads(conversation.messages) if conversation.messages else []
            context = json.loads(conversation.conversation_context) if conversation.conversation_context else {}
            
            return {
                'conversation_id': conversation.id,
                'session_id': conversation.session_id,
                'user_id': conversation.user_id,
                'user_type': conversation.user_type,
                'language': conversation.language,
                'status': conversation.status,
                'messages': messages,
                'context': context,
                'statistics': {
                    'total_messages': conversation.total_messages,
                    'user_messages': conversation.user_messages,
                    'ai_responses': conversation.ai_responses,
                    'avg_response_confidence': conversation.avg_response_confidence,
                    'duration_minutes': conversation.duration_minutes
                },
                'feedback': {
                    'satisfaction_rating': conversation.satisfaction_rating,
                    'resolved_query': conversation.resolved_query,
                    'escalated_to_human': conversation.escalated_to_human
                },
                'timestamps': {
                    'started_at': conversation.started_at.isoformat(),
                    'last_message_at': conversation.last_message_at.isoformat() if conversation.last_message_at else None,
                    'ended_at': conversation.ended_at.isoformat() if conversation.ended_at else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return None
    
    def _generate_welcome_message(self, language: str, user_type: str) -> str:
        """
        Generate appropriate welcome message based on language and user type.
        """
        welcome_messages = {
            'english': {
                'client': "Hello! I'm your FixMate AI assistant. I can help you with booking services, checking job status, pricing information, and general questions. How can I assist you today?",
                'fixer': "Hi there! I'm here to help you with job assignments, performance insights, earnings questions, and platform guidance. What would you like to know?",
                'anonymous': "Welcome to FixMate-SA! I'm your AI assistant. I can help you learn about our services, pricing, and how to get started. What can I help you with?"
            },
            'afrikaans': {
                'client': "Hallo! Ek is jou FixMate AI-assistent. Ek kan jou help met die bespreek van dienste, werk status, pryse, en algemene vrae. Hoe kan ek jou vandag help?",
                'fixer': "Hallo daar! Ek is hier om jou te help met werk opdragte, prestasie insigte, verdienste vrae, en platform leiding. Wat wil jy weet?",
                'anonymous': "Welkom by FixMate-SA! Ek is jou AI-assistent. Ek kan jou help om te leer oor ons dienste, pryse, en hoe om te begin. Waarmee kan ek jou help?"
            },
            'zulu': {
                'client': "Sawubona! Ngingumphathi wakho we-AI wase-FixMate. Ngingakusiza ngokubhuka amasevisi, ukuhlola isimo somsebenzi, ulwazi lwentengo, nemibuzo ejwayelekile. Ngingakusiza kanjani namuhla?",
                'fixer': "Sawubona! Ngilapha ukusiza ngokwabelwa kwemisebenzi, ukuqwashisa ngokusebenza, imibuzo yokuhola, nokuholela kweplatform. Ufuna ukwazi kuphi?",
                'anonymous': "Siyakwamukela ku-FixMate-SA! Ngingumphathi wakho we-AI. Ngingakusiza ukufunda ngamasevisi ethu, amanani, nokuthi ungaqala kanjani. Ngingakusiza ngani?"
            }
        }
        
        return welcome_messages.get(language, welcome_messages['english']).get(user_type, welcome_messages['english']['anonymous'])
    
    def _generate_ai_response(
        self, 
        db: Session, 
        conversation: AIConversation, 
        user_message: str, 
        message_history: List[Dict]
    ) -> Dict:
        """
        Generate AI response using context and intent recognition.
        """
        try:
            # Detect intent
            intent = self._detect_intent(user_message)
            
            # Get conversation context
            context = json.loads(conversation.conversation_context) if conversation.conversation_context else {}
            
            # Generate response based on intent
            if intent == 'greeting':
                response = self._handle_greeting(conversation.language)
            elif intent == 'job_status':
                response = self._handle_job_status_inquiry(db, conversation, user_message)
            elif intent == 'pricing':
                response = self._handle_pricing_inquiry(conversation.language)
            elif intent == 'booking':
                response = self._handle_booking_inquiry(conversation.language)
            elif intent == 'help':
                response = self._handle_help_request(conversation.language, conversation.user_type)
            elif intent == 'complaint':
                response = self._handle_complaint(conversation.language)
            elif intent == 'compliment':
                response = self._handle_compliment(conversation.language)
            else:
                response = self._handle_general_query(db, conversation, user_message)
            
            # Use AI service for complex responses if available
            if ai_service.model and response.get('use_ai', False):
                ai_prompt = self._build_ai_prompt(conversation, user_message, intent, message_history)
                try:
                    ai_response = ai_service.model.generate_content(ai_prompt)
                    response['message'] = ai_response.text.strip()
                    response['confidence'] = min(0.9, response.get('confidence', 0.7) + 0.1)
                except Exception as e:
                    logger.warning(f"AI service failed, using template response: {e}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return {
                'message': "I'm sorry, I'm having trouble understanding. Could you please rephrase your question?",
                'intent': 'error',
                'confidence': 0.3
            }
    
    def _detect_intent(self, message: str) -> str:
        """
        Detect user intent from message.
        """
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent
        
        return 'general'
    
    def _detect_language(self, message: str, current_language: str) -> str:
        """
        Detect message language (simplified detection).
        """
        # Simple keyword-based detection
        language_keywords = {
            'afrikaans': ['jy', 'ek', 'is', 'die', 'en', 'wat', 'hoe', 'waar'],
            'zulu': ['ngi', 'uku', 'uma', 'nge', 'ku', 'nga', 'si', 'ama'],
            'xhosa': ['ndi', 'uku', 'ukuba', 'nge', 'ku', 'nga', 'si', 'ama'],
            'sotho': ['ke', 'ho', 'ha', 'le', 'ba', 'mo', 'se', 'di']
        }
        
        message_lower = message.lower()
        
        for lang, keywords in language_keywords.items():
            if sum(1 for keyword in keywords if keyword in message_lower) >= 2:
                return lang
        
        return current_language  # Default to current language
    
    def _should_escalate(self, message: str) -> bool:
        """
        Check if conversation should be escalated to human.
        """
        message_lower = message.lower()
        return any(trigger in message_lower for trigger in self.escalation_triggers)
    
    def _is_conversation_expired(self, conversation: AIConversation) -> bool:
        """
        Check if conversation has expired.
        """
        if not conversation.last_message_at:
            return False
        
        time_since_last = datetime.utcnow() - conversation.last_message_at
        return time_since_last.total_seconds() > (self.conversation_timeout * 60)
    
    def _escalate_conversation(self, db: Session, conversation: AIConversation, reason: str) -> Dict:
        """
        Escalate conversation to human support.
        """
        try:
            conversation.status = 'escalated'
            conversation.escalated_to_human = True
            conversation.ended_at = datetime.utcnow()
            
            # Create notification for support team
            if conversation.user_id:
                notification = NotificationQueue(
                    recipient_id=conversation.user_id,
                    notification_type='in_app',
                    category='support',
                    priority='high',
                    title='Chat Escalated to Human Support',
                    message='Your conversation has been transferred to our human support team. Someone will assist you shortly.',
                    context_data=json.dumps({
                        'conversation_id': conversation.id,
                        'escalation_reason': reason
                    })
                )
                db.add(notification)
            
            db.commit()
            
            return {
                'success': True,
                'escalated': True,
                'message': "I'm connecting you with a human support agent who can better assist you. Please wait a moment.",
                'reason': reason
            }
            
        except Exception as e:
            logger.error(f"Error escalating conversation: {e}")
            return {
                'success': False,
                'message': "I apologize for the difficulty. Please contact our support team directly for assistance."
            }
    
    def _handle_greeting(self, language: str) -> Dict:
        """Handle greeting messages."""
        greetings = {
            'english': "Hello! How can I help you today?",
            'afrikaans': "Hallo! Hoe kan ek jou vandag help?",
            'zulu': "Sawubona! Ngingakusiza kanjani namuhla?",
            'xhosa': "Molo! Ndingakunceda njani namhlanje?",
            'sotho': "Dumela! Nka o thusa jwang kajeno?"
        }
        
        return {
            'message': greetings.get(language, greetings['english']),
            'intent': 'greeting',
            'confidence': 0.9
        }
    
    def _handle_job_status_inquiry(self, db: Session, conversation: AIConversation, message: str) -> Dict:
        """Handle job status inquiries."""
        if not conversation.user_id:
            return {
                'message': "To check your job status, please log in to your account first.",
                'intent': 'job_status',
                'confidence': 0.8
            }
        
        # Get recent jobs for user
        recent_jobs = db.query(Job).filter(
            Job.user_id == conversation.user_id
        ).order_by(Job.created_at.desc()).limit(3).all()
        
        if not recent_jobs:
            return {
                'message': "You don't have any jobs on record. Would you like to book a service?",
                'intent': 'job_status',
                'confidence': 0.8,
                'actions': ['suggest_booking']
            }
        
        job_statuses = []
        for job in recent_jobs:
            status_text = f"• {job.service} - {job.status.title()}"
            if job.fixer:
                status_text += f" (Fixer: {job.fixer.name})"
            job_statuses.append(status_text)
        
        message = "Here are your recent jobs:\n" + "\n".join(job_statuses)
        
        return {
            'message': message,
            'intent': 'job_status',
            'confidence': 0.9,
            'actions': ['job_status_provided']
        }
    
    def _handle_pricing_inquiry(self, language: str) -> Dict:
        """Handle pricing inquiries."""
        pricing_responses = {
            'english': "Our pricing varies by service type and complexity. Typical rates: Plumbing R300-800, Electrical R400-1000, Handyman R200-600. You'll get exact quotes when you book. Would you like to request a quote?",
            'afrikaans': "Ons pryse wissel volgens diens tipe en kompleksiteit. Tipiese tariewe: Loodgietery R300-800, Elektries R400-1000, Handyman R200-600. Jy sal presiese kwotasies kry wanneer jy bespreek.",
            'zulu': "Amanani ethu ahluka ngokohlobo lwesevisi nobunzima. Amanani avamile: Izimpompi R300-800, Ugesi R400-1000, Umsebenzi wezandla R200-600."
        }
        
        return {
            'message': pricing_responses.get(language, pricing_responses['english']),
            'intent': 'pricing',
            'confidence': 0.8,
            'actions': ['suggest_quote']
        }
    
    def _handle_booking_inquiry(self, language: str) -> Dict:
        """Handle booking inquiries."""
        booking_responses = {
            'english': "I can help you start the booking process! What type of service do you need? We offer plumbing, electrical, handyman, cleaning, and many other services.",
            'afrikaans': "Ek kan jou help om die besprekingsproses te begin! Watter tipe diens benodig jy? Ons bied loodgietery, elektries, handyman, skoonmaak, en baie ander dienste aan.",
            'zulu': "Ngingakusiza ukuqala inqubo yokubhuka! Uhlobo luni lwesevisi oyidingiyo? Sinikeza amaphayipi, ugesi, umsebenzi wezandla, ukuhlanza, nezinye izinsizakalo eziningi."
        }
        
        return {
            'message': booking_responses.get(language, booking_responses['english']),
            'intent': 'booking',
            'confidence': 0.8,
            'actions': ['suggest_service_selection']
        }
    
    def _handle_help_request(self, language: str, user_type: str) -> Dict:
        """Handle general help requests."""
        help_responses = {
            'english': {
                'client': "I can help you with: 1) Booking services 2) Checking job status 3) Pricing information 4) Finding fixers 5) Account questions. What would you like help with?",
                'fixer': "I can help you with: 1) Job assignments 2) Earnings and payments 3) Performance insights 4) Platform features 5) Account management. What do you need help with?",
                'anonymous': "I can help you learn about: 1) Our services 2) How FixMate works 3) Pricing 4) Getting started 5) Finding fixers. What interests you?"
            }
        }
        
        return {
            'message': help_responses.get(language, help_responses['english']).get(user_type, help_responses['english']['anonymous']),
            'intent': 'help',
            'confidence': 0.9
        }
    
    def _handle_complaint(self, language: str) -> Dict:
        """Handle complaints."""
        complaint_responses = {
            'english': "I'm sorry to hear you're having an issue. I want to help resolve this for you. Can you please tell me more details about what happened? For serious issues, I can connect you with our support team.",
            'afrikaans': "Ek is jammer om te hoor jy het 'n probleem. Ek wil help om dit vir jou op te los. Kan jy asseblief meer besonderhede vertel oor wat gebeur het?",
            'zulu': "Ngiyaxolisa ukuzwa ukuthi unenkinga. Ngifuna ukusiza ukuxazulula lokhu kuwe. Ungakwazi ukungitshela imininingwane eminingi ngalokho okwenzekayo?"
        }
        
        return {
            'message': complaint_responses.get(language, complaint_responses['english']),
            'intent': 'complaint',
            'confidence': 0.8,
            'actions': ['collect_complaint_details']
        }
    
    def _handle_compliment(self, language: str) -> Dict:
        """Handle compliments and thanks."""
        compliment_responses = {
            'english': "Thank you so much for your kind words! I'm glad I could help. Is there anything else you'd like assistance with?",
            'afrikaans': "Baie dankie vir jou vriendelike woorde! Ek is bly ek kon help. Is daar enigiets anders waarmee ek kan help?",
            'zulu': "Siyabonga kakhulu ngamazwi akho amnandi! Ngiyajabula ukuthi ngikwazile ukusiza. Kukhona okunye ongathanda ukusizwa ngakho?"
        }
        
        return {
            'message': compliment_responses.get(language, compliment_responses['english']),
            'intent': 'compliment',
            'confidence': 0.9
        }
    
    def _handle_general_query(self, db: Session, conversation: AIConversation, message: str) -> Dict:
        """Handle general queries with AI assistance."""
        return {
            'message': "I understand you have a question. Let me help you with that. Could you please provide a bit more detail about what you're looking for?",
            'intent': 'general',
            'confidence': 0.6,
            'use_ai': True  # Flag to use AI service if available
        }
    
    def _build_ai_prompt(
        self, 
        conversation: AIConversation, 
        user_message: str, 
        intent: str, 
        message_history: List[Dict]
    ) -> str:
        """
        Build prompt for AI service.
        """
        context = json.loads(conversation.conversation_context) if conversation.conversation_context else {}
        
        prompt = f"""
You are a helpful AI assistant for FixMate-SA, a South African home services platform.

Context:
- User type: {conversation.user_type}
- Language: {conversation.language} ({self.supported_languages.get(conversation.language, conversation.language)})
- Detected intent: {intent}
- Previous topics: {context.get('topics_discussed', [])}

User message: "{user_message}"

Please provide a helpful, friendly response in {self.supported_languages.get(conversation.language, 'English')}. 
Keep responses concise (under 200 words) and actionable.
If you cannot help with something, politely suggest contacting human support.

Response:
"""
        
        return prompt

# Global instance
ai_assistant = AIMultilingualAssistant()