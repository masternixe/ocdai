"""
Face Matching Module
"""
import cv2
import numpy as np
import face_recognition
from typing import Dict, Optional, Tuple
from deepface import DeepFace
from config import Config


class FaceMatcher:
    """Face comparison and matching"""
    
    def __init__(self, threshold: float = None):
        self.threshold = threshold or Config.FACE_MATCH_THRESHOLD
        self.distance_threshold = Config.FACE_DISTANCE_THRESHOLD
    
    def compare_faces_dlib(self, face1: np.ndarray, face2: np.ndarray) -> Dict[str, any]:
        """Compare faces using face_recognition (dlib)"""
        # Convert to RGB
        rgb1 = cv2.cvtColor(face1, cv2.COLOR_BGR2RGB) if len(face1.shape) == 3 else face1
        rgb2 = cv2.cvtColor(face2, cv2.COLOR_BGR2RGB) if len(face2.shape) == 3 else face2
        
        # Get face encodings
        encodings1 = face_recognition.face_encodings(rgb1)
        encodings2 = face_recognition.face_encodings(rgb2)
        
        if not encodings1 or not encodings2:
            return {
                "success": False,
                "error": "Could not detect face in one or both images"
            }
        
        # Calculate face distance
        face_distance = face_recognition.face_distance([encodings1[0]], encodings2[0])[0]
        
        # Compare faces
        match = face_recognition.compare_faces([encodings1[0]], encodings2[0], 
                                              tolerance=self.distance_threshold)[0]
        
        # Calculate similarity score (inverse of distance)
        similarity_score = 1 - face_distance
        
        return {
            "success": True,
            "match": match,
            "distance": float(face_distance),
            "similarity_score": float(similarity_score),
            "confidence": float(similarity_score * 100),
            "method": "dlib"
        }
    
    def compare_faces_deepface(self, face1_path: str, face2_path: str) -> Dict[str, any]:
        """Compare faces using DeepFace"""
        try:
            result = DeepFace.verify(
                img1_path=face1_path,
                img2_path=face2_path,
                model_name='VGG-Face',
                enforce_detection=False
            )
            
            return {
                "success": True,
                "match": result['verified'],
                "distance": result['distance'],
                "similarity_score": 1 - (result['distance'] / result['threshold']),
                "confidence": (1 - (result['distance'] / result['threshold'])) * 100,
                "method": "deepface",
                "model": result['model']
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "deepface"
            }
    
    def compare_faces_opencv(self, face1: np.ndarray, face2: np.ndarray) -> Dict[str, any]:
        """Compare faces using OpenCV (simpler method)"""
        # Resize to same size
        size = (100, 100)
        face1_resized = cv2.resize(face1, size)
        face2_resized = cv2.resize(face2, size)
        
        # Convert to grayscale
        gray1 = cv2.cvtColor(face1_resized, cv2.COLOR_BGR2GRAY) if len(face1_resized.shape) == 3 else face1_resized
        gray2 = cv2.cvtColor(face2_resized, cv2.COLOR_BGR2GRAY) if len(face2_resized.shape) == 3 else face2_resized
        
        # Calculate histogram similarity
        hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
        hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
        
        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        
        # Calculate structural similarity
        ssim_score = self._calculate_ssim(gray1, gray2)
        
        # Combined score
        combined_score = (similarity + ssim_score) / 2
        
        match = combined_score > self.threshold
        
        return {
            "success": True,
            "match": match,
            "similarity_score": float(combined_score),
            "confidence": float(combined_score * 100),
            "hist_similarity": float(similarity),
            "ssim_score": float(ssim_score),
            "method": "opencv"
        }
    
    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate Structural Similarity Index"""
        C1 = 6.5025
        C2 = 58.5225
        
        img1 = img1.astype(np.float64)
        img2 = img2.astype(np.float64)
        
        mu1 = cv2.GaussianBlur(img1, (11, 11), 1.5)
        mu2 = cv2.GaussianBlur(img2, (11, 11), 1.5)
        
        mu1_sq = mu1 ** 2
        mu2_sq = mu2 ** 2
        mu1_mu2 = mu1 * mu2
        
        sigma1_sq = cv2.GaussianBlur(img1 ** 2, (11, 11), 1.5) - mu1_sq
        sigma2_sq = cv2.GaussianBlur(img2 ** 2, (11, 11), 1.5) - mu2_sq
        sigma12 = cv2.GaussianBlur(img1 * img2, (11, 11), 1.5) - mu1_mu2
        
        ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
                   ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
        
        return float(ssim_map.mean())
    
    def match_faces(self, face1: np.ndarray, face2: np.ndarray, 
                   method: str = "dlib") -> Dict[str, any]:
        """Match two face images using specified method"""
        if method == "dlib":
            return self.compare_faces_dlib(face1, face2)
        elif method == "opencv":
            return self.compare_faces_opencv(face1, face2)
        else:
            return self.compare_faces_dlib(face1, face2)
    
    def create_comparison_image(self, face1: np.ndarray, face2: np.ndarray, 
                               match_result: Dict) -> np.ndarray:
        """Create side-by-side comparison image"""
        # Resize both images to same height
        h1, w1 = face1.shape[:2]
        h2, w2 = face2.shape[:2]
        
        target_height = 300
        new_w1 = int(w1 * (target_height / h1))
        new_w2 = int(w2 * (target_height / h2))
        
        resized1 = cv2.resize(face1, (new_w1, target_height))
        resized2 = cv2.resize(face2, (new_w2, target_height))
        
        # Create comparison image
        comparison = np.hstack([resized1, resized2])
        
        # Add text overlay
        match_text = "MATCH" if match_result.get("match", False) else "NO MATCH"
        confidence = match_result.get("confidence", 0)
        
        color = (0, 255, 0) if match_result.get("match", False) else (0, 0, 255)
        
        cv2.putText(comparison, f"{match_text}: {confidence:.1f}%", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Add labels
        cv2.putText(comparison, "Document", (10, target_height - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(comparison, "Live", (new_w1 + 10, target_height - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return comparison

