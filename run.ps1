Clear-Host
Write-Host "Starting Mediguard Backend Server... `n`n"

# 1. Run Migrations (Assuming uv is used for managing commands)
Write-Host "Running Database Migrations..."
uv run manage.py makemigrations
uv run manage.py migrate

Write-Host "`nMigrations complete. Starting Server..."

# 2. Start the main server (This command blocks and keeps the tab open)
uv run manage.py runserver