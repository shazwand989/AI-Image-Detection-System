# Flask Application Startup Script

Write-Host "🚀 Starting AI Image Detection Flask Application..." -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "⚠️  Virtual environment not found!" -ForegroundColor Yellow
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "Please copy .env.example to .env and configure it" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Run: copy .env.example .env" -ForegroundColor Cyan
    Write-Host ""
    exit
}

# Install/update dependencies
Write-Host "📦 Checking dependencies..." -ForegroundColor Cyan
pip install -q -r requirements.txt

Write-Host ""
Write-Host "✅ Dependencies ready" -ForegroundColor Green
Write-Host ""

# Run the application
Write-Host "🌐 Starting Flask server..." -ForegroundColor Cyan
Write-Host "📍 Server will be available at: http://localhost:4000" -ForegroundColor Green
Write-Host "🛑 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python server.py
