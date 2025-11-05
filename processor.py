"""
Document Processor - Main processing logic
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, Optional, List
import pytesseract
from pdf2image import convert_from_path
import passporteye
from datetime import datetime
import re

from ocr_engine import OCREngine
from face_detector import FaceDetector
from config import Config
import utils


class DocumentProcessor:
    """Main document processing class"""
    
    def __init__(self, mode: str = "native"):
        self.mode = mode
        self.ocr_engine = OCREngine(mode)
        self.face_detector = FaceDetector()
    
    def load_document(self, file_path: Path) -> List[np.ndarray]:
        """Load document and convert to images"""
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.pdf':
            return self._load_pdf(file_path)
        else:
            return self._load_image(file_path)
    
    def _load_pdf(self, pdf_path: Path) -> List[np.ndarray]:
        """Load PDF and convert to images"""
        images = convert_from_path(str(pdf_path), dpi=300)
        
        # Convert PIL images to numpy arrays
        np_images = []
        for img in images:
            np_img = np.array(img)
            np_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
            np_images.append(np_img)
        
        return np_images
    
    def _load_image(self, image_path: Path) -> List[np.ndarray]:
        """Load image file"""
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        return [img]
    
    def detect_document_type(self, image: np.ndarray, text: str) -> str:
        """Detect document type from image and text"""
        text_lower = text.lower()
        
        # Check for passport indicators
        if any(word in text_lower for word in ['passport', 'passeport', 'pasaporte']):
            return "passport"
        
        # Check for UAE EID
        if 'emirates id' in text_lower or 'uae' in text_lower or '784-' in text:
            return "uae_eid"
        
        # Check for Canadian documents
        if 'canada' in text_lower or 'ontario' in text_lower or 'photo card' in text_lower or 'carte' in text_lower:
            return "canada_id"
        
        # Check for MRZ pattern (indicates passport)
        if 'P<' in text or '<<' in text:
            return "passport"
        
        # Generic NID
        if any(word in text_lower for word in ['national id', 'identity card', 'id card']):
            return "nid"
        
        return "unknown"
    
    def process_passport(self, image: np.ndarray, ocr_result: Dict) -> Dict:
        """Process passport document"""
        text = ocr_result['full_text']
        
        # Try to use passporteye for MRZ
        mrz_data = self._extract_mrz_passporteye(image)
        
        # Extract fields
        extracted_data = {
            "document_type": "passport",
            "full_name": None,
            "passport_number": None,
            "nationality": None,
            "date_of_birth": None,
            "gender": None,
            "issue_date": None,
            "expiry_date": None,
            "place_of_birth": None,
            "mrz_lines": None
        }
        
        # Get from MRZ if available
        if mrz_data:
            extracted_data.update(mrz_data)
        
        # Supplement with OCR
        if not extracted_data["passport_number"]:
            extracted_data["passport_number"] = self.ocr_engine.extract_document_number(text, "passport")
        
        # Extract dates
        dates = self.ocr_engine.parse_dates(text)
        if dates and not extracted_data["date_of_birth"]:
            extracted_data["date_of_birth"] = utils.parse_date(dates[0]) if len(dates) > 0 else None
        if dates and not extracted_data["expiry_date"]:
            extracted_data["expiry_date"] = utils.parse_date(dates[-1]) if len(dates) > 1 else None
        
        # Extract name (usually at top of passport)
        name_patterns = [
            r'(?:Name|Surname|Given Names)[:\s]+([A-Z\s]+)',
            r'([A-Z]{2,}\s+[A-Z\s]+)(?=\n)'
        ]
        name = self.ocr_engine.find_field_by_pattern(text, name_patterns)
        if name and not extracted_data["full_name"]:
            extracted_data["full_name"] = name
        
        # Nationality
        nationality_patterns = [
            r'Nationality[:\s]+([A-Z\s]+)',
            r'National[:\s]+([A-Z\s]+)'
        ]
        nationality = self.ocr_engine.find_field_by_pattern(text, nationality_patterns)
        if nationality and not extracted_data["nationality"]:
            extracted_data["nationality"] = nationality
        
        return extracted_data
    
    def process_uae_eid(self, image: np.ndarray, ocr_result: Dict) -> Dict:
        """Process UAE Emirates ID"""
        text = ocr_result['full_text']
        
        extracted_data = {
            "document_type": "uae_eid",
            "id_number": None,
            "full_name": None,
            "full_name_arabic": None,
            "nationality": None,
            "date_of_birth": None,
            "gender": None,
            "issue_date": None,
            "expiry_date": None
        }
        
        # Extract ID number (format: 784-YYYY-NNNNNNN-N)
        id_patterns = [
            r'(784[-\s]?\d{4}[-\s]?\d{7}[-\s]?\d)',
            r'ID\s*(?:Number)?[:\s]*(784[-\s]?\d{4}[-\s]?\d{7}[-\s]?\d)'
        ]
        id_number = self.ocr_engine.find_field_by_pattern(text, id_patterns)
        if id_number:
            extracted_data["id_number"] = id_number
        
        # Extract name
        name_patterns = [
            r'Name[:\s]+([A-Z\s]+)',
            r'(?:^|\n)([A-Z]{2,}\s+[A-Z\s]+)(?=\n)'
        ]
        name = self.ocr_engine.find_field_by_pattern(text, name_patterns)
        if name:
            extracted_data["full_name"] = name
        
        # Extract dates
        dates = self.ocr_engine.parse_dates(text)
        if len(dates) >= 1:
            extracted_data["date_of_birth"] = utils.parse_date(dates[0])
        if len(dates) >= 2:
            extracted_data["issue_date"] = utils.parse_date(dates[1])
        if len(dates) >= 3:
            extracted_data["expiry_date"] = utils.parse_date(dates[2])
        
        # Nationality
        extracted_data["nationality"] = "United Arab Emirates"
        
        return extracted_data
    
    def process_canada_id(self, image: np.ndarray, ocr_result: Dict) -> Dict:
        """Process Canadian ID/Photo Card"""
        text = ocr_result['full_text']
        
        extracted_data = {
            "document_type": "canada_id",
            "full_name": None,
            "id_number": None,
            "address": None,
            "issue_date": None,
            "expiry_date": None,
            "raw_text": text  # Always include raw text
        }
        
        print(f"DEBUG CANADA ID: Processing text:\n{text}")
        
        # Extract name - look for lines with comma-separated words after NAME
        lines = text.split('\n')
        name_candidates = []
        
        for i, line in enumerate(lines):
            if 'NAME' in line.upper():
                # Look at next few lines for name pattern
                for j in range(i+1, min(i+5, len(lines))):
                    if ',' in lines[j] and any(c.isalpha() for c in lines[j]):
                        name_candidates.append(lines[j].strip())
        
        # Look for the line with most comma-separated parts (likely the actual name)
        if name_candidates:
            best_candidate = max(name_candidates, key=lambda x: x.count(','))
            print(f"DEBUG CANADA ID: Name candidates: {name_candidates}")
            print(f"DEBUG CANADA ID: Best name line: {best_candidate}")
            
            # Try to parse comma-separated format
            parts = [p.strip() for p in best_candidate.split(',') if p.strip()]
            if len(parts) >= 2:
                # Assume LAST,FIRST or LAST,FIRST,MIDDLE
                extracted_data["full_name"] = f"{parts[1]} {parts[2] if len(parts) > 2 else ''} {parts[0]}".strip()
                print(f"DEBUG CANADA ID: Parsed name: {extracted_data['full_name']}")
        
        # Extract ID number (flexible pattern for OCR errors)
        id_patterns = [
            r'(\d{3}\s*[-\s]*\s*[A-Z0-9]{2,4}\s*[-\s]*\s*\d{4,5})',
        ]
        id_number = self.ocr_engine.find_field_by_pattern(text, id_patterns)
        if id_number:
            extracted_data["id_number"] = id_number.strip()
            print(f"DEBUG CANADA ID: Found ID: {id_number}")
        
        # Extract address - look for street patterns
        address_patterns = [
            r'(\d+[-\s]+\d*\s*[A-Z\s]+(?:DR|DRIVE|ST|STREET|AVE|AVENUE|RD|ROAD|BLVD|CENTRE)[^\n]*)',
            r'(\d+\s+[A-Z\s]+(?:DR|ST|AVE|RD)[^\n]+)'
        ]
        for line in lines:
            for pattern in address_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    addr = match.group(1).strip()
                    # Try to find city and province on next line
                    line_idx = lines.index(line)
                    if line_idx + 1 < len(lines):
                        next_line = lines[line_idx + 1].strip()
                        if next_line and len(next_line) > 2:
                            addr += ", " + next_line
                    extracted_data["address"] = addr
                    print(f"DEBUG CANADA ID: Found address: {addr}")
                    break
        
        # Extract all numbers that look like dates (including OCR errors)
        date_patterns = [
            r'\b(20\d{6})\b',  # 20221231 (year starting with 20)
            r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b',  # 12/31/2022
            r'\b(\d{4}[/-]\d{2}[/-]\d{2})\b',  # 2022-12-31
            r'\b([0o2]\d{7})\b',  # Handle OCR errors (o/O instead of 0)
        ]
        found_dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Clean up OCR errors in dates
                cleaned = match.replace('o', '0').replace('O', '0').replace('z', '2')
                if cleaned.isdigit() and len(cleaned) == 8:
                    found_dates.append(cleaned)
        
        print(f"DEBUG CANADA ID: Raw date search in text")
        print(f"DEBUG CANADA ID: Found dates: {found_dates}")
        
        if len(found_dates) >= 1:
            extracted_data["issue_date"] = utils.parse_date(found_dates[0])
        if len(found_dates) >= 2:
            extracted_data["expiry_date"] = utils.parse_date(found_dates[-1])
        
        # If still no dates, manually look for 8-digit sequences
        if not found_dates:
            all_sequences = re.findall(r'[0-9ozOZ]{8,}', text)
            print(f"DEBUG CANADA ID: All 8-digit sequences found: {all_sequences}")
            for seq in all_sequences:
                cleaned = seq.replace('o', '0').replace('O', '0').replace('z', '2').replace('Z', '2')
                if len(cleaned) == 8:
                    found_dates.append(cleaned)
                    print(f"DEBUG CANADA ID: Converted '{seq}' to '{cleaned}'")
            
            # Now parse the found dates
            if len(found_dates) >= 1:
                extracted_data["issue_date"] = utils.parse_date(found_dates[0])
            if len(found_dates) >= 2:
                extracted_data["expiry_date"] = utils.parse_date(found_dates[-1])
        
        return extracted_data
    
    def _extract_mrz_passporteye(self, image: np.ndarray) -> Optional[Dict]:
        """Extract MRZ using passporteye library"""
        try:
            # Convert to PIL Image
            pil_image = utils.cv2_to_pil(image)
            
            # Use passporteye
            mrz = passporteye.read_mrz(pil_image)
            
            if mrz:
                mrz_data = mrz.to_dict()
                return {
                    "full_name": f"{mrz_data.get('names', '')} {mrz_data.get('surname', '')}".strip(),
                    "passport_number": mrz_data.get('number', ''),
                    "nationality": mrz_data.get('country', ''),
                    "date_of_birth": mrz_data.get('date_of_birth', ''),
                    "gender": mrz_data.get('sex', ''),
                    "expiry_date": mrz_data.get('expiration_date', ''),
                    "mrz_lines": [mrz_data.get('mrz_type', ''), mrz_data.get('raw_text', '')]
                }
        except Exception as e:
            print(f"MRZ extraction failed: {e}")
        
        return None
    
    def process_document(self, file_path: Path) -> Dict:
        """Process document and extract all information"""
        start_time = datetime.now()
        
        # Load document
        images = self.load_document(file_path)
        
        if not images:
            return {
                "success": False,
                "error": "Could not load document"
            }
        
        # Use first page/image
        image = images[0]
        print(f"DEBUG PROCESSOR: Image loaded, shape: {image.shape}")
        
        # Perform OCR
        print("DEBUG PROCESSOR: Starting OCR extraction...")
        ocr_result = self.ocr_engine.extract_text(image)
        print(f"DEBUG PROCESSOR: OCR complete. Confidence: {ocr_result.get('confidence', 0):.1f}%")
        
        # Detect document type
        doc_type = self.detect_document_type(image, ocr_result['full_text'])
        print(f"DEBUG PROCESSOR: Detected document type: {doc_type}")
        
        # Process based on type
        if doc_type == "passport":
            extracted_data = self.process_passport(image, ocr_result)
        elif doc_type == "uae_eid":
            extracted_data = self.process_uae_eid(image, ocr_result)
        elif doc_type == "canada_id":
            extracted_data = self.process_canada_id(image, ocr_result)
        else:
            extracted_data = {
                "document_type": doc_type,
                "raw_text": ocr_result['full_text']
            }
        
        # Extract face
        face_image = self.face_detector.extract_face_from_document(image)
        face_path = None
        
        if face_image is not None:
            face_path = self.face_detector.save_face(
                face_image, 
                Config.EXTRACTED_FACES_DIR,
                prefix=f"doc_{doc_type}"
            )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "document_type": doc_type,
            "extracted_data": extracted_data,
            "face_image_path": str(face_path) if face_path else None,
            "confidence_score": ocr_result['confidence'],
            "processing_time": processing_time,
            "ocr_details": ocr_result
        }

