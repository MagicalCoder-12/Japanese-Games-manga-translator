#!/usr/bin/env python
"""
Enhanced OCR Launcher with Region Selection and Hotkeys
Features:
- Interactive region selection with visual feedback
- Region memory per game/executable
- Re-OCR hotkey (Ctrl+Shift+R)
- Auto-send to translator app
- Real-time translation
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import cv2
import numpy as np
import json
import os
import threading
import time
import psutil
try:
    import win32gui
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("Warning: pywin32 not available. Game detection will be limited.")
from PIL import Image, ImageTk
try:
    import keyboard  # For global hotkeys
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("Warning: keyboard module not available. Hotkeys will not work.")
from datetime import datetime
import re

# Import our existing modules
try:
    from jap_extracter import extract_japanese_text, normalize_for_translation
    OCR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OCR module not available: {e}")
    OCR_AVAILABLE = False
    
    def extract_japanese_text(region):
        return "OCR not available - please install manga-ocr"
    
    def normalize_for_translation(text):
        return text

try:
    from translator_app import ScreenTranslatorApp
    TRANSLATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Translator module not available: {e}")
    TRANSLATOR_AVAILABLE = False
    ScreenTranslatorApp = object  # Dummy class


class GameRegionManager:
    """Manages OCR regions for different games/executables"""
    
    def __init__(self, config_file="region_config.json"):
        self.config_file = config_file
        self.regions = self.load_regions()
        
    def load_regions(self):
        """Load saved regions from config file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading regions: {e}")
                return {}
        return {}
    
    def save_regions(self):
        """Save regions to config file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.regions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving regions: {e}")
    
    def get_active_window_info(self):
        """Get the executable name of the currently active window"""
        if not WIN32_AVAILABLE:
            return "unknown", "Unknown Window (pywin32 not available)"
            
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            exe_name = process.name().lower()
            window_title = win32gui.GetWindowText(hwnd)
            return exe_name, window_title
        except Exception as e:
            print(f"Error getting active window: {e}")
            return "unknown", "Unknown Window"
    
    def save_region_for_game(self, region):
        """Save region for the currently active game"""
        exe_name, window_title = self.get_active_window_info()
        if exe_name not in self.regions:
            self.regions[exe_name] = []
        
        # Store region with timestamp and window info
        region_data = {
            "region": region,
            "timestamp": datetime.now().isoformat(),
            "window_title": window_title,
            "last_used": datetime.now().isoformat()
        }
        
        self.regions[exe_name].append(region_data)
        self.save_regions()
        return exe_name
    
    def get_regions_for_current_game(self):
        """Get saved regions for the currently active game"""
        exe_name, _ = self.get_active_window_info()
        return self.regions.get(exe_name, [])
    
    def get_last_region_for_game(self):
        """Get the most recently used region for current game"""
        regions = self.get_regions_for_current_game()
        if regions:
            # Sort by last_used timestamp
            regions.sort(key=lambda x: x.get('last_used', ''), reverse=True)
            return regions[0]['region']
        return None


class RegionSelector:
    """Interactive region selector overlay"""
    
    def __init__(self):
        self.root = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None
        self.region_selected = None
        
    def select_region(self):
        """Show fullscreen overlay for region selection"""
        # Hide the main window temporarily
        if hasattr(self, 'main_root') and self.main_root:
            self.main_root.withdraw()
        
        # Create transparent overlay window
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.configure(bg='black')
        self.root.title("Select OCR Region")
        self.root.config(cursor="crosshair")
        
        # Canvas for drawing selection rectangle
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        self.canvas.create_text(
            self.root.winfo_screenwidth() // 2,
            50,
            text="Click and drag to select OCR region\nRelease mouse to confirm | Press ESC to cancel",
            fill='white',
            font=('Arial', 16, 'bold')
        )
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", self.cancel)
        self.root.bind("<Return>", self.confirm)
        
        # Start the selection loop
        self.root.mainloop()
        
        # Restore main window
        if hasattr(self, 'main_root') and self.main_root:
            self.main_root.deiconify()
            
        return self.region_selected
    
    def on_click(self, event):
        """Start of region selection"""
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
    
    def on_drag(self, event):
        """Dragging to define region"""
        if self.rect:
            self.canvas.delete(self.rect)
        
        self.end_x = event.x
        self.end_y = event.y
        
        # Draw rectangle
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.end_x, self.end_y,
            outline='red', width=2, fill='red', stipple='gray25'
        )
        
        # Show size info
        width = abs(self.end_x - self.start_x)
        height = abs(self.end_y - self.start_y)
        if width > 10 and height > 10:  # Only show if region is large enough
            self.canvas.create_text(
                self.start_x + width//2, self.start_y - 20,
                text=f"{width}×{height} pixels",
                fill='white', font=('Arial', 10, 'bold'),
                tags='size_info'
            )
    
    def on_release(self, event):
        """End of region selection"""
        if self.start_x is not None and self.end_x is not None:
            # Normalize coordinates
            x1, x2 = sorted([self.start_x, self.end_x])
            y1, y2 = sorted([self.start_y, self.end_y])
            
            self.region_selected = (x1, y1, x2 - x1, y2 - y1)
            
            # Visual confirmation - change rectangle color
            if self.rect:
                self.canvas.delete(self.rect)
                self.rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline='lime', width=3, fill='lime', stipple='gray25'
                )
                # Add confirmation text
                self.canvas.create_text(
                    x1 + (x2-x1)//2, y1 + (y2-y1)//2,
                    text="REGION SELECTED!\nClick anywhere or press Enter to confirm",
                    fill='white', font=('Arial', 12, 'bold'),
                    justify='center'
                )
            
            # Auto-confirm on mouse release after a short delay
            self.root.after(300, self.confirm)
    
    def confirm(self, event=None):
        """Confirm region selection"""
        if self.region_selected:
            self.root.quit()
            self.root.destroy()
        elif event:  # Only show message if triggered by key press
            print("No region selected yet. Please click and drag to select a region.")
    
    def cancel(self, event=None):
        """Cancel region selection"""
        self.region_selected = None
        self.root.quit()
        self.root.destroy()


class OCRLauncherApp:
    """Main OCR launcher application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("OCR Text Extractor Launcher")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Initialize managers
        self.region_manager = GameRegionManager()
        self.last_region = None
        self.last_exe = None
        self.translator_app = None
        self.ocr_running = False
        
        # Setup UI
        self.setup_ui()
        
        # Register hotkeys
        self.register_hotkeys()
        
        # Start translator app in background
        self.start_translator_app()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🎮 OCR Text Extractor", 
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Current game info
        self.game_info_var = tk.StringVar(value="Current Game: Unknown")
        game_label = ttk.Label(
            main_frame, 
            textvariable=self.game_info_var,
            font=("Arial", 10)
        )
        game_label.pack(pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Select Region button
        self.select_btn = ttk.Button(
            button_frame,
            text="🎯 Select OCR Region",
            command=self.select_region,
            width=20
        )
        self.select_btn.pack(pady=5)
        
        # Re-OCR button
        self.reocr_btn = ttk.Button(
            button_frame,
            text="🔁 Re-OCR Last Region (Ctrl+Shift+R)",
            command=self.reocr_last_region,
            width=30,
            state=tk.DISABLED
        )
        self.reocr_btn.pack(pady=5)
        
        # Toggle auto-OCR button
        self.auto_btn = ttk.Button(
            button_frame,
            text="⚡ Start Auto-OCR",
            command=self.toggle_auto_ocr,
            width=20
        )
        self.auto_btn.pack(pady=5)
        
        # Separator
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=20)
        
        # Recent regions
        recent_label = ttk.Label(
            main_frame,
            text="💾 Recent Regions:",
            font=("Arial", 12, "bold")
        )
        recent_label.pack(anchor=tk.W)
        
        # Listbox for recent regions
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.region_listbox = tk.Listbox(list_frame, height=8)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.region_listbox.yview)
        self.region_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.region_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load recent regions
        self.refresh_region_list()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Select a region to begin OCR")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Update game info periodically
        self.update_game_info()
    
    def register_hotkeys(self):
        """Register global hotkeys"""
        if not KEYBOARD_AVAILABLE:
            self.status_var.set("Hotkeys not available (keyboard module missing)")
            return
            
        try:
            # Re-OCR hotkey: Ctrl+Shift+R
            keyboard.add_hotkey('ctrl+shift+r', self.reocr_last_region)
            print("Registered hotkey: Ctrl+Shift+R for Re-OCR")
        except Exception as e:
            print(f"Failed to register hotkeys: {e}")
            self.status_var.set("Hotkey registration failed")
    
    def start_translator_app(self):
        """Start the translator app in a separate thread"""
        if not TRANSLATOR_AVAILABLE:
            self.status_var.set("Translator not available")
            return
            
        def run_translator():
            try:
                # Create root for translator app
                translator_root = tk.Tk()
                translator_root.withdraw()  # Hide initially
                self.translator_app = ScreenTranslatorApp(translator_root)
                translator_root.mainloop()
            except Exception as e:
                print(f"Error starting translator app: {e}")
        
        thread = threading.Thread(target=run_translator, daemon=True)
        thread.start()
        time.sleep(1)  # Give it time to initialize
    
    def update_game_info(self):
        """Update the current game information"""
        exe_name, window_title = self.region_manager.get_active_window_info()
        self.game_info_var.set(f"Current Game: {exe_name} - {window_title[:30]}...")
        self.root.after(1000, self.update_game_info)  # Update every second
    
    def select_region(self):
        """Select a new OCR region"""
        self.status_var.set("Selecting region...")
        
        # Show region selector
        selector = RegionSelector()
        selector.main_root = self.root
        region = selector.select_region()
        
        if region and len(region) == 4:
            # Save region for current game
            exe_name = self.region_manager.save_region_for_game(region)
            self.last_region = region
            self.last_exe = exe_name
            
            # Enable Re-OCR button
            self.reocr_btn.config(state=tk.NORMAL)
            
            self.status_var.set(f"Region selected for {exe_name}: {region}")
            self.refresh_region_list()
            
            # Perform initial OCR
            self.perform_ocr(region)
        else:
            self.status_var.set("Region selection cancelled")
    
    def reocr_last_region(self):
        """Re-OCR the last selected region"""
        if not self.last_region:
            # Try to get last region for current game
            region = self.region_manager.get_last_region_for_game()
            if region:
                self.last_region = region
            else:
                self.status_var.set("No region selected yet")
                return
        
        self.status_var.set("Re-OCR in progress...")
        self.perform_ocr(self.last_region)
    
    def toggle_auto_ocr(self):
        """Toggle continuous OCR mode"""
        if not self.last_region:
            self.status_var.set("Please select a region first")
            return
            
        self.ocr_running = not self.ocr_running
        
        if self.ocr_running:
            self.auto_btn.config(text="⏹️ Stop Auto-OCR")
            self.status_var.set("Auto-OCR started")
            self.start_continuous_ocr()
        else:
            self.auto_btn.config(text="⚡ Start Auto-OCR")
            self.status_var.set("Auto-OCR stopped")
    
    def start_continuous_ocr(self):
        """Start continuous OCR in background"""
        def continuous_ocr():
            while self.ocr_running and self.last_region:
                self.perform_ocr(self.last_region)
                time.sleep(2)  # OCR every 2 seconds
        
        thread = threading.Thread(target=continuous_ocr, daemon=True)
        thread.start()
    
    def perform_ocr(self, region):
        """Perform OCR on the specified region"""
        try:
            # Extract text
            text = extract_japanese_text(region)
            
            if text and text.strip():
                # Send to translator app
                self.send_to_translator(text)
                self.status_var.set(f"OCR successful: {len(text)} characters extracted")
            else:
                self.status_var.set("No text detected in region")
                
        except Exception as e:
            self.status_var.set(f"OCR Error: {str(e)}")
            print(f"OCR Error: {e}")
    
    def send_to_translator(self, text):
        """Send extracted text to translator app"""
        if not self.translator_app:
            self.status_var.set("Translator app not ready")
            return
            
        try:
            # Chunk long text if needed
            chunks = self.chunk_text(text)
            
            # Send each chunk for translation
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    # Update translator input (thread-safe)
                    self.root.after(0, self.update_translator_input, chunk, i, len(chunks))
                    
        except Exception as e:
            self.status_var.set(f"Failed to send to translator: {e}")
    
    def chunk_text(self, text, max_length=500):
        """Split long text into manageable chunks"""
        if len(text) <= max_length:
            return [text]
        
        # Split by sentences first
        sentences = re.split(r'[。！？.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Add punctuation back if it was a sentence ending
            if len(current_chunk) > 0 and text[len(current_chunk):len(current_chunk)+1] in '。！？.!?':
                sentence = text[len(current_chunk):len(current_chunk)+1] + sentence
            
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If still too long, force split
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= max_length:
                final_chunks.append(chunk)
            else:
                # Split by max_length
                for i in range(0, len(chunk), max_length):
                    final_chunks.append(chunk[i:i+max_length])
        
        return final_chunks
    
    def update_translator_input(self, text, chunk_index, total_chunks):
        """Update translator app input field (called from main thread)"""
        if not self.translator_app:
            return
            
        try:
            # Clear and insert new text
            self.translator_app.input_text.delete(1.0, tk.END)
            self.translator_app.input_text.insert(tk.END, text)
            
            # Auto-translate
            self.translator_app.start_translation()
            
            # Update status
            if total_chunks > 1:
                self.status_var.set(f"Translated chunk {chunk_index + 1}/{total_chunks}")
            else:
                self.status_var.set("Translation sent to translator app")
                
        except Exception as e:
            print(f"Error updating translator: {e}")
    
    def refresh_region_list(self):
        """Refresh the list of recent regions"""
        self.region_listbox.delete(0, tk.END)
        
        for exe_name, regions in self.region_manager.regions.items():
            self.region_listbox.insert(tk.END, f"--- {exe_name} ---")
            for region_data in regions[-3:]:  # Show last 3 regions
                region = region_data['region']
                timestamp = region_data.get('timestamp', 'Unknown')
                title = region_data.get('window_title', 'Unknown')[:30]
                self.region_listbox.insert(
                    tk.END, 
                    f"  {region} | {title}"
                )


def main():
    root = tk.Tk()
    app = OCRLauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()