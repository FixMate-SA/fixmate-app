import os
import io
import tempfile
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai

# Fallback import for OpenAI to handle deployment issues
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    print("Warning: OpenAI library not available - AI features will use fallback")
    OpenAI = None
    OPENAI_AVAILABLE = False

from dotenv import load_dotenv

load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

logger = logging.getLogger(__name__)

class EnhancedAIService:
    """
    Enhanced AI Service with hybrid Gemini + OpenAI integration
    for advanced smart matching and reinforcement learning
    """
    def __init__(self):
        # Gemini for multilingual and general AI tasks
        self.gemini_model = genai.GenerativeModel('models/gemini-1.5-flash') if GEMINI_API_KEY else None
        
        # OpenAI for advanced reasoning and reinforcement learning
        self.openai_client = None
        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.openai_client = None
        
        # Matching performance tracking
        self.matching_history = []
        self.success_patterns = {}
        
        logger.info(f"Enhanced AI Service initialized - Gemini: {'✓' if self.gemini_model else '✗'}, OpenAI: {'✓' if self.openai_client else '✗'}")

        # For backward compatibility
        self.model = self.gemini_model

    def transcribe_audio(self, audio_data: bytes) -> str:
        """
        Transcribe audio using Google Gemini AI with support for South African languages.
        """
        if not self.model or not GEMINI_API_KEY:
            return "Transcription service not available. Please configure GEMINI_API_KEY."
        
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name
            
            # Upload to Gemini
            audio_file = genai.upload_file(temp_audio_path, mime_type='audio/wav')
            
            # Transcribe with South African context
            transcription_prompt = [
                """Please transcribe the following audio clearly and accurately. 
                The speaker is from South Africa and might be speaking in English, Afrikaans, Zulu, Xhosa, Sotho, or other South African languages.
                If the audio is in a language other than English, please also provide an English translation.
                
                Format your response as:
                Transcription: [original text]
                Translation: [English translation if needed]
                
                If the audio is unclear or cannot be transcribed, please indicate that.""",
                audio_file
            ]
            
            response = self.model.generate_content(transcription_prompt)
            
            # Clean up
            genai.delete_file(audio_file.name)
            os.unlink(temp_audio_path)
            
            if response.text:
                return response.text.strip()
            else:
                return "Could not transcribe audio. Please try speaking more clearly."
                
        except Exception as e:
            print(f"Error in transcription: {e}")
            return "Error processing audio. Please try again."
    
    def classify_service_request(self, description: str) -> str:
        """
        Classify a service request using AI.
        """
        if not self.model or not GEMINI_API_KEY:
            return self._fallback_classification(description)
        
        try:
            prompt = f"""
            Analyze the following service request from a South African user and classify it into one of these categories:
            - plumbing
            - electrical
            - carpentry
            - painting
            - cleaning
            - gardening
            - appliance repair
            - roofing
            - flooring
            - hvac
            - handyman
            - tech support
            - tutoring
            - beauty services
            - catering
            - photography
            - other
            
            Return ONLY the category name in lowercase.
            
            Service request: "{description}"
            
            Category:
            """
            
            response = self.model.generate_content(prompt)
            classification = response.text.strip().lower()
            
            valid_categories = [
                'plumbing', 'electrical', 'carpentry', 'painting', 'cleaning',
                'gardening', 'appliance repair', 'roofing', 'flooring', 'hvac',
                'handyman', 'tech support', 'tutoring', 'beauty services',
                'catering', 'photography', 'other'
            ]
            
            if classification in valid_categories:
                return classification
            else:
                return 'handyman'
                
        except Exception as e:
            print(f"Error in classification: {e}")
            return self._fallback_classification(description)
    
    def _fallback_classification(self, description: str) -> str:
        """
        Fallback classification using keyword matching.
        """
        desc = description.lower()
        
        if any(k in desc for k in ['plumb', 'pipe', 'leak', 'geyser', 'tap', 'toilet', 'drain']):
            return 'plumbing'
        elif any(k in desc for k in ['light', 'electr', 'plug', 'wiring', 'switch', 'power']):
            return 'electrical'
        elif any(k in desc for k in ['paint', 'wall', 'colour', 'brush']):
            return 'painting'
        elif any(k in desc for k in ['clean', 'vacuum', 'mop', 'dust']):
            return 'cleaning'
        elif any(k in desc for k in ['garden', 'grass', 'tree', 'plant']):
            return 'gardening'
        elif any(k in desc for k in ['roof', 'leak', 'tile', 'gutter']):
            return 'roofing'
        elif any(k in desc for k in ['floor', 'tile', 'wood', 'carpet']):
            return 'flooring'
        elif any(k in desc for k in ['aircon', 'air conditioning', 'heating', 'hvac']):
            return 'hvac'
        elif any(k in desc for k in ['appliance', 'fridge', 'washing', 'stove', 'microwave']):
            return 'appliance repair'
        elif any(k in desc for k in ['wood', 'cabinet', 'shelf', 'door', 'window']):
            return 'carpentry'
        elif any(k in desc for k in ['computer', 'phone', 'tech', 'wifi', 'internet']):
            return 'tech support'
        elif any(k in desc for k in ['tutor', 'teach', 'lesson', 'study', 'homework']):
            return 'tutoring'
        elif any(k in desc for k in ['hair', 'nails', 'beauty', 'makeup']):
            return 'beauty services'
        elif any(k in desc for k in ['food', 'cook', 'cater', 'party', 'event']):
            return 'catering'
        elif any(k in desc for k in ['photo', 'picture', 'wedding', 'event']):
            return 'photography'
        else:
            return 'handyman'
    
    def analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of feedback.
        """
        if not self.model or not GEMINI_API_KEY:
            return 'neutral'
        
        try:
            prompt = f"""
            Analyze the sentiment of this customer feedback and classify it as:
            - positive
            - negative
            - neutral
            
            Return ONLY the sentiment classification.
            
            Feedback: "{text}"
            
            Sentiment:
            """
            
            response = self.model.generate_content(prompt)
            sentiment = response.text.strip().lower()
            
            if sentiment in ['positive', 'negative', 'neutral']:
                return sentiment
            else:
                return 'neutral'
                
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return 'neutral'
    
    def generate_business_insight(self, job_data: list) -> str:
        """
        Generate business insights for fixers based on job data.
        """
        if not self.model or not GEMINI_API_KEY or not job_data:
            return "No insights available at this time."
        
        try:
            prompt = f"""
            You are a business analyst for FixMate-SA, a South African service platform.
            Analyze the following job data and provide one specific, actionable business insight 
            that could help fixers earn more money.
            
            Focus on:
            - High-demand services in specific areas
            - Emerging trends
            - Skills gaps in the market
            - Seasonal opportunities
            
            Job data:
            {job_data}
            
            Provide a single, clear business insight in one sentence.
            
            Insight:
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"Error generating insight: {e}")
            return "Could not generate business insight at this time."
    
    def calculate_smart_match_score(self, fixer_data: dict, job_data: dict) -> dict:
        """
        Calculate AI-powered smart matching score between fixer and job.
        Uses multiple factors beyond just proximity for fair and efficient matching.
        """
        try:
            # Base scoring factors
            factors = {
                'skill_match': 0,      # How well fixer skills match job requirements
                'success_rate': 0,     # Historical success rate for similar jobs
                'location_score': 0,   # Distance-based scoring with travel optimization
                'availability': 0,     # Current availability and schedule fit
                'preference_match': 0, # Client language/cultural preference matching
                'reliability': 0,      # Overall reliability score
                'fairness_boost': 0    # Fair distribution boost for less busy fixers
            }
            
            # 1. Skill Match Analysis (0-30 points)
            if self.model and GEMINI_API_KEY:
                skill_prompt = f"""
                Analyze how well this fixer's skills match the job requirements:
                
                Fixer Skills: {fixer_data.get('services', '')}
                Job Service: {job_data.get('service', '')}
                Job Description: {job_data.get('description', '')}
                
                Rate the skill match from 0-30 where:
                - 30: Perfect specialist match
                - 20-25: Very good match with relevant experience
                - 15-19: Good match with some relevant skills
                - 10-14: Basic match, can handle but not specialized
                - 0-9: Poor match or no relevant skills
                
                Return only the numeric score.
                """
                
                try:
                    response = self.model.generate_content(skill_prompt)
                    factors['skill_match'] = min(30, max(0, int(response.text.strip())))
                except:
                    # Fallback to keyword matching
                    factors['skill_match'] = self._fallback_skill_match(fixer_data, job_data)
            else:
                factors['skill_match'] = self._fallback_skill_match(fixer_data, job_data)
            
            # 2. Success Rate Factor (0-20 points)
            completion_rate = fixer_data.get('completion_rate', 100.0)
            client_satisfaction = fixer_data.get('rating', 0.0)
            factors['success_rate'] = min(20, (completion_rate / 100 * 15) + (client_satisfaction * 2))
            
            # 3. Location Score with Route Optimization (0-20 points)
            distance_km = fixer_data.get('distance_km', float('inf'))
            if distance_km <= 5:
                factors['location_score'] = 20
            elif distance_km <= 10:
                factors['location_score'] = 15
            elif distance_km <= 20:
                factors['location_score'] = 10
            elif distance_km <= 30:
                factors['location_score'] = 5
            else:
                factors['location_score'] = 0
            
            # 4. Availability Score (0-15 points)
            if fixer_data.get('is_available', False):
                current_jobs = fixer_data.get('current_jobs', 0)
                if current_jobs == 0:
                    factors['availability'] = 15
                elif current_jobs == 1:
                    factors['availability'] = 8
                else:
                    factors['availability'] = 0
            
            # 5. Language/Cultural Preference Match (0-10 points)
            client_language = job_data.get('client_language', 'english')
            fixer_languages = fixer_data.get('languages', ['english'])
            if client_language in fixer_languages:
                factors['preference_match'] = 10
            elif 'english' in fixer_languages:
                factors['preference_match'] = 5
            
            # 6. Reliability Score (0-15 points)
            response_time = fixer_data.get('avg_response_time', 60)  # minutes
            reliability_score = fixer_data.get('reliability_score', 100.0)
            
            # Convert response time to score (faster = better)
            if response_time <= 5:
                response_score = 8
            elif response_time <= 15:
                response_score = 6
            elif response_time <= 30:
                response_score = 4
            elif response_time <= 60:
                response_score = 2
            else:
                response_score = 0
            
            factors['reliability'] = response_score + (reliability_score / 100 * 7)
            
            # 7. Fairness Boost for Equal Opportunity (0-10 points)
            # Give boost to fixers who haven't had recent jobs
            last_job_hours = fixer_data.get('hours_since_last_job', 0)
            if last_job_hours >= 168:  # 1 week
                factors['fairness_boost'] = 10
            elif last_job_hours >= 72:  # 3 days
                factors['fairness_boost'] = 6
            elif last_job_hours >= 24:  # 1 day
                factors['fairness_boost'] = 3
            
            # Calculate total score
            total_score = sum(factors.values())
            
            # Generate AI explanation if available
            explanation = self._generate_match_explanation(factors, fixer_data, job_data)
            
            return {
                'total_score': round(total_score, 2),
                'max_possible_score': 110,
                'percentage': round((total_score / 110) * 100, 1),
                'factors': factors,
                'explanation': explanation,
                'recommendation': 'excellent' if total_score >= 85 else 'good' if total_score >= 65 else 'fair' if total_score >= 45 else 'poor'
            }
            
        except Exception as e:
            print(f"Error calculating match score: {e}")
            return {
                'total_score': 0,
                'max_possible_score': 110,
                'percentage': 0,
                'factors': factors,
                'explanation': 'Error calculating match score',
                'recommendation': 'poor'
            }
    
    def _fallback_skill_match(self, fixer_data: dict, job_data: dict) -> float:
        """Fallback skill matching using keyword analysis"""
        fixer_services = fixer_data.get('services', '').lower()
        job_service = job_data.get('service', '').lower()
        job_description = job_data.get('description', '').lower()
        
        # Direct service match
        if job_service in fixer_services:
            return 25
        
        # Keyword matching
        job_keywords = job_service.split() + job_description.split()
        matches = sum(1 for keyword in job_keywords if len(keyword) > 3 and keyword in fixer_services)
        
        return min(20, matches * 3)
    
    def _generate_match_explanation(self, factors: dict, fixer_data: dict, job_data: dict) -> str:
        """Generate human-readable explanation of match score"""
        explanations = []
        
        if factors['skill_match'] >= 20:
            explanations.append("Excellent skill match for this service type")
        elif factors['skill_match'] >= 15:
            explanations.append("Good skill match with relevant experience")
        elif factors['skill_match'] >= 10:
            explanations.append("Basic skill match")
        
        if factors['success_rate'] >= 15:
            explanations.append("High success rate and client satisfaction")
        
        if factors['location_score'] >= 15:
            explanations.append("Very close to job location")
        elif factors['location_score'] >= 10:
            explanations.append("Reasonable distance to job")
        
        if factors['availability'] >= 12:
            explanations.append("Immediately available")
        
        if factors['fairness_boost'] >= 6:
            explanations.append("Hasn't had recent jobs (fair distribution)")
        
        return "; ".join(explanations) if explanations else "Standard match"
    
    def rank_fixers_for_job(self, fixers_data: list, job_data: dict) -> list:
        """
        Rank fixers for a job using AI-powered smart matching.
        Returns sorted list with best matches first.
        """
        ranked_fixers = []
        
        for fixer in fixers_data:
            match_score = self.calculate_smart_match_score(fixer, job_data)
            
            ranked_fixers.append({
                'fixer_id': fixer.get('id'),
                'fixer_name': fixer.get('name'),
                'fixer_phone': fixer.get('phone'),
                'match_score': match_score['total_score'],
                'match_percentage': match_score['percentage'],
                'recommendation': match_score['recommendation'],
                'explanation': match_score['explanation'],
                'factors': match_score['factors'],
                'fixer_data': fixer
            })
        
        # Sort by match score (highest first)
        ranked_fixers.sort(key=lambda x: x['match_score'], reverse=True)
        
        return ranked_fixers
    
    def generate_matching_insights(self, job_data: dict, ranked_fixers: list) -> dict:
        """
        Generate insights about the matching process for this job.
        """
        if not ranked_fixers:
            return {
                'status': 'no_matches',
                'message': 'No eligible fixers found for this job',
                'recommendations': ['Consider expanding search radius', 'Adjust job requirements']
            }
        
        best_match = ranked_fixers[0]
        insights = {
            'status': 'matches_found',
            'total_candidates': len(ranked_fixers),
            'best_match': {
                'fixer_name': best_match['fixer_name'],
                'score': best_match['match_score'],
                'percentage': best_match['match_percentage'],
                'explanation': best_match['explanation']
            },
            'quality_distribution': {},
            'recommendations': []
        }
        
        # Analyze quality distribution
        excellent = sum(1 for f in ranked_fixers if f['recommendation'] == 'excellent')
        good = sum(1 for f in ranked_fixers if f['recommendation'] == 'good')
        fair = sum(1 for f in ranked_fixers if f['recommendation'] == 'fair')
        poor = sum(1 for f in ranked_fixers if f['recommendation'] == 'poor')
        
        insights['quality_distribution'] = {
            'excellent': excellent,
            'good': good,
            'fair': fair,
            'poor': poor
        }
        
        # Generate recommendations
        if excellent >= 3:
            insights['recommendations'].append('Multiple excellent matches available - expect quick assignment')
        elif excellent + good >= 2:
            insights['recommendations'].append('Good quality matches available')
        elif fair + good + excellent == 0:
            insights['recommendations'].append('Consider adjusting job requirements or expanding search area')
        
        if best_match['match_percentage'] < 50:
            insights['recommendations'].append('Best match is below 50% - consider reviewing job details')
        
        return insights

    # ==================== ENHANCED AI MATCHING METHODS ====================
    
    def calculate_enhanced_match_score(self, fixer_data: dict, job_data: dict, context: dict = None) -> dict:
        """
        Enhanced AI-powered matching with reinforcement learning and advanced algorithms
        """
        try:
            # Use OpenAI for advanced reasoning if available, fallback to Gemini
            if self.openai_client:
                return self._openai_enhanced_matching(fixer_data, job_data, context)
            elif self.gemini_model:
                return self._gemini_enhanced_matching(fixer_data, job_data, context)
            else:
                return self._fallback_enhanced_matching(fixer_data, job_data, context)
        
        except Exception as e:
            logger.error(f"Error in enhanced matching: {e}")
            return self.calculate_smart_match_score(fixer_data, job_data)

    def _openai_enhanced_matching(self, fixer_data: dict, job_data: dict, context: dict = None) -> dict:
        """
        OpenAI-powered enhanced matching with advanced reasoning
        """
        try:
            # Prepare enhanced matching prompt
            matching_prompt = self._build_enhanced_matching_prompt(fixer_data, job_data, context)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert job-matching AI for FixMate-SA, analyzing complex matching factors with advanced reasoning."},
                    {"role": "user", "content": matching_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse OpenAI response
            result = json.loads(response.choices[0].message.content)
            
            # Apply reinforcement learning adjustments
            result = self._apply_reinforcement_learning(result, fixer_data, job_data)
            
            return result
            
        except Exception as e:
            logger.error(f"OpenAI enhanced matching error: {e}")
            return self._gemini_enhanced_matching(fixer_data, job_data, context)

    def _gemini_enhanced_matching(self, fixer_data: dict, job_data: dict, context: dict = None) -> dict:
        """
        Gemini-powered enhanced matching with multilingual support
        """
        try:
            matching_prompt = self._build_enhanced_matching_prompt(fixer_data, job_data, context)
            
            response = self.gemini_model.generate_content(matching_prompt)
            result = json.loads(response.text)
            
            # Apply language preference enhancements
            result = self._apply_language_preferences(result, fixer_data, job_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini enhanced matching error: {e}")
            return self._fallback_enhanced_matching(fixer_data, job_data, context)

    def _build_enhanced_matching_prompt(self, fixer_data: dict, job_data: dict, context: dict = None) -> str:
        """
        Build comprehensive matching prompt for enhanced analysis
        """
        context = context or {}
        
        return f"""
        Analyze this job-fixer match using advanced algorithms and provide a detailed scoring:

        === JOB DETAILS ===
        Service: {job_data.get('service', '')}
        Description: {job_data.get('description', '')}
        Location: {job_data.get('location', '')}
        Urgency: {job_data.get('urgency', 'normal')}
        Budget: R{job_data.get('estimated_price', 'N/A')}
        Client Language: {job_data.get('preferred_language', 'English')}
        Time Window: {job_data.get('preferred_time', 'Flexible')}

        === FIXER PROFILE ===
        Skills: {fixer_data.get('services', '')}
        Experience: {fixer_data.get('experience_years', 0)} years
        Rating: {fixer_data.get('rating', 0)}/5.0 ({fixer_data.get('total_reviews', 0)} reviews)
        Success Rate: {fixer_data.get('completion_rate', 100)}%
        Languages: {fixer_data.get('languages', ['English'])}
        Availability: {fixer_data.get('availability', 'Unknown')}
        Location: {fixer_data.get('location', '')}
        Distance: {fixer_data.get('distance_km', 'N/A')} km
        Recent Jobs: {fixer_data.get('recent_job_count', 0)} (last 30 days)

        === CONTEXT DATA ===
        Historical Success: {context.get('historical_success_rate', 'N/A')}
        Similar Jobs: {context.get('similar_jobs_completed', 0)}
        Peak Hours: {context.get('is_peak_hours', False)}
        Weather: {context.get('weather_conditions', 'Good')}

        ANALYZE AND SCORE (0-100):
        1. Skill Match (0-25): Exact specialization vs basic capability
        2. Success Probability (0-20): Historical success + fixer reliability  
        3. Location Optimization (0-15): Distance + route efficiency + travel patterns
        4. Availability Fit (0-15): Time alignment + workload balance
        5. Language/Cultural Match (0-10): Communication effectiveness
        6. Fair Distribution (0-10): Prevent over-booking, support newer fixers
        7. Reinforcement Bonus (0-5): Learning from past successful matches

        Return JSON:
        {{
            "total_score": 0-100,
            "breakdown": {{
                "skill_match": 0-25,
                "success_probability": 0-20, 
                "location_optimization": 0-15,
                "availability_fit": 0-15,
                "language_match": 0-10,
                "fair_distribution": 0-10,
                "reinforcement_bonus": 0-5
            }},
            "confidence_level": "high|medium|low",
            "success_prediction": "90% likely to complete successfully",
            "risk_factors": ["weather dependent", "first-time client"],
            "optimization_suggestions": ["schedule during morning hours"],
            "match_reasoning": "Detailed explanation of why this is a good/poor match"
        }}
        """

    def _apply_reinforcement_learning(self, result: dict, fixer_data: dict, job_data: dict) -> dict:
        """
        Apply reinforcement learning adjustments based on historical performance
        """
        try:
            fixer_id = fixer_data.get('id', '')
            service_type = job_data.get('service', '')
            
            # Get historical performance patterns
            pattern_key = f"{fixer_id}_{service_type}"
            if pattern_key in self.success_patterns:
                pattern = self.success_patterns[pattern_key]
                
                # Adjust scores based on learned patterns
                if pattern['success_rate'] > 0.9:
                    result['breakdown']['reinforcement_bonus'] = min(5, result['breakdown'].get('reinforcement_bonus', 0) + 3)
                elif pattern['success_rate'] < 0.7:
                    result['breakdown']['reinforcement_bonus'] = max(0, result['breakdown'].get('reinforcement_bonus', 0) - 2)
                
                # Update total score
                result['total_score'] = sum(result['breakdown'].values())
                
                # Add learning insights
                result['learning_insights'] = {
                    'historical_success_rate': pattern['success_rate'],
                    'pattern_confidence': pattern['confidence'],
                    'similar_jobs_completed': pattern['job_count']
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Reinforcement learning error: {e}")
            return result

    def _apply_language_preferences(self, result: dict, fixer_data: dict, job_data: dict) -> dict:
        """
        Apply South African language preference matching
        """
        try:
            client_lang = job_data.get('preferred_language', 'English')
            fixer_langs = fixer_data.get('languages', ['English'])
            
            # South African language hierarchy for matching
            sa_language_groups = {
                'English': ['English'],
                'Afrikaans': ['Afrikaans', 'English'],
                'Zulu': ['Zulu', 'English'],
                'Xhosa': ['Xhosa', 'English'],
                'Sotho': ['Sotho', 'English'],
                'Tswana': ['Tswana', 'English'],
                'Venda': ['Venda', 'English'],
                'Tsonga': ['Tsonga', 'English'],
                'Swati': ['Swati', 'English'],
                'Ndebele': ['Ndebele', 'English'],
                'Pedi': ['Pedi', 'English']
            }
            
            # Enhanced language matching
            if client_lang in fixer_langs:
                # Perfect match
                result['breakdown']['language_match'] = min(10, result['breakdown'].get('language_match', 0) + 3)
            elif client_lang in sa_language_groups and any(lang in fixer_langs for lang in sa_language_groups[client_lang]):
                # Good regional match
                result['breakdown']['language_match'] = min(10, result['breakdown'].get('language_match', 0) + 2)
            elif 'English' in fixer_langs:
                # English fallback (standard in SA)
                result['breakdown']['language_match'] = min(10, result['breakdown'].get('language_match', 0) + 1)
            
            # Update total
            result['total_score'] = sum(result['breakdown'].values())
            
            return result
            
        except Exception as e:
            logger.error(f"Language preference error: {e}")
            return result

    def _fallback_enhanced_matching(self, fixer_data: dict, job_data: dict, context: dict = None) -> dict:
        """
        Fallback enhanced matching when AI services are unavailable
        """
        # Use the existing smart match score as base
        base_result = self.calculate_smart_match_score(fixer_data, job_data)
        
        # Add enhanced structure
        enhanced_result = {
            "total_score": base_result.get('total_score', 0),
            "breakdown": {
                "skill_match": base_result.get('factors', {}).get('skill_match', 0),
                "success_probability": base_result.get('factors', {}).get('success_rate', 0),
                "location_optimization": base_result.get('factors', {}).get('location_score', 0),
                "availability_fit": base_result.get('factors', {}).get('availability', 0),
                "language_match": base_result.get('factors', {}).get('preference_match', 0),
                "fair_distribution": base_result.get('factors', {}).get('fairness_boost', 0),
                "reinforcement_bonus": 0
            },
            "confidence_level": "medium",
            "success_prediction": f"{min(95, max(60, base_result.get('total_score', 0)))}% likely to complete successfully",
            "risk_factors": ["Limited AI analysis available"],
            "optimization_suggestions": ["Standard matching applied"],
            "match_reasoning": base_result.get('explanation', 'Basic matching algorithm used')
        }
        
        return enhanced_result

    def update_matching_performance(self, fixer_id: str, job_id: str, service_type: str, 
                                   success: bool, completion_time: float = None, 
                                   client_satisfaction: float = None):
        """
        Update reinforcement learning patterns based on job outcomes
        """
        try:
            pattern_key = f"{fixer_id}_{service_type}"
            
            if pattern_key not in self.success_patterns:
                self.success_patterns[pattern_key] = {
                    'success_rate': 1.0 if success else 0.0,
                    'job_count': 1,
                    'confidence': 0.1,
                    'avg_completion_time': completion_time,
                    'avg_satisfaction': client_satisfaction
                }
            else:
                pattern = self.success_patterns[pattern_key]
                
                # Update success rate with weighted average
                pattern['success_rate'] = (pattern['success_rate'] * pattern['job_count'] + (1.0 if success else 0.0)) / (pattern['job_count'] + 1)
                pattern['job_count'] += 1
                pattern['confidence'] = min(1.0, pattern['confidence'] + 0.1)
                
                if completion_time:
                    pattern['avg_completion_time'] = (pattern.get('avg_completion_time', completion_time) + completion_time) / 2
                
                if client_satisfaction:
                    pattern['avg_satisfaction'] = (pattern.get('avg_satisfaction', client_satisfaction) + client_satisfaction) / 2
            
            # Store in matching history
            self.matching_history.append({
                'timestamp': datetime.now().isoformat(),
                'fixer_id': fixer_id,
                'job_id': job_id,
                'service_type': service_type,
                'success': success,
                'completion_time': completion_time,
                'satisfaction': client_satisfaction
            })
            
            # Keep only last 1000 entries
            if len(self.matching_history) > 1000:
                self.matching_history = self.matching_history[-1000:]
                
            logger.info(f"Updated matching performance for {pattern_key}: {pattern['success_rate']:.2f} success rate")
            
        except Exception as e:
            logger.error(f"Error updating matching performance: {e}")

    def get_matching_insights(self, timeframe_days: int = 30) -> dict:
        """
        Get analytical insights from matching performance data
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=timeframe_days)
            
            recent_matches = [
                match for match in self.matching_history 
                if datetime.fromisoformat(match['timestamp']) > cutoff_date
            ]
            
            if not recent_matches:
                return {"message": "No recent matching data available"}
            
            # Calculate insights
            total_matches = len(recent_matches)
            successful_matches = sum(1 for match in recent_matches if match['success'])
            success_rate = successful_matches / total_matches if total_matches > 0 else 0
            
            # Service type performance
            service_performance = {}
            for match in recent_matches:
                service = match['service_type']
                if service not in service_performance:
                    service_performance[service] = {'total': 0, 'successful': 0}
                service_performance[service]['total'] += 1
                if match['success']:
                    service_performance[service]['successful'] += 1
            
            # Calculate service success rates
            for service in service_performance:
                perf = service_performance[service]
                perf['success_rate'] = perf['successful'] / perf['total'] if perf['total'] > 0 else 0
            
            # Top performing patterns
            top_patterns = sorted(
                [(k, v) for k, v in self.success_patterns.items() if v['job_count'] >= 3],
                key=lambda x: x[1]['success_rate'],
                reverse=True
            )[:10]
            
            return {
                'timeframe_days': timeframe_days,
                'total_matches': total_matches,
                'success_rate': success_rate,
                'service_performance': service_performance,
                'top_patterns': [
                    {
                        'pattern': pattern[0],
                        'success_rate': pattern[1]['success_rate'],
                        'job_count': pattern[1]['job_count'],
                        'confidence': pattern[1]['confidence']
                    }
                    for pattern in top_patterns
                ],
                'recommendations': self._generate_matching_recommendations(service_performance, top_patterns)
            }
            
        except Exception as e:
            logger.error(f"Error generating matching insights: {e}")
            return {"error": str(e)}

    def _generate_matching_recommendations(self, service_performance: dict, top_patterns: list) -> list:
        """
        Generate recommendations based on matching performance analysis
        """
        recommendations = []
        
        try:
            # Identify underperforming services
            for service, perf in service_performance.items():
                if perf['success_rate'] < 0.7 and perf['total'] >= 5:
                    recommendations.append(f"Service '{service}' has low success rate ({perf['success_rate']:.1%}). Consider reviewing fixer qualifications.")
            
            # Identify top performers
            if top_patterns:
                best_pattern = top_patterns[0]
                recommendations.append(f"Pattern '{best_pattern[0]}' shows excellent performance ({best_pattern[1]['success_rate']:.1%}). Consider promoting similar matches.")
            
            # General recommendations
            if len(service_performance) > 0:
                avg_success = sum(perf['success_rate'] for perf in service_performance.values()) / len(service_performance)
                if avg_success > 0.85:
                    recommendations.append("Overall matching performance is excellent. Continue current strategies.")
                elif avg_success < 0.75:
                    recommendations.append("Overall matching performance needs improvement. Consider enhancing fixer vetting or client requirements.")
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Unable to generate specific recommendations due to data analysis error.")
        
        return recommendations

# Global instance
ai_service = EnhancedAIService()