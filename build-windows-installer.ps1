# Windows Installer Build Script for NeuroInsight
# Run this on a Windows machine with PowerShell

Write-Host "=== NeuroInsight Windows Installer Build Script ===" -ForegroundColor Green
Write-Host "This script builds the complete Windows installer package" -ForegroundColor Yellow
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>$null
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check Git (for Git LFS)
try {
    $gitVersion = git --version 2>$null
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git not found. Please install Git" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Building NeuroInsight Windows Installer..." -ForegroundColor Green

# Step 1: Install Python dependencies
Write-Host "Step 1: Installing Python dependencies..." -ForegroundColor Yellow
pip install -r desktop_alone/requirements.txt
pip install pyinstaller requests
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python dependencies installed" -ForegroundColor Green

# Step 2: Build Python backend
Write-Host "Step 2: Building Python backend executable..." -ForegroundColor Yellow
Set-Location desktop_alone
pyinstaller build.spec --clean --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build backend" -ForegroundColor Red
    exit 1
}

# Verify backend was built
if (Test-Path "dist/neuroinsight-backend/neuroinsight-backend.exe") {
    $backendSize = (Get-Item "dist/neuroinsight-backend/neuroinsight-backend.exe").Length / 1MB
    Write-Host "✅ Backend built successfully: $($backendSize.ToString("F1")) MB" -ForegroundColor Green
} else {
    Write-Host "❌ Backend executable not found" -ForegroundColor Red
    exit 1
}

# Step 3: Verify frontend exists
Write-Host "Step 3: Verifying frontend..." -ForegroundColor Yellow
if (Test-Path "frontend/index.html") {
    Write-Host "✅ Frontend found" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend not found" -ForegroundColor Red
    exit 1
}

# Step 4: Install Electron dependencies
Write-Host "Step 4: Installing Electron dependencies..." -ForegroundColor Yellow
Set-Location electron-app
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Electron dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Electron dependencies installed" -ForegroundColor Green

# Step 5: Build Windows installer
Write-Host "Step 5: Building Windows installer..." -ForegroundColor Yellow
npm run build:win
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build Windows installer" -ForegroundColor Red
    exit 1
}

# Step 6: Verify build output
Write-Host "Step 6: Verifying build output..." -ForegroundColor Yellow
Set-Location dist
$installerFiles = Get-ChildItem -Filter "*.exe" -Name
if ($installerFiles) {
    Write-Host "✅ Windows installer(s) created:" -ForegroundColor Green
    foreach ($file in $installerFiles) {
        $size = (Get-Item $file).Length / 1MB
        Write-Host "   - $file ($($size.ToString("F1")) MB)" -ForegroundColor White
    }
} else {
    Write-Host "❌ No installer files found" -ForegroundColor Red
    exit 1
}

# Step 7: Generate checksums
Write-Host "Step 7: Generating checksums..." -ForegroundColor Yellow
foreach ($file in $installerFiles) {
    $hash = Get-FileHash -Algorithm SHA256 $file
    "$($hash.Hash)  $file" | Out-File -FilePath "checksums-windows.txt" -Append
}
Write-Host "✅ Checksums generated: checksums-windows.txt" -ForegroundColor Green

# Step 8: Create README
Write-Host "Step 8: Creating installation documentation..." -ForegroundColor Yellow
$readmeContent = @"
# NeuroInsight Windows Installer

## Installation & Verification

### System Requirements
- Windows 10/11 (64-bit)
- 8GB RAM recommended
- 10GB free disk space
- Docker Desktop (optional, for full FastSurfer functionality)

### Verify Integrity
Run this command in PowerShell:
```powershell
Get-FileHash -Algorithm SHA256 NeuroInsight-*.exe
```
Compare with checksums-windows.txt

### Install the Application
1. Double-click the .exe installer
2. Follow the installation wizard
3. Launch NeuroInsight from desktop shortcut

### Features
- Complete MRI analysis pipeline
- Hippocampal asymmetry calculation
- Interactive 3D visualization
- Self-contained installation
- Docker-aware (automatic detection)

### Troubleshooting
- If Docker unavailable: Runs in limited mode
- Check logs: `%APPDATA%\NeuroInsight\logs\`
- Antivirus: May flag as unknown publisher (expected)

---
Built on: $(Get-Date)
Installer files: $($installerFiles -join ', ')
"@

$readmeContent | Out-File -FilePath "README-Windows.md" -Encoding UTF8
Write-Host "✅ Documentation created: README-Windows.md" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Windows installer build complete!" -ForegroundColor Green
Write-Host "Files created in: $(Get-Location)\dist\" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the installer on a clean Windows machine" -ForegroundColor White
Write-Host "2. Test with Docker Desktop installed" -ForegroundColor White
Write-Host "3. Test without Docker (fallback mode)" -ForegroundColor White
Write-Host "4. Upload to GitHub Releases for distribution" -ForegroundColor White

