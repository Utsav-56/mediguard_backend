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
    param([string]$Prefix = "pg_db")
    
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
        DataPath = Join-Path $script:Config.DBnginBasePath "Data\postgresql\$($latestVersion.Name)"
        ExePath = Join-Path $latestVersion.FullName "bin\postgres.exe"
    }
}

function Test-PostgreSQLRunning {
    param([string]$Port = $script:Config.PostgresPort)
    
    # Test port connectivity
    $tcpTest = Test-NetConnection -ComputerName "localhost" -Port $Port -WarningAction SilentlyContinue -InformationAction SilentlyContinue 
    
    Start-Sleep -Milliseconds 200

    if (-not $tcpTest.TcpTestSucceeded) {
        Write-Log "Port $Port is not in use" -Level Info
        return $false
    }
    
    # Verify it's the correct PostgreSQL instance
    try {
        $paths = Get-PostgreSQLPaths
        $runningProcesses = Get-Process -Name postgres -ErrorAction SilentlyContinue
        
        foreach ($proc in $runningProcesses) {
            try {
                $procPath = (Get-Process -Id $proc.Id -FileVersionInfo).FileName
                if ($procPath -eq $paths.ExePath) {
                    $customLogDir = Join-Path $script:Config.Root $script:Config.LogsDir
                    Write-Log "PostgreSQL $($paths.Version) is running on port $Port" -Level Info
                    Write-Log "Session logs: $customLogDir" -Level Info
                    
                    return $true
                }
            } catch { continue }
        }
        
        Write-Log "Port $Port is in use by another process" -Level Warning
        return $false
    }
    catch {
        Write-Log "Error checking PostgreSQL status: $_" -Level Error
        return $false
    }
}

function Start-PostgreSQL {
    param([string]$Port = $script:Config.PostgresPort)
    
    try {
        $paths = Get-PostgreSQLPaths
        $logFile = Get-LogFilePath -Prefix "postgres"
        
        if (-not (Test-Path $paths.DataPath)) {
            throw "Data directory not found at $($paths.DataPath)"
        }
        
        # Add binaries to PATH
        $env:PATH = "$($paths.BinPath);$env:PATH"
        
        Write-Log "Starting PostgreSQL $($paths.Version)" -Level Info
        Write-Log "Port: $Port | Session log: $logFile" -Level Info
        
        # Start PostgreSQL with stdout/stderr redirected to custom log location
        Start-Process -FilePath $paths.ExePath `
                      -ArgumentList "-D `"$($paths.DataPath)`" -p $Port" `
                      -RedirectStandardOutput $logFile `
                      -RedirectStandardError $logFile `
                      -NoNewWindow
        
        Write-Log "PostgreSQL started successfully" -Level Info
        Write-Log "All logs are being written to: $(Join-Path $script:Config.Root $script:Config.LogsDir)" -Level Info
        
        return $true
    }
    catch {
        Write-Log "Failed to start PostgreSQL: $_" -Level Error
        return $false
    }
}
#endregion

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
    
    # Ensure PostgreSQL is running
    if (-not (Test-PostgreSQLRunning)) {
        Write-Log "Starting PostgreSQL server..." -Level Info
        
        if (Start-PostgreSQL) {
            Start-Sleep -Seconds 3  # Brief wait for server initialization
        }
        else {
            Write-Log "PostgreSQL failed to start. Exiting." -Level Error
            exit 1
        }
    }
    
    # Start Django server
    Start-DjangoServer -EnableNetworkAccess:$HostDjango
}

# Execute main function
Start-Application -HostDjango:$hostDjango
#endregion