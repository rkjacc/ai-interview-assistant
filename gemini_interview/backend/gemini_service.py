import os
from google import genai
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import GEMINI_MODEL_NAME, GEMINI_API_KEY


class GeminiService:
    """Service class to handle Gemini API interactions"""
    
    def __init__(self, api_key: str = None):
        """Initialize Gemini service with API key"""
        # Use provided key, fall back to config
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("API key not found. Set GEMINI_API_KEY env var or add to secret_api_key.txt")
        
        self.client = genai.Client(api_key=self.api_key)
        # Use model name from centralized config
        self.model_name = GEMINI_MODEL_NAME
    
    def generate_interview_qa(self, experience_tools: str, num_questions: int) -> str:
        """Generate interview Q&A based on experience"""
        prompt = f"""
Role: Expert Technical Interviewer

Candidate Profile: {experience_tools}

Task: Create {num_questions} interview questions with answers based on this experience.

Format each Q&A as JSON without markdown:
{{
"Topic": "Subject",
"Question": "Question text",
"Answer": "Answer text"
}}

Separate questions with blank lines.
"""
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text if response else ""
        except Exception as e:
            print(f"[ERROR] API Error: {str(e)}")
            return ""
