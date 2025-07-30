import os
import io
import tempfile
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel('models/gemini-1.5-flash') if GEMINI_API_KEY else None
    
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

# Global instance
ai_service = AIService()