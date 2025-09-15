param(
    [switch]$Help,
    [switch]$NoAlias,
    [switch]$AliasOnly,
    [switch]$Verbose
)

# Script configuration
$script:noAlias = $NoAlias
$script:aliasOnly = $AliasOnly
$script:verbose = $Verbose

# Help function
function Show-Help {
    Write-Host "Usage: .\venvshell.ps1 [-Help] [-NoAlias] [-AliasOnly] [-Verbose]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Help       Show this help message"
    Write-Host "  -NoAlias    Skip alias creation"
    Write-Host "  -AliasOnly  Only create aliases, skip venv activation"
    Write-Host "  -Verbose    Enable verbose output"
    Write-Host ""
    Write-Host "This script activates the MediGuard backend virtual environment and sets up useful aliases."
    Write-Host ""
    Write-Host "Available aliases after activation:"
    Write-Host "  py <command>           - Run Python command via uv"
    Write-Host "  dj <command> [args]    - Run Django management commands"
    Write-Host "  createsu               - Create Django superuser"
    Write-Host "  makemig                - Make migrations and migrate"
    Write-Host ""
    Write-Host "Django command examples:"
    Write-Host "  dj runserver           - Start development server"
    Write-Host "  dj migrate             - Run migrations"
    Write-Host "  dj makemigrations      - Create new migrations"
    Write-Host "  dj startapp myapp      - Create new Django app"
    Write-Host "  dj test                - Run tests"
    Write-Host "  dj collectstatic       - Collect static files"
    Write-Host "  dj shell               - Open Django shell"
    Write-Host ""
}

# Check for help option
if ($Help) {
    Show-Help
    exit 0
}

# Optimized color output functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [ValidateSet("White", "Cyan", "Green", "Yellow", "Red")]
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Info { param([string]$Message) Write-ColorOutput "[INFO] $Message" "Cyan" }
function Write-Success { param([string]$Message) Write-ColorOutput "[SUCCESS] $Message" "Green" }
function Write-Warning { param([string]$Message) Write-ColorOutput "[WARNING] $Message" "Yellow" }
function Write-Error { param([string]$Message) Write-ColorOutput "[ERROR] $Message" "Red" }
function Write-Verbose { param([string]$Message) if ($script:verbose) { Write-ColorOutput "[VERBOSE] $Message" "Gray" } }

function Write-Break { param([int]$Count = 1) 1..$Count | ForEach-Object { Write-Host "" } }

# Function to set up all aliases and functions in global scope
function Set-ProjectAliases {
    Write-Verbose "Setting up project aliases and functions..."
    
    # Define the Django management function in global scope
    $global:_djFunction = {
        param(
            [Parameter(Mandatory=$true, Position=0)]
            [string]$Command,
            
            [Parameter(ValueFromRemainingArguments=$true)]
            [string[]]$Arguments
        )
        
        # Construct the full command
        $fullCommand = "uv run manage.py $Command"
        if ($Arguments) {
            $fullCommand += " " + ($Arguments -join " ")
        }
        
        if ($script:verbose) {
            Write-Host "[VERBOSE] Executing: $fullCommand" -ForegroundColor Gray
        }
        
        # Execute the command
        try {
            Invoke-Expression $fullCommand
        }
        catch {
            Write-Host "[ERROR] Failed to execute Django command: $($_.Exception.Message)" -ForegroundColor Red
            return $false
        }
        return $true
    }
    
    # Define makemig function in global scope
    $global:_makemigFunction = {
        param(
            [Parameter(ValueFromRemainingArguments=$true)]
            [string[]]$Arguments
        )
        
        Write-Host "[INFO] Running makemigrations..." -ForegroundColor Cyan
        if (& $global:_djFunction "makemigrations" @Arguments) {
            Write-Host "[INFO] Running migrate..." -ForegroundColor Cyan
            & $global:_djFunction "migrate"
        } else {
            Write-Host "[ERROR] Makemigrations failed, skipping migrate" -ForegroundColor Red
        }
    }
    
    # Define createsu function in global scope
    $global:_createsuFunction = {
        & $global:_djFunction "createsuperuser"
    }
    
    # Create global functions
    Set-Item -Path "function:global:_dj" -Value $global:_djFunction -Force
    Set-Item -Path "function:global:_makemig" -Value $global:_makemigFunction -Force
    Set-Item -Path "function:global:_createsu" -Value $global:_createsuFunction -Force
    
    # Core aliases
    Set-Alias -Name py -Value "uv run" -Scope Global -Force
    Set-Alias -Name dj -Value _dj -Scope Global -Force
    
    # Convenience aliases
    Set-Alias -Name createsu -Value _createsu -Scope Global -Force
    Set-Alias -Name makemig -Value _makemig -Scope Global -Force
    
    Write-Success "Aliases and functions created successfully!"
    Write-Info "Available commands: py, dj, createsu, makemig"
}

