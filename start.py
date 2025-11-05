"""
Quick start script for the application
"""
import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    try:
        import streamlit
        import fastapi
        import cv2
        import pytesseract
        import face_recognition
        print("✓ All Python dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        return False

def check_tesseract():
    """Check if Tesseract is installed"""
    print("\nChecking Tesseract OCR...")
    
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        print(f"✓ Tesseract installed: {result.stdout.split()[1]}")
        return True
    except FileNotFoundError:
        print("✗ Tesseract not found")
        print("\nPlease install Tesseract OCR:")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  Linux: sudo apt-get install tesseract-ocr")
        print("  Mac: brew install tesseract")
        return False

def initialize_database():
    """Initialize database if not exists"""
    print("\nInitializing database...")
    
    if Path("documents.db").exists():
        print("✓ Database already exists")
        return True
    
    try:
        from models import init_db
        init_db()
        print("✓ Database initialized")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    directories = ['uploads', 'extracted_faces', 'live_captures']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✓ Directories created")
    return True

def check_env_file():
    """Check if .env file exists"""
    print("\nChecking configuration...")
    
    if not Path(".env").exists():
        print("⚠ .env file not found")
        print("  Copy env_template.txt to .env and configure")
        print("  cp env_template.txt .env")
        return False
    else:
        print("✓ Configuration file found")
        return True

def start_application(mode='streamlit'):
    """Start the application"""
    
    if mode == 'streamlit':
        print("\n" + "="*60)
        print("Starting Streamlit Application...")
        print("="*60)
        print("\nAccess at: http://localhost:8501")
        print("Press Ctrl+C to stop\n")
        
        try:
            subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'])
        except KeyboardInterrupt:
            print("\n\nApplication stopped.")
    
    elif mode == 'api':
        print("\n" + "="*60)
        print("Starting API Server...")
        print("="*60)
        print("\nAccess at: http://localhost:8000")
        print("API Docs: http://localhost:8000/docs")
        print("Press Ctrl+C to stop\n")
        
        try:
            subprocess.run([sys.executable, 'api.py'])
        except KeyboardInterrupt:
            print("\n\nAPI server stopped.")
    
    elif mode == 'both':
        print("\n" + "="*60)
        print("Starting Both Services...")
        print("="*60)
        print("\nStreamlit: http://localhost:8501")
        print("API: http://localhost:8000")
        print("Press Ctrl+C to stop\n")
        
        try:
            # Start API in background
            api_process = subprocess.Popen([sys.executable, 'api.py'])
            
            # Start Streamlit in foreground
            subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'])
        except KeyboardInterrupt:
            print("\n\nStopping services...")
            api_process.terminate()
            print("Services stopped.")

def main():
    """Main function"""
    print("="*60)
    print("Document Processing System - Quick Start")
    print("="*60)
    
    # Check all requirements
    checks = [
        check_dependencies(),
        check_tesseract(),
        initialize_database(),
        create_directories(),
        check_env_file()
    ]
    
    if not all(checks):
        print("\n" + "="*60)
        print("⚠ Setup incomplete. Please fix the issues above.")
        print("="*60)
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✓ All checks passed!")
    print("="*60)
    
    # Ask user which mode to start
    print("\nSelect mode to start:")
    print("1. Streamlit Web Application (default)")
    print("2. API Server only")
    print("3. Both (API + Streamlit)")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip() or '1'
    
    if choice == '1':
        start_application('streamlit')
    elif choice == '2':
        start_application('api')
    elif choice == '3':
        start_application('both')
    elif choice == '4':
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice. Starting Streamlit...")
        start_application('streamlit')

if __name__ == "__main__":
    main()

