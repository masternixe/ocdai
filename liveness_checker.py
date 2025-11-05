"""
Liveness Detection Module
"""
import cv2
import numpy as np
import dlib
from typing import Dict, List, Optional, Tuple
from scipy.spatial import distance as dist
from collections import deque
from config import Config
import utils


class LivenessChecker:
    """Liveness detection using blink and head movement"""
    
    # Eye Aspect Ratio (EAR) threshold for blink detection
    EAR_THRESHOLD = 0.25
    EAR_CONSEC_FRAMES = 3
    
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        try:
            # Try to load shape predictor
            self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        except:
            self.predictor = None
        
        self.blink_counter = 0
        self.frame_counter = 0
        self.blink_history = deque(maxlen=100)
        
    def eye_aspect_ratio(self, eye_points: np.ndarray) -> float:
        """Calculate Eye Aspect Ratio (EAR)"""
        # Compute euclidean distances between vertical eye landmarks
        A = dist.euclidean(eye_points[1], eye_points[5])
        B = dist.euclidean(eye_points[2], eye_points[4])
        
        # Compute euclidean distance between horizontal eye landmarks
        C = dist.euclidean(eye_points[0], eye_points[3])
        
        # Eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear
    
    def get_eye_regions(self, landmarks) -> Tuple[np.ndarray, np.ndarray]:
        """Extract left and right eye coordinates from landmarks"""
        # dlib face landmarks: left eye (36-41), right eye (42-47)
        left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
        right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])
        
        return left_eye, right_eye
    
    def detect_blink(self, frame: np.ndarray) -> Tuple[bool, float]:
        """Detect blink in a single frame"""
        if self.predictor is None:
            return False, 0.0
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        
        if len(faces) == 0:
            return False, 0.0
        
        # Use first detected face
        face = faces[0]
        landmarks = self.predictor(gray, face)
        
        # Get eye regions
        left_eye, right_eye = self.get_eye_regions(landmarks)
        
        # Calculate EAR for both eyes
        left_ear = self.eye_aspect_ratio(left_eye)
        right_ear = self.eye_aspect_ratio(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        # Check if blink occurred
        is_blink = avg_ear < self.EAR_THRESHOLD
        
        return is_blink, avg_ear
    
    def count_blinks(self, frames: List[np.ndarray]) -> int:
        """Count blinks across multiple frames"""
        blink_count = 0
        consecutive_closed = 0
        
        for frame in frames:
            is_blink, _ = self.detect_blink(frame)
            
            if is_blink:
                consecutive_closed += 1
            else:
                if consecutive_closed >= self.EAR_CONSEC_FRAMES:
                    blink_count += 1
                consecutive_closed = 0
        
        return blink_count
    
    def check_head_movement(self, frames: List[np.ndarray]) -> bool:
        """Detect head movement across frames"""
        if len(frames) < 5:
            return False
        
        face_positions = []
        
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)
            
            if len(faces) > 0:
                face = faces[0]
                center_x = (face.left() + face.right()) / 2
                center_y = (face.top() + face.bottom()) / 2
                face_positions.append((center_x, center_y))
        
        if len(face_positions) < 5:
            return False
        
        # Calculate movement variance
        positions = np.array(face_positions)
        variance = np.var(positions, axis=0)
        
        # If variance is above threshold, head movement detected
        movement_threshold = 100
        return np.any(variance > movement_threshold)
    
    def passive_liveness_check(self, image: np.ndarray) -> Dict[str, any]:
        """Passive liveness detection (texture analysis)"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Check for JPEG artifacts (signs of photo of photo)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_score = laplacian.var()
        
        # Check color distribution
        color_variance = np.var(image)
        
        # Check for screen moiré patterns
        fft = np.fft.fft2(gray)
        fft_shift = np.fft.fftshift(fft)
        magnitude_spectrum = np.abs(fft_shift)
        
        # High frequency content indicates real face
        high_freq_score = np.mean(magnitude_spectrum[magnitude_spectrum > np.percentile(magnitude_spectrum, 90)])
        
        is_live = (
            texture_score > 50 and
            color_variance > 100 and
            high_freq_score > 10
        )
        
        confidence = min(100, (texture_score / 100 + color_variance / 1000 + high_freq_score / 100) * 33.3)
        
        return {
            "is_live": bool(is_live),
            "confidence": float(confidence),
            "texture_score": float(texture_score),
            "color_variance": float(color_variance),
            "high_freq_score": float(high_freq_score)
        }
    
    def check_liveness(self, image: np.ndarray, frames: Optional[List[np.ndarray]] = None) -> Dict[str, any]:
        """Comprehensive liveness check"""
        quality_checks = utils.check_image_quality(image)
        
        # Passive liveness
        passive_result = self.passive_liveness_check(image)
        
        result = {
            "quality_checks": quality_checks,
            "passive_liveness": passive_result,
            "blink_count": int(0),
            "head_movement_detected": bool(False),
            "liveness_score": float(0.0),
            "passed": bool(False)
        }
        
        # Active liveness (if frames provided)
        if frames and len(frames) > 1:
            blink_count = self.count_blinks(frames)
            head_movement = self.check_head_movement(frames)
            
            result["blink_count"] = int(blink_count)
            result["head_movement_detected"] = bool(head_movement)
            
            # Calculate liveness score
            blink_score = min(100, (blink_count / Config.BLINK_THRESHOLD) * 50)
            movement_score = 50 if head_movement else 0
            passive_score = passive_result["confidence"]
            
            liveness_score = (blink_score + movement_score + passive_score) / 3
            result["liveness_score"] = float(liveness_score)
            result["passed"] = bool(liveness_score > 50)
        else:
            # Only passive liveness
            result["liveness_score"] = float(passive_result["confidence"])
            result["passed"] = bool(passive_result["is_live"])
        
        return result
    
    def analyze_single_image(self, image: np.ndarray) -> Dict[str, any]:
        """Analyze a single captured image for liveness"""
        return self.check_liveness(image)

