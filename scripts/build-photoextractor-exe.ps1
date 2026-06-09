$ErrorActionPreference = "Stop"

Write-Host "Building PhotoExtractor.exe (optimized)..." -ForegroundColor Cyan

$RepoRoot = Resolve-Path "$PSScriptRoot\.."
$PhotoExtractorRoot = Resolve-Path "$RepoRoot\..\PhotoExtractor"

Set-Location $PhotoExtractorRoot

# Evita vazar PYTHONPATH do albumai-studio/backend para o PyInstaller
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue

if (!(Test-Path ".venv")) {
  Write-Host "Creating virtual environment..." -ForegroundColor Yellow
  python -m venv .venv
}

$Python = Join-Path $PhotoExtractorRoot ".venv\Scripts\python.exe"

Write-Host "Upgrading pip..." -ForegroundColor Yellow
& $Python -m pip install --upgrade pip --quiet

Write-Host "Installing dependencies..." -ForegroundColor Yellow
& $Python -m pip install -r requirements.txt --quiet
& $Python -m pip install pyinstaller --quiet

Write-Host "Cleaning old builds..." -ForegroundColor Yellow
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force PhotoExtractor.spec -ErrorAction SilentlyContinue

Write-Host "Building with PyInstaller (--onedir, optimized)..." -ForegroundColor Yellow

& $Python -m PyInstaller `
  --onedir `
  --name PhotoExtractor `
  --console `
  --clean `
  --noconfirm `
  --copy-metadata transformers `
  --copy-metadata torch `
  --copy-metadata torchvision `
  --copy-metadata tokenizers `
  --copy-metadata safetensors `
  --copy-metadata huggingface-hub `
  --collect-submodules transformers.models.grounding_dino `
  --collect-submodules transformers.models.bert `
  --collect-submodules transformers.models.auto `
  --collect-data transformers `
  --exclude-module tensorflow `
  --exclude-module keras `
  --exclude-module flax `
  --exclude-module jax `
  --exclude-module jaxlib `
  --exclude-module torchaudio `
  --exclude-module tensorboard `
  --exclude-module pytest `
  --exclude-module IPython `
  --exclude-module notebook `
  --exclude-module pandas `
  --exclude-module numpy.tests `
  --exclude-module scipy.tests `
  --exclude-module matplotlib.tests `
  --exclude-module transformers.cli `
  --exclude-module transformers.testing_utils `
  main.py

Write-Host ""
Write-Host "✅ EXE gerado em:" -ForegroundColor Green
Write-Host "$PhotoExtractorRoot\dist\PhotoExtractor\PhotoExtractor.exe" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para usar:" -ForegroundColor Cyan
Write-Host ".\dist\PhotoExtractor\PhotoExtractor.exe --help" -ForegroundColor White
Write-Host ".\dist\PhotoExtractor\PhotoExtractor.exe --input input --output output --device cpu" -ForegroundColor White

