# Gemini Interview Q&A Generator

**Version 2.0** - Professional Resume Processing & Excel Export

## Overview
A full-stack web application that generates comprehensive interview questions and answers using Google's Gemini 2.5 Flash API. **Now with professional resume parsing, PII redaction, and Excel export!**

Built with **Streamlit** (frontend) and **FastAPI** (backend).

## ✨ Features

### Version 2.0 (NEW!)
- 📄 **Resume Upload** - PDF and Word file support
- 🔒 **PII Redaction** - Automatic removal of sensitive data before LLM processing
- 📊 **Excel Export** - Professional formatted spreadsheets with styling
- 🧠 **No PII Exposure** - Skills extracted locally, only technical content sent to AI
- 🔍 **Enhanced Parsing** - Improved Q&A extraction and structuring

### Core Features
- 💡 Generate customizable interview Q&A pairs (5-100 questions)
- 📝 Text input or file upload for candidate profiles
- 📥 Upload PDF/DOCX resumes for automatic processing
- 💾 Download results as Excel (formatted) or Text
- 🏥 Real-time API health monitoring
- 🎨 Beautiful, responsive UI with dark mode support

🏗️ **Architecture:**
- **Frontend:** Streamlit for user-friendly interface
- **Backend:** FastAPI for robust API endpoints  
- **Service Layer:** Modular services for resume parsing, PII redaction, Excel export
- **Security:** No PII sent to LLM - everything extracted locally

