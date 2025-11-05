# 🚀 IntelliMatch AI - Startup Script
# This script starts the backend server

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  IntelliMatch AI - Starting Backend Server" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    
    # Activate virtual environment
    Write-Host "  Activating virtual environment..." -ForegroundColor Cyan
    & .\.venv\Scripts\Activate.ps1
    
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host "  Please create it with: python -m venv .venv" -ForegroundColor Yellow
    Write-Host "  Then install dependencies: pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if main.py exists
if (Test-Path ".\src\api\main.py") {
    Write-Host "✓ API main.py found" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "✗ API main.py not found!" -ForegroundColor Red
    Write-Host "  Expected path: .\src\api\main.py" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Display information
Write-Host "📋 Server Information:" -ForegroundColor Cyan
Write-Host "  • Backend URL: http://localhost:8000" -ForegroundColor White
Write-Host "  • API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  • ReDoc: http://localhost:8000/redoc" -ForegroundColor White
Write-Host "  • Health Check: http://localhost:8000/health" -ForegroundColor White
Write-Host ""

Write-Host "🎯 Quick Tips:" -ForegroundColor Cyan
Write-Host "  • Press Ctrl+C to stop the server" -ForegroundColor White
Write-Host "  • Test API: python test_integration.py" -ForegroundColor White
Write-Host "  • View logs: Check console output below" -ForegroundColor White
Write-Host ""

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Starting server..." -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
python src\api\main.py

# If server exits
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Server stopped" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
