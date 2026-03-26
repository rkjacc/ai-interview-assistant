"""
Centralized configuration for Gemini Interview Q&A Generator
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API Configuration
def get_api_key():
    """Get API key from environment variable or secret_api_key.txt file"""
    # First, try environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    # Then, try reading from secret_api_key.txt
    try:
        config_dir = Path(__file__).parent
        secret_file = config_dir / "secret_api_key.txt"
        
        if secret_file.exists():
            with open(secret_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("api_key"):
                        key_part = line.split("=", 1)[1].strip()
                        api_key = key_part.strip('"').strip("'")
                        if api_key and api_key != "YOUR_KEY_HERE":
                            return api_key
    except Exception as e:
        print(f"Error reading API key from file: {e}")
    
    return None

GEMINI_API_KEY = get_api_key()
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash-lite")

# Number of interview questions to generate
DEFAULT_NUM_QUESTIONS = 15

# FastAPI Configuration
FASTAPI_HOST = "127.0.0.1"
FASTAPI_PORT = 8000

# Streamlit Configuration
STREAMLIT_PORT = 8501
