$script:Config = @{
    # DBngin Paths (Confirmed)
    PgBin  = "C:\Users\HELIOS\AppData\Local\com.tinyapp.DBngin\Binaries\postgresql\17.0\bin"
    PgData = "C:\Users\HELIOS\AppData\Local\com.tinyapp.DBngin\Engines\postgresql\ee5e2771-ee32-4fd4-970d-73f66b566356"
}

# Add the bin directory to the Path
$env:Path += ";$($script:Config.PgBin)"

Write-Host "Starting PostgreSQL server..."

$pgCtlPath = Join-Path -Path $script:Config.PgBin -ChildPath "pg_ctl.exe"

# --- FIX 1: Correctly expand the variable inside the string for 'start' command ---
# We use $() to force evaluation of the complex property access before the string is passed.
Start-Process -FilePath $pgCtlPath -ArgumentList "-D $($script:Config.PgData) start" -NoNewWindow 

Write-Host "PostgreSQL server started. Verifying status..."

# Give it a moment to change state
Start-Sleep -Seconds 2

# --- FIX 2: Correctly expand the variable for 'status' command ---
# Use the call operator (&) and ensure the variable is expanded correctly.
# The path should be quoted in case of spaces, which is handled here:
& $pgCtlPath -D "$($script:Config.PgData)" status

Write-Host "------------------------------------------------------------------"
Write-Host "PostgreSQL is running (or status is reported above). DO NOT CLOSE THIS TAB to ensure server stability."

# Blocking command to keep the tab open (from the previous suggestion)
Read-Host -Prompt "Press Enter to manually close this tab (This will NOT stop the server)"