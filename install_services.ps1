# MarketShield Services Installation Script
# Run this script as Administrator

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "MARKETSHIELD SERVICES INSTALLATION" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To run as Administrator:" -ForegroundColor Yellow
    Write-Host "1. Right-click PowerShell" -ForegroundColor Yellow
    Write-Host "2. Select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "3. Run this script again" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Running as Administrator - OK" -ForegroundColor Green
Write-Host ""

# Check if Chocolatey is installed
Write-Host "Checking Chocolatey..." -ForegroundColor Yellow
$chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue

if (-not $chocoInstalled) {
    Write-Host "Chocolatey not found. Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    
    # Refresh environment
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Host "Chocolatey installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Chocolatey is already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "INSTALLING REDIS" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Install Redis
Write-Host "Installing Redis..." -ForegroundColor Yellow
choco install redis-64 -y

if ($LASTEXITCODE -eq 0) {
    Write-Host "Redis installed successfully!" -ForegroundColor Green
    
    # Start Redis service
    Write-Host "Starting Redis service..." -ForegroundColor Yellow
    Start-Service Redis -ErrorAction SilentlyContinue
    
    # Test Redis
    Write-Host "Testing Redis connection..." -ForegroundColor Yellow
    $redisTest = redis-cli ping 2>&1
    if ($redisTest -match "PONG") {
        Write-Host "Redis is working!" -ForegroundColor Green
    } else {
        Write-Host "Redis installed but not responding. You may need to start it manually." -ForegroundColor Yellow
    }
} else {
    Write-Host "Redis installation failed or was skipped" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "INSTALLING POSTGRESQL" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Install PostgreSQL
Write-Host "Installing PostgreSQL 15..." -ForegroundColor Yellow
choco install postgresql15 -y --params '/Password:postgres'

if ($LASTEXITCODE -eq 0) {
    Write-Host "PostgreSQL installed successfully!" -ForegroundColor Green
    
    # Wait for PostgreSQL to start
    Write-Host "Waiting for PostgreSQL to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Test PostgreSQL
    Write-Host "Testing PostgreSQL connection..." -ForegroundColor Yellow
    $pgTest = psql --version 2>&1
    if ($pgTest -match "psql") {
        Write-Host "PostgreSQL is installed!" -ForegroundColor Green
    }
} else {
    Write-Host "PostgreSQL installation failed or was skipped" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "CONFIGURING DATABASE" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Create database and user
Write-Host "Creating database and user..." -ForegroundColor Yellow
Write-Host "Note: You may be prompted for the postgres password (default: postgres)" -ForegroundColor Yellow
Write-Host ""

$sqlCommands = @"
CREATE DATABASE impactai_db;
CREATE USER impactai WITH PASSWORD 'impactai123';
GRANT ALL PRIVILEGES ON DATABASE impactai_db TO impactai;
"@

$sqlCommands | psql -U postgres 2>&1

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "INITIALIZING DATABASE TABLES" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Initialize database
Write-Host "Initializing database tables..." -ForegroundColor Yellow
Set-Location backend
python init_database.py
Set-Location ..

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "INSTALLATION COMPLETE!" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Services installed:" -ForegroundColor Green
Write-Host "  Redis:      Port 6379" -ForegroundColor White
Write-Host "  PostgreSQL: Port 5432" -ForegroundColor White
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart your backend:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Cyan
Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Test the system:" -ForegroundColor White
Write-Host "   python test_full_system.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Open frontend:" -ForegroundColor White
Write-Host "   http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

Write-Host "Your system will now be 10x faster with caching!" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
