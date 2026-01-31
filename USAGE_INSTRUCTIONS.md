# Japanese to English Translator - Usage Instructions

## Overview
This application provides a simple GUI interface to translate Japanese text to English using the Ollama API and the `lauchacarro/qwen2.5-translator:latest` model.

## Prerequisites
- Python 3.8 or higher
- Ollama installed and running
- The `lauchacarro/qwen2.5-translator:latest` model downloaded

## Installation Steps

### 1. Install Ollama
- Download and install Ollama from [ollama.com](https://ollama.com/)
- Start the Ollama service

### 2. Download the Required Model
Run the following command to download the translator model:
```bash
ollama pull lauchacarro/qwen2.5-translator:latest
```

### 3. Set Up the Python Environment
You have two options:

#### Option A: Using Conda (Recommended)
```bash
# Create and activate the environment
conda env create -f environment.yml
conda activate txt_translator

# Run the application
python run_app.py
```

#### Option B: Using pip
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python run_app.py
```

### 4. Alternative Setup Method
You can also run the setup script which will guide you through the process:
```bash
python setup.py
```

## Running the Application

### Method 1: Python Script
```bash
python run_app.py
```

### Method 2: Batch File (Windows)
Double-click on `run_translator.bat` or run:
```bash
run_translator.bat
```

### Method 3: PowerShell (Windows)
```powershell
.\run_translator.ps1
```

## Application Features

1. **Input Area**: Large text box for entering or pasting Japanese text
2. **Paste Button**: Click to paste text from clipboard (or use Ctrl+V)
3. **Translate Button**: Initiates the translation process
4. **Output Area**: Displays the English translation
5. **Clear Button**: Clears both input and output text areas
6. **Status Bar**: Shows current status and operation results

## How to Use

1. Open the application
2. Enter Japanese text in the top text area, or use the "📋 Paste Text" button (or Ctrl+V) to paste from clipboard
3. Click the "🔄 Translate" button to start the translation
4. Wait for the translation to complete (status bar will show progress)
5. View the English translation in the bottom text area
6. Use "🗑️ Clear" to clear both text areas if needed

## Troubleshooting

### Common Issues:

1. **Model not found error**: Make sure you have pulled the correct model:
   ```bash
   ollama pull lauchacarro/qwen2.5-translator:latest
   ```

2. **Ollama not accessible**: Ensure Ollama service is running

3. **Dependency errors**: Make sure you're running in the correct Python environment

4. **Application freezes**: The UI runs in a separate thread during translation, but large texts may take time to process

### Testing Ollama Connection:
Run the test script to verify everything works:
```bash
python test_ollama.py
```

## Technical Details

- Uses the Ollama Python library to communicate with the local Ollama server
- Employs threading to prevent UI freezing during translation
- Uses tkinter for the graphical interface
- Automatically handles Japanese character encoding
- Provides real-time status updates

## Customization

The application can be easily modified to support other language pairs by changing the prompt in the `perform_translation` method of the `ScreenTranslatorApp` class.

## Files Included

- `translator_app.py`: Main application code
- `run_app.py`: Launcher script with dependency checks
- `setup.py`: Interactive setup script
- `test_ollama.py`: Connectivity and model availability tester
- `environment.yml`: Conda environment specification
- `requirements.txt`: Python package requirements
- `run_translator.bat`: Windows batch file to run the application
- `run_translator.ps1`: Windows PowerShell script to run the application
- `README.md`: General project information
- `USAGE_INSTRUCTIONS.md`: This file