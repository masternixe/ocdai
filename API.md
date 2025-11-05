# API Documentation

REST API for Document Processing & Liveness Detection System

## Base URL

```
http://localhost:8000
```

## Authentication

All API endpoints (except `/api/health`) require authentication via API key.

### Header
```
X-API-Key: your_api_key_here
```

### Example
```bash
curl -H "X-API-Key: your_api_key" http://localhost:8000/api/health
```

## Endpoints

### 1. Health Check

Check API status and configuration.

**Endpoint**: `GET /api/health`

**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "mode": "native",
  "timestamp": "2024-01-01T12:00:00"
}
```

**Example**:
```bash
curl http://localhost:8000/api/health
```

---

### 2. Extract Document

Extract data and face from passport or National ID.

**Endpoint**: `POST /api/extract-document`

**Authentication**: Required

**Content-Type**: `multipart/form-data`

**Parameters**:
- `file` (required): Document file (PDF, JPG, PNG, etc.)

**Response**:
```json
{
  "success": true,
  "document_id": 1,
  "document_type": "passport",
  "extracted_data": {
    "document_type": "passport",
    "full_name": "JOHN DOE",
    "passport_number": "AB1234567",
    "nationality": "USA",
    "date_of_birth": "1990-01-01",
    "gender": "M",
    "issue_date": "2020-01-01",
    "expiry_date": "2030-01-01",
    "place_of_birth": "NEW YORK"
  },
  "face_image_base64": "base64_encoded_image_data...",
  "confidence_score": 87.5,
  "processing_time": 2.34
}
```

**Error Response**:
```json
{
  "detail": "Unsupported file format"
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad request (invalid file, format not supported)
- `401`: Unauthorized (invalid API key)
- `500`: Internal server error

**Examples**:

**cURL**:
```bash
curl -X POST http://localhost:8000/api/extract-document \
  -H "X-API-Key: your_api_key" \
  -F "file=@passport.jpg"
```

**Python**:
```python
import requests

url = "http://localhost:8000/api/extract-document"
headers = {"X-API-Key": "your_api_key"}
files = {"file": open("passport.jpg", "rb")}

response = requests.post(url, headers=headers, files=files)
data = response.json()
print(data)
```

**JavaScript**:
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/api/extract-document', {
  method: 'POST',
  headers: {
    'X-API-Key': 'your_api_key'
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

---

### 3. Capture Liveness

Verify liveness of captured face image.

**Endpoint**: `POST /api/capture-liveness`

**Authentication**: Required

**Content-Type**: `application/json`

**Body**:
```json
{
  "image_base64": "base64_encoded_image_string"
}
```

**Response**:
```json
{
  "success": true,
  "liveness_id": 1,
  "liveness_score": 75.2,
  "liveness_passed": true,
  "quality_checks": {
    "brightness": 128.5,
    "blur_score": 456.7,
    "contrast": 67.8,
    "is_bright_enough": true,
    "is_sharp_enough": true,
    "has_good_contrast": true
  },
  "live_image_base64": "base64_encoded_face_image...",
  "processing_time": 0.5
}
```

**Error Response**:
```json
{
  "detail": "No face detected in image"
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad request (no face detected)
- `401`: Unauthorized
- `500`: Internal server error

**Examples**:

**cURL**:
```bash
# First, convert image to base64
BASE64_IMAGE=$(base64 -w 0 selfie.jpg)

curl -X POST http://localhost:8000/api/capture-liveness \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\": \"$BASE64_IMAGE\"}"
```

**Python**:
```python
import requests
import base64

url = "http://localhost:8000/api/capture-liveness"
headers = {
    "X-API-Key": "your_api_key",
    "Content-Type": "application/json"
}

with open("selfie.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

data = {"image_base64": image_base64}
response = requests.post(url, headers=headers, json=data)
print(response.json())
```

---

### 4. Match Faces

Compare document face with live captured face.

**Endpoint**: `POST /api/match-faces`

**Authentication**: Required

**Content-Type**: `application/json`

**Body**:
```json
{
  "document_id": 1,
  "liveness_id": 1
}
```

**Response**:
```json
{
  "success": true,
  "match_id": 1,
  "match_score": 0.92,
  "match_distance": 0.35,
  "match_passed": true,
  "threshold_used": 0.6,
  "processing_time": 0.5
}
```

**Error Response**:
```json
{
  "detail": "Document or face image not found"
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad request (face matching failed)
- `404`: Document or liveness record not found
- `401`: Unauthorized
- `500`: Internal server error

**Examples**:

**cURL**:
```bash
curl -X POST http://localhost:8000/api/match-faces \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"document_id": 1, "liveness_id": 1}'
```

**Python**:
```python
import requests

url = "http://localhost:8000/api/match-faces"
headers = {
    "X-API-Key": "your_api_key",
    "Content-Type": "application/json"
}
data = {
    "document_id": 1,
    "liveness_id": 1
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

---

### 5. Get Record

Retrieve document processing record by ID.

**Endpoint**: `GET /api/records/{document_id}`

**Authentication**: Required

**Parameters**:
- `document_id` (path): Document record ID

**Response**:
```json
{
  "id": 1,
  "document_type": "passport",
  "file_name": "passport.jpg",
  "extracted_data": {
    "full_name": "JOHN DOE",
    "passport_number": "AB1234567",
    ...
  },
  "confidence_score": 87.5,
  "status": "completed",
  "created_at": "2024-01-01T12:00:00",
  "processed_at": "2024-01-01T12:00:05"
}
```

**Example**:
```bash
curl http://localhost:8000/api/records/1 \
  -H "X-API-Key: your_api_key"
```

---

## Complete Workflow Example

### Python Complete Flow

```python
import requests
import base64
from pathlib import Path

API_URL = "http://localhost:8000"
API_KEY = "your_api_key"
HEADERS = {"X-API-Key": API_KEY}

# Step 1: Extract document
print("Step 1: Extracting document...")
with open("passport.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"{API_URL}/api/extract-document",
        headers=HEADERS,
        files=files
    )

doc_result = response.json()
document_id = doc_result["document_id"]
print(f"Document extracted. ID: {document_id}")
print(f"Name: {doc_result['extracted_data']['full_name']}")

# Step 2: Capture liveness
print("\nStep 2: Checking liveness...")
with open("selfie.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

response = requests.post(
    f"{API_URL}/api/capture-liveness",
    headers={**HEADERS, "Content-Type": "application/json"},
    json={"image_base64": image_base64}
)

liveness_result = response.json()
liveness_id = liveness_result["liveness_id"]
print(f"Liveness checked. ID: {liveness_id}")
print(f"Passed: {liveness_result['liveness_passed']}")
print(f"Score: {liveness_result['liveness_score']:.1f}%")

# Step 3: Match faces
print("\nStep 3: Matching faces...")
response = requests.post(
    f"{API_URL}/api/match-faces",
    headers={**HEADERS, "Content-Type": "application/json"},
    json={
        "document_id": document_id,
        "liveness_id": liveness_id
    }
)

match_result = response.json()
print(f"Match result: {'PASS' if match_result['match_passed'] else 'FAIL'}")
print(f"Match score: {match_result['match_score']*100:.1f}%")
```

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid input or parameters |
| 401 | Unauthorized - Invalid or missing API key |
| 404 | Not Found - Resource doesn't exist |
| 413 | Payload Too Large - File size exceeds limit |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server-side error |

---

## Rate Limiting

Default rate limits:
- 100 requests per hour per API key
- Configurable in `.env` file

When rate limit is exceeded:
```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

---

## Interactive API Documentation

FastAPI provides interactive API documentation:

### Swagger UI
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

### OpenAPI JSON
```
http://localhost:8000/openapi.json
```

---

## Data Models

### DocumentData
```json
{
  "document_type": "string",
  "full_name": "string",
  "document_number": "string",
  "nationality": "string",
  "date_of_birth": "string (YYYY-MM-DD)",
  "gender": "string (M/F)",
  "issue_date": "string (YYYY-MM-DD)",
  "expiry_date": "string (YYYY-MM-DD)",
  "place_of_birth": "string"
}
```

### QualityChecks
```json
{
  "brightness": "float",
  "blur_score": "float",
  "contrast": "float",
  "is_bright_enough": "boolean",
  "is_sharp_enough": "boolean",
  "has_good_contrast": "boolean"
}
```

---

## Best Practices

1. **Always check response status code** before parsing JSON
2. **Handle errors gracefully** with try-catch blocks
3. **Store API key securely** - never commit to version control
4. **Use HTTPS in production** to encrypt data in transit
5. **Implement retry logic** for network failures
6. **Respect rate limits** to avoid throttling
7. **Validate file sizes** before upload (max 10MB default)
8. **Check liveness_passed** before trusting results
9. **Store document_id and liveness_id** for audit trail
10. **Log API requests** for debugging and monitoring

---

## Testing with Postman

### Import Collection

Create Postman collection:

1. **Environment Variables**:
   - `base_url`: http://localhost:8000
   - `api_key`: your_api_key

2. **Headers** (set at collection level):
   - `X-API-Key`: {{api_key}}

3. **Requests**:
   - Health Check (GET)
   - Extract Document (POST with file)
   - Capture Liveness (POST with JSON)
   - Match Faces (POST with JSON)
   - Get Record (GET)

---

## Security

### API Key Management

Generate secure API key:
```python
import secrets
api_key = secrets.token_urlsafe(32)
print(api_key)
```

Set in `.env`:
```
API_KEY=generated_key_here
```

### HTTPS Configuration

For production, use HTTPS:

1. Obtain SSL certificate
2. Configure uvicorn with SSL:
   ```bash
   uvicorn api:app \
     --host 0.0.0.0 \
     --port 443 \
     --ssl-keyfile=/path/to/key.pem \
     --ssl-certfile=/path/to/cert.pem
   ```

3. Or use reverse proxy (nginx/Apache)

---

## Support

For API issues:
- Check response error messages
- Verify API key is correct
- Ensure file format is supported
- Check file size limits
- Review API logs

API logs location: `stdout` or configure logging in `api.py`

