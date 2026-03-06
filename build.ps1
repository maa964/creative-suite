# build.ps1 - Creative Suite build script
# Usage: .\build.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== Creative Suite Build ===" -ForegroundColor Cyan

# 1. Install dependencies
Write-Host "`n[1/4] Installing dependencies..." -ForegroundColor Yellow
poetry install
if ($LASTEXITCODE -ne 0) { Write-Error "poetry install failed"; exit 1 }

# 2. Run tests
Write-Host "`n[2/4] Running tests..." -ForegroundColor Yellow
poetry run python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) { Write-Error "Tests failed"; exit 1 }

# 3. Lint (optional - runs if ruff is available)
Write-Host "`n[3/4] Linting..." -ForegroundColor Yellow
try {
    $ruffVersion = poetry run python -m ruff --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        poetry run python -m ruff check apps/ launcher/ server/ engine/
        if ($LASTEXITCODE -ne 0) { Write-Warning "Lint warnings found" }
    }
    else {
        Write-Host "  ruff not installed, skipping lint" -ForegroundColor DarkGray
    }
}
catch {
    Write-Host "  ruff check encountered an error, skipping lint" -ForegroundColor DarkGray
}

# 4. Build package
Write-Host "`n[4/4] Building package..." -ForegroundColor Yellow
# Check if package-mode is false in pyproject.toml
$isNonPackage = Select-String -Path "pyproject.toml" -Pattern "package-mode\s*=\s*false"
if ($isNonPackage) {
    Write-Host "  package-mode is false, skipping poetry build" -ForegroundColor DarkGray
}
else {
    poetry build
    if ($LASTEXITCODE -ne 0) { Write-Error "Build failed"; exit 1 }
}

# 5. Build Executable with PyInstaller
Write-Host "`n[5/6] Building Executable with PyInstaller..." -ForegroundColor Yellow
poetry run pyinstaller --noconfirm --onedir --windowed --name "launcher" "launcher/main.py"
if ($LASTEXITCODE -ne 0) { Write-Warning "PyInstaller build failed or PyInstaller not installed properly" }

# 6. Build Installer with Inno Setup
Write-Host "`n[6/6] Building Installer with Inno Setup..." -ForegroundColor Yellow
$ISCC_Path = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (Test-Path $ISCC_Path) {
    & $ISCC_Path "installer.iss"
    if ($LASTEXITCODE -ne 0) { Write-Warning "Inno Setup compilation failed" }
} else {
    Write-Host "  Inno Setup (ISCC.exe) not found at $ISCC_Path, skipping installer build" -ForegroundColor DarkGray
}

Write-Host "`n=== Build complete ===" -ForegroundColor Green
