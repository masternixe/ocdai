"""
Database Models and Schemas
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from config import Config

Base = declarative_base()

# SQLAlchemy Models
class DocumentRecord(Base):
    """Database model for processed documents"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(String(50))  # passport, uae_eid, nid
    file_name = Column(String(255))
    file_path = Column(String(500))
    processing_mode = Column(String(20))  # native or api
    
    # Extracted data
    extracted_data = Column(JSON)
    face_image_path = Column(String(500))
    confidence_score = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Status
    status = Column(String(20))  # processing, completed, failed
    error_message = Column(Text, nullable=True)


class LivenessRecord(Base):
    """Database model for liveness checks"""
    __tablename__ = "liveness_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer)
    
    # Liveness data
    live_image_path = Column(String(500))
    liveness_score = Column(Float)
    liveness_passed = Column(String(10))  # pass, fail
    
    # Detection details
    blink_count = Column(Integer, nullable=True)
    head_movement_detected = Column(String(10), nullable=True)
    quality_checks = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class FaceMatchRecord(Base):
    """Database model for face matching results"""
    __tablename__ = "face_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer)
    liveness_id = Column(Integer)
    
    # Match results
    match_score = Column(Float)
    match_distance = Column(Float)
    match_result = Column(String(10))  # pass, fail
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic Schemas for API
class DocumentData(BaseModel):
    """Schema for extracted document data"""
    document_type: str
    full_name: Optional[str] = None
    document_number: Optional[str] = None
    nationality: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    place_of_birth: Optional[str] = None
    mrz_lines: Optional[List[str]] = None
    additional_fields: Optional[Dict[str, Any]] = None


class DocumentExtractResponse(BaseModel):
    """API response for document extraction"""
    success: bool
    document_id: int
    document_type: str
    extracted_data: DocumentData
    face_image_base64: Optional[str] = None
    confidence_score: float
    processing_time: float


class LivenessCheckResponse(BaseModel):
    """API response for liveness check"""
    success: bool
    liveness_id: int
    liveness_score: float
    liveness_passed: bool
    quality_checks: Dict[str, Any]
    live_image_base64: Optional[str] = None
    processing_time: float


class FaceMatchResponse(BaseModel):
    """API response for face matching"""
    success: bool
    match_id: int
    match_score: float
    match_distance: float
    match_passed: bool
    threshold_used: float
    processing_time: float


class HealthResponse(BaseModel):
    """API health check response"""
    status: str
    version: str
    mode: str
    timestamp: str


# Database initialization
def init_db():
    """Initialize database"""
    engine = create_engine(Config.DATABASE_URL, echo=Config.DEBUG)
    Base.metadata.create_all(bind=engine)
    return engine


def get_db_session():
    """Get database session"""
    engine = create_engine(Config.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

