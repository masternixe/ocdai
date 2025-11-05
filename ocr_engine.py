"""
OCR Engine - Native and API modes
"""
import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from config import Config
import re


class OCREngine:
    """OCR processing with native and API mode support"""
    
    def __init__(self, mode: str = "native"):
        self.mode = mode
        if Config.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        return enhanced
    
    def extract_text_native(self, image: np.ndarray) -> Dict[str, any]:
        """Extract text using Tesseract OCR"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Try OCR on original grayscale first
            print("DEBUG OCR: Trying OCR on grayscale image...")
            full_text_original = pytesseract.image_to_string(gray, lang='eng')
            
            # Also try on preprocessed version
            print("DEBUG OCR: Trying OCR on preprocessed image...")
            preprocessed = self.preprocess_image(image)
            full_text_preprocessed = pytesseract.image_to_string(preprocessed, lang='eng')
            
            # Use whichever gave better results
            if len(full_text_original) > len(full_text_preprocessed):
                print("DEBUG OCR: Using original grayscale version")
                working_image = gray
                full_text = full_text_original
            else:
                print("DEBUG OCR: Using preprocessed version")
                working_image = preprocessed
                full_text = full_text_preprocessed
            
            # Get detailed OCR data with lower confidence threshold
            data = pytesseract.image_to_data(
                working_image, output_type=pytesseract.Output.DICT, lang='eng'
            )
            
            # Extract text with confidence
            text_blocks = []
            confidences = []
            
            # Use lower threshold temporarily
            threshold = min(Config.OCR_CONFIDENCE_THRESHOLD, 30)
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > threshold:
                    text = data['text'][i].strip()
                    if text:
                        text_blocks.append(text)
                        confidences.append(float(data['conf'][i]))
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            print(f"DEBUG OCR: Found {len(text_blocks)} text blocks, confidence: {avg_confidence:.1f}%")
            print(f"DEBUG OCR: Full text preview: {full_text[:200]}")
            print(f"DEBUG OCR: Text blocks: {text_blocks[:10]}")
            
            return {
                "full_text": full_text,
                "text_blocks": text_blocks,
                "confidence": avg_confidence,
                "word_count": len(text_blocks)
            }
        except Exception as e:
            print(f"ERROR in OCR: {e}")
            import traceback
            traceback.print_exc()
            return {
                "full_text": "",
                "text_blocks": [],
                "confidence": 0.0,
                "word_count": 0,
                "error": str(e)
            }
    
    def extract_text_api(self, image: np.ndarray) -> Dict[str, any]:
        """Extract text using cloud API (Azure/AWS/Google)"""
        # Placeholder for API implementation
        # In production, this would call actual APIs
        return {
            "full_text": "",
            "text_blocks": [],
            "confidence": 0.0,
            "word_count": 0,
            "api_used": "none"
        }
    
    def extract_text(self, image: np.ndarray) -> Dict[str, any]:
        """Extract text based on configured mode"""
        if self.mode == "api":
            return self.extract_text_api(image)
        else:
            return self.extract_text_native(image)
    
    def find_field_by_pattern(self, text: str, patterns: List[str]) -> Optional[str]:
        """Find field value using regex patterns"""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip() if match.groups() else match.group(0).strip()
        return None
    
    def extract_mrz(self, text: str) -> Optional[List[str]]:
        """Extract MRZ lines from text"""
        # MRZ lines are typically 44 or 36 characters
        lines = text.split('\n')
        mrz_lines = []
        
        for line in lines:
            clean_line = re.sub(r'[^A-Z0-9<]', '', line.upper())
            if len(clean_line) in [30, 36, 44]:
                mrz_lines.append(clean_line)
        
        return mrz_lines if len(mrz_lines) >= 2 else None
    
    def parse_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        date_patterns = [
            r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b',
            r'\b(\d{4}[/-]\d{2}[/-]\d{2})\b',
            r'\b(\d{2}\s+[A-Za-z]{3}\s+\d{4})\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return list(set(dates))
    
    def extract_document_number(self, text: str, doc_type: str) -> Optional[str]:
        """Extract document number based on document type"""
        patterns = {
            "passport": [
                r'PASSPORT\s*(?:NO|NUMBER|#)?\s*[:\-]?\s*([A-Z0-9]{6,12})',
                r'P(?:NO|#)?\s*[:\-]?\s*([A-Z0-9]{6,12})',
                r'\b([A-Z]{1,2}\d{7,9})\b'
            ],
            "uae_eid": [
                r'ID\s*(?:NO|NUMBER)?\s*[:\-]?\s*(\d{3}-\d{4}-\d{7}-\d{1})',
                r'(\d{3}[-\s]?\d{4}[-\s]?\d{7}[-\s]?\d{1})'
            ]
        }
        
        if doc_type in patterns:
            return self.find_field_by_pattern(text, patterns[doc_type])
        
        return None

