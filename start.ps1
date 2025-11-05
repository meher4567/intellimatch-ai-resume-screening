# 🚀 IntelliMatch AI - Master Startup Script
# This script provides options to start backend, frontend, or both

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  IntelliMatch AI - Master Control Panel" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "What would you like to do?" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Start Backend Only (Port 8000)" -ForegroundColor White
Write-Host "  2. Start Frontend Only (Port 5173)" -ForegroundColor White
Write-Host "  3. Test Backend API" -ForegroundColor White
Write-Host "  4. Open API Documentation" -ForegroundColor White
Write-Host "  5. View Quick Commands" -ForegroundColor White
Write-Host "  6. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting Backend Server..." -ForegroundColor Green
        Write-Host ""
        .\start_backend.ps1
    }
    "2" {
        Write-Host ""
        Write-Host "Starting Frontend Server..." -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠  Make sure backend is running in another terminal!" -ForegroundColor Yellow
        Write-Host ""
        .\start_frontend.ps1
    }
    "3" {
        Write-Host ""
        Write-Host "Testing Backend API..." -ForegroundColor Green
        Write-Host ""
        
        # Activate venv and run test
        if (Test-Path ".\.venv\Scripts\Activate.ps1") {
            & .\.venv\Scripts\Activate.ps1
            python test_integration.py
        } else {
            Write-Host "✗ Virtual environment not found!" -ForegroundColor Red
            Write-Host ""
        }
    }
    "4" {
        Write-Host ""
        Write-Host "Opening API Documentation..." -ForegroundColor Green
        Write-Host ""
        Start-Process "http://localhost:8000/docs"
        Write-Host "✓ Browser opened to http://localhost:8000/docs" -ForegroundColor Green
        Write-Host ""
        Write-Host "If page doesn't load, make sure backend is running:" -ForegroundColor Yellow
        Write-Host "  .\start_backend.ps1" -ForegroundColor Cyan
        Write-Host ""
    }
    "5" {
        Write-Host ""
        if (Test-Path ".\QUICK_COMMANDS.md") {
            Get-Content ".\QUICK_COMMANDS.md"
        } else {
            Write-Host "Quick Commands:" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Start Backend:" -ForegroundColor Yellow
            Write-Host "  .\start_backend.ps1" -ForegroundColor White
            Write-Host ""
            Write-Host "Start Frontend:" -ForegroundColor Yellow
            Write-Host "  cd frontend; npm run dev" -ForegroundColor White
            Write-Host ""
            Write-Host "Test API:" -ForegroundColor Yellow
            Write-Host "  python test_integration.py" -ForegroundColor White
            Write-Host ""
        }
    }
    "6" {
        Write-Host ""
        Write-Host "Goodbye! 👋" -ForegroundColor Green
        Write-Host ""
        exit 0
    }
    default {
        Write-Host ""
        Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
        Write-Host ""
        exit 1
    }
}
