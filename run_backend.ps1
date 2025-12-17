# This script launches all Mediguard components in separate Windows Terminal tabs 
# within the existing Windows Terminal window (using -w 0).

# --- Core Function to Execute Commands in a New WT Tab ---
function Run-wt {
    param (
        [Parameter(Mandatory=$true)][string]$Title,
        [Parameter(Mandatory=$true)][string]$Cwd,
        [Parameter(Mandatory=$true)][string]$ScriptFile # Path to the .ps1 script to run
    )

    Write-Host "--- Opening tab for: $Title ---"

    # Use Start-Process to launch wt without blocking the script's execution.
    # Arguments:
    # -w 0 new-tab: Use existing window, open new tab
    # -d $Cwd: Set the starting directory
    # --title $Title: Set the tab title
    # pwsh -NoExit -c: Use PowerShell, keep the tab open after script, execute the command string
    # The command string executes the specified script file.
    Start-Process wt -ArgumentList "-w 0 new-tab -d `"$Cwd`" --title `"$Title`" pwsh -NoExit -c ""`"./$ScriptFile`"`""
}


$script:Paths = @{
    # Use dedicated keys for better organization
    Backend = "D:\college_projects\mediguard_backend"
    Socket  = "D:\college_projects\mediguard_socket"
}

# 1. Launch PostgreSQL Server (New dedicated tab)
# The run_db.ps1 script is in the backend directory.
Run-wt -Title "PostgreSQL Server" -Cwd $script:Paths.Backend -ScriptFile "run_db.ps1"
Start-Sleep -Seconds 3 # Give the database time to start before migrations

# 2. Launch Backend Server (New tab)
# The backend run script is called run.ps1
Run-wt -Title "mediguard_backend" -Cwd $script:Paths.Backend -ScriptFile "run.ps1"

# 3. Launch Socket Server (New tab)
# The socket run script is called run.ps1
Run-wt -Title "mediguard_socket" -Cwd $script:Paths.Socket -ScriptFile "run.ps1"

Write-Host "`nAll three Mediguard components have been launched in new tabs."