# Function to activate virtual environment
function Start-VirtualEnvironment {
    $cwd = Get-Location
    Write-Info "Current working directory: $cwd"
    
    # Check if virtual environment exists
    $venvPath = Join-Path $cwd ".venv"
    if (-not (Test-Path $venvPath)) {
        Write-Warning "Virtual environment not found. Creating one..."
        Write-Info "Running 'uv venv' to create virtual environment..."
        
        try {
            & uv venv
            if (-not (Test-Path $venvPath)) {
                throw "Virtual environment directory was not created"
            }
            Write-Success "Virtual environment created successfully!"
            Write-Break
        }
        catch {
            Write-Error "Failed to create virtual environment: $($_.Exception.Message)"
            Write-Error "Please ensure UV is properly installed and accessible."
            return $false
        }
    } else {
        Write-Verbose "Virtual environment found at: $venvPath"
    }
    
    # Activate virtual environment
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    if (-not (Test-Path $activateScript)) {
        Write-Error "Activation script not found at: $activateScript"
        Write-Error "The virtual environment may be corrupted. Try deleting .venv folder and run again."
        return $false
    }
    
    Write-Info "Activating virtual environment..."
    try {
        . $activateScript
        
        # Verify activation
        if (-not $env:VIRTUAL_ENV) {
            throw "VIRTUAL_ENV environment variable not set after activation"
        }
        
        Write-Success "Virtual environment activated successfully!"
        Write-Info "Virtual environment path: $env:VIRTUAL_ENV"
        
        # Show Python path
        $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
        if ($pythonPath) {
            Write-Verbose "Using Python from: $pythonPath"
        }
        
        return $true
    }
    catch {
        Write-Error "Failed to activate virtual environment: $($_.Exception.Message)"
        Write-Warning "Try running manually: $activateScript"
        return $false
    }
}

# ================ Main Script Execution ==================

Write-Host "================= MediGuard Backend Environment ================" -ForegroundColor Magenta
Write-Break

# Handle alias-only mode
if ($script:aliasOnly) {
    Write-Info "Running in alias-only mode..."
    Set-ProjectAliases
    Write-Break
    Write-Success "Aliases set up successfully! Virtual environment activation skipped."
    exit 0
}

# Activate virtual environment
if (Start-VirtualEnvironment) {
    Write-Break
    Write-Success "Environment is ready!"
    
    # Set up aliases unless disabled
    if (-not $script:noAlias) {
        Set-ProjectAliases
        Write-Break
        Write-Info "Quick start examples:"
        Write-Host "  dj runserver           # Start development server"
        Write-Host "  dj migrate             # Run database migrations" 
        Write-Host "  makemig                # Create and apply migrations"
        Write-Host "  createsu               # Create superuser"
        Write-Host "  py --version           # Check Python version"
    }
} else {
    Write-Error "Failed to set up environment. Please check the errors above."
    exit 1
}

Write-Break
Write-Host "Happy coding! 🚀" -ForegroundColor Green