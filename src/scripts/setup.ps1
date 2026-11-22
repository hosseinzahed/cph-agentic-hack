# Setup for CPH Agentic Hack (Windows PowerShell). Run from the repository root:
#   .\src\scripts\setup.ps1
$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

Write-Host "==> 1/4 Creating virtual environment in .venv" -ForegroundColor Cyan
if (-not (Test-Path ".venv")) {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { py -3 -m venv .venv } else { python -m venv .venv }
}
$python = Join-Path $root ".venv\Scripts\python.exe"
& $python -c "import sys; assert sys.version_info >= (3, 11), f'Python 3.11+ required, found {sys.version}'"
if ($LASTEXITCODE -ne 0) { throw "Python 3.11 or later is required." }

Write-Host "==> 2/4 Installing dependencies" -ForegroundColor Cyan
& $python -m pip install --upgrade pip --quiet
& $python -m pip install -e ".[dev]" --quiet
if ($LASTEXITCODE -ne 0) { throw "pip install failed (check your proxy settings, see README Troubleshooting)." }

Write-Host "==> 3/4 Downloading the Copilot SDK runtime (optional)" -ForegroundColor Cyan
& $python -m copilot download-runtime
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Could not download the Copilot runtime now. The SDK will retry on first use. The app still works without it."
}

Write-Host "==> 4/4 Seeding the SQLite database with synthetic data" -ForegroundColor Cyan
& $python src\backend\scripts\seed.py
if ($LASTEXITCODE -ne 0) { throw "Seeding failed." }

Write-Host ""
Write-Host "Done! Next steps:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python src\scripts\check_env.py"
Write-Host "  uvicorn backend.app.main:app --app-dir src --reload"
Write-Host "  then open http://localhost:8000"
