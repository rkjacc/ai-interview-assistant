import os
import json
from google import genai
from pathlib import Path
import sys
import re
from typing import List, Dict

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import GEMINI_MODEL_NAME, GEMINI_API_KEY
from logger import get_app_logger

_app_log = get_app_logger()


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
        """
        Generate interview Q&A based on experience.
        
        Args:
            experience_tools: Candidate's skills, tools, and experience
            num_questions: Number of questions to generate
            
        Returns:
            Raw response text from Gemini containing Q&A pairs
        """
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
        _app_log.info(
            "[LLM] Sending request to Gemini | model=%s | "
            "prompt_length=%d chars | num_questions=%d",
            self.model_name,
            len(prompt),
            num_questions,
        )
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            response_text = response.text if response else ""
            _app_log.info(
                "[LLM] Response received from Gemini | model=%s | "
                "response_length=%d chars",
                self.model_name,
                len(response_text),
            )
            return response_text
        except Exception as e:
            _app_log.error("[LLM] Gemini API error: %s", str(e))
            print(f"[ERROR] API Error: {str(e)}")
            return ""
    
    @staticmethod
    def parse_qa_response(response_text: str) -> List[Dict[str, str]]:
        """
        Parse Q&A response from Gemini into structured JSON objects.
        
        Args:
            response_text: Raw response text from Gemini
            
        Returns:
            List of dictionaries with Topic, Question, Answer
        """
        qa_items = []
        
        if not response_text:
            return qa_items
        
        # Try to parse JSON objects
        # Look for JSON patterns: {...} on individual lines
        json_pattern = r'\{[^{}]*"Topic"[^{}]*"Question"[^{}]*"Answer"[^{}]*\}'
        matches = re.finditer(json_pattern, response_text, re.DOTALL)
        
        for match in matches:
            try:
                json_str = match.group(0)
                # Clean up the JSON
                json_str = json_str.replace('\n', ' ')
                qa_data = json.loads(json_str)
                
                # Validate required fields
                if all(key in qa_data for key in ['Topic', 'Question', 'Answer']):
                    qa_items.append({
                        'Topic': str(qa_data['Topic']).strip(),
                        'Question': str(qa_data['Question']).strip(),
                        'Answer': str(qa_data['Answer']).strip()
                    })
            except json.JSONDecodeError:
                continue
        
        # Fallback: If no JSON objects found, try line-by-line parsing
        if not qa_items:
            qa_items = GeminiService._parse_fallback(response_text)
        
        return qa_items
    
    @staticmethod
    def _parse_fallback(text: str) -> List[Dict[str, str]]:
        """
        Fallback parsing method for non-JSON formatted responses.
        
        Args:
            text: Response text to parse
            
        Returns:
            List of Q&A dictionaries
        """
        qa_items = []
        current_qa = {}
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            
            if line.startswith('"Topic"') or line.startswith('Topic:'):
                if current_qa and 'Topic' in current_qa:
                    if 'Question' in current_qa and 'Answer' in current_qa:
                        qa_items.append(current_qa)
                    current_qa = {}
                
                # Extract topic value
                value = line.split(':', 1)[1] if ':' in line else line.split(':', 1)[1]
                current_qa['Topic'] = value.strip().strip('"')
            
            elif line.startswith('"Question"') or line.startswith('Question:'):
                value = line.split(':', 1)[1] if ':' in line else line.split(':', 1)[1]
                current_qa['Question'] = value.strip().strip('"')
            
            elif line.startswith('"Answer"') or line.startswith('Answer:'):
                value = line.split(':', 1)[1] if ':' in line else line.split(':', 1)[1]
                current_qa['Answer'] = value.strip().strip('"')
        
        # Add last item
        if current_qa and all(key in current_qa for key in ['Topic', 'Question', 'Answer']):
            qa_items.append(current_qa)
        
        return qa_items
