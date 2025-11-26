param(
    [switch]$hostDjango,
    [string]$Port = "5432",
    [string]$DjangoPort = "2005"
)

#region Script Initialization
$ErrorActionPreference = "Stop"
$script:Config = @{
    Root = Split-Path -Parent $MyInvocation.MyCommand.Path
    DBnginBasePath = Join-Path $env:LOCALAPPDATA "com.tinyapp.DBngin"
    PostgresPort = $Port
    DjangoPort = $DjangoPort
    LogsDir = "z_logs"
}

Set-Location $script:Config.Root

# Activate virtual environment
$venvActivate = Join-Path $script:Config.Root "venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
}
#endregion

#region Logging Functions
function Get-LogFilePath {
    param([string]$Prefix = "postgres")
    
    $sessionId = Get-Date -Format "yyyy_MM_dd__HH_mm_ss"
    $logDir = Join-Path $script:Config.Root $script:Config.LogsDir
    $logFile = Join-Path $logDir "${Prefix}_${sessionId}.log"
    
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    return $logFile
}

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("Info", "Warning", "Error")]
        [string]$Level = "Info"
    )
    
    $color = switch ($Level) {
        "Info" { "White" }
        "Warning" { "Yellow" }
        "Error" { "Red" }
    }
    
    Write-Host "[$Level] $Message" -ForegroundColor $color
}
#endregion

#region PostgreSQL Functions
function Get-PostgreSQLPaths {
    $binariesPath = Join-Path $script:Config.DBnginBasePath "Binaries\postgresql"
    
    if (-not (Test-Path $binariesPath)) {
        throw "DBngin PostgreSQL binaries not found at $binariesPath"
    }
    
    $latestVersion = Get-ChildItem -Path $binariesPath -Directory |
                     Sort-Object Name -Descending |
                     Select-Object -First 1
    
    if (-not $latestVersion) {
        throw "No PostgreSQL versions found"
    }
    
    return @{
        Version = $latestVersion.Name
        BinPath = Join-Path $latestVersion.FullName "bin"
        ExePath = Join-Path $latestVersion.FullName "bin\postgres.exe"
    }
}

function Get-ProcessUsingPort {
    param([string]$Port)
    
    $netstat = netstat -ano | Select-String ":$Port\s" | Select-Object -First 1
    if ($netstat) {
        $processId = ($netstat -split '\s+')[-1]
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        return $process
    }
    return $null
}

function Start-PostgreSQL {
    param([string]$Port = $script:Config.PostgresPort)
    
    try {
        $paths = Get-PostgreSQLPaths
        $logFile = Get-LogFilePath
        
        # Add binaries to PATH
        $env:PATH = "$($paths.BinPath);$env:PATH"
        
        Write-Log "Starting PostgreSQL $($paths.Version) on port $Port" -Level Info
        Write-Log "Session log: $logFile" -Level Info
        
        # Start PostgreSQL - redirect stderr to stdout by using 2>&1 in the command
        $process = Start-Process -FilePath $paths.ExePath `
                      -ArgumentList "-p $Port" `
                      -RedirectStandardOutput $logFile `
                      -NoNewWindow `
                      -PassThru
        
        # Wait a moment to see if it starts
        Start-Sleep -Seconds 2
        
        if ($process.HasExited) {
            throw "PostgreSQL failed to start. Check log: $logFile"
        }
        
        Write-Log "PostgreSQL started successfully (PID: $($process.Id))" -Level Info
        return $true
    }
    catch {
        Write-Log "Failed to start PostgreSQL: $_" -Level Error
        
        # Check if port is in use
        $blockingProcess = Get-ProcessUsingPort -Port $Port
        
        if ($blockingProcess) {
            Write-Log "Port $Port is being used by: $($blockingProcess.ProcessName) (PID: $($blockingProcess.Id))" -Level Warning
            
            $response = Read-Host "Do you want to kill this process and retry? (Y/N)"
            
            if ($response -eq 'Y' -or $response -eq 'y') {
                try {
                    Stop-Process -Id $blockingProcess.Id -Force
                    Write-Log "Process killed. Retrying..." -Level Info
                    Start-Sleep -Seconds 1
                    
                    # Retry starting PostgreSQL
                    return Start-PostgreSQL -Port $Port
                }
                catch {
                    Write-Log "Failed to kill process: $_" -Level Error
                    return $false
                }
            }
            else {
                Write-Log "User chose not to kill the blocking process" -Level Info
                return $false
            }
        }
        
        return $false
    }
}

#region Network Functions
function Get-LocalIPAddress {
    $ip = Get-NetIPAddress -AddressFamily IPv4 `
                           -InterfaceAlias "Wi-Fi", "Ethernet" `
                           -ErrorAction SilentlyContinue |
          Where-Object { $_.IPAddress -notlike "169.254.*" -and $_.IPAddress -ne "127.0.0.1" } |
          Select-Object -ExpandProperty IPAddress -First 1
    
    return $ip
}
#endregion

#region Django Functions
function Start-DjangoServer {
    param([switch]$EnableNetworkAccess)
    
    if ($EnableNetworkAccess) {
        $localIP = Get-LocalIPAddress
        $serverUrl = "http://${localIP}:$($script:Config.DjangoPort)"
        
        Write-Host @"

╔════════════════════════════════════════════════════════╗
║  Django Server Starting (Network Accessible)          ║
╠════════════════════════════════════════════════════════╣
║  Network URL: $serverUrl
║  Local URL:   http://127.0.0.1:$($script:Config.DjangoPort)
╚════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan
        
        $command = "uv run manage.py runserver ${localIP}:$($script:Config.DjangoPort)"
    }
    else {
        Write-Host @"

╔════════════════════════════════════════════════════════╗
║  Django Server Starting (Local Only)                  ║
╠════════════════════════════════════════════════════════╣
║  Local URL: http://127.0.0.1:$($script:Config.DjangoPort)
╚════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan
        
        $command = "uv run manage.py runserver $($script:Config.DjangoPort)"
    }
    
    Invoke-Expression $command
}
#endregion

#region Main Execution
function Start-Application {
    param([switch]$HostDjango)
    
    Write-Log "Starting MediGuard Backend..." -Level Info
    
    # Start PostgreSQL
    if (-not (Start-PostgreSQL)) {
        Write-Log "PostgreSQL failed to start. Exiting." -Level Error
        exit 1
    }
    
    # Start Django server
    Start-DjangoServer -EnableNetworkAccess:$HostDjango
}

# Execute main function
Start-Application -HostDjango:$hostDjango
#endregion