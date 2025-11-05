# Passport & NID Document Processing System with Liveness Detection

Complete document information extraction system that processes passports and National IDs, performs liveness detection, and matches faces.

## Features

- **Document Processing**: Extract text and data from passports and National IDs (UAE EID, etc.)
- **Face Extraction**: Automatically detect and extract face photos from documents
- **MRZ Parsing**: Read Machine Readable Zone from passports
- **Liveness Detection**: Anti-spoofing checks using blink detection and passive analysis
- **Face Matching**: Compare document face with live captured face
- **Dual Mode**: Native (open-source) and API (cloud services) modes
- **Web UI**: User-friendly Streamlit interface
- **REST API**: FastAPI backend for integration

## Supported Documents

- Passports (South Asia, Middle East, Europe, Africa, China, Russia)
- UAE National ID (Emirates ID)
- Other regional National IDs

## Supported Formats

PDF, JPG, JPEG, PNG, BMP, TIFF

## Installation

### Prerequisites

- Python 3.8+
- Tesseract OCR
- dlib shape predictor (optional, for advanced liveness)

### Step 1: Clone Repository

```bash
cd ocdai
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Tesseract OCR

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Add to PATH or set TESSERACT_PATH in .env

**Linux:**
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-ara  # Arabic support
```

**Mac:**
```bash
brew install tesseract
brew install tesseract-lang  # Additional languages
```

### Step 4: Download dlib Shape Predictor (Optional)

For enhanced liveness detection:
```bash
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
```

### Step 5: Configure Environment

Copy `env_template.txt` to `.env` and configure:
```bash
cp env_template.txt .env
```

Edit `.env` with your settings.

## Usage

### Run Streamlit Web Application

```bash
streamlit run app.py
```

Access at: http://localhost:8501

### Run FastAPI Server

```bash
python api.py
```

Or:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

Access API docs at: http://localhost:8000/docs

### Run Both (Streamlit + API)

Terminal 1:
```bash
python api.py
```

Terminal 2:
```bash
streamlit run app.py
```

## Project Structure

```
ocdai/
├── app.py                  # Streamlit web application
├── api.py                  # FastAPI REST API server
├── config.py               # Configuration management
├── models.py               # Database models and schemas
├── processor.py            # Main document processing logic
├── ocr_engine.py           # OCR wrapper (native/API)
├── face_detector.py        # Face detection and extraction
├── liveness_checker.py     # Liveness detection
├── face_matcher.py         # Face comparison
├── utils.py                # Helper functions
├── requirements.txt        # Python dependencies
├── env_template.txt        # Environment variables template
├── README.md               # This file
├── uploads/                # Uploaded documents
├── extracted_faces/        # Extracted face images
└── live_captures/          # Live captured selfies
```

## API Endpoints

### Health Check
```
GET /api/health
```

### Extract Document
```
POST /api/extract-document
Content-Type: multipart/form-data
X-API-Key: your_api_key

Body: file (document image/PDF)

Response: {
  "success": true,
  "document_id": 1,
  "document_type": "passport",
  "extracted_data": {...},
  "face_image_base64": "...",
  "confidence_score": 85.5,
  "processing_time": 2.3
}
```

### Capture Liveness
```
POST /api/capture-liveness
Content-Type: application/json
X-API-Key: your_api_key

Body: {
  "image_base64": "..."
}

Response: {
  "success": true,
  "liveness_id": 1,
  "liveness_score": 75.2,
  "liveness_passed": true,
  "quality_checks": {...}
}
```

### Match Faces
```
POST /api/match-faces
Content-Type: application/json
X-API-Key: your_api_key

Body: {
  "document_id": 1,
  "liveness_id": 1
}

Response: {
  "success": true,
  "match_id": 1,
  "match_score": 0.92,
  "match_passed": true,
  "threshold_used": 0.6
}
```

## Configuration

### Processing Modes

**Native Mode** (Default)
- Uses open-source libraries
- No API costs
- Good accuracy
- Works offline

**API Mode**
- Uses cloud services (Azure, AWS, Google)
- Higher accuracy
- Requires API keys
- Internet connection required

### Adjustable Settings

In Streamlit UI sidebar or `.env` file:

- `OCR_CONFIDENCE_THRESHOLD`: Minimum OCR confidence (default: 60)
- `FACE_MATCH_THRESHOLD`: Face matching threshold (default: 0.6)
- `LIVENESS_SENSITIVITY`: Low, medium, or high (default: medium)
- `MIN_FACE_SIZE`: Minimum face size in pixels (default: 100)

## Extracted Fields

### Passport
- Full Name
- Passport Number
- Nationality
- Date of Birth
- Gender
- Issue Date
- Expiry Date
- Place of Birth
- MRZ Lines
- Face Photograph

### UAE Emirates ID
- ID Number
- Full Name (English and Arabic)
- Nationality
- Date of Birth
- Gender
- Issue Date
- Expiry Date
- Face Photograph

## Security

- API key authentication for REST API
- Input file validation
- Secure file storage
- SQL injection prevention
- XSS protection

**Important**: Change default API key and secret key in production!

## Performance

- Document processing: < 10 seconds
- Face matching: < 3 seconds
- Supports concurrent API requests
- Efficient memory management

## Troubleshooting

### Low OCR Accuracy
- Ensure good lighting and high-resolution images
- Install additional Tesseract language packs
- Try API mode for better results
- Adjust OCR_CONFIDENCE_THRESHOLD

### Face Detection Issues
- Ensure face is clearly visible
- Check lighting conditions
- Adjust MIN_FACE_SIZE setting
- Use higher resolution images

### Liveness Check Fails
- Ensure good lighting
- Look directly at camera
- Remove glasses if possible
- Try different LIVENESS_SENSITIVITY

### Dependencies Installation Issues

**dlib installation error:**
```bash
# Install CMake first
pip install cmake
pip install dlib
```

**Tesseract not found:**
- Verify installation: `tesseract --version`
- Set TESSERACT_PATH in .env

## Development

### Adding New Document Types

1. Create extraction logic in `processor.py`
2. Add field patterns in `ocr_engine.py`
3. Update `DocumentData` schema in `models.py`
4. Test with sample documents

### Extending API

1. Add endpoint in `api.py`
2. Create response model in `models.py`
3. Update API documentation
4. Test with Postman/curl

## Testing

Test with sample documents:
```bash
# Place test documents in uploads/
python -c "
from processor import DocumentProcessor
from pathlib import Path
proc = DocumentProcessor()
result = proc.process_document(Path('uploads/test.pdf'))
print(result)
"
```

## API Documentation

Full API documentation (OpenAPI/Swagger):
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

All rights reserved.

## Support

For issues and questions, contact your development team.

## Version

1.0.0

## Credits

Built with:
- Streamlit
- FastAPI
- OpenCV
- Tesseract OCR
- face_recognition
- DeepFace
- dlib

