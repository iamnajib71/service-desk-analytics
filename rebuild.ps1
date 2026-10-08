param([string]$Python = 'python', [switch]$InstallOnly)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (!(Test-Path '.venv/Scripts/python.exe')) {
    & $Python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 from python.org, then rerun. Virtual environment creation failed.' }
}
& .venv/Scripts/python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
if (!$InstallOnly) {
    & .venv/Scripts/python.exe scripts/build.py
    if ($LASTEXITCODE -ne 0) { throw 'Pipeline failed.' }
}
