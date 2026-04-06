from pydantic import BaseModel
from typing import Optional, List


class InterviewRequest(BaseModel):
    """Request model for generating interview Q&A from text"""
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


class QAItem(BaseModel):
    """Single Q&A item"""
    Topic: str
    Question: str
    Answer: str


class ResumeUploadRequest(BaseModel):
    """Request model for resume upload and processing"""
    num_questions: int = 30


class ResumeProcessResponse(BaseModel):
    """Response model for resume processing"""
    status: str
    extracted_text: Optional[str] = None
    redacted_text: Optional[str] = None
    qa_items: Optional[List[QAItem]] = None
    file_metadata: Optional[dict] = None
    error: Optional[str] = None


class PIIReport(BaseModel):
    """Report of PII detected in resume"""
    emails: List[str] = []
    phone_numbers: List[str] = []
    urls: List[str] = []
    detected_pii: bool = False
