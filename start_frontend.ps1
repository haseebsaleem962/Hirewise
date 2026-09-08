# Start Frontend
Write-Host "=== HireWise - Frontend ===" -ForegroundColor Cyan
Set-Location -Path (Join-Path $PSScriptRoot "frontend")

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Node dependencies..." -ForegroundColor Yellow
    npm install
}

# Start Next.js dev server
Write-Host "Starting Next.js dev server on port 3000..." -ForegroundColor Green
npm run dev
