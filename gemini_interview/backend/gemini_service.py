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
    
    # Supported programming languages for code examples
    SUPPORTED_LANGUAGES = [
        'python', 'javascript', 'typescript', 'java', 'c#', 'csharp',
        'go', 'rust', 'php', 'ruby', 'swift', 'kotlin',
        'c++', 'cpp', 'sql', 'r', 'scala'
    ]
    
    def __init__(self, api_key: str = None):
        """Initialize Gemini service with API key"""
        # Use provided key, fall back to config
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("API key not found. Set GEMINI_API_KEY env var or add to secret_api_key.txt")
        
        self.client = genai.Client(api_key=self.api_key)
        # Use model name from centralized config
        self.model_name = GEMINI_MODEL_NAME
    
    @staticmethod
    def extract_programming_languages(experience_text: str) -> str:
        """
        Extract programming languages from candidate's experience text.
        
        Args:
            experience_text: Candidate's experience/skills text
            
        Returns:
            Comma-separated string of detected languages, or 'Python' as default
        """
        if not experience_text:
            return "Python"
        
        experience_lower = experience_text.lower()
        detected_languages = []
        
        language_keywords = {
            'python': ['python', 'django', 'flask', 'fastapi', 'celery', 'pandas', 'numpy'],
            'javascript': ['javascript', 'js', 'node.js', 'nodejs', 'express', 'react', 'vue', 'angular', 'webpack'],
            'typescript': ['typescript', 'ts', 'nestjs', 'angular'],
            'java': ['java', 'spring', 'spring boot', 'maven', 'gradle', 'junit', 'hibernate'],
            'c#': ['c#', 'csharp', '.net', 'dotnet', 'asp.net', 'entity framework'],
            'go': ['golang', 'go', 'gin', 'goroutine'],
            'rust': ['rust', 'cargo', 'actix'],
            'php': ['php', 'laravel', 'symfony', 'composer'],
            'sql': ['sql', 'postgresql', 'postgres', 'mysql', 'oracle', 'tsql', 't-sql', 'sqlite', 'mongodb', 'redis'],
            'swift': ['swift', 'ios', 'xcode'],
            'kotlin': ['kotlin', 'android'],
            'ruby': ['ruby', 'rails', 'sinatra'],
        }
        
        for language, keywords in language_keywords.items():
            for keyword in keywords:
                if keyword in experience_lower:
                    if language not in detected_languages:
                        detected_languages.append(language)
                    break
        
        if detected_languages:
            return ', '.join(detected_languages)
        return "Python"
    
    def generate_interview_qa(self, experience_tools: str, num_questions: int) -> str:
        """
        Generate interview Q&A based on experience with diverse question types.
        
        Args:
            experience_tools: Candidate's skills, tools, and experience
            num_questions: Number of questions to generate
            
        Returns:
            Raw response text from Gemini containing Q&A pairs
        """
        # Extract programming languages from candidate profile
        detected_languages = self.extract_programming_languages(experience_tools)
        
        # Calculate question distribution
        technical_count = int(num_questions * 0.40)
        project_count = int(num_questions * 0.40)
        coding_count = num_questions - technical_count - project_count
        
        prompt = f"""
You are an expert technical interviewer creating interview questions for a software engineer.

CANDIDATE PROFILE:
{experience_tools}

TASK: Generate exactly {num_questions} interview questions with comprehensive answers following this distribution:
- {technical_count} TECHNICAL questions (~40%)
- {project_count} PROJECT/EXPERIENCE & TOOLS questions (~40%)
- {coding_count} CODING/PRACTICAL questions (~20%)

QUESTION TYPE GUIDELINES:

1. TECHNICAL QUESTIONS (Core Concepts & Architecture):
   - Deep dive into design patterns, architecture principles, scalability
   - System design, performance optimization, security best practices
   - Technologies, frameworks, libraries in their experience
   - Focus on "why" and "how" over surface-level knowledge
   - Ask about trade-offs and decision-making

2. PROJECT/EXPERIENCE & TOOLS QUESTIONS (Real-World Application):
   - Behavioral questions about actual projects and experiences
   - How they used specific tools, frameworks, or technologies
   - Problem-solving approaches and challenges overcome
   - Team collaboration and technical leadership
   - Decision-making in real scenarios

3. CODING/PRACTICAL QUESTIONS (Web Development Focused):
   - Practical web application scenarios (API design, validation, async handling)
   - Database query optimization, backend logic
   - Bug fixing or code improvement challenges
   - Technology to use: {detected_languages}
   - IMPORTANT: Provide runnable code examples in answers with:
     * Correct implementation
     * Edge cases and error handling
     * Performance considerations
     * Best practices and comments

ANSWER REQUIREMENTS:
- Each answer MUST be comprehensive (150-300 words for technical/project, 200-400 words for coding)
- Include code examples for coding questions with proper syntax highlighting
- Explain concepts clearly with real-world examples
- For coding questions: include the complete function/class implementation
- Mention edge cases, performance considerations, and best practices
- Be specific - avoid generic answers

FORMAT REQUIREMENT:
Return each Q&A as valid JSON on separate lines (no markdown, no triple backticks):
{{"Topic": "Subject", "Question": "Question text", "Answer": "Answer text with code examples if needed"}}

IMPORTANT: Separate each JSON object with a blank line. Ensure each JSON is valid and properly escaped.
"""
        
        _app_log.info(
            "[LLM] Sending request to Gemini | model=%s | "
            "prompt_length=%d chars | num_questions=%d | "
            "distribution=tech:%d project:%d coding:%d | detected_languages=%s",
            self.model_name,
            len(prompt),
            num_questions,
            technical_count,
            project_count,
            coding_count,
            detected_languages,
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
        Improved to handle comprehensive answers with code examples.
        
        Args:
            response_text: Raw response text from Gemini
            
        Returns:
            List of dictionaries with Topic, Question, Answer
        """
        qa_items = []
        
        if not response_text:
            return qa_items
        
        # Split by blank lines to separate JSON objects
        # Each JSON object should be on its own block
        blocks = re.split(r'\n\s*\n', response_text)
        
        for block in blocks:
            block = block.strip()
            if not block or not block.startswith('{'):
                continue
            
            try:
                # Try to parse JSON directly
                # Handle cases where the JSON might span multiple lines
                qa_data = json.loads(block)
                
                # Validate required fields
                if all(key in qa_data for key in ['Topic', 'Question', 'Answer']):
                    qa_items.append({
                        'Topic': str(qa_data['Topic']).strip(),
                        'Question': str(qa_data['Question']).strip(),
                        'Answer': str(qa_data['Answer']).strip()
                    })
            except json.JSONDecodeError:
                # Try regex pattern matching as fallback for inline JSON
                json_pattern = r'\{[^{}]*"Topic"[^{}]*"Question"[^{}]*"Answer"[^{}]*\}'
                match = re.search(json_pattern, block, re.DOTALL)
                if match:
                    try:
                        json_str = match.group(0)
                        qa_data = json.loads(json_str)
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
