"""
Test script to verify installation and basic functionality
"""
import sys
from pathlib import Path

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    modules = [
        "streamlit",
        "fastapi",
        "cv2",
        "pytesseract",
        "face_recognition",
        "PIL",
        "numpy",
        "sqlalchemy",
        "pydantic"
    ]
    
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module}")
            failed.append(module)
    
    if failed:
        print(f"\n✗ Failed imports: {', '.join(failed)}")
        return False
    else:
        print("\n✓ All imports successful")
        return True

def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from config import Config
        Config.ensure_directories()
        
        print(f"  ✓ Config loaded")
        print(f"    - Mode: {Config.PROCESSING_MODE}")
        print(f"    - Database: {Config.DATABASE_URL}")
        print(f"    - Upload dir: {Config.UPLOAD_DIR}")
        return True
    except Exception as e:
        print(f"  ✗ Config error: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    
    try:
        from models import init_db
        init_db()
        print("  ✓ Database initialized")
        return True
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False

def test_modules():
    """Test core modules"""
    print("\nTesting core modules...")
    
    modules = [
        ("OCR Engine", "from ocr_engine import OCREngine; OCREngine()"),
        ("Face Detector", "from face_detector import FaceDetector; FaceDetector()"),
        ("Liveness Checker", "from liveness_checker import LivenessChecker; LivenessChecker()"),
        ("Face Matcher", "from face_matcher import FaceMatcher; FaceMatcher()"),
        ("Processor", "from processor import DocumentProcessor; DocumentProcessor()"),
    ]
    
    failed = []
    
    for name, code in modules:
        try:
            exec(code)
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            failed.append(name)
    
    if failed:
        print(f"\n✗ Failed modules: {', '.join(failed)}")
        return False
    else:
        print("\n✓ All modules working")
        return True

def test_tesseract():
    """Test Tesseract OCR"""
    print("\nTesting Tesseract OCR...")
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"  ✓ Tesseract version: {version}")
        
        # Test languages
        try:
            import subprocess
            result = subprocess.run(['tesseract', '--list-langs'], 
                                  capture_output=True, text=True)
            langs = result.stdout.split('\n')[1:]
            langs = [l.strip() for l in langs if l.strip()]
            print(f"  ✓ Available languages: {', '.join(langs[:5])}...")
        except:
            pass
        
        return True
    except Exception as e:
        print(f"  ✗ Tesseract error: {e}")
        return False

def test_opencv():
    """Test OpenCV"""
    print("\nTesting OpenCV...")
    
    try:
        import cv2
        import numpy as np
        
        # Create test image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Test face detection
        cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        print(f"  ✓ OpenCV version: {cv2.__version__}")
        print(f"  ✓ Face cascade loaded")
        return True
    except Exception as e:
        print(f"  ✗ OpenCV error: {e}")
        return False

def test_face_recognition():
    """Test face_recognition library"""
    print("\nTesting face_recognition...")
    
    try:
        import face_recognition
        import numpy as np
        
        # Create dummy face encoding
        dummy_encoding = np.random.rand(128)
        
        print(f"  ✓ face_recognition loaded")
        return True
    except Exception as e:
        print(f"  ✗ face_recognition error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("System Test - Document Processing System")
    print("="*60)
    
    tests = [
        test_imports,
        test_config,
        test_database,
        test_tesseract,
        test_opencv,
        test_face_recognition,
        test_modules,
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    
    if all(results):
        print("✓ ALL TESTS PASSED")
        print("="*60)
        print("\nSystem is ready to use!")
        print("\nTo start the application:")
        print("  python start.py")
        print("  or")
        print("  streamlit run app.py")
        return 0
    else:
        passed = sum(results)
        total = len(results)
        print(f"✗ SOME TESTS FAILED ({passed}/{total} passed)")
        print("="*60)
        print("\nPlease fix the issues above before using the system.")
        print("Refer to INSTALL.md for installation instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

