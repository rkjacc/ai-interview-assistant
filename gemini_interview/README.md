# Gemini Interview Q&A Generator

## Overview
A full-stack web application that generates comprehensive interview questions and answers using Google's Gemini 2.5 Flash API. Built with **Streamlit** (frontend) and **FastAPI** (backend).

## Features
✨ **Core Features:**
- Generate customizable interview Q&A pairs
- Text input or file upload for candidate profiles
- Includes coding-focused questions relevant to candidate experience
- Download results as text files
- Real-time API health monitoring
- Beautiful, responsive UI

🏗️ **Architecture:**
- **Frontend:** Streamlit for user-friendly interface
- **Backend:** FastAPI for robust API endpoints
- **Service Layer:** Modular Gemini service for API interactions
- **File Upload:** Support for text files with candidate information

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

## Project Structure
```
gemini_interview/
├── backend/
│   ├── __init__.py              # Package init
│   ├── main.py                  # FastAPI application
│   ├── models.py                # Pydantic models
│   ├── gemini_service.py        # Gemini API service layer
│   └── requirements.txt          # Backend dependencies
├── frontend/
│   └── streamlit_app.py         # Streamlit UI application
├── gemini001.py                 # Original script (legacy)
├── requirements.txt             # All dependencies
├── secret_api_key.txt           # API key (add your key here)
├── run.bat                      # Windows startup script
├── run.sh                       # Linux/Mac startup script
├── README.md                    # This file
└── .gitignore                   # Git ignore rules
```

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

## Usage Examples

### Example 1: Text Input
1. Open Streamlit UI
2. Go to "📝 Text Input" tab
3. Enter candidate experience: `Python, Pandas, NumPy, SQL, Statistics, Machine Learning`
4. Set number of questions: 30
5. Click "🚀 Generate Q&A"
6. Download results

### Example 2: File Upload
1. Create a file `candidate_profile.txt`:
```
Python
PySpark
Pandas
NumPy
Data Analysis
MySQL
SQL
Matplotlib
Data Profiling
ETL
Apache Spark
Statistics
Machine Learning
```
2. Go to "📄 File Upload" tab
3. Upload the file
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
