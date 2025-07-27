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

# Global instance
ai_service = AIService()