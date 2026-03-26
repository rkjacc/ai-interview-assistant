import sys
import os
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import InterviewRequest, InterviewResponse, FileUploadRequest
from gemini_service import GeminiService

# Import centralized config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import GEMINI_API_KEY

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Gemini Interview Q&A API",
    description="API for generating interview questions using Google Gemini",
    version="1.0.0"
)

# Add CORS middleware to allow Streamlit requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instance
gemini_service = None


@app.on_event("startup")
async def startup_event():
    """Initialize Gemini service on startup"""
    global gemini_service
    try:
        if GEMINI_API_KEY:
            gemini_service = GeminiService(GEMINI_API_KEY)
            print("[OK] Gemini Service ready")
        else:
            print("[INFO] Running without API key (demo mode)")
            gemini_service = None
    except Exception as e:
        print(f"[ERROR] Startup failed: {str(e)}")
        gemini_service = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Gemini Interview Q&A API",
        "endpoints": {
            "generate": "/api/generate",
            "health": "/health",
            "upload": "/api/upload"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    service_status = "connected" if gemini_service else "disconnected"
    return {
        "status": "ok",
        "gemini_service": service_status
    }


@app.post("/api/generate", response_model=InterviewResponse)
async def generate_interview(request: InterviewRequest):
    """
    Generate interview questions and answers based on candidate experience
    
    Args:
        request: InterviewRequest containing candidate experience and num_questions
        
    Returns:
        InterviewResponse with generated Q&A
    """
    if not gemini_service:
        raise HTTPException(
            status_code=503,
            detail="Gemini Service not available. Check API key configuration."
        )
    
    if not request.candidate_experience.strip():
        raise HTTPException(
            status_code=400,
            detail="Candidate experience cannot be empty"
        )
    
    if request.num_questions < 1 or request.num_questions > 100:
        raise HTTPException(
            status_code=400,
            detail="Number of questions must be between 1 and 100"
        )
    
    try:
        result = gemini_service.generate_interview_qa(
            request.candidate_experience,
            request.num_questions
        )
        
        return InterviewResponse(
            status="success",
            data=result
        )
    except Exception as e:
        return InterviewResponse(
            status="error",
            error=str(e)
        )


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a text file containing candidate experience/profile
    
    Args:
        file: Uploaded text file
        
    Returns:
        File content and metadata
    """
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        
        return {
            "status": "success",
            "filename": file.filename,
            "content": text_content,
            "size": len(text_content)
        }
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be in UTF-8 text format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@app.post("/api/generate-from-upload")
async def generate_from_upload(
    file: UploadFile = File(...),
    num_questions: int = 30
):
    """
    Combined endpoint: Upload file and generate interview Q&A
    
    Args:
        file: Uploaded text file with candidate experience
        num_questions: Number of questions to generate
        
    Returns:
        Generated interview Q&A
    """
    if not gemini_service:
        raise HTTPException(
            status_code=503,
            detail="Gemini Service not available"
        )
    
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode("utf-8")
        
        if not text_content.strip():
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        # Generate Q&A
        result = gemini_service.generate_interview_qa(
            text_content,
            num_questions
        )
        
        return {
            "status": "success",
            "filename": file.filename,
            "num_questions": num_questions,
            "generated_qa": result
        }
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be in UTF-8 text format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )
