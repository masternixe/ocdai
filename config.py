"""
Configuration Management for Document Processing System
"""
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Application settings
    APP_NAME = "Passport & NID Document Processing System"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./documents.db")
    
    # File storage
    UPLOAD_DIR = Path("uploads")
    EXTRACTED_FACES_DIR = Path("extracted_faces")
    LIVE_CAPTURES_DIR = Path("live_captures")
    
    # Processing mode
    PROCESSING_MODE = os.getenv("PROCESSING_MODE", "native")  # native or api
    
    # OCR Settings
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", None)
    OCR_CONFIDENCE_THRESHOLD = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "60.0"))
    
    # Face matching settings
    FACE_MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", "0.6"))
    FACE_DISTANCE_THRESHOLD = float(os.getenv("FACE_DISTANCE_THRESHOLD", "0.6"))
    
    # Liveness detection settings
    LIVENESS_SENSITIVITY = os.getenv("LIVENESS_SENSITIVITY", "medium")  # low, medium, high
    BLINK_THRESHOLD = int(os.getenv("BLINK_THRESHOLD", "2"))
    MIN_FACE_SIZE = int(os.getenv("MIN_FACE_SIZE", "100"))
    
    # Document validation
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    SUPPORTED_FORMATS = ["pdf", "jpg", "jpeg", "png", "bmp", "tiff"]
    
    # API Keys (for API mode)
    # Azure
    AZURE_CV_KEY = os.getenv("AZURE_CV_KEY", "")
    AZURE_CV_ENDPOINT = os.getenv("AZURE_CV_ENDPOINT", "")
    AZURE_FORM_KEY = os.getenv("AZURE_FORM_KEY", "")
    AZURE_FORM_ENDPOINT = os.getenv("AZURE_FORM_ENDPOINT", "")
    
    # AWS
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    
    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # API Server settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    API_KEY = os.getenv("API_KEY", "dev_api_key_change_in_production")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret_key_in_production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))  # seconds
    
    # Performance
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    PROCESSING_TIMEOUT = int(os.getenv("PROCESSING_TIMEOUT", "30"))  # seconds
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        cls.UPLOAD_DIR.mkdir(exist_ok=True)
        cls.EXTRACTED_FACES_DIR.mkdir(exist_ok=True)
        cls.LIVE_CAPTURES_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Validate configuration and check required dependencies"""
        errors = []
        
        if cls.PROCESSING_MODE == "api":
            if not cls.AZURE_CV_KEY and not cls.AWS_ACCESS_KEY and not cls.GOOGLE_APPLICATION_CREDENTIALS:
                errors.append("API mode requires at least one API provider configured")
        
        if cls.TESSERACT_PATH and not Path(cls.TESSERACT_PATH).exists():
            errors.append(f"Tesseract path not found: {cls.TESSERACT_PATH}")
        
        return errors


# Create directories on import
Config.ensure_directories()

