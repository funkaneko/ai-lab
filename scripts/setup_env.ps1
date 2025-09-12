Param()
$ErrorActionPreference = 'Stop'

python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
if (-not (Test-Path .env) -and (Test-Path .env.example)) { Copy-Item .env.example .env }
Write-Host "`n✅ Environment ready. Activate with: . .\.venv\Scripts\Activate.ps1"
