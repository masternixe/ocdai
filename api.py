"""
FastAPI REST API Server
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from pathlib import Path
import cv2
import numpy as np
from typing import Optional
import base64

from processor import DocumentProcessor
from face_detector import FaceDetector
from liveness_checker import LivenessChecker
from face_matcher import FaceMatcher
from models import (
    DocumentExtractResponse, LivenessCheckResponse, FaceMatchResponse,
    HealthResponse, init_db, get_db_session, DocumentRecord, LivenessRecord, FaceMatchRecord
)
from config import Config
import utils

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Document Processing & Liveness Detection API",
    description="API for passport/NID extraction, liveness detection, and face matching",
    version=Config.VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
processor = DocumentProcessor(mode=Config.PROCESSING_MODE)
face_detector = FaceDetector()
liveness_checker = LivenessChecker()
face_matcher = FaceMatcher()


# Security - API Key validation
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key from header"""
    if not x_api_key or x_api_key != Config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=Config.VERSION,
        mode=Config.PROCESSING_MODE,
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/api/extract-document")
async def extract_document(
    file: UploadFile = File(...),
    api_key: str = Depends(verify_api_key)
):
    """
    Extract data from passport or NID document
    
    - **file**: Document file (PDF, JPG, PNG, etc.)
    - Returns extracted data and face image
    """
    # Validate file
    if not utils.validate_file_format(file.filename, Config.SUPPORTED_FORMATS):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    # Save uploaded file
    file_path = utils.save_uploaded_file(file, Config.UPLOAD_DIR)
    
    try:
        # Process document
        result = processor.process_document(file_path)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))
        
        # Save to database
        db = get_db_session()
        doc_record = DocumentRecord(
            document_type=result["document_type"],
            file_name=file.filename,
            file_path=str(file_path),
            processing_mode=Config.PROCESSING_MODE,
            extracted_data=result["extracted_data"],
            face_image_path=result["face_image_path"],
            confidence_score=result["confidence_score"],
            processed_at=datetime.utcnow(),
            status="completed"
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)
        
        # Encode face image to base64
        face_base64 = None
        if result["face_image_path"]:
            face_base64 = utils.image_to_base64(Path(result["face_image_path"]))
        
        return {
            "success": True,
            "document_id": doc_record.id,
            "document_type": result["document_type"],
            "extracted_data": result["extracted_data"],
            "face_image_base64": face_base64,
            "confidence_score": result["confidence_score"],
            "processing_time": result["processing_time"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.post("/api/capture-liveness")
async def capture_liveness(
    image_base64: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Capture and verify live face
    
    - **image_base64**: Base64 encoded image
    - Returns liveness check results
    """
    try:
        # Decode image
        image = utils.base64_to_image(image_base64)
        image_cv = utils.pil_to_cv2(image)
        
        # Check liveness
        liveness_result = liveness_checker.check_liveness(image_cv)
        
        # Extract face
        face_result = face_detector.extract_largest_face(image_cv)
        
        if not face_result:
            raise HTTPException(status_code=400, detail="No face detected in image")
        
        face_image, _ = face_result
        
        # Save face image
        face_path = face_detector.save_face(
            face_image,
            Config.LIVE_CAPTURES_DIR,
            prefix="live"
        )
        
        # Save to database
        db = get_db_session()
        liveness_record = LivenessRecord(
            liveness_score=liveness_result["liveness_score"],
            liveness_passed="pass" if liveness_result["passed"] else "fail",
            blink_count=liveness_result.get("blink_count", 0),
            quality_checks=liveness_result["quality_checks"],
            live_image_path=str(face_path)
        )
        db.add(liveness_record)
        db.commit()
        db.refresh(liveness_record)
        
        # Encode face to base64
        live_face_base64 = utils.image_to_base64(face_path)
        
        return {
            "success": True,
            "liveness_id": liveness_record.id,
            "liveness_score": liveness_result["liveness_score"],
            "liveness_passed": liveness_result["passed"],
            "quality_checks": liveness_result["quality_checks"],
            "live_image_base64": live_face_base64,
            "processing_time": 0.5
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.post("/api/match-faces")
async def match_faces(
    document_id: int,
    liveness_id: int,
    api_key: str = Depends(verify_api_key)
):
    """
    Compare document face with live captured face
    
    - **document_id**: ID of processed document
    - **liveness_id**: ID of liveness check
    - Returns match score and decision
    """
    try:
        db = get_db_session()
        
        # Get document record
        doc_record = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
        if not doc_record or not doc_record.face_image_path:
            raise HTTPException(status_code=404, detail="Document or face image not found")
        
        # Get liveness record
        liveness_record = db.query(LivenessRecord).filter(LivenessRecord.id == liveness_id).first()
        if not liveness_record or not liveness_record.live_image_path:
            raise HTTPException(status_code=404, detail="Liveness record or face image not found")
        
        # Load images
        doc_face = cv2.imread(doc_record.face_image_path)
        live_face = cv2.imread(liveness_record.live_image_path)
        
        if doc_face is None or live_face is None:
            raise HTTPException(status_code=400, detail="Could not load face images")
        
        # Match faces
        match_result = face_matcher.match_faces(doc_face, live_face)
        
        if not match_result["success"]:
            raise HTTPException(status_code=400, detail=match_result.get("error", "Face matching failed"))
        
        # Save match result
        match_record = FaceMatchRecord(
            document_id=document_id,
            liveness_id=liveness_id,
            match_score=match_result["similarity_score"],
            match_distance=match_result.get("distance", 0),
            match_result="pass" if match_result["match"] else "fail"
        )
        db.add(match_record)
        db.commit()
        db.refresh(match_record)
        
        return {
            "success": True,
            "match_id": match_record.id,
            "match_score": match_result["similarity_score"],
            "match_distance": match_result.get("distance", 0),
            "match_passed": match_result["match"],
            "threshold_used": Config.FACE_MATCH_THRESHOLD,
            "processing_time": 0.5
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/api/records/{document_id}")
async def get_record(
    document_id: int,
    api_key: str = Depends(verify_api_key)
):
    """Get document processing record"""
    db = get_db_session()
    try:
        record = db.query(DocumentRecord).filter(DocumentRecord.id == document_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        
        return {
            "id": record.id,
            "document_type": record.document_type,
            "file_name": record.file_name,
            "extracted_data": record.extracted_data,
            "confidence_score": record.confidence_score,
            "status": record.status,
            "created_at": record.created_at.isoformat(),
            "processed_at": record.processed_at.isoformat() if record.processed_at else None
        }
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.API_HOST, port=Config.API_PORT)

