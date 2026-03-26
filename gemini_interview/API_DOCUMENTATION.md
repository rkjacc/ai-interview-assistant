# API Documentation

## Base URL
```
http://localhost:8001
```

## Interactive API Docs
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Endpoints

### 1. Welcome
```
GET /
```

**Response:**
```json
{
  "message": "Gemini Interview Q&A Generator API",
  "version": "1.0",
  "endpoints": [
    "/api/generate",
    "/api/upload",
    "/api/generate-from-upload"
  ]
}
```

### 2. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "api": "ready",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 3. Generate Q&A from Text

```
POST /api/generate
Content-Type: application/json
```

**Request Body:**
```json
{
  "experience": "Python, FastAPI, PostgreSQL, Docker, Kubernetes",
  "num_questions": 5
}
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| experience | string | Yes | Candidate experience and tech stack |
| num_questions | integer | No | Number of questions (default: 5) |

**Response (200 OK):**
```json
{
  "experience": "Python, FastAPI, PostgreSQL, Docker, Kubernetes",
  "num_questions": 5,
  "questions_and_answers": "Topic: Docker\nQuestion: What are Docker containers...\nAnswer: Docker containers are...",
  "model": "gemini-2.5-flash-preview-09-2025",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Experience and num_questions are required"
}
```

**Response (500 Internal Server Error):**
```json
{
  "detail": "Failed to generate Q&A"
}
```

---

## 4. Upload File

```
POST /api/upload
Content-Type: multipart/form-data
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | file | Yes | CV or document file (.txt, .pdf, .docx) |

**Response (200 OK):**
```json
{
  "filename": "resume.txt",
  "size_bytes": 2048,
  "extracted_text": "John Doe...",
  "message": "File processed successfully"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "No file provided"
}
```

**Response (413 Payload Too Large):**
```json
{
  "detail": "File too large"
}
```

---

## 5. Generate Q&A from Uploaded File

```
POST /api/generate-from-upload
Content-Type: multipart/form-data
```

**Parameters:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| file | file | Yes | CV or document file |
| num_questions | integer | No | Number of questions (default: 5) |

**Response (200 OK):**
```json
{
  "filename": "resume.txt",
  "num_questions": 5,
  "questions_and_answers": "Based on the CV content...",
  "model": "gemini-2.5-flash-preview-09-2025",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Example Requests

### Using curl

**Generate from text:**
```bash
curl -X POST http://localhost:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "experience": "Python, FastAPI, MongoDB",
    "num_questions": 3
  }'
```

**Upload file:**
```bash
curl -X POST http://localhost:8001/api/upload \
  -F "file=@resume.txt"
```

**Generate from file:**
```bash
curl -X POST http://localhost:8001/api/generate-from-upload \
  -F "file=@resume.txt" \
  -F "num_questions=5"
```

**Health check:**
```bash
curl http://localhost:8001/health
```

### Using Python

```python
import requests

# Generate Q&A
response = requests.post(
    "http://localhost:8001/api/generate",
    json={
        "experience": "Python, FastAPI, PostgreSQL",
        "num_questions": 5
    }
)
print(response.json())

# Upload and process
with open("resume.txt", "rb") as f:
    response = requests.post(
        "http://localhost:8001/api/generate-from-upload",
        files={"file": f},
        data={"num_questions": 5}
    )
print(response.json())
```

### Using JavaScript

```javascript
// Generate Q&A
fetch('http://localhost:8001/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    experience: 'Python, FastAPI, PostgreSQL',
    num_questions: 5
  })
})
.then(r => r.json())
.then(data => console.log(data));

// Upload file
const formData = new FormData();
formData.append('file', document.getElementById('fileInput').files[0]);
formData.append('num_questions', 5);

fetch('http://localhost:8001/api/generate-from-upload', {
  method: 'POST',
  body: formData
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## Error Codes

| Code | Message | Meaning |
|------|---------|---------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters |
| 413 | Payload Too Large | File exceeds size limit |
| 500 | Internal Server Error | Backend processing error |
| 503 | Service Unavailable | Gemini API not available |

---

## Response Format

All responses follow this structure:

**Success (2xx):**
```json
{
  "data_field1": "value1",
  "data_field2": "value2",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Error (4xx, 5xx):**
```json
{
  "detail": "Error message explaining what went wrong"
}
```

---

## Rate Limiting

- No rate limiting on development instance
- Production should implement rate limiting

---

## Demo Mode

When no API key is configured:
- Endpoints return empty or demo responses
- Error details indicate demo mode
- Enable by providing API key in `secret_api_key.txt`

---

## Models

### InterviewRequest
```json
{
  "experience": "string (required)",
  "num_questions": "integer (optional, default: 5)"
}
```

### InterviewResponse
```json
{
  "experience": "string",
  "num_questions": "integer",
  "questions_and_answers": "string",
  "model": "string",
  "timestamp": "string"
}
```

### FileUploadRequest
```json
{
  "file": "file object",
  "num_questions": "integer (optional)"
}
```

---

## CORS Configuration

CORS is enabled for:
- Origin: `http://localhost:*`
- Methods: GET, POST, OPTIONS
- Headers: Content-Type

---

## Performance Tips

1. **Batch requests**: Process multiple candidates in sequence
2. **File size**: Keep files under 5MB for optimal performance
3. **Timeout**: Set client timeout to at least 30 seconds
4. **Questions**: 5-10 questions recommended for balanced response

---

## Support

- Check `/health` endpoint for backend status
- Review API docs at `/docs`
- Check browser console for frontend errors
- Look at server logs for backend errors

---

**API Version**: 1.0  
**Last Updated**: 2024  
**Status**: ✅ Ready for use
