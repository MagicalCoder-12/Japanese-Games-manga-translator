@echo off
setlocal

echo Starting OCR Text Extractor...
echo.

REM Activate conda environment
CALL conda activate screen-translator

REM Check if activation was successful
if errorlevel 1 (
    echo Error: Failed to activate conda environment 'screen-translator'
    echo Please make sure the environment exists and conda is in your PATH
    echo.
    echo You can create the environment with: conda env create -f environment.yml
    pause
    exit /b 1
)

echo Conda environment activated successfully.
echo.

REM Run the application
python ocr_launcher.py

pause