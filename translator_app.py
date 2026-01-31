import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import ollama
import pyperclip
import threading
import re
import pyautogui
import cv2
import numpy as np
from PIL import Image
from manga_ocr import MangaOcr
import json
import os

class ScreenTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Japanese to English Translator with OCR")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Initialize MangaOCR
        self.manga_ocr = None
        self.initialize_ocr()
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # OCR variables
        self.last_region = None
        self.ocr_running = False
        
        self.setup_ui()
        
    def initialize_ocr(self):
        """Initialize MangaOCR with error handling"""
        try:
            self.manga_ocr = MangaOcr()
            print("✓ MangaOCR initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize MangaOCR: {e}")
            self.manga_ocr = None
            
    def normalize_for_translation(self, text: str) -> str:
        """
        Critical OCR post-processing to clean manga-style artifacts while preserving meaning.
        Handles OCR noise, punctuation normalization, and text structure preservation.
        """
        if not text:
            return text
            
        # Remove stray characters and OCR noise
        import re
        # Remove trailing/leading single kana characters (common OCR artifacts)
        text = re.sub(r'[\u3000\s]*[\u3041-\u3096\u30A1-\u30FA]{1,2}[\u3000\s]*$', ' ', text)
        text = re.sub(r'^[\u3000\s]*[\u3041-\u3096\u30A1-\u30FA]{1,2}[\u3000\s]*', ' ', text)
            
        # Remove repeated symbols and noise
        text = re.sub(r'[\uFF5E\u301C\u2026\u2025]{2,}', ' ', text)
        text = re.sub(r'[\u3000\s]{2,}', ' ', text)
            
        # Normalize punctuation
        punctuation_fixes = {
            '……': '・・・',
            '。。': '。。',
            '、、': '、、',
            '？！': '！？',
            '？』': '！？',
            '?!' : '！？',
            '!?' : '！？',
            '。、': '、',
            '、。': '。',
        }
            
        for bad, good in punctuation_fixes.items():
            text = text.replace(bad, good)
            
        # Fix broken line structures and merge split sentences
        # Remove line breaks within sentences
        text = re.sub(r'(?<=[\u3041-\u3096\u30A1-\u30FA\u4E00-\u9FFF])\n(?=[\u3041-\u3096\u30A1-\u30FA\u4E00-\u9FFF])', '', text)
            
        # Normalize Japanese punctuation spacing
        text = re.sub(r'([、。！？])\s+', r'\1', text)  # Remove spaces after punctuation
        text = re.sub(r'\s+([、。！？])', r'\1', text)  # Remove spaces before punctuation
            
        # Clean up multiple punctuation marks
        text = re.sub(r'([。！？])\1{2,}', r'\1\1', text)  # Limit to 2 consecutive same punctuation
        text = re.sub(r'([、])\1{2,}', r'\1\1', text)    # Limit to 2 consecutive commas
            
        # Remove leading/trailing whitespace and normalize internal spacing
        text = re.sub(r'\s+', ' ', text).strip()
            
        # Ensure proper sentence boundaries
        text = re.sub(r'([。！？])([\u3041-\u3096\u30A1-\u30FA\u4E00-\u9FFF])', r'\1 \2', text)
            
        return text.strip()
        
    def extract_japanese_text(self, region):
        """
        MangaOCR-based extraction with critical post-processing for clean output.
        Handles both vertical manga text and horizontal game text.
        """
        if not self.manga_ocr:
            return "OCR not available - MangaOCR failed to initialize"
            
        try:
            # Capture screen region
            screenshot = pyautogui.screenshot(region=region)
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Save temp image for MangaOCR
            temp_path = "_ocr_tmp.png"
            cv2.imwrite(temp_path, img)
            
            # Extract raw text
            raw_text = self.manga_ocr(temp_path)
            raw_text = raw_text.strip()
            
            # Apply critical post-processing
            processed_text = self.normalize_for_translation(raw_text)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            return processed_text
            
        except Exception as e:
            print(f"❌ MangaOCR failed: {e}")
            return f"OCR Error: {str(e)}"
    
    def setup_ui(self):
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Single OCR tab
        self.ocr_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ocr_frame, text="🔍 OCR")
        self.setup_ocr_tab()
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Settings")
        self.setup_settings_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready - Press 'S' to select region or use buttons")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 10), padx=10)
        
        # Bind keyboard shortcuts
        self.root.bind('<s>', lambda e: self.select_ocr_region())
        self.root.bind('<S>', lambda e: self.select_ocr_region())
        

        
    def setup_ocr_tab(self):
        """Setup the OCR functionality tab"""
        main_frame = ttk.Frame(self.ocr_frame, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for proper resizing
        self.ocr_frame.columnconfigure(0, weight=1)
        self.ocr_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)  # OCR output area
        main_frame.rowconfigure(6, weight=1)  # Translation output area
        
        # Title
        title_label = ttk.Label(main_frame, text="Japanese OCR & Translation", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        # OCR region info frame
        region_frame = ttk.LabelFrame(main_frame, text="Region Selection", padding="10")
        region_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        region_frame.columnconfigure(1, weight=1)
        
        self.region_var = tk.StringVar(value="No region selected")
        region_label = ttk.Label(region_frame, text="Current Region:")
        region_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        region_display = ttk.Label(region_frame, textvariable=self.region_var, font=("Arial", 10, "bold"))
        region_display.grid(row=0, column=1, sticky=tk.W)
        
        # OCR action buttons - exactly 3 buttons in order
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(0, 20), sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        # Button 1: Select Region
        select_region_btn = ttk.Button(button_frame, text="🎯 Select Region", 
                                      command=self.select_ocr_region)
        select_region_btn.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Button 2: Extract OCR
        extract_ocr_btn = ttk.Button(button_frame, text="🔍 Extract OCR", 
                                    command=self.perform_ocr)
        extract_ocr_btn.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Button 3: Translate
        translate_btn = ttk.Button(button_frame, text="🌐 Translate", 
                                  command=self.translate_ocr_text)
        translate_btn.grid(row=0, column=2, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # OCR Output section (processed Japanese text)
        ocr_output_label = ttk.Label(main_frame, text="OCR Output (Processed Japanese Text):", font=("Arial", 12, "bold"))
        ocr_output_label.grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        ocr_output_frame = ttk.Frame(main_frame)
        ocr_output_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        ocr_output_frame.columnconfigure(0, weight=1)
        ocr_output_frame.rowconfigure(0, weight=1)
        
        self.ocr_output_text = scrolledtext.ScrolledText(
            ocr_output_frame, 
            height=10, 
            wrap=tk.WORD,
            font=("Meiryo", 11)
        )
        self.ocr_output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Translation Output section (English text)
        translation_output_label = ttk.Label(main_frame, text="Translation Output (English):", font=("Arial", 12, "bold"))
        translation_output_label.grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        
        translation_output_frame = ttk.Frame(main_frame)
        translation_output_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        translation_output_frame.columnconfigure(0, weight=1)
        translation_output_frame.rowconfigure(0, weight=1)
        
        self.translation_output_text = scrolledtext.ScrolledText(
            translation_output_frame, 
            height=10, 
            wrap=tk.WORD,
            font=("Arial", 11),
            state=tk.DISABLED
        )
        self.translation_output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def setup_settings_tab(self):
        """Setup the settings tab with OCR configuration"""
        main_frame = ttk.Frame(self.settings_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Application Settings", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # OCR Settings Frame
        ocr_frame = ttk.LabelFrame(main_frame, text="OCR Settings", padding="10")
        ocr_frame.pack(fill=tk.X, pady=(0, 20))
        
        # OCR Model Status
        model_status_frame = ttk.Frame(ocr_frame)
        model_status_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(model_status_frame, text="OCR Model Status:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.ocr_status_var = tk.StringVar(value="Initializing..." if self.manga_ocr else "Not Available")
        ocr_status_label = ttk.Label(model_status_frame, textvariable=self.ocr_status_var, 
                                    foreground="green" if self.manga_ocr else "red")
        ocr_status_label.pack(anchor=tk.W)
        
        # OCR Controls
        controls_frame = ttk.Frame(ocr_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        reload_ocr_btn = ttk.Button(controls_frame, text="🔄 Reload OCR Model", 
                                   command=self.reload_ocr_model)
        reload_ocr_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        test_ocr_btn = ttk.Button(controls_frame, text="🧪 Test OCR", 
                                 command=self.test_ocr)
        test_ocr_btn.pack(side=tk.LEFT)
        
        # Information Section
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        info_text = """Japanese OCR & Translation Tool\n\nWorkflow:\n1. Select screen region containing Japanese text\n2. Extract and process OCR text (automatic post-processing)\n3. Translate processed text to English\n\nFeatures:\n• Single-tab interface focused on OCR workflow\n• Handles both vertical manga and horizontal game text\n• Advanced OCR post-processing for clean output\n• Copy processed text and translations to clipboard"""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)
        
        # About Section
        about_frame = ttk.LabelFrame(main_frame, text="About", padding="10")
        about_frame.pack(fill=tk.X)
        
        about_text = "Japanese Text Translator v1.0\nBuilt with MangaOCR and Ollama translation"
        about_label = ttk.Label(about_frame, text=about_text, justify=tk.CENTER)
        about_label.pack()
        
    # Translation methods (same as original)
    def paste_text(self):
        """Paste text from clipboard"""
        try:
            clipboard_content = pyperclip.paste()
            if clipboard_content.strip():
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(tk.END, clipboard_content)
                self.status_var.set(f"Pasted {len(clipboard_content)} characters from clipboard")
            else:
                self.status_var.set("Clipboard is empty")
        except Exception as e:
            messagebox.showerror("Error", f"Could not paste from clipboard: {str(e)}")
            
    def start_translation(self):
        """Start translation in a separate thread"""
        input_text = self.input_text.get(1.0, tk.END).strip()
        
        if not input_text:
            messagebox.showwarning("Warning", "Please enter some Japanese text to translate.")
            return
            
        # Disable translate button during processing
        self.translate_btn.config(state=tk.DISABLED)
        self.status_var.set("Translating...")
        
        # Start translation in a separate thread
        thread = threading.Thread(target=self.perform_translation, args=(input_text, False))
        thread.daemon = True
        thread.start()
        
    def perform_translation(self, text_to_translate, from_ocr=False):
        """Perform the actual translation using Ollama"""
        try:
            # Prepare the prompt for the translator model
            prompt = f"""Translate the following Japanese text to English. 
            Only return the English translation without any additional commentary or explanation:

            {text_to_translate}"""
            
            # Call the Ollama model
            response = ollama.chat(
                model='lauchacarro/qwen2.5-translator:latest',
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            # Extract the translated text
            if hasattr(response, 'message'):
                translated_text = response.message.content.strip()
            else:
                translated_text = response['message']['content'].strip()
            
            # Update the UI in the main thread
            if from_ocr:
                self.root.after(0, self.update_ocr_translation_result, translated_text)
            else:
                self.root.after(0, self.update_translation_result, translated_text)
            
        except Exception as e:
            error_msg = f"Translation failed: {str(e)}"
            print(error_msg)
            if from_ocr:
                self.root.after(0, self.ocr_translation_error, str(e))
            else:
                self.root.after(0, self.translation_error, str(e))
                
    # New OCR methods
    def select_ocr_region(self):
        """Interactive region selection overlay"""
        # Create fullscreen overlay window
        self.root.withdraw()  # Hide main window
        
        overlay = tk.Tk()
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-alpha', 0.3)
        overlay.configure(bg='black')
        overlay.title("Select OCR Region")
        overlay.config(cursor="crosshair")
        
        # Variables to track selection
        start_x = start_y = None
        end_x = end_y = None
        rect = None
        
        # Create canvas
        canvas = tk.Canvas(overlay, bg='black', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        canvas.create_text(
            overlay.winfo_screenwidth() // 2,
            50,
            text="Click and drag to select OCR region\nRelease mouse to confirm | Press ESC to cancel",
            fill='white',
            font=('Arial', 16, 'bold')
        )
        
        def on_click(event):
            nonlocal start_x, start_y, rect
            start_x = event.x
            start_y = event.y
            if rect:
                canvas.delete(rect)
        
        def on_drag(event):
            nonlocal end_x, end_y, rect
            if rect:
                canvas.delete(rect)
            
            end_x = event.x
            end_y = event.y
            
            # Draw rectangle
            rect = canvas.create_rectangle(
                start_x, start_y, end_x, end_y,
                outline='red', width=2, fill='red', stipple='gray25'
            )
            
            # Show size info
            width = abs(end_x - start_x)
            height = abs(end_y - start_y)
            if width > 10 and height > 10:
                canvas.create_text(
                    start_x + width//2, start_y - 20,
                    text=f"{width}×{height} pixels",
                    fill='white', font=('Arial', 10, 'bold'),
                    tags='size_info'
                )
        
        def on_release(event):
            nonlocal rect
            if start_x is not None and end_x is not None:
                # Normalize coordinates
                x1, x2 = sorted([start_x, end_x])
                y1, y2 = sorted([start_y, end_y])
                
                region = (x1, y1, x2 - x1, y2 - y1)
                self.last_region = region
                
                # Visual confirmation
                if rect:
                    canvas.delete(rect)
                    rect = canvas.create_rectangle(
                        x1, y1, x2, y2,
                        outline='lime', width=3, fill='lime', stipple='gray25'
                    )
                    canvas.create_text(
                        x1 + (x2-x1)//2, y1 + (y2-y1)//2,
                        text="REGION SELECTED!\nClick anywhere or press Enter to confirm",
                        fill='white', font=('Arial', 12, 'bold'),
                        justify='center'
                    )
                
                # Update UI and close overlay
                self.root.after(0, self.update_region_display, region)
                overlay.after(300, lambda: close_overlay(region))
        
        def close_overlay(region):
            overlay.destroy()
            self.root.deiconify()  # Show main window
            self.status_var.set(f"Region selected: {region}")
        
        def cancel(event=None):
            overlay.destroy()
            self.root.deiconify()
            self.status_var.set("Region selection cancelled")
        
        def confirm(event=None):
            if self.last_region:
                close_overlay(self.last_region)
            else:
                print("No region selected yet. Please click and drag to select a region.")
        
        # Bind events
        canvas.bind("<Button-1>", on_click)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        overlay.bind("<Escape>", cancel)
        overlay.bind("<Return>", confirm)
        
        # Start the overlay
        overlay.mainloop()
        
    def update_region_display(self, region):
        """Update the region display in the UI"""
        self.region_var.set(f"X:{region[0]}, Y:{region[1]}, W:{region[2]}, H:{region[3]}")
        
    def perform_ocr(self):
        """Extract OCR from selected region and display processed text"""
        if not self.last_region:
            messagebox.showwarning("Warning", "Please select an OCR region first.")
            return
            
        if not self.manga_ocr:
            messagebox.showerror("Error", "OCR model not available. Check settings.")
            return
            
        self.status_var.set("Extracting and processing OCR...")
        
        # Run OCR in separate thread
        thread = threading.Thread(target=self._run_ocr_extraction)
        thread.daemon = True
        thread.start()
        
    def _run_ocr_extraction(self):
        """Run OCR extraction and processing in background thread"""
        try:
            processed_text = self.extract_japanese_text(self.last_region)
            self.root.after(0, self.update_ocr_output, processed_text)
        except Exception as e:
            self.root.after(0, self.ocr_extraction_error, str(e))
            
    def update_ocr_output(self, processed_text):
        """Update OCR output with processed text"""
        self.ocr_output_text.delete(1.0, tk.END)
        self.ocr_output_text.insert(tk.END, processed_text)
        self.status_var.set(f"OCR extracted and processed: {len(processed_text)} characters")
        
    def translate_ocr_text(self):
        """Translate the processed OCR text to English"""
        processed_text = self.ocr_output_text.get(1.0, tk.END).strip()
        
        if not processed_text:
            messagebox.showwarning("Warning", "No OCR text available to translate.")
            return
            
        if processed_text.startswith("OCR Error:") or processed_text.startswith("No text detected"):
            messagebox.showwarning("Warning", "Cannot translate error message or empty text.")
            return
            
        self.status_var.set("Translating processed OCR text...")
        
        # Run translation in separate thread
        thread = threading.Thread(target=self._run_ocr_translation, args=(processed_text,))
        thread.daemon = True
        thread.start()
        
    def _run_ocr_translation(self, text_to_translate):
        """Run OCR text translation in background thread"""
        try:
            # Prepare translation prompt
            prompt = f"""Translate the following Japanese text to English. 
            Only return the English translation without any additional commentary:

            {text_to_translate}"""
            
            # Call Ollama translation model
            response = ollama.chat(
                model='lauchacarro/qwen2.5-translator:latest',
                messages=[{'role': 'user', 'content': prompt}]
            )
            
            # Extract translated text
            if hasattr(response, 'message'):
                translated_text = response.message.content.strip()
            else:
                translated_text = response['message']['content'].strip()
            
            self.root.after(0, self.update_translation_output, translated_text)
            
        except Exception as e:
            self.root.after(0, self.translation_error, str(e))
            
    def update_translation_output(self, translated_text):
        """Update translation output with English text"""
        self.translation_output_text.config(state=tk.NORMAL)
        self.translation_output_text.delete(1.0, tk.END)
        self.translation_output_text.insert(tk.END, translated_text)
        self.translation_output_text.config(state=tk.DISABLED)
        self.status_var.set(f"Translation completed ({len(translated_text)} characters)")
        
    def ocr_extraction_error(self, error_message):
        """Handle OCR extraction errors"""
        self.ocr_output_text.delete(1.0, tk.END)
        self.ocr_output_text.insert(tk.END, f"OCR Error: {error_message}")
        self.status_var.set(f"OCR extraction failed: {error_message}")
        
    def translation_error(self, error_message):
        """Handle translation errors"""
        self.translation_output_text.config(state=tk.NORMAL)
        self.translation_output_text.delete(1.0, tk.END)
        self.translation_output_text.insert(tk.END, f"Translation Error: {error_message}")
        self.translation_output_text.config(state=tk.DISABLED)
        self.status_var.set(f"Translation failed: {error_message}")
        
    def copy_ocr_text(self):
        """Copy processed OCR text to clipboard"""
        text = self.ocr_output_text.get(1.0, tk.END).strip()
        if text and not text.startswith("OCR Error"):
            pyperclip.copy(text)
            self.status_var.set("OCR text copied to clipboard")
        else:
            self.status_var.set("No OCR text to copy")
            
    def copy_translation_text(self):
        """Copy English translation to clipboard"""
        text = self.translation_output_text.get(1.0, tk.END).strip()
        if text and not text.startswith("Translation Error"):
            pyperclip.copy(text)
            self.status_var.set("Translation copied to clipboard")
        else:
            self.status_var.set("No translation to copy")
            
    def clear_all_text(self):
        """Clear all text areas"""
        self.ocr_output_text.delete(1.0, tk.END)
        self.translation_output_text.config(state=tk.NORMAL)
        self.translation_output_text.delete(1.0, tk.END)
        self.translation_output_text.config(state=tk.DISABLED)
        self.status_var.set("All text cleared")
        
    # Settings methods
    def reload_ocr_model(self):
        """Reload the OCR model"""
        self.status_var.set("Reloading OCR model...")
        self.ocr_status_var.set("Reloading...")
        
        def reload_thread():
            try:
                self.manga_ocr = MangaOcr()
                self.root.after(0, lambda: self.ocr_status_var.set("Ready"))
                self.root.after(0, lambda: self.status_var.set("OCR model reloaded successfully"))
            except Exception as e:
                self.root.after(0, lambda: self.ocr_status_var.set("Failed"))
                self.root.after(0, lambda: self.status_var.set(f"Failed to reload OCR: {str(e)}"))
                
        thread = threading.Thread(target=reload_thread)
        thread.daemon = True
        thread.start()
        
    def test_ocr(self):
        """Test OCR functionality with a small region"""
        if not self.manga_ocr:
            messagebox.showerror("Error", "OCR model not available.")
            return
            
        # Test with a small region (top-left corner)
        test_region = (100, 100, 200, 50)
        self.status_var.set("Testing OCR...")
        
        def test_thread():
            try:
                text = self.extract_japanese_text(test_region)
                self.root.after(0, lambda: messagebox.showinfo("OCR Test", 
                    f"OCR Test Result:\nRegion: {test_region}\nText: '{text[:100]}{'...' if len(text) > 100 else ''}'"))
                self.root.after(0, lambda: self.status_var.set("OCR test completed"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("OCR Test Failed", str(e)))
                self.root.after(0, lambda: self.status_var.set("OCR test failed"))
                
        thread = threading.Thread(target=test_thread)
        thread.daemon = True
        thread.start()
        
    # Original translation methods (modified for tabbed interface)
    def update_translation_result(self, translated_text):
        """Update the output text widget with the translation result"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, translated_text)
        self.output_text.config(state=tk.DISABLED)
        
        self.translate_btn.config(state=tk.NORMAL)
        self.status_var.set(f"Translation completed successfully ({len(translated_text)} characters)")
    
    def translation_error(self, error_message):
        """Handle translation errors"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Translation Error: {error_message}")
        self.output_text.config(state=tk.DISABLED)
        
        self.translate_btn.config(state=tk.NORMAL)
        self.status_var.set(f"Translation failed: {error_message}")
        
    def clear_text(self):
        """Clear both input and output text areas"""
        self.input_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.status_var.set("Cleared translation text")

def main():
    root = tk.Tk()
    app = ScreenTranslatorApp(root)
    
    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()