# 🚀 Quick Start Guide - v2.0 Features

## Installation (One Time)

### 1. Install New Dependencies
```bash
pip install -r requirements.txt
```

This adds:
- `pdfplumber` - PDF parsing
- `python-docx` - Word file parsing  
- `openpyxl` - Excel generation
- `regex` - Advanced pattern matching

### 2. Make Sure API Key is Set
Check that you have either:
- `secret_api_key.txt` in `gemini_interview/` folder, OR
- Environment variable `GEMINI_API_KEY` set

```bash
# Windows
set GEMINI_API_KEY=your_key_here

# Linux/Mac
export GEMINI_API_KEY=your_key_here
```

## Running the Application

### Easiest Way (Recommended)

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

This will:
1. Automatically start FastAPI backend on http://localhost:8001
2. Automatically start Streamlit frontend on http://localhost:8501
3. Open Streamlit in your browser

### Manual Way (If Needed)

**Terminal 1 - Backend:**
```bash
cd gemini_interview
python -m uvicorn backend.main:app --port 8001 --reload
```

**Terminal 2 - Frontend:**
```bash
cd gemini_interview
streamlit run frontend/streamlit_app.py
```

## Using the New Features

### 🎯 Method 1: Upload Resume & Generate Questions (NEW!)

**Recommended for most users!**

1. **Open the app** → http://localhost:8501
2. **Click "📄 Resume Upload" tab**
3. **Upload your resume** (PDF or DOCX)
4. **Set desired question count** (slider: 5-100)
5. **Click "🚀 Process & Generate Q&A"**
6. **Review PII Detection Report** - Shows what sensitive info was removed
7. **Download Results**:
   - 📊 **Excel** (formatted, professional table)
   - 📄 **Text** (plain text backup)

**What Happens Automatically:**
```
Resume Upload
    ↓
Text Extraction (PDF/DOCX)
    ↓
PII Detection (Find sensitive data)
    ↓
PII Redaction (Remove it)
    ↓
Skills Extraction (Keep technical content)
    ↓
Gemini Q&A Generation (Only skills sent to AI)
    ↓
Excel/Text Export
```

### 🎯 Method 2: Text Input (Original, Still Available)

1. **Open the app** → http://localhost:8501
2. **Click "📝 Text Input" tab**
3. **Type or paste skills/experience**
   - Example: `Python, Django, PostgreSQL, REST APIs`
4. **Set question count**
5. **Click "🚀 Generate Q&A"**
6. **Download as Excel or Text**

### 🎯 Method 3: API Calls (For Developers)

**Upload resume and get Q&A:**
```bash
curl -X POST "http://localhost:8001/api/process-resume?num_questions=30" \
  -F "file=@resume.pdf"
```

**Convert Q&A to Excel:**
```bash
curl -X POST "http://localhost:8001/api/download-excel" \
  -d "qa_items_json=[{\"Topic\":\"Python\",\"Question\":\"...\",\"Answer\":\"...\"}]" \
  -o results.xlsx
```

## 🔒 Security Features

### What Gets Removed Before Sending to AI?

✅ **Automatically detected and removed:**
- Email addresses
- Phone numbers
- Website URLs
- Company names  
- Personal names
- Mailing addresses
- And more...

✅ **What's NOT removed (needed for questions):**
- Programming languages
- Software/frameworks
- Tools and platforms
- Years of experience
- Technical skills
- Job titles/roles
- Industry experience

### Example
**Original Resume:** "John Smith, john@example.com, worked at Google as Senior Python Developer"

**Sent to AI:** "[NAME], [EMAIL], worked at [COMPANY] as Senior Python Developer"

This way your private information is protected while still getting relevant questions!

## 📊 Excel Export Features

The Excel file is professionally formatted with:

- **Header Row** - Dark blue background, white bold text
- **Structured Columns** - Topic | Question | Answer
- **Color Coding**:
  - Topics in light blue (#D9E1F2)
  - Questions in very light blue (#E7F3FF)
  - Answers in light gray (#F0F0F0)
- **Auto-sizing** - Columns and rows adjust to content
- **Professional Font** - Calibri 11pt
- **Timestamp** - When the file was generated
- **Summary Stats** - Total questions count
- **Proper Borders** - Clean table formatting

Perfect for:
- Interview panel review
- Training materials
- LinkedIn content
- Portfolio building

## 🐛 Troubleshooting

### "No module named 'pdfplumber'"
```bash
pip install -r requirements.txt
```

### "API Key not found"
1. Create `secret_api_key.txt` in `gemini_interview/` folder
2. Add one line: `api_key = "YOUR_KEY_HERE"`
3. Or set environment variable: `export GEMINI_API_KEY=your_key`

### "Cannot upload DOCX file"
- Make sure file is actually `.docx` format (not `.doc`)
- Check file isn't corrupted
- Try opening it in Word first

### "Backend not running"
```bash
# Make sure you're in the right directory
cd gemini_interview

# Check if running on port 8001
python -m uvicorn backend.main:app --port 8001
```

### "Excel download fails"
- Check that Q&A items were generated successfully
- Try smaller number of questions (e.g., 10)
- Check backend logs for errors

## 📝 Example Resume Upload Workflow

1. **You**: Upload `resume.pdf`
   - 5-year Python developer with Django and PostgreSQL experience
   - One sentence says: "Previously worked at TechCorp"
   - Includes work email: john@company.com

2. **App Processes**:
   - ✓ Extracts: "5-year Python Django PostgreSQL developer"
   - ✓ Removes: "TechCorp" company name
   - ✓ Removes: "john@company.com" email
   - ✓ Keeps: Technical skills and experience

3. **Sent to Gemini**:
   - "5-year [COMPANY] Python Django PostgreSQL developer"
   - Only technical skills, no personal info!

4. **You Get**:
   - 30 interview questions about Django, Python, databases, etc.
   - Safe, privacy-protected Q&A
   - Professional Excel spreadsheet

## 🎓 Learning Resources

- **Full Upgrade Guide**: See `UPGRADE_GUIDE.md` for complete technical details
- **API Documentation**: Check FastAPI docs at http://localhost:8001/docs
- **Code Comments**: All new modules have detailed docstrings

## 💡 Pro Tips

1. **Better Questions** = Better Resume Input
   - More detailed resume = more targeted questions
   - Specific technologies = more relevant questions

2. **Use Excel for Teams**
   - Download as Excel
   - Share with interview panel
   - Easy to review and annotate

3. **Multiple Candidates**
   - Process resume 1 → Download Excel
   - Process resume 2 → Download Excel  
   - Compare candidate questions across Excel files

4. **Privacy First**
   - All processing happens locally
   - Only skills sent to Gemini
   - Review the PII report to see what was removed

## 🚀 Next Steps

1. **Try it out!** Upload a resume and see the magic happen
2. **Download Excel** - Check the formatting  
3. **Read UPGRADE_GUIDE.md** - Understand the technical details
4. **Share feedback** - Let us know what you think!

---

**Questions?** Check the UPGRADE_GUIDE.md or review error messages in the terminal.

**Happy interviewing! 🎯**
