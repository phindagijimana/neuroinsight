@echo off
REM Windows Installer Build Script for NeuroInsight (Batch Version)
REM Run this on a Windows machine

echo === NeuroInsight Windows Installer Build Script ===
echo This script builds the complete Windows installer package
echo.

REM Check prerequisites
echo Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Python not found. Please install Python 3.9+
    pause
    exit /b 1
)
echo ✅ Python found

REM Check Node.js
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
echo ✅ Node.js found

REM Check Git
git --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Git not found. Please install Git
    pause
    exit /b 1
)
echo ✅ Git found

echo.
echo Building NeuroInsight Windows Installer...

REM Step 1: Install Python dependencies
echo Step 1: Installing Python dependencies...
pip install -r desktop_alone/requirements.txt
pip install pyinstaller requests
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)
echo ✅ Python dependencies installed

REM Step 2: Build Python backend
echo Step 2: Building Python backend executable...
cd desktop_alone
pyinstaller build.spec --clean --noconfirm
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to build backend
    pause
    exit /b 1
)

REM Verify backend was built
if exist "dist\neuroinsight-backend\neuroinsight-backend.exe" (
    for %%A in ("dist\neuroinsight-backend\neuroinsight-backend.exe") do set "size=%%~zA"
    set /a "sizeMB=%size%/1024/1024"
    echo ✅ Backend built successfully: !sizeMB! MB
) else (
    echo ❌ Backend executable not found
    pause
    exit /b 1
)

REM Step 3: Verify frontend exists
echo Step 3: Verifying frontend...
if exist "frontend\index.html" (
    echo ✅ Frontend found
) else (
    echo ❌ Frontend not found
    pause
    exit /b 1
)

REM Step 4: Install Electron dependencies
echo Step 4: Installing Electron dependencies...
cd electron-app
npm install
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to install Electron dependencies
    pause
    exit /b 1
)
echo ✅ Electron dependencies installed

REM Step 5: Build Windows installer
echo Step 5: Building Windows installer...
npm run build:win
if %ERRORLEVEL% neq 0 (
    echo ❌ Failed to build Windows installer
    pause
    exit /b 1
)

REM Step 6: Verify build output
echo Step 6: Verifying build output...
cd dist
if exist "*.exe" (
    echo ✅ Windows installer(s) created:
    for %%f in (*.exe) do (
        for %%A in ("%%f") do set "size=%%~zA"
        set /a "sizeMB=!size!/1024/1024"
        echo    - %%f (!sizeMB! MB)
    )
) else (
    echo ❌ No installer files found
    pause
    exit /b 1
)

REM Step 7: Generate checksums
echo Step 7: Generating checksums...
echo. > checksums-windows.txt
for %%f in (*.exe) do (
    for /f "tokens=*" %%h in ('powershell -command "Get-FileHash -Algorithm SHA256 '%%f' | Select-Object -ExpandProperty Hash"') do (
        echo %%h  %%f >> checksums-windows.txt
    )
)
echo ✅ Checksums generated: checksums-windows.txt

REM Step 8: Create README
echo Step 8: Creating installation documentation...
echo # NeuroInsight Windows Installer > README-Windows.md
echo. >> README-Windows.md
echo ## Installation ^& Verification >> README-Windows.md
echo. >> README-Windows.md
echo ### System Requirements >> README-Windows.md
echo - Windows 10/11 ^(64-bit^) >> README-Windows.md
echo - 8GB RAM recommended >> README-Windows.md
echo - 10GB free disk space >> README-Windows.md
echo - Docker Desktop ^(optional, for full FastSurfer functionality^) >> README-Windows.md
echo. >> README-Windows.md
echo ### Verify Integrity >> README-Windows.md
echo Run this command in PowerShell: >> README-Windows.md
echo ```powershell >> README-Windows.md
echo Get-FileHash -Algorithm SHA256 NeuroInsight-*.exe >> README-Windows.md
echo ``` >> README-Windows.md
echo Compare with checksums-windows.txt >> README-Windows.md
echo. >> README-Windows.md
echo ### Install the Application >> README-Windows.md
echo 1. Double-click the .exe installer >> README-Windows.md
echo 2. Follow the installation wizard >> README-Windows.md
echo 3. Launch NeuroInsight from desktop shortcut >> README-Windows.md
echo. >> README-Windows.md
echo ### Features >> README-Windows.md
echo - Complete MRI analysis pipeline >> README-Windows.md
echo - Hippocampal asymmetry calculation >> README-Windows.md
echo - Interactive 3D visualization >> README-Windows.md
echo - Self-contained installation >> README-Windows.md
echo - Docker-aware ^(automatic detection^) >> README-Windows.md
echo. >> README-Windows.md
echo ### Troubleshooting >> README-Windows.md
echo - If Docker unavailable: Runs in limited mode >> README-Windows.md
echo - Check logs: %%APPDATA%%\NeuroInsight\logs\ >> README-Windows.md
echo - Antivirus: May flag as unknown publisher ^(expected^) >> README-Windows.md
echo. >> README-Windows.md
echo --- >> README-Windows.md
echo Built on: %DATE% %TIME% >> README-Windows.md
echo. >> README-Windows.md
echo ✅ Documentation created: README-Windows.md

echo.
echo 🎉 Windows installer build complete!
echo Files created in: %CD%\dist\
echo.
echo Next steps:
echo 1. Test the installer on a clean Windows machine
echo 2. Test with Docker Desktop installed
echo 3. Test without Docker ^(fallback mode^)
echo 4. Upload to GitHub Releases for distribution

pause
