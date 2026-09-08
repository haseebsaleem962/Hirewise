# Start Backend
Write-Host "=== HireWise - Backend ===" -ForegroundColor Cyan
Set-Location -Path (Join-Path $PSScriptRoot "backend")

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check if model exists, train if not
$modelPath = Join-Path $PSScriptRoot "backend\ml\models\resume_classifier.pkl"
if (-not (Test-Path $modelPath)) {
    Write-Host "ML model not found. Training..." -ForegroundColor Yellow
    python train_model.py
}

# Start Flask
Write-Host "Starting Flask server on port 5000..." -ForegroundColor Green
python app.py
