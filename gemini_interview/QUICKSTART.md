# 🚀 Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
# Navigate to project
cd de_genai\gemini_interview

# Install all packages
pip install -r requirements.txt
```

### Step 2: Configure API Key
Edit `secret_api_key.txt`:
```
api_key = "paste_your_gemini_api_key_here"
```

Get your free API key: https://aistudio.google.com/

### Step 3: Run the App

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
bash run.sh
```

That's it! 🎉 The app will automatically:
- Start FastAPI backend on `http://localhost:8000`
- Open Streamlit UI on `http://localhost:8501`

---

## Manual Start (if scripts don't work)

**Terminal 1:**
```bash
cd gemini_interview
python backend/main.py
```

**Terminal 2:**
```bash
cd gemini_interview
streamlit run frontend/streamlit_app.py
```

---

## How to Use

1. **Text Input Method:**
   - Go to "📝 Text Input" tab
   - Type candidate skills: `Python, Pandas, SQL, Data Analysis`
   - Click "🚀 Generate Q&A"
   - Download the results

2. **File Upload Method:**
   - Go to "📄 File Upload" tab
   - Upload a `.txt` file with skills/experience
   - Click "🚀 Generate Q&A"
   - Download the results

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Backend Not Running" | Run `python backend/main.py` in another terminal |
| "Import google.genai not found" | Run `pip install -r requirements.txt` |
| "API Key not found" | Check `secret_api_key.txt` format |
| Port 8000/8501 in use | Close other apps or change ports |

---

## Project Structure
```
gemini_interview/
├── backend/           # FastAPI server
│   ├── main.py       # Main API endpoints
│   ├── gemini_service.py  # Gemini integration
│   └── models.py     # Data models
├── frontend/         # Streamlit UI
│   └── streamlit_app.py
├── requirements.txt  # All dependencies
└── README.md        # Full documentation
```

---

## Next Steps

✨ Try these:
- Generate 50 questions instead of 30
- Upload a multi-line candidate profile
- Save results and compare formats
- Extend with custom prompts

🤖 See README.md for full documentation!
