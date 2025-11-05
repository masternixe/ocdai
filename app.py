"""
Streamlit Web Application - Main UI
"""
import streamlit as st
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import json
from datetime import datetime
import pandas as pd

from processor import DocumentProcessor
from face_detector import FaceDetector
from liveness_checker import LivenessChecker
from face_matcher import FaceMatcher
from models import init_db, get_db_session, DocumentRecord, LivenessRecord, FaceMatchRecord
from config import Config
import utils

# Page config
st.set_page_config(
    page_title="Document Processing & Liveness Detection",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Session state initialization
if 'processing_mode' not in st.session_state:
    st.session_state.processing_mode = Config.PROCESSING_MODE

if 'current_document' not in st.session_state:
    st.session_state.current_document = None

if 'document_face' not in st.session_state:
    st.session_state.document_face = None

if 'live_face' not in st.session_state:
    st.session_state.live_face = None

if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None


# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Mode selection
    st.subheader("Processing Mode")
    mode = st.radio(
        "Select mode:",
        options=["native", "api"],
        format_func=lambda x: "Native (Open Source)" if x == "native" else "API (Cloud Services)",
        index=0 if st.session_state.processing_mode == "native" else 1
    )
    st.session_state.processing_mode = mode
    
    st.divider()
    
    # Configuration
    st.subheader("Configuration")
    
    face_threshold = st.slider(
        "Face Match Threshold",
        min_value=0.0,
        max_value=1.0,
        value=Config.FACE_MATCH_THRESHOLD,
        step=0.05,
        help="Lower = more strict matching"
    )
    
    ocr_confidence = st.slider(
        "OCR Confidence Threshold",
        min_value=0,
        max_value=100,
        value=int(Config.OCR_CONFIDENCE_THRESHOLD),
        step=5,
        help="Minimum confidence for OCR results"
    )
    
    st.divider()
    
    # System info
    st.subheader("System Info")
    st.text(f"Version: {Config.VERSION}")
    st.text(f"Mode: {mode}")
    st.text(f"Database: SQLite")


# Main content
st.title("📄 Passport & NID Document Processing System")
st.markdown("**Extract, Verify, and Match** - Complete document processing with liveness detection")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📤 Upload Document", 
    "🤳 Live Capture", 
    "🔍 Face Matching", 
    "📊 History",
    "📖 Documentation"
])

