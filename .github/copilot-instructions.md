# 🤖 Copilot & AI Agent Instructions for Gemini Interview Q&A Generator

## Project Overview
- **Architecture:** Modular Python project with FastAPI backend (`backend/`), Streamlit frontend (`frontend/`), and a Gemini API service layer (`gemini_service.py`).
- **Data Flow:**
  - User interacts via Streamlit UI (`streamlit_app.py`)
  - UI sends requests to FastAPI backend (`main.py`)
  - Backend delegates Q&A generation to Gemini service (`gemini_service.py`)
  - API key required for real responses; demo mode available if missing

## Key Workflows
- **Install dependencies:**
  ```bash
  cd gemini_interview
  pip install -r requirements.txt
  ```
- **API Key setup:**
  - Add `api_key = "YOUR_KEY"` to `secret_api_key.txt` in `gemini_interview/` or set `GEMINI_API_KEY` env var
- **Start app:**
  - Windows: `run.bat`
  - Linux/Mac: `bash run.sh`
- **Verify setup:** `verify.bat` or `python test_startup.py`
- **Access points:**
  - Streamlit UI: http://localhost:8501
  - FastAPI docs: http://localhost:8000/docs

## Conventions & Patterns
- **Backend:**
  - All API endpoints in `backend/main.py`
  - Data models in `backend/models.py` (Pydantic)
  - Gemini API logic isolated in `backend/gemini_service.py`
  - Input validation and error handling at endpoint level
- **Frontend:**
  - Single entry: `frontend/streamlit_app.py`
  - Communicates with backend via HTTP
  - Supports text input and `.txt` file upload
- **Configuration:**
  - No secrets in code; use `secret_api_key.txt` or env vars
  - `.env.example` provided for reference
  - `.gitignore` blocks secrets and venv
- **Testing:**
  - Use `test_startup.py` for environment checks
  - Health endpoint: `/health` (backend)

## Integration & Extensibility
- **Gemini API:**
  - All calls routed through `gemini_service.py`
  - Demo mode if no API key
- **Add endpoints:**
  - Define in `backend/main.py`, use models from `models.py`
- **Frontend changes:**
  - Update `streamlit_app.py` for new features

## Troubleshooting
- Port in use: Run `verify.bat` or check with `netstat`
- API key issues: Ensure correct file format or env var
- Dependency errors: Reinstall with `pip install -r requirements.txt`

## References
- See `README.md`, `QUICKSTART.md`, and code comments in `main.py` and `streamlit_app.py` for further details.
