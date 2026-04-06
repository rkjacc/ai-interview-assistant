import sys
import os
from pathlib import Path
import tempfile
import base64

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from dotenv import load_dotenv

from models import InterviewRequest, InterviewResponse, FileUploadRequest, ResumeProcessResponse, QAItem
from gemini_service import GeminiService
from resume_parser import ResumeParser
from pii_redactor import PIIRedactor
from excel_exporter import ExcelExporter
from logger import get_app_logger, get_pii_audit_logger

# Import centralized config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import GEMINI_API_KEY

# Load environment variables
load_dotenv()

# Module-level loggers
_app_log   = get_app_logger()
_audit_log = get_pii_audit_logger()

# Initialize FastAPI app
app = FastAPI(
    title="Gemini Interview Q&A API",
    description="API for generating interview questions using Google Gemini with resume parsing",
    version="2.0.0"
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
    _app_log.info("[STARTUP] FastAPI application starting up")
    try:
        if GEMINI_API_KEY:
            gemini_service = GeminiService(GEMINI_API_KEY)
            _app_log.info(
                "[STARTUP] Gemini service initialized | model=%s",
                gemini_service.model_name,
            )
            print("[OK] Gemini Service ready")
        else:
            _app_log.warning("[STARTUP] No API key found — running in demo mode")
            print("[INFO] Running without API key (demo mode)")
            gemini_service = None
    except Exception as e:
        _app_log.error("[STARTUP] Failed to initialize Gemini service: %s", str(e))
        print(f"[ERROR] Startup failed: {str(e)}")
        gemini_service = None


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Gemini Interview Q&A API v2.0",
        "endpoints": {
            "generate": "/api/generate",
            "process_resume": "/api/process-resume",
            "download_excel": "/api/download-excel",
            "health": "/health",
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
    _app_log.info(
        "[REQUEST] POST /api/generate | experience_length=%d | num_questions=%d",
        len(request.candidate_experience),
        request.num_questions,
    )

    if not gemini_service:
        _app_log.error("[REQUEST] Rejected — Gemini service not available")
        raise HTTPException(
            status_code=503,
            detail="Gemini Service not available. Check API key configuration."
        )
    
    if not request.candidate_experience.strip():
        _app_log.warning("[REQUEST] Rejected — candidate_experience is empty")
        raise HTTPException(
            status_code=400,
            detail="Candidate experience cannot be empty"
        )
    
    if request.num_questions < 1 or request.num_questions > 100:
        _app_log.warning(
            "[REQUEST] Rejected — invalid num_questions=%d", request.num_questions
        )
        raise HTTPException(
            status_code=400,
            detail="Number of questions must be between 1 and 100"
        )
    
    try:
        _app_log.info(
            "[STEP 1] Sending experience text to LLM | text_length=%d chars",
            len(request.candidate_experience),
        )
        result = gemini_service.generate_interview_qa(
            request.candidate_experience,
            request.num_questions
        )
        _app_log.info(
            "[STEP 2] LLM response received | response_length=%d chars",
            len(result) if result else 0,
        )
        qa_items = GeminiService.parse_qa_response(result)
        _app_log.info(
            "[COMPLETE] /api/generate done | questions_parsed=%d", len(qa_items)
        )
        return InterviewResponse(
            status="success",
            data=result
        )
    except Exception as e:
        _app_log.error("[ERROR] /api/generate failed: %s", str(e))
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


@app.post("/api/process-resume")
async def process_resume(file: UploadFile = File(...), num_questions: int = 30):
    """
    Process resume (PDF/DOCX), extract skills, redact PII, and generate interview Q&A.
    
    Args:
        file: Resume file (PDF or DOCX)
        num_questions: Number of interview questions to generate
        
    Returns:
        Processed skills, redacted text, and generated Q&A as structured JSON
    """
    if not gemini_service:
        raise HTTPException(
            status_code=503,
            detail="Gemini Service not available. Check API key configuration."
        )
    
    if num_questions < 1 or num_questions > 100:
        raise HTTPException(
            status_code=400,
            detail="Number of questions must be between 1 and 100"
        )
    
    # Check file type
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ['.pdf', '.docx']:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload PDF or DOCX file."
        )
    
    _app_log.info(
        "[REQUEST] POST /api/process-resume | filename=%s | num_questions=%d",
        file.filename,
        num_questions,
    )
    _audit_log.info("=" * 70)
    _audit_log.info("RESUME PROCESSING AUDIT START")
    _audit_log.info(
        "File: %s | Requested questions: %d", file.filename, num_questions
    )

    try:
        # -- STEP 1: Save uploaded file to temp location ---------------------
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp_file:
            content = await file.read()
            file_size = len(content)
            tmp_file.write(content)
            tmp_path = tmp_file.name

        _app_log.info(
            "[STEP 1] File saved to temp | path=%s | size=%d bytes",
            tmp_path,
            file_size,
        )
        _audit_log.info(
            "[STEP 1 - FILE RECEIVED] filename=%s | size=%d bytes | type=%s",
            file.filename,
            file_size,
            file_extension,
        )

        # -- STEP 2: Parse resume text ----------------------------------------
        extracted_text, file_type = ResumeParser.extract_from_file(tmp_path)

        if not extracted_text.strip():
            _app_log.warning("[STEP 2] No text extracted from resume")
            _audit_log.warning("[STEP 2 - EXTRACT] No text could be extracted")
            raise ValueError("No text could be extracted from resume")

        _app_log.info(
            "[STEP 2] Text extracted from %s | raw_length=%d chars",
            file_type.upper(),
            len(extracted_text),
        )
        _audit_log.info(
            "[STEP 2 - EXTRACT] Raw text extracted from %s | length=%d chars",
            file_type.upper(),
            len(extracted_text),
        )

        # -- STEP 3: Clean extracted text ------------------------------------
        cleaned_text = ResumeParser.clean_text(extracted_text)

        _app_log.info(
            "[STEP 3] Text cleaned | cleaned_length=%d chars",
            len(cleaned_text),
        )
        _audit_log.info(
            "[STEP 3 - CLEAN] Text normalised | length=%d chars",
            len(cleaned_text),
        )

        # -- STEP 4: Scan for PII --------------------------------------------
        pii_summary = PIIRedactor.get_pii_summary(cleaned_text)
        emails_found  = pii_summary.get("emails", [])
        phones_found  = pii_summary.get("phone_numbers", [])
        urls_found    = pii_summary.get("urls", [])
        any_pii_found = bool(emails_found or phones_found or urls_found)

        _app_log.info(
            "[STEP 4] PII scan complete | emails=%d | phones=%d | urls=%d",
            len(emails_found),
            len(phones_found),
            len(urls_found),
        )
        _audit_log.info(
            "[STEP 4 - PII SCAN] Results: emails=%d | phones=%d | urls=%d",
            len(emails_found),
            len(phones_found),
            len(urls_found),
        )
        if emails_found:
            _audit_log.info(
                "[STEP 4 - PII SCAN] Emails detected: %s",
                ", ".join(emails_found),
            )
        if phones_found:
            _audit_log.info(
                "[STEP 4 - PII SCAN] Phone numbers detected: %s",
                ", ".join(phones_found),
            )
        if urls_found:
            _audit_log.info(
                "[STEP 4 - PII SCAN] URLs detected: %s",
                ", ".join(urls_found),
            )
        if not any_pii_found:
            _audit_log.info(
                "[STEP 4 - PII SCAN] No standard PII patterns found in text"
            )

        # -- STEP 5: Redact PII (aggressive: also strips company names) ------
        redacted_text = PIIRedactor.redact_all(cleaned_text, aggressive=True)

        _app_log.info(
            "[STEP 5] PII redaction applied (aggressive=True) | "
            "redacted_length=%d chars | original_length=%d chars",
            len(redacted_text),
            len(cleaned_text),
        )
        _audit_log.info(
            "[STEP 5 - REDACT] Redaction complete (aggressive mode) | "
            "emails→[EMAIL] | phones→[PHONE] | urls→[URL] | company_names→[COMPANY]"
        )
        _audit_log.info(
            "[STEP 5 - REDACT] Text length before=%d | after=%d chars",
            len(cleaned_text),
            len(redacted_text),
        )
        # Show the first 300 chars of the redacted text so the reader can confirm
        preview = redacted_text[:300].replace("\n", " ").strip()
        _audit_log.info(
            "[STEP 5 - REDACT] Redacted text preview (first 300 chars): %s",
            preview,
        )

        # Verify no raw PII slipped through the redaction
        post_pii = PIIRedactor.get_pii_summary(redacted_text)
        remaining_emails = post_pii.get("emails", [])
        remaining_phones = post_pii.get("phone_numbers", [])
        remaining_urls   = post_pii.get("urls", [])
        pii_cleared = not (remaining_emails or remaining_phones or remaining_urls)

        if pii_cleared:
            _audit_log.info(
                "[STEP 5 - REDACT] VERIFIED: No raw email/phone/URL patterns "
                "remain in text after redaction"
            )
        else:
            _audit_log.warning(
                "[STEP 5 - REDACT] WARNING: Some patterns still present after "
                "redaction — emails=%d | phones=%d | urls=%d",
                len(remaining_emails),
                len(remaining_phones),
                len(remaining_urls),
            )

        # -- STEP 6: Send REDACTED text to LLM --------------------------------
        _app_log.info(
            "[STEP 6] Sending REDACTED text to Gemini LLM | "
            "text_length=%d chars | num_questions=%d",
            len(redacted_text),
            num_questions,
        )
        _audit_log.info(
            "[STEP 6 - LLM INPUT] Sending POST-REDACTION text to LLM only | "
            "length=%d chars | num_questions=%d",
            len(redacted_text),
            num_questions,
        )
        if pii_cleared:
            _audit_log.info(
                "[STEP 6 - LLM INPUT] AUDIT PASS: LLM receives redacted text — "
                "emails_cleared=%d | phones_cleared=%d | urls_cleared=%d",
                len(emails_found),
                len(phones_found),
                len(urls_found),
            )
        else:
            _audit_log.warning(
                "[STEP 6 - LLM INPUT] AUDIT WARN: Residual PII may be present "
                "in LLM input — review redaction logic"
            )

        qa_response = gemini_service.generate_interview_qa(redacted_text, num_questions)

        # -- STEP 7: Parse LLM response ---------------------------------------
        qa_items = GeminiService.parse_qa_response(qa_response)

        _app_log.info(
            "[STEP 7] LLM response parsed | qa_items=%d", len(qa_items)
        )

        # Clean up temp file
        os.unlink(tmp_path)
        _app_log.debug("[CLEANUP] Temp file removed: %s", tmp_path)

        _app_log.info(
            "[COMPLETE] /api/process-resume done | filename=%s | questions=%d",
            file.filename,
            len(qa_items),
        )
        _audit_log.info(
            "[COMPLETE] Processing finished | questions_generated=%d",
            len(qa_items),
        )
        _audit_log.info("RESUME PROCESSING AUDIT END")
        _audit_log.info("=" * 70)

        return {
            "status": "success",
            "filename": file.filename,
            "file_type": file_type,
            "extracted_text_length": len(cleaned_text),
            "pii_detected": any_pii_found,
            "pii_summary": pii_summary,
            "redacted_text": redacted_text,
            "qa_items": qa_items,
            "total_questions": len(qa_items)
        }
    
    except ValueError as e:
        _app_log.warning("[ERROR] /api/process-resume validation error: %s", str(e))
        _audit_log.warning("[ERROR] Resume processing aborted: %s", str(e))
        _audit_log.info("RESUME PROCESSING AUDIT END (aborted)")
        _audit_log.info("=" * 70)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _app_log.error("[ERROR] /api/process-resume unexpected error: %s", str(e))
        _audit_log.error("[ERROR] Unexpected error during resume processing: %s", str(e))
        _audit_log.info("RESUME PROCESSING AUDIT END (error)")
        _audit_log.info("=" * 70)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )


@app.post("/api/download-excel")
async def download_excel_qa(qa_items_json: str, candidate_name: str = ""):
    """
    Convert Q&A items to Excel and return as file download.
    
    Args:
        qa_items_json: JSON string containing list of QA items
        candidate_name: Optional candidate name for filename
        
    Returns:
        Excel file as streaming response
    """
    try:
        import json
        
        # Parse JSON string to list of dicts
        qa_items = json.loads(qa_items_json)
        
        # Create workbook
        workbook = ExcelExporter.create_qa_workbook(
            qa_items,
            candidate_info={"Candidate": candidate_name} if candidate_name else None
        )
        
        # Generate filename
        filename = ExcelExporter.generate_filename(candidate_name)
        
        # Save to bytes
        excel_bytes = ExcelExporter.save_to_bytes(workbook)
        
        # Return as streaming response
        return StreamingResponse(
            iter([excel_bytes]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for QA items")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating Excel: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )
