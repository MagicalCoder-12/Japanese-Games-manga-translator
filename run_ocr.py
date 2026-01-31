#!/usr/bin/env python
"""
Quick launcher for the OCR extractor
"""
import subprocess
import sys
import os

def main():
    print("🚀 Launching OCR Text Extractor...")
    try:
        # Run the OCR launcher
        subprocess.run([sys.executable, "ocr_launcher.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 OCR Extractor stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()