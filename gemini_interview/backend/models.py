from pydantic import BaseModel
from typing import Optional


class InterviewRequest(BaseModel):
    """Request model for generating interview Q&A"""
    candidate_experience: str
    num_questions: int = 30
    description: Optional[str] = None


class InterviewResponse(BaseModel):
    """Response model for interview Q&A"""
    status: str
    data: Optional[str] = None
    error: Optional[str] = None


class FileUploadRequest(BaseModel):
    """Request model for file uploads"""
    filename: str
    content: str
