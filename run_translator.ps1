# Japanese Text Translator Launcher
Write-Host "Starting Japanese Text Translator..." -ForegroundColor Green
Write-Host ""

# Try to activate conda environment
try {
    conda activate screen-translator 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Activated screen-translator environment" -ForegroundColor Green
    } else {
        Write-Host "Warning: Could not activate screen-translator environment" -ForegroundColor Yellow
        Write-Host "Make sure you have the required packages installed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Warning: Conda not found or environment activation failed" -ForegroundColor Yellow
    Write-Host "Make sure you have the required packages installed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Launching application..." -ForegroundColor Cyan

# Run the main application
python run_app.py

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")