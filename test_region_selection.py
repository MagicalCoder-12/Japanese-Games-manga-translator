#!/usr/bin/env python
"""
Test script for region selection functionality
"""
import tkinter as tk
from ocr_launcher import RegionSelector

def test_region_selection():
    """Test the region selection functionality"""
    print("Testing region selection...")
    print("Instructions:")
    print("1. Click and drag to select a region")
    print("2. Release the mouse button - selection should confirm automatically")
    print("3. If it works, the window should close after releasing mouse")
    print("4. Press ESC to cancel if needed")
    print()
    
    selector = RegionSelector()
    region = selector.select_region()
    
    if region:
        print(f"✓ Region selected successfully: {region}")
        print("Test PASSED - Mouse release is working correctly!")
    else:
        print("✗ Region selection was cancelled or failed")
        print("Test FAILED - Mouse release might not be working")

if __name__ == "__main__":
    test_region_selection()