# Tab 1: Document Upload
with tab1:
    st.header("Upload Document")
    st.markdown("Upload a passport or National ID document for processing")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a document file",
            type=Config.SUPPORTED_FORMATS,
            help="Supported formats: PDF, JPG, PNG, BMP, TIFF"
        )
        
        if uploaded_file:
            # Display uploaded file
            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, caption="Uploaded Document", use_container_width=True)
            else:
                st.success(f"✅ Uploaded: {uploaded_file.name}")
            
            if st.button("🔄 Process Document", type="primary", use_container_width=True):
                with st.spinner("Processing document..."):
                    # Save file
                    file_path = utils.save_uploaded_file(uploaded_file, Config.UPLOAD_DIR)
                    
                    # Process
                    processor = DocumentProcessor(mode=st.session_state.processing_mode)
                    result = processor.process_document(file_path)
                    
                    if result["success"]:
                        # Save to session state
                        st.session_state.current_document = result
                        st.session_state.extracted_data = result["extracted_data"]
                        st.session_state.document_face = result["face_image_path"]
                        
                        # Save to database
                        db = get_db_session()
                        doc_record = DocumentRecord(
                            document_type=result["document_type"],
                            file_name=uploaded_file.name,
                            file_path=str(file_path),
                            processing_mode=st.session_state.processing_mode,
                            extracted_data=result["extracted_data"],
                            face_image_path=result["face_image_path"],
                            confidence_score=result["confidence_score"],
                            processed_at=datetime.utcnow(),
                            status="completed"
                        )
                        db.add(doc_record)
                        db.commit()
                        st.session_state.document_id = doc_record.id
                        db.close()
                        
                        st.success("✅ Document processed successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    with col2:
        if st.session_state.current_document:
            st.subheader("Extracted Information")
            
            result = st.session_state.current_document
            
            # Document type
            doc_type = result["document_type"].upper().replace("_", " ")
            st.metric("Document Type", doc_type)
            
            # Confidence score
            confidence = result["confidence_score"]
            st.metric("Confidence Score", f"{confidence:.1f}%")
            
            st.divider()
            
            # Extracted data
            st.subheader("Document Fields")
            extracted = result["extracted_data"]
            
            # Show structured fields first
            has_structured_data = False
            for key, value in extracted.items():
                if value and key not in ["raw_text", "document_type"]:
                    label = key.replace("_", " ").title()
                    st.text(f"{label}: {value}")
                    has_structured_data = True
            
            # If no structured data or document type is unknown, show raw text
            if not has_structured_data or result["document_type"] == "unknown":
                if "raw_text" in extracted and extracted["raw_text"]:
                    st.divider()
                    st.subheader("Extracted Text (Raw OCR)")
                    st.text_area("Full Text", extracted["raw_text"], height=200)
            
            # Download button
            json_data = json.dumps(extracted, indent=2)
            st.download_button(
                "💾 Download JSON",
                data=json_data,
                file_name=f"extracted_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
            # Extracted face
            if result["face_image_path"]:
                st.divider()
                st.subheader("Extracted Face")
                face_img = cv2.imread(result["face_image_path"])
                face_img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
                st.image(face_img_rgb, caption="Face from Document", width=200)


# Tab 2: Live Capture
with tab2:
    st.header("Live Face Capture with Liveness Detection")
    st.markdown("Capture a live selfie for verification")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Capture Live Photo")
        
        # Camera input
        camera_photo = st.camera_input("Take a selfie")
        
        if camera_photo:
            if st.button("✅ Verify Liveness", type="primary", use_container_width=True):
                with st.spinner("Checking liveness..."):
                    # Load image
                    image = Image.open(camera_photo)
                    image_cv = utils.pil_to_cv2(image)
                    
                    # Check liveness
                    liveness_checker = LivenessChecker()
                    liveness_result = liveness_checker.check_liveness(image_cv)
                    
                    # Extract face
                    face_detector = FaceDetector()
                    face_result = face_detector.extract_largest_face(image_cv)
                    
                    if face_result:
                        face_image, _ = face_result
                        
                        # Save face
                        face_path = face_detector.save_face(
                            face_image,
                            Config.LIVE_CAPTURES_DIR,
                            prefix="live"
                        )
                        
                        st.session_state.live_face = str(face_path)
                        
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
                        st.session_state.liveness_id = liveness_record.id
                        db.close()
                        
                        st.session_state.liveness_result = liveness_result
                        st.rerun()
                    else:
                        st.error("❌ No face detected in image")
    
    with col2:
        if 'liveness_result' in st.session_state:
            st.subheader("Liveness Check Results")
            
            result = st.session_state.liveness_result
            
            # Liveness status
            if result["passed"]:
                st.success("✅ LIVENESS CHECK PASSED")
            else:
                st.error("❌ LIVENESS CHECK FAILED")
            
            # Score
            score = result["liveness_score"]
            st.metric("Liveness Score", f"{score:.1f}%")
            
            st.divider()
            
            # Quality checks
            st.subheader("Quality Checks")
            quality = result["quality_checks"]
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Brightness", f"{quality['brightness']:.1f}")
                st.metric("Blur Score", f"{quality['blur_score']:.1f}")
            with col_b:
                st.metric("Contrast", f"{quality['contrast']:.1f}")
            
            # Show captured face
            if st.session_state.live_face:
                st.divider()
                st.subheader("Captured Face")
                live_img = cv2.imread(st.session_state.live_face)
                live_img_rgb = cv2.cvtColor(live_img, cv2.COLOR_BGR2RGB)
                st.image(live_img_rgb, caption="Live Capture", width=200)


# Tab 3: Face Matching
with tab3:
    st.header("Face Matching")
    st.markdown("Compare document face with live captured face")
    
    if st.session_state.document_face and st.session_state.live_face:
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.subheader("Document Face")
            doc_img = cv2.imread(st.session_state.document_face)
            doc_img_rgb = cv2.cvtColor(doc_img, cv2.COLOR_BGR2RGB)
            st.image(doc_img_rgb, use_container_width=True)
        
        with col2:
            st.subheader("Live Face")
            live_img = cv2.imread(st.session_state.live_face)
            live_img_rgb = cv2.cvtColor(live_img, cv2.COLOR_BGR2RGB)
            st.image(live_img_rgb, use_container_width=True)
        
        with col3:
            st.subheader("Match Result")
            
            if st.button("🔍 Compare Faces", type="primary", use_container_width=True):
                with st.spinner("Matching faces..."):
                    try:
                        print("DEBUG FACE MATCH: Button clicked!")
                        print(f"DEBUG FACE MATCH: Doc face path: {st.session_state.document_face}")
                        print(f"DEBUG FACE MATCH: Live face path: {st.session_state.live_face}")
                        
                        # Load images
                        doc_face = cv2.imread(st.session_state.document_face)
                        live_face = cv2.imread(st.session_state.live_face)
                        
                        print(f"DEBUG FACE MATCH: Doc face loaded: {doc_face is not None}")
                        print(f"DEBUG FACE MATCH: Live face loaded: {live_face is not None}")
                        
                        if doc_face is None or live_face is None:
                            st.error("❌ Error: Could not load face images")
                            st.stop()
                        
                        # Match faces
                        face_matcher = FaceMatcher(threshold=face_threshold)
                        print("DEBUG FACE MATCH: Starting face comparison...")
                        match_result = face_matcher.match_faces(doc_face, live_face)
                        print(f"DEBUG FACE MATCH: Match result: {match_result}")
                        
                        if match_result["success"]:
                            # Save to database
                            try:
                                db = get_db_session()
                                match_record = FaceMatchRecord(
                                    document_id=st.session_state.get('document_id'),
                                    liveness_id=st.session_state.get('liveness_id'),
                                    match_score=match_result["similarity_score"],
                                    match_distance=match_result.get("distance", 0),
                                    match_result="pass" if match_result["match"] else "fail"
                                )
                                db.add(match_record)
                                db.commit()
                                db.close()
                                print("DEBUG FACE MATCH: Saved to database")
                            except Exception as db_error:
                                print(f"DEBUG FACE MATCH: Database error (non-critical): {db_error}")
                            
                            st.session_state.match_result = match_result
                            print("DEBUG FACE MATCH: Saved to session state, rerunning...")
                            st.rerun()
                        else:
                            st.error(f"❌ Face matching failed: {match_result.get('error', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"❌ Error during face matching: {str(e)}")
                        print(f"DEBUG FACE MATCH: Exception: {e}")
                        import traceback
                        traceback.print_exc()
        
        # Show results
        if 'match_result' in st.session_state:
            st.divider()
            result = st.session_state.match_result
            
            if result["match"]:
                st.success("✅ FACES MATCH")
            else:
                st.error("❌ FACES DO NOT MATCH")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Match Score", f"{result['similarity_score']*100:.1f}%")
            with col_b:
                st.metric("Confidence", f"{result['confidence']:.1f}%")
            with col_c:
                st.metric("Threshold", f"{face_threshold*100:.0f}%")
            
            # Comparison image
            doc_face = cv2.imread(st.session_state.document_face)
            live_face = cv2.imread(st.session_state.live_face)
            matcher = FaceMatcher(threshold=face_threshold)
            comparison = matcher.create_comparison_image(doc_face, live_face, result)
            comparison_rgb = cv2.cvtColor(comparison, cv2.COLOR_BGR2RGB)
            st.image(comparison_rgb, caption="Side-by-Side Comparison", use_container_width=True)
    
    else:
        st.info("ℹ️ Please complete document upload and live capture first")


# Tab 4: History
with tab4:
    st.header("Processing History")
    
    db = get_db_session()
    
    # Get recent records
    records = db.query(DocumentRecord).order_by(DocumentRecord.created_at.desc()).limit(50).all()
    
    if records:
        # Create dataframe
        data = []
        for record in records:
            data.append({
                "ID": record.id,
                "Type": record.document_type,
                "File": record.file_name,
                "Confidence": f"{record.confidence_score:.1f}%",
                "Date": record.created_at.strftime("%Y-%m-%d %H:%M"),
                "Status": record.status
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # View details
        selected_id = st.number_input("Enter ID to view details:", min_value=1, step=1)
        
        if st.button("View Details"):
            record = db.query(DocumentRecord).filter(DocumentRecord.id == selected_id).first()
            if record:
                st.subheader(f"Record #{record.id}")
                st.json(record.extracted_data)
            else:
                st.warning("Record not found")
    else:
        st.info("No records found")
    
    db.close()


# Tab 5: Documentation
with tab5:
    st.header("Documentation")
    
    st.markdown("""
    ## 📖 User Guide
    
    ### Getting Started
    
    1. **Choose Processing Mode**
       - Native Mode: Uses open-source libraries
       - API Mode: Uses cloud services for better accuracy
    
    2. **Upload Document**
       - Go to "Upload Document" tab
       - Upload passport or National ID (PDF, JPG, PNG)
       - Click "Process Document"
       - View extracted information
    
    3. **Capture Live Photo**
       - Go to "Live Capture" tab
       - Take a selfie using your webcam
       - System checks for liveness
       - View quality metrics
    
    4. **Match Faces**
       - Go to "Face Matching" tab
       - Click "Compare Faces"
       - View match results and confidence scores
    
    ### Supported Documents
    
    - **Passports**: South Asia, Middle East, Europe, Africa, China, Russia
    - **UAE National ID (EID)**
    - **Other National IDs**
    
    ### File Formats
    
    - PDF
    - JPG/JPEG
    - PNG
    - BMP
    - TIFF
    
    ### Configuration
    
    Adjust settings in the sidebar:
    - Face Match Threshold: Controls matching strictness
    - OCR Confidence: Minimum confidence for text extraction
    
    ### API Access
    
    REST API available at: `http://localhost:8000/api/`
    
    Endpoints:
    - `POST /api/extract-document` - Extract document data
    - `POST /api/capture-liveness` - Verify liveness
    - `POST /api/match-faces` - Match faces
    - `GET /api/health` - Health check
    
    Requires API key in header: `X-API-Key`
    
    ### Troubleshooting
    
    **Low OCR accuracy:**
    - Ensure good lighting
    - Use high-resolution images
    - Try API mode for better results
    
    **Liveness check fails:**
    - Ensure good lighting
    - Look directly at camera
    - Remove glasses if possible
    
    **Face matching fails:**
    - Ensure clear face photos
    - Check lighting conditions
    - Adjust match threshold in settings
    """)


# Footer
st.divider()
st.markdown(
    f"<center>Document Processing System v{Config.VERSION} | "
    f"Mode: {st.session_state.processing_mode.upper()}</center>",
    unsafe_allow_html=True
)

