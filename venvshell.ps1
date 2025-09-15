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

function br {
    param([int]$Count = 1)
    for ($i = 0; $i -lt $Count; $i++) {
        Write-Host ""
    }
}

# ================ Main Script ==================

Write-Host "================= Activating Virtual Environment ================"
br

$cwd = Get-Location
Write-Info "Current working directory: $cwd"

# Check if the virtual environment directory exists
if (-not (Test-Path "$cwd/.venv")) {
    Write-Warning "Virtual environment not found. Creating one..."
    Write-Info "Running 'uv venv' to create virtual environment..."
    
    try {
        uv venv
        if (-not (Test-Path "$cwd/.venv")) {
            throw "Virtual environment directory was not created"
        }
        Write-Success "Virtual environment created successfully!"
        br
    }
    catch {
        Write-Error "Failed to create virtual environment: $($_.Exception.Message)"
        Write-Error "Please run setup.ps1 first or check if UV is properly installed."
        exit 1
    }
} else {
    Write-Info "Virtual environment found. Proceeding to activate..."
}

# Check if activation script exists
$activateScript = "$cwd/.venv/Scripts/Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Error "Activation script not found at: $activateScript"
    Write-Error "The virtual environment may be corrupted. Try deleting .venv folder and run setup.ps1 again."
    exit 1
}

# Activate the virtual environment using dot-sourcing
Write-Info "Activating virtual environment..."
try {
    # Use dot-sourcing to run the script in the current scope
    . $activateScript
    
    # Verify activation by checking if VIRTUAL_ENV is set
    if ($env:VIRTUAL_ENV) {
        Write-Success "Virtual environment activated successfully!"
        Write-Info "Virtual environment path: $env:VIRTUAL_ENV"
        
        # Show Python path to confirm we're using the virtual environment
        $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
        if ($pythonPath) {
            Write-Info "Using Python from: $pythonPath"
        }
    } else {
        throw "VIRTUAL_ENV environment variable not set after activation"
    }
}
catch {
    Write-Error "Failed to activate virtual environment: $($_.Exception.Message)"
    Write-Warning "Try running this manually: .\.venv\Scripts\Activate.ps1"
    Write-Warning "Or delete the .venv folder and run again"
    exit 1
}

br
Write-Success "Environment is ready! You can now run Python commands."
Write-Info "Example: python manage.py runserver"
Write-Host ""