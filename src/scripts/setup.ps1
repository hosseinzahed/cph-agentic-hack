# Setup for CPH Agentic Hack (Windows PowerShell 5.1 or PowerShell 7). Run from the repository root:
#   .\src\scripts\setup.ps1
# If scripts are blocked: powershell -ExecutionPolicy Bypass -File .\src\scripts\setup.ps1

# Native tools (pip, python) write warnings to stderr; check exit codes explicitly instead.
$ErrorActionPreference = "Continue"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $root
$python = Join-Path $root ".venv\Scripts\python.exe"

function Fail($message) {
    Write-Host "ERROR: $message" -ForegroundColor Red
    exit 1
}

# An existing .venv is reused only if it has Python 3.11+ and a working pip.
function Test-Venv {
    if (-not (Test-Path $python)) { return $false }
    & $python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { return $false }
    & $python -m pip --version 2>&1 | Out-Null
    return ($LASTEXITCODE -eq 0)
}

# Pick the first Python 3.11+ (the py launcher first, then python on PATH).
function Find-Python {
    $candidates = @(@("py", "-3.13"), @("py", "-3.12"), @("py", "-3.11"), @("python"), @("python3"))
    foreach ($candidate in $candidates) {
        $exe = $candidate[0]
        $extra = @($candidate | Select-Object -Skip 1)
        if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
        & $exe @extra -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { return , $candidate }
    }
    return $null
}

Write-Host "==> 1/4 Creating virtual environment in .venv" -ForegroundColor Cyan
if (-not (Test-Venv)) {
    if (Test-Path ".venv") {
        Write-Host "    Existing .venv is broken or uses Python < 3.11: recreating it."
        Remove-Item -Recurse -Force ".venv"
    }
    $base = Find-Python
    if (-not $base) { Fail "Python 3.11+ not found. Install it from python.org (tick 'Add to PATH') and rerun." }
    $exe = $base[0]
    $extra = @($base | Select-Object -Skip 1)
    & $exe @extra -m venv .venv
    if ($LASTEXITCODE -ne 0) { Fail "Could not create .venv." }
}

Write-Host "==> 2/4 Installing dependencies" -ForegroundColor Cyan
& $python -m pip install --upgrade pip --quiet
& $python -m pip install -e ".[dev]" --quiet
if ($LASTEXITCODE -ne 0) { Fail "pip install failed (check your proxy settings, see README Troubleshooting)." }

Write-Host "==> 3/4 Downloading the Copilot SDK runtime (optional)" -ForegroundColor Cyan
& $python -m copilot download-runtime
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Could not download the Copilot runtime now. The SDK will retry on first use. The app still works without it."
}

Write-Host "==> 4/4 Seeding the SQLite database with synthetic data" -ForegroundColor Cyan
& $python src\backend\scripts\seed.py
if ($LASTEXITCODE -ne 0) { Fail "Seeding failed." }

Write-Host ""
Write-Host "Done! Next steps:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python src\scripts\check_env.py"
Write-Host "  uvicorn backend.app.main:app --app-dir src --reload"
Write-Host "  then open http://localhost:8000"
