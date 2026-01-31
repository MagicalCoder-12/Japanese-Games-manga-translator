#!/usr/bin/env python
"""
Main launcher script for the Japanese Text Translator application
"""
import sys
import os

def check_dependencies():
    """Check if required packages are available"""
    missing_packages = []
    
    try:
        import ollama
    except ImportError:
        missing_packages.append("ollama")
        
    try:
        import pyperclip
    except ImportError:
        missing_packages.append("pyperclip")
        
    try:
        import pyautogui
    except ImportError:
        missing_packages.append("pyautogui")
        
    try:
        import cv2
    except ImportError:
        missing_packages.append("opencv-python")
        
    try:
        from manga_ocr import MangaOcr
    except ImportError:
        missing_packages.append("manga-ocr")
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        print("Or activate your conda environment with all dependencies")
        return False
        
    return True

def main():
    print("Starting Japanese Text Translator...")
    print("Features: Manual translation, Screen OCR, Automatic translation")
    
    if not check_dependencies():
        sys.exit(1)
    
    # Import and run the main application
    try:
        from translator_app import main as app_main
        print("Launching application...")
        app_main()
    except Exception as e:
        print(f"Error launching application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()