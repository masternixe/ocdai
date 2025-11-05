# Installation Guide

Complete step-by-step installation instructions for the Document Processing System.

## System Requirements

### Minimum Requirements
- CPU: 2+ cores
- RAM: 4GB+
- Storage: 2GB free space
- OS: Windows 10+, Ubuntu 18.04+, macOS 10.14+

### Recommended Requirements
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 5GB free space
- GPU: Optional (for faster processing)

## Installation Steps

### 1. Python Installation

Ensure Python 3.8+ is installed:

```bash
python --version
# Should show Python 3.8.x or higher
```

If not installed:
- **Windows**: Download from python.org
- **Linux**: `sudo apt-get install python3.8 python3-pip`
- **Mac**: `brew install python@3.8`

### 2. Clone/Extract Project

```bash
cd /path/to/ocdai
```

### 3. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note**: This may take 5-10 minutes.

### 5. Install Tesseract OCR

#### Windows

1. Download installer: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer (use default location: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH or note installation path
4. Set in `.env`:
   ```
   TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

Verify installation:
```bash
tesseract --version
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-ara  # Arabic support
sudo apt-get install tesseract-ocr-eng  # English (usually included)
```

Verify:
```bash
tesseract --version
```

#### macOS

```bash
brew install tesseract
brew install tesseract-lang  # Additional languages
```

Verify:
```bash
tesseract --version
```

### 6. Install System Dependencies

#### Linux Additional Dependencies

```bash
# OpenCV dependencies
sudo apt-get install libsm6 libxext6 libxrender-dev libgomp1

# dlib dependencies
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
sudo apt-get install libx11-dev libgtk-3-dev

# Poppler for PDF processing
sudo apt-get install poppler-utils
```

#### macOS Additional Dependencies

```bash
brew install cmake
brew install poppler
```

#### Windows Additional Dependencies

For PDF processing, download poppler:
1. Download from: http://blog.alivate.com.au/poppler-windows/
2. Extract to `C:\poppler`
3. Add `C:\poppler\bin` to PATH

### 7. Download Face Landmark Model (Optional)

For advanced liveness detection:

```bash
# Download shape predictor
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

# Extract
bunzip2 shape_predictor_68_face_landmarks.dat.bz2
```

Or download manually from: http://dlib.net/files/

Place in project root directory.

### 8. Configure Environment

Copy template and edit:

```bash
cp env_template.txt .env
```

Edit `.env` file with your settings:

```ini
# Minimal configuration
DEBUG=False
PROCESSING_MODE=native

# If Tesseract not in PATH (Windows)
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe

# Security - CHANGE THESE
API_KEY=your_secure_random_api_key
SECRET_KEY=your_secure_random_secret_key
```

### 9. Initialize Database

```bash
python -c "from models import init_db; init_db()"
```

This creates `documents.db` SQLite database.

### 10. Verify Installation

Test imports:

```bash
python -c "
import streamlit
import fastapi
import cv2
import pytesseract
import face_recognition
print('All imports successful!')
"
```

Test Tesseract:

```bash
tesseract --list-langs
# Should show: eng, ara, etc.
```

## First Run

### Start Streamlit Application

```bash
streamlit run app.py
```

Browser should open automatically to: http://localhost:8501

### Start API Server

```bash
python api.py
```

API available at: http://localhost:8000
API docs at: http://localhost:8000/docs

## Troubleshooting

### Issue: "ModuleNotFoundError"

**Solution**: Install missing package
```bash
pip install <package-name>
```

### Issue: "tesseract is not installed"

**Solution**: Install Tesseract and add to PATH, or set TESSERACT_PATH in .env

**Windows**: Set in .env:
```
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Issue: dlib installation fails

**Solution**: Install CMake first
```bash
pip install cmake
pip install dlib
```

**Alternative**: Use precompiled wheel
```bash
pip install dlib-binary
```

### Issue: "No module named 'cv2'"

**Solution**: Reinstall OpenCV
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python
```

### Issue: PDF processing fails

**Solution**: Install poppler-utils

**Linux**:
```bash
sudo apt-get install poppler-utils
```

**Mac**:
```bash
brew install poppler
```

**Windows**: Download poppler and add to PATH

### Issue: face_recognition installation fails

**Windows users**: face_recognition requires dlib, which needs Visual Studio C++ compiler.

**Solution**:
1. Install Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
2. Or use precompiled wheels from: https://github.com/ageitgey/face_recognition/issues

**Alternative**:
```bash
pip install face-recognition-models
pip install dlib-binary
pip install face-recognition
```

### Issue: Port already in use

**Solution**: Change port in config

For Streamlit:
```bash
streamlit run app.py --server.port 8502
```

For API:
Edit `.env`:
```
API_PORT=8001
```

### Issue: Low OCR accuracy

**Solutions**:
1. Install more language packs:
   ```bash
   # Linux
   sudo apt-get install tesseract-ocr-all
   ```

2. Use higher DPI for PDFs (edit processor.py):
   ```python
   images = convert_from_path(str(pdf_path), dpi=600)  # Changed from 300
   ```

3. Try API mode with cloud services

### Issue: Camera not working in Streamlit

**Solution**: Ensure HTTPS or localhost. Streamlit camera requires secure context.

If accessing remotely, use SSH tunnel:
```bash
ssh -L 8501:localhost:8501 user@remote-server
```

## API Mode Setup (Optional)

For enhanced accuracy using cloud services:

### Azure Setup

1. Create Azure Computer Vision resource
2. Get API key and endpoint
3. Add to `.env`:
   ```
   AZURE_CV_KEY=your_key_here
   AZURE_CV_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   ```

### AWS Setup

1. Create AWS account and get credentials
2. Enable Textract and Rekognition
3. Add to `.env`:
   ```
   AWS_ACCESS_KEY=your_access_key
   AWS_SECRET_KEY=your_secret_key
   AWS_REGION=us-east-1
   ```

### Google Cloud Setup

1. Create Google Cloud project
2. Enable Vision API
3. Download credentials JSON
4. Add to `.env`:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
   ```

## Production Deployment

### Security Checklist

- [ ] Change API_KEY in .env
- [ ] Change SECRET_KEY in .env
- [ ] Set DEBUG=False
- [ ] Use HTTPS/SSL certificates
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Regular backups of database

### Performance Optimization

1. Use production ASGI server:
   ```bash
   pip install gunicorn
   gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. Set up reverse proxy (nginx):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:8501;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
       }
   }
   ```

3. Use process manager (systemd/supervisor)

## Updating

To update the application:

```bash
# Pull latest code
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart services
```

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove project directory
rm -rf /path/to/ocdai

# Remove system packages (optional)
# Linux:
sudo apt-get remove tesseract-ocr
# Mac:
brew uninstall tesseract
```

## Support

For installation issues:
1. Check error messages carefully
2. Verify all prerequisites are installed
3. Check Python and package versions
4. Consult README.md and project documentation

## Next Steps

After successful installation:
1. Read README.md for usage instructions
2. Review API documentation at /docs
3. Test with sample documents
4. Configure settings in Streamlit sidebar
5. Explore API endpoints

