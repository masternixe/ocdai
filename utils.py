"""
Utility functions
"""
import base64
import hashlib
import io
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
from PIL import Image
import numpy as np
import cv2


def save_uploaded_file(uploaded_file, upload_dir: Path) -> Path:
    """Save uploaded file and return path"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_hash = hashlib.md5(uploaded_file.read()).hexdigest()[:8]
    uploaded_file.seek(0)
    
    file_extension = Path(uploaded_file.name).suffix
    file_name = f"{timestamp}_{file_hash}{file_extension}"
    file_path = upload_dir / file_name
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    
    return file_path


def image_to_base64(image_path: Path) -> str:
    """Convert image to base64 string"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def base64_to_image(base64_string: str) -> Image.Image:
    """Convert base64 string to PIL Image"""
    image_data = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(image_data))


def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV format"""
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)


def cv2_to_pil(cv2_image: np.ndarray) -> Image.Image:
    """Convert OpenCV image to PIL Image"""
    return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))


def validate_file_format(file_name: str, allowed_formats: list) -> bool:
    """Validate file format"""
    extension = Path(file_name).suffix.lower().lstrip('.')
    return extension in allowed_formats


def validate_file_size(file_size: int, max_size: int) -> bool:
    """Validate file size"""
    return file_size <= max_size


def check_image_quality(image: np.ndarray) -> dict:
    """Check image quality metrics"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # Brightness
    brightness = np.mean(gray)
    
    # Blur detection using Laplacian variance
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    blur_score = laplacian.var()
    
    # Contrast
    contrast = gray.std()
    
    return {
        "brightness": float(brightness),
        "blur_score": float(blur_score),
        "contrast": float(contrast),
        "is_bright_enough": bool(brightness > 50),
        "is_sharp_enough": bool(blur_score > 100),
        "has_good_contrast": bool(contrast > 30)
    }


def parse_date(date_string: str) -> Optional[str]:
    """Parse and normalize date string"""
    if not date_string:
        return None
    
    date_formats = [
        "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d",
        "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y",
        "%Y%m%d"
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_string.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return date_string


def is_document_expired(expiry_date_str: str) -> bool:
    """Check if document is expired"""
    try:
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
        return expiry_date < datetime.now()
    except:
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    keepcharacters = ('.', '_', '-')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()


def crop_face_region(image: np.ndarray, face_location: Tuple[int, int, int, int]) -> np.ndarray:
    """Crop face region from image"""
    top, right, bottom, left = face_location
    return image[top:bottom, left:right]


def resize_image(image: np.ndarray, max_width: int = 800, max_height: int = 600) -> np.ndarray:
    """Resize image while maintaining aspect ratio"""
    height, width = image.shape[:2]
    
    if width <= max_width and height <= max_height:
        return image
    
    ratio = min(max_width / width, max_height / height)
    new_width = int(width * ratio)
    new_height = int(height * ratio)
    
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)


def draw_face_box(image: np.ndarray, face_location: Tuple[int, int, int, int], 
                   label: str = "", color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
    """Draw bounding box around face"""
    image_copy = image.copy()
    top, right, bottom, left = face_location
    
    cv2.rectangle(image_copy, (left, top), (right, bottom), color, 2)
    
    if label:
        cv2.putText(image_copy, label, (left, top - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return image_copy

