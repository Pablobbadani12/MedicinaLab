param(
    [string]$Port = "8000"
)

Write-Host "Iniciando Django en 0.0.0.0:$Port ..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe manage.py runserver "0.0.0.0:$Port"
