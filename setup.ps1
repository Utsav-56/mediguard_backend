# MediGuard Backend Automated Setup Script (Windows PowerShell)
# This script automatically installs Python, UV, and sets up the MediGuard backend

param(
    [switch]$SkipAdminCheck,
    [switch]$Help
)

# Color functions for better output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "[INFO] $Message" "Cyan"
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" "Green"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" "Yellow"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" "Red"
}

# Function to check if running as administrator
function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to check if a command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to check if Winget is available
function Test-Winget {
    if (Test-Command "winget") {
        Write-Success "Winget is available"
        return $true
    } else {
        Write-Warning "Winget is not available"
        return $false
    }
}

# Function to install Python using Winget
function Install-Python {
    Write-Info "Installing Python using Winget..."
    
    try {
        if (Test-Winget) {
            winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements
            Write-Success "Python installed successfully!"
            
            # Refresh environment variables
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            
            return $true
        } else {
            Write-Error "Winget is not available. Please install Python manually from python.org"
            return $false
        }
    }
    catch {
        Write-Error "Failed to install Python: $($_.Exception.Message)"
        return $false
    }
}

# Function to install UV
function Install-UV {
    Write-Info "Installing UV (Python dependency manager)..."
    
    try {
        # Use the official UV installation script
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        
        # Add UV to PATH for current session
        $uvPath = "$env:USERPROFILE\.cargo\bin"
        if (Test-Path $uvPath) {
            $env:PATH += ";$uvPath"
        }
        
        Write-Success "UV installed successfully!"
        return $true
    }
    catch {
        Write-Error "Failed to install UV: $($_.Exception.Message)"
        return $false
    }
}

# Function to check Python installation
function Test-Python {
    $pythonCommands = @("python", "py")
    
    foreach ($cmd in $pythonCommands) {
        if (Test-Command $cmd) {
            try {
                $version = & $cmd --version 2>&1
                if ($version -match "Python (\d+)\.(\d+)") {
                    $major = [int]$matches[1]
                    $minor = [int]$matches[2]
                    
                    if ($major -eq 3 -and $minor -ge 10) {
                        Write-Success "Python $($matches[0]) is already installed and compatible"
                        return $true
                    } else {
                        Write-Warning "Python $($matches[0]) is installed but version 3.10+ is recommended"
                    }
                }
            }
            catch {
                continue
            }
        }
    }
    
    Write-Warning "Python 3.10+ is not installed or not found in PATH"
    return $false
}

# Function to check UV installation
function Test-UV {
    if (Test-Command "uv") {
        Write-Success "UV is already installed"
        return $true
    } else {
        # Check if UV is in the typical installation location
        $uvPath = "$env:USERPROFILE\.cargo\bin\uv.exe"
        if (Test-Path $uvPath) {
            $env:PATH += ";$([System.IO.Path]::GetDirectoryName($uvPath))"
            Write-Success "UV found and added to PATH"
            return $true
        }
        
        Write-Warning "UV is not installed"
        return $false
    }
}

# Function to show help
function Show-Help {
    Write-Host ""
    Write-ColorOutput "MediGuard Backend Setup Script" "Cyan"
    Write-Host ""
    Write-Host "This script automatically installs Python, UV, and sets up the MediGuard backend."
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\setup.ps1                    # Run normal setup"
    Write-Host "  .\setup.ps1 -SkipAdminCheck   # Skip administrator check"
    Write-Host "  .\setup.ps1 -Help             # Show this help"
    Write-Host ""
    Write-Host "Note: Administrator privileges are recommended for installing Python via Winget."
    Write-Host ""
}

# Main setup function
function Start-Setup {
    Write-Host ""
    Write-ColorOutput "================================" "Cyan"
    Write-ColorOutput "  MediGuard Backend Setup" "Cyan"
    Write-ColorOutput "================================" "Cyan"
    Write-Host ""
    
    # Check if running as administrator (unless skipped)
    if (-not $SkipAdminCheck -and -not (Test-Admin)) {
        Write-Warning "This script is not running as Administrator."
        Write-Host "Some installations may fail without administrator privileges."
        Write-Host ""
        $response = Read-Host "Do you want to continue anyway? (y/N)"
        if ($response -notmatch "^[Yy]") {
            Write-Host "Please run PowerShell as Administrator and try again."
            exit 1
        }
    }
    
    # Check and install Python
    if (-not (Test-Python)) {
        if (-not (Install-Python)) {
            Write-Error "Python installation failed. Please install Python manually."
            exit 1
        }
    }
    
    # Check and install UV
    if (-not (Test-UV)) {
        if (-not (Install-UV)) {
            Write-Error "UV installation failed. Please install UV manually."
            exit 1
        }
    }
    
    # Ensure we're in the correct directory
    if (-not (Test-Path "manage.py")) {
        Write-Error "manage.py not found. Please run this script from the MediGuard backend directory."
        exit 1
    }
    
    Write-Info "Setting up virtual environment and dependencies..."
    
    # Sync dependencies with UV
    try {
        uv sync
        Write-Success "Dependencies installed successfully!"
    }
    catch {
        Write-Error "Failed to install dependencies: $($_.Exception.Message)"
        Write-Host "You may need to restart your terminal and try again."
        exit 1
    }
    
    Write-Success "Setup completed successfully!"
    Write-Host ""
    Write-ColorOutput "🎉 MediGuard backend is ready!" "Green"
    Write-Host ""
    Write-Host "To start the development server, run:"
    Write-ColorOutput "  uv run manage.py runserver" "Yellow"
    Write-Host ""
    Write-Host "Or activate the virtual environment and run:"
    Write-ColorOutput "  .\.venv\Scripts\Activate.ps1" "Yellow"
    Write-ColorOutput "  python manage.py runserver" "Yellow"
    Write-Host ""
    Write-Host "Then visit: http://127.0.0.1:8000/"
    Write-Host ""
}

# Script entry point
if ($Help) {
    Show-Help
    exit 0
}

# Check execution policy
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted") {
    Write-Warning "PowerShell execution policy is set to Restricted."
    Write-Host "You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    Write-Host "Or run this script with: powershell -ExecutionPolicy Bypass -File setup.ps1"
    Write-Host ""
}

# Run the main setup
Start-Setup