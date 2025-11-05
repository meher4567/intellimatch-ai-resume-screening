# 🎨 IntelliMatch AI - Frontend Startup Script
# This script starts the React development server

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  IntelliMatch AI - Starting Frontend Server" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if frontend directory exists
if (Test-Path ".\frontend") {
    Write-Host "✓ Frontend directory found" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "✗ Frontend directory not found!" -ForegroundColor Red
    Write-Host "  Expected path: .\frontend" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Navigate to frontend
Set-Location .\frontend

# Check if node_modules exists
if (Test-Path ".\node_modules") {
    Write-Host "✓ Node modules found" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "⚠  Node modules not found" -ForegroundColor Yellow
    Write-Host "  Installing dependencies..." -ForegroundColor Cyan
    Write-Host ""
    npm install
    Write-Host ""
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        Write-Host ""
        Set-Location ..
        exit 1
    }
    
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
    Write-Host ""
}

# Display information
Write-Host "📋 Frontend Information:" -ForegroundColor Cyan
Write-Host "  • Frontend URL: http://localhost:5173" -ForegroundColor White
Write-Host "  • Alternative: http://localhost:3000" -ForegroundColor White
Write-Host "  • Backend API: http://localhost:8000" -ForegroundColor White
Write-Host ""

Write-Host "🎯 Quick Tips:" -ForegroundColor Cyan
Write-Host "  • Press Ctrl+C to stop the server" -ForegroundColor White
Write-Host "  • Make sure backend is running first!" -ForegroundColor White
Write-Host "  • Browser will open automatically" -ForegroundColor White
Write-Host ""

Write-Host "⚠  Important:" -ForegroundColor Yellow
Write-Host "  Backend server must be running on port 8000" -ForegroundColor White
Write-Host "  If not running, open another terminal and run:" -ForegroundColor White
Write-Host "    .\start_backend.ps1" -ForegroundColor Cyan
Write-Host ""

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Starting React development server..." -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Start the development server
npm run dev

# If server exits
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Frontend server stopped" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan

# Return to root directory
Set-Location ..
