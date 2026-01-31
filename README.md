# Japanese Text Translator

A comprehensive Japanese to English translation tool with integrated OCR capabilities for extracting text from games, manga, and other applications.

## Features

- **Manual Translation**: Paste Japanese text for translation
- **Screen OCR**: Extract Japanese text from any screen region
- **Automatic Translation**: Direct translation of OCR-extracted text
- **Tabbed Interface**: Clean, organized user interface
- **Cross-platform Support**: Works with both vertical manga text and horizontal game text
- **Clipboard Integration**: Easy copy/paste functionality

## Installation

### Prerequisites
- Python 3.8+
- Conda environment (recommended)

### Setup

1. **Create and activate conda environment**:
```bash
conda env create -f environment.yml
conda activate screen-translator
```

2. **Or install dependencies manually**:
```bash
pip install -r requirements.txt
```

### Required Dependencies
- `manga-ocr` - For Japanese text recognition
- `ollama` - For translation (using qwen2.5-translator model)
- `pyautogui` - For screen capture
- `opencv-python` - For image processing
- `pyperclip` - For clipboard operations
- `Pillow` - For image handling

## Usage

### Quick Start
1. Run the application:
   - **Windows**: Double-click `run_translator.bat` or `run_translator.ps1`
   - **Command line**: `python run_app.py`

2. The application will start with three tabs:
   - **📝 Translation**: Manual text translation
   - **🔍 OCR**: Screen text extraction
   - **⚙️ Settings**: Configuration and testing

### Manual Translation
1. Switch to the "Translation" tab
2. Paste Japanese text using:
   - Ctrl+V shortcut
   - "Paste Text" button
3. Click "Translate" to get English translation

### Screen OCR
1. Switch to the "OCR" tab
2. Click "Select OCR Region" to define capture area
3. Choose one of these options:
   - **Capture & OCR**: Extract text from selected region
   - **OCR + Translate**: Extract and translate in one step
4. Use copy buttons to save results to clipboard

### Settings
- Reload OCR model if needed
- Test OCR functionality
- View application information

## Project Structure

```
txt_translator/
├── translator_app.py      # Main application (tabbed interface)
├── run_app.py            # Application launcher with dependency checking
├── run_translator.bat    # Windows batch launcher
├── run_translator.ps1    # Windows PowerShell launcher
├── requirements.txt      # Python dependencies
├── environment.yml       # Conda environment specification
└── README.md            # This file
```

## Key Improvements

### Removed Features
- ❌ Game adaptive region memory (as requested)
- ❌ Complex hotkey system
- ❌ Multiple launcher scripts

### Added Features
- ✅ Integrated tabbed interface
- ✅ Simplified OCR region selection
- ✅ Direct OCR-to-translation workflow
- ✅ Unified application launcher
- ✅ Better error handling and user feedback

## OCR Capabilities

The application uses MangaOCR which:
- Handles both **vertical Japanese text** (manga) and **horizontal text** (games)
- Preserves Japanese punctuation and formatting
- Removes common OCR artifacts while maintaining text structure
- Works with various font styles and sizes

## Translation

Uses Ollama with the `lauchacarro/qwen2.5-translator` model for:
- Accurate Japanese to English translation
- Context-aware translations
- Clean output without additional commentary

## Troubleshooting

### Common Issues

1. **OCR not working**:
   - Check that MangaOCR is properly installed
   - Verify the model is loaded in Settings tab
   - Test with the "Test OCR" button

2. **Translation failing**:
   - Ensure Ollama is running
   - Check that the translation model is available
   - Verify internet connection if using online models

3. **Region selection issues**:
   - Make sure to click and drag (not just click)
   - Release mouse button to confirm selection
   - Press ESC to cancel selection

### Dependencies Check
Run the launcher script - it will automatically check for missing dependencies and provide installation instructions.

## Development

### Adding New Features
The modular structure makes it easy to extend:
- Add new tabs to the notebook interface
- Extend OCR capabilities in the `extract_japanese_text` method
- Add new translation models in the `perform_translation` method

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.