## Prerequisites
- Python 3.8+
- Google Gemini API key (get from [Google AI Studio](https://aistudio.google.com/))
- Virtual environment tool (venv or conda)

## Installation

### 1. Set Up Virtual Environment
```bash
cd de_genai
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies
```bash
cd gemini_interview
pip install -r requirements.txt
```

### 3. Configure API Key
Create `secret_api_key.txt` in the `gemini_interview/` directory:
```
api_key = "YOUR_ACTUAL_GEMINI_API_KEY_HERE"
```

Or set environment variable:
```bash
set GEMINI_API_KEY=your_api_key_here  # Windows
export GEMINI_API_KEY=your_api_key_here  # Linux/Mac
```

## Project Structure
```
gemini_interview/
├── backend/
│   ├── __init__.py              # Package init
│   ├── main.py                  # FastAPI application (v2.0+)
│   ├── models.py                # Pydantic models
│   ├── gemini_service.py        # Gemini API service layer
│   ├── resume_parser.py         # NEW: Resume text extraction
│   ├── pii_redactor.py          # NEW: PII detection & removal
│   └── excel_exporter.py        # NEW: Excel file generation
├── frontend/
│   └── streamlit_app.py         # Streamlit UI application (v2.0+)
├── requirements.txt             # All dependencies (updated)
├── secret_api_key.txt           # API key (add your key here)
├── run.bat                      # Windows startup script
├── run.sh                       # Linux/Mac startup script
├── README.md                    # This file
├── UPGRADE_GUIDE.md             # NEW: Detailed v2.0 changes
└── .gitignore                   # Git ignore rules
```

## 🎯 What's New in v2.0?

**See [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md) for comprehensive documentation!**

### New Features:
- 📄 **Resume Upload** - Support for PDF and DOCX files
- 🔒 **PII Redaction** - Automatic removal of sensitive data before LLM processing
- 📊 **Excel Export** - Professional formatted spreadsheets with styling
- 🏗️ **New Backend Modules**:
  - `resume_parser.py` - Extract text from PDF/DOCX files
  - `pii_redactor.py` - Detect and remove PII (emails, phone, URLs, names, companies)
  - `excel_exporter.py` - Generate beautifully formatted Excel workbooks

### New API Endpoints:
- `POST /api/process-resume` - Upload resume and generate Q&A with PII redaction
- `POST /api/download-excel` - Convert Q&A to formatted Excel file

### Security:
- **NO PII sent to LLM** - Skills and experience extracted locally before AI processing
- **Automatic Detection** - Emails, phone numbers, URLs, company names automatically detected
- **Privacy Protected** - Complete PII removal before Gemini API call

## Usage

### Option 1: Automated (Recommended)

**Windows:**
```bash
cd gemini_interview
run.bat
```

**Linux/Mac:**
```bash
cd gemini_interview
bash run.sh
```

### Option 2: Manual

**Terminal 1 - Start FastAPI Backend:**
```bash
cd gemini_interview
python backend/main.py
```
FastAPI will run on `http://localhost:8000`

**Terminal 2 - Start Streamlit Frontend:**
```bash
cd gemini_interview
streamlit run frontend/streamlit_app.py
```
Streamlit will open in your browser (typically `http://localhost:8501`)

## API Endpoints

### Health Check
```
GET /health
```
Check if the backend is running and Gemini service is connected.

### Generate Q&A (Text Input)
```
POST /api/generate
Content-Type: application/json

{
  "candidate_experience": "Python, PySpark, pandas, SQL, data analysis",
  "num_questions": 30
}
```

### Upload File
```
POST /api/upload
Content-Type: multipart/form-data

file: <text_file>
```

### Generate from Upload
```
POST /api/generate-from-upload
Content-Type: multipart/form-data

file: <text_file>
num_questions: 30
```

### Process Resume (NEW in v2.0)
```
POST /api/process-resume
Content-Type: multipart/form-data

file: <pdf_or_docx_file>
num_questions: 30

Response:
{
  "status": "success",
  "filename": "resume.pdf",
  "file_type": "pdf",
  "extracted_text_length": 5234,
  "pii_detected": true,
  "pii_summary": {
    "emails": [...],
    "phone_numbers": [...],
    "urls": [...]
  },
  "qa_items": [
    {
      "Topic": "Python",
      "Question": "What is a decorator?",
      "Answer": "..."
    }
  ],
  "total_questions": 30
}
```

### Download Excel (NEW in v2.0)
```
POST /api/download-excel
Content-Type: application/x-www-form-urlencoded

qa_items_json: [{"Topic": "...", "Question": "...", "Answer": "..."}]
candidate_name: John Doe

Response: Excel file (XLSX) attachment
```

## Usage Examples

### Example 1: Text Input
1. Open Streamlit UI (http://localhost:8501)
2. Go to "📝 Text Input" tab
3. Enter candidate experience: `Python, Pandas, NumPy, SQL, Statistics, Machine Learning`
4. Set number of questions: 30
5. Click "🚀 Generate Q&A"
6. Download as Excel or Text

### Example 2: Resume Upload (NEW in v2.0)
1. Open Streamlit UI (http://localhost:8501)
2. Go to "📄 Resume Upload" tab
3. Upload your resume in PDF or DOCX format
4. Set number of questions: 30
5. Click "🚀 Process & Generate Q&A"
6. Review PII Detection Report
7. Download results as Excel (formatted) or Text

### Example 3: File Upload (Legacy)
1. Create a file `candidate_profile.txt` with skills listed
2. Go to Streamlit UI
3. Upload the text file
4. Click "🚀 Generate Q&A"
5. Download results

## Configuration

### Environment Variables
Create a `.env` file in `gemini_interview/` for alternative API key configuration:
```
GEMINI_API_KEY=your_api_key_here
```

### Streamlit Configuration
Edit `.streamlit/config.toml` to customize UI settings:
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

## Troubleshooting

### Issue: "API Backend Not Running"
**Solution:** Ensure FastAPI is running in another terminal:
```bash
python backend/main.py
```

### Issue: "Import 'google.genai' could not be resolved"
**Solution:** Ensure packages are installed:
```bash
pip install -r requirements.txt
```

### Issue: "API Key not found"
**Solution:** Verify `secret_api_key.txt` exists with format:
```
api_key = "your_key_here"
```

### Issue: Connection refused on port 8000/8501
**Solution:** Ports might be in use. Kill processes:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

## API Response Examples

### Success Response
```json
{
  "status": "success",
  "data": "{\n\"Topic\": \"Python Basics\",\n\"Question\": \"Explain list comprehensions\",\n\"Answer\": \"...\"}"
}
```

### Error Response
```json
{
  "status": "error",
  "error": "API Key not configured"
}
```

## Performance Notes
- Default: 30 questions takes ~30-60 seconds
- Max: 100 questions may take 2-3 minutes
- Adjust `num_questions` slider based on time requirements

## Security Notes
⚠️ **Important:**
- Never commit `secret_api_key.txt` to version control
- Keep API keys private and secure
- Use environment variables in production
- `.gitignore` is configured to prevent accidental commits

## Development

### Add New Endpoints
1. Add models to `backend/models.py`
2. Add endpoint to `backend/main.py`
3. Test with FastAPI docs: `http://localhost:8000/docs`

### Customize Frontend
1. Edit `frontend/streamlit_app.py`
2. Changes auto-reload when file saves
3. Refer to [Streamlit docs](https://docs.streamlit.io/)

### Extend Gemini Service
1. Edit `backend/gemini_service.py`
2. Add new methods to `GeminiService` class
3. Update `main.py` to expose new endpoints

## Requirements
See [requirements.txt](requirements.txt) for all dependencies:
- **FastAPI** 0.104.1
- **Streamlit** 1.28.1
- **Uvicorn** 0.24.0
- **Google-genai** (latest)
- **Requests** 2.31.0
- And more...

## Contributing
Feel free to extend this project with:
- Additional output formats (PDF, JSON)
- Database integration for storing Q&A
- User authentication
- Batch processing
- Custom prompt templates

## License
This project is open source. Use it freely for learning and development.

## Support
For issues with:
- **Gemini API:** Check [Google AI Documentation](https://ai.google.dev/)
- **FastAPI:** See [FastAPI Docs](https://fastapi.tiangolo.com/)
- **Streamlit:** Visit [Streamlit Community](https://discuss.streamlit.io/)
