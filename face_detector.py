"""
Face Detection and Extraction
"""
import cv2
import numpy as np
import face_recognition
from typing import List, Optional, Tuple, Dict
from PIL import Image
from pathlib import Path
from config import Config
import utils


class FaceDetector:
    """Face detection from documents and live images"""
    
    def __init__(self):
        self.cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
    
    def detect_faces_opencv(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces using OpenCV Haar Cascade"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        faces = self.cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(Config.MIN_FACE_SIZE, Config.MIN_FACE_SIZE)
        )
        
        # Convert to (top, right, bottom, left) format
        face_locations = []
        for (x, y, w, h) in faces:
            face_locations.append((y, x + w, y + h, x))
        
        return face_locations
    
    def detect_faces_dlib(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces using face_recognition library (dlib)"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if len(image.shape) == 3 else image
        face_locations = face_recognition.face_locations(rgb_image, model="hog")
        return face_locations
    
    def detect_faces(self, image: np.ndarray, method: str = "dlib") -> List[Tuple[int, int, int, int]]:
        """Detect faces using specified method"""
        if method == "opencv":
            return self.detect_faces_opencv(image)
        else:
            return self.detect_faces_dlib(image)
    
    def extract_largest_face(self, image: np.ndarray) -> Optional[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
        """Extract the largest face from image"""
        face_locations = self.detect_faces(image)
        
        if not face_locations:
            return None
        
        # Find largest face
        largest_face = max(face_locations, key=lambda loc: (loc[2] - loc[0]) * (loc[1] - loc[3]))
        
        # Crop face
        top, right, bottom, left = largest_face
        face_image = image[top:bottom, left:right]
        
        return face_image, largest_face
    
    def extract_face_from_document(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extract face from document photo"""
        result = self.extract_largest_face(image)
        if result:
            face_image, _ = result
            return face_image
        return None
    
    def save_face(self, face_image: np.ndarray, save_dir: Path, prefix: str = "face") -> Path:
        """Save face image to disk"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.jpg"
        filepath = save_dir / filename
        
        cv2.imwrite(str(filepath), face_image)
        return filepath
    
    def get_face_encoding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Get face encoding for comparison"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if len(image.shape) == 3 else image
        
        encodings = face_recognition.face_encodings(rgb_image)
        if encodings:
            return encodings[0]
        return None
    
    def get_face_landmarks(self, image: np.ndarray) -> List[Dict]:
        """Get facial landmarks"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if len(image.shape) == 3 else image
        return face_recognition.face_landmarks(rgb_image)
    
    def detect_eyes(self, face_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect eyes in face image"""
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY) if len(face_image.shape) == 3 else face_image
        
        eyes = self.eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        
        eye_locations = []
        for (x, y, w, h) in eyes:
            eye_locations.append((x, y, w, h))
        
        return eye_locations
    
    def validate_face_quality(self, face_image: np.ndarray) -> Dict[str, any]:
        """Validate face image quality"""
        quality_checks = utils.check_image_quality(face_image)
        
        # Additional face-specific checks
        height, width = face_image.shape[:2]
        
        quality_checks.update({
            "width": width,
            "height": height,
            "is_large_enough": width >= Config.MIN_FACE_SIZE and height >= Config.MIN_FACE_SIZE,
            "aspect_ratio": width / height if height > 0 else 0
        })
        
        # Check if eyes are detectable
        eyes = self.detect_eyes(face_image)
        quality_checks["eyes_detected"] = len(eyes) >= 2
        
        return quality_checks
    
    def enhance_face_image(self, face_image: np.ndarray) -> np.ndarray:
        """Enhance face image for better recognition"""
        # Convert to LAB color space
        lab = cv2.cvtColor(face_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l_clahe = clahe.apply(l)
        
        # Merge channels
        enhanced = cv2.merge([l_clahe, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
        
        return denoised

