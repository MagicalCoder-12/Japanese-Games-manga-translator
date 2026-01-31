@echo off
title Japanese Text Translator
echo Starting Japanese Text Translator...
echo.

REM Activate conda environment if available
call conda activate screen-translator 2>nul
if errorlevel 1 (
    echo Warning: Could not activate screen-translator environment
    echo Make sure you have the required packages installed
    echo.
)

REM Run the main application
python run_app.py

pause