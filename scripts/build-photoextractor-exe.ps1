$ErrorActionPreference = "Stop"

Write-Host "Building PhotoExtractor.exe..." -ForegroundColor Cyan

$Root = Resolve-Path "..\PhotoExtractor"
Set-Location $Root

if (!(Test-Path ".venv")) {
  python -m venv .venv
}

.\.venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

pyinstaller `
  --onefile `
  --name PhotoExtractor `
  --console `
  --collect-all transformers `
  --collect-all torch `
  --collect-all PIL `
  --collect-all numpy `
  main.py

Write-Host ""
Write-Host "EXE gerado em:" -ForegroundColor Green
Write-Host "$Root\dist\PhotoExtractor.exe" -ForegroundColor Yellow
