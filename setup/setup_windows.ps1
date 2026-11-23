$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
Set-Location $RootDir

function Find-Python {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @("py", "-3")
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        return @("python")
    }
    else {
        throw "Python 3 was not found. Please install Python 3 first."
    }
}

$PythonCmd = Find-Python

Write-Host "[1/4] Creating virtual environment at $RootDir\.venv"
if ($PythonCmd.Count -eq 2) {
    & $PythonCmd[0] $PythonCmd[1] -m venv .venv
}
else {
    & $PythonCmd[0] -m venv .venv
}

$VenvPython = Join-Path $RootDir ".venv\Scripts\python.exe"

Write-Host "[2/4] Upgrading pip"
& $VenvPython -m pip install --upgrade pip setuptools wheel

Write-Host "[3/4] Installing required packages (GPU preferred, CPU fallback)"
& $VenvPython scripts\install_dependencies.py

Write-Host "[4/4] Checking environment"
& $VenvPython scripts\check_environment.py

Write-Host ""
Write-Host "Setup complete."
Write-Host "Activate the environment with:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "Then launch Jupyter with:"
Write-Host "  jupyter lab"
