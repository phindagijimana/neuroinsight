# Desktop Testing Commands - All Platforms

**Quick command reference for testing NeuroInsight Desktop on Linux, macOS, and Windows**

---

## 📋 Table of Contents

- [Linux Commands](#-linux-commands)
- [macOS Commands](#-macos-commands)
- [Windows Commands](#-windows-commands)
- [Cross-Platform Tests](#-cross-platform-tests)
- [Quick Test Checklist](#-quick-test-checklist)

---

## 🐧 Linux Commands

### Installation & Setup

```bash
# Download from GitHub Actions
wget https://github.com/phindagijimana/neuroinsight/actions/artifacts/[ARTIFACT_ID]/zip

# Or use curl
curl -L -o neuroinsight-linux.zip "https://github.com/phindagijimana/neuroinsight/actions/artifacts/[ARTIFACT_ID]/zip"

# Extract
unzip neuroinsight-linux.zip

# You'll get TWO files:
# - NeuroInsight-*.AppImage (the app)
# - checksums-linux.txt (for verification)

# IMPORTANT: Verify checksum before running!
sha256sum -c checksums-linux.txt
# Expected output: NeuroInsight-*.AppImage: OK ✅

# Make executable
chmod +x NeuroInsight-*.AppImage

# Run
./NeuroInsight-*.AppImage
```

### Verify Installation

```bash
# Check file exists
ls -lh NeuroInsight-*.AppImage

# Verify it's executable
file NeuroInsight-*.AppImage

# Check SHA256 checksum
sha256sum NeuroInsight-*.AppImage
cat checksums-linux.txt
```

### Run with Debug Output

```bash
# Run with console output
./NeuroInsight-*.AppImage 2>&1 | tee neuroinsight-debug.log

# Run in background
./NeuroInsight-*.AppImage &

# Run with specific log level
DEBUG=* ./NeuroInsight-*.AppImage
```

### Check Logs

```bash
# Navigate to log directory
cd ~/.config/neuroinsight/logs/

# List log files
ls -lh

# View main log (last 30 lines)
tail -30 neuroinsight.log

# View errors only
cat errors.log

# View crashes
cat crashes.log

# Watch logs in real-time
tail -f neuroinsight.log

# Search for errors
grep -i "error\|failed\|crash" neuroinsight.log

# Check frontend loading
grep "Loading frontend" neuroinsight.log

# Check backend status
grep "Backend" neuroinsight.log | tail -5
```

### Check Processes

```bash
# Check if NeuroInsight is running
ps aux | grep -i neuroinsight

# Check backend process
ps aux | grep neuroinsight-backend

# Kill processes if needed
pkill -f NeuroInsight
pkill -f neuroinsight-backend
```

### Check System Resources

```bash
# Check available memory
free -h

# Check disk space
df -h ~/.config/neuroinsight/

# Monitor CPU usage
top | grep -i neuroinsight

# Monitor memory usage
ps aux | grep -i neuroinsight | awk '{print $4, $11}'
```

### Verify AppImage Contents

```bash
# Extract AppImage
./NeuroInsight-*.AppImage --appimage-extract

# Check frontend exists
ls squashfs-root/resources/app/frontend/index.html

# Check backend exists
ls squashfs-root/resources/neuroinsight-backend/

# Clean up
rm -rf squashfs-root
```

### Clean Uninstall

```bash
# Remove AppImage
rm NeuroInsight-*.AppImage

# Remove data and logs
rm -rf ~/.config/neuroinsight/

# Remove cache
rm -rf ~/.cache/neuroinsight/
```

---

## 🍎 macOS Commands

### Installation & Setup

```bash
# Download from GitHub Actions (or from releases)
# After downloading, extract the artifact:
unzip neuroinsight-mac.zip

# You'll get TWO or MORE files:
# - NeuroInsight-*.dmg (the installer)
# - checksums-mac.txt (for verification)

# IMPORTANT: Verify checksum before installing!
shasum -a 256 -c checksums-mac.txt
# Expected output: NeuroInsight-*.dmg: OK ✅

# OR manually:
shasum -a 256 NeuroInsight-*.dmg
cat checksums-mac.txt
# Compare - should match!

# Mount DMG
hdiutil attach NeuroInsight-*.dmg

# Copy to Applications
cp -R "/Volumes/NeuroInsight/NeuroInsight.app" /Applications/

# Unmount DMG
hdiutil detach "/Volumes/NeuroInsight"

# Remove quarantine (bypass Gatekeeper)
sudo xattr -rd com.apple.quarantine /Applications/NeuroInsight.app

# Launch
open /Applications/NeuroInsight.app
```

### Verify Installation

```bash
# Check app exists
ls -lh /Applications/NeuroInsight.app

# Verify bundle structure
ls /Applications/NeuroInsight.app/Contents/

# Verify checksum was done (see above)
```

### Run with Debug Output

```bash
# Run from command line with output
/Applications/NeuroInsight.app/Contents/MacOS/NeuroInsight 2>&1 | tee ~/neuroinsight-debug.log

# Run and capture first 15 seconds
timeout 15s /Applications/NeuroInsight.app/Contents/MacOS/NeuroInsight 2>&1 | tee ~/debug.log

# View captured log
cat ~/neuroinsight-debug.log
```

### Check Logs

```bash
# Navigate to log directory
cd ~/Library/Logs/NeuroInsight/

# List log files
ls -lh

# View main log (last 30 lines)
tail -30 main.log

# View errors
cat errors.log

# View crashes
cat crashes.log

# Watch logs in real-time
tail -f main.log

# Check for key errors
cat main.log | grep -E "(Loading frontend|Failed to load|ERROR|Backend is ready)"
```

### Alternative Log Location

```bash
# Application Support logs
cd ~/Library/Application\ Support/NeuroInsight/

# View backend log
tail -50 backend.log

# Check database
ls -lh neuroinsight.db
```

### Check Processes

```bash
# Check if running
ps aux | grep -i NeuroInsight

# Check backend process
ps aux | grep neuroinsight-backend

# Kill processes if needed
killall NeuroInsight
pkill -f neuroinsight-backend
```

### Verify App Bundle

```bash
# Check if frontend is bundled
cd /Applications/NeuroInsight.app/Contents/Resources
npx asar list app.asar | grep "frontend/index.html"

# Expected output:
# /frontend/index.html  ✅

# Extract and check main.js
cd /tmp
npx asar extract /Applications/NeuroInsight.app/Contents/Resources/app.asar neuroinsight-check
grep "const frontendPath" neuroinsight-check/src/main.js
rm -rf neuroinsight-check

# Expected: path.join(__dirname, 'frontend', 'index.html')  ✅
```

### Check System Resources

```bash
# Check available memory
vm_stat | grep "Pages free"

# Check disk space
df -h ~/Library/Application\ Support/NeuroInsight/

# Monitor activity
top -pid $(pgrep -i neuroinsight)
```

### Check macOS System Logs

```bash
# View system logs for NeuroInsight
log show --predicate 'process == "NeuroInsight"' --last 5m

# View with errors only
log show --predicate 'process == "NeuroInsight" AND messageType == error' --last 10m

# Stream logs
log stream --predicate 'process == "NeuroInsight"'
```

### Clean Uninstall

```bash
# Remove app
rm -rf /Applications/NeuroInsight.app

# Remove logs
rm -rf ~/Library/Logs/NeuroInsight/

# Remove data
rm -rf ~/Library/Application\ Support/NeuroInsight/

# Remove preferences
rm -rf ~/Library/Preferences/com.neuroinsight.desktop.*

# Remove cache
rm -rf ~/Library/Caches/com.neuroinsight.desktop.*
```

---

## 🪟 Windows Commands

### Installation & Setup

```powershell
# Download from GitHub Actions
# After downloading, extract the artifact:
Expand-Archive neuroinsight-windows.zip

# You'll get TWO files:
# - NeuroInsight-Setup-*.exe (the installer)
# - checksums-windows.txt (for verification)

# IMPORTANT: Verify checksum before installing!
# Quick verification:
$expected = (Get-Content checksums-windows.txt).Split()[0]
$actual = (Get-FileHash "NeuroInsight-Setup-*.exe" -Algorithm SHA256).Hash
if ($expected -eq $actual) { 
    Write-Host "✅ Checksum verified! Safe to install." -ForegroundColor Green 
} else { 
    Write-Host "❌ Checksum MISMATCH! Do not install!" -ForegroundColor Red 
    exit
}

# Run installer with GUI
Start-Process "NeuroInsight-Setup.exe" -Wait

# Or run installer silently (automated testing)
Start-Process "NeuroInsight-Setup.exe" -ArgumentList "/S" -Wait

# Launch app
& "C:\Program Files\NeuroInsight\NeuroInsight.exe"
```

### Verify Installation

```powershell
# Check if installed
Test-Path "C:\Program Files\NeuroInsight\NeuroInsight.exe"

# Check file details
Get-Item "C:\Program Files\NeuroInsight\NeuroInsight.exe" | Select-Object *

# List installation directory
Get-ChildItem "C:\Program Files\NeuroInsight\" -Recurse
```

### Run with Debug Output

```powershell
# Run from PowerShell
& "C:\Program Files\NeuroInsight\NeuroInsight.exe"

# Run and capture output
& "C:\Program Files\NeuroInsight\NeuroInsight.exe" 2>&1 | Tee-Object -FilePath "$env:USERPROFILE\Desktop\neuroinsight-debug.log"

# Run as administrator
Start-Process "C:\Program Files\NeuroInsight\NeuroInsight.exe" -Verb RunAs
```

### Check Logs

```powershell
# Navigate to log directory
cd "$env:APPDATA\neuroinsight\logs"

# List log files
Get-ChildItem

# View main log (last 30 lines)
Get-Content neuroinsight.log -Tail 30

# View errors only
Get-Content errors.log

# View crashes
Get-Content crashes.log

# Watch logs in real-time (similar to tail -f)
Get-Content neuroinsight.log -Wait -Tail 10

# Search for errors
Select-String -Path "*.log" -Pattern "ERROR|FAILED|CRASH"

# Check frontend loading
Select-String -Path "neuroinsight.log" -Pattern "Loading frontend"

# Check backend status
Select-String -Path "neuroinsight.log" -Pattern "Backend" | Select-Object -Last 5
```

### Alternative: Using Command Prompt

```cmd
REM Navigate to logs
cd %APPDATA%\neuroinsight\logs

REM View last 20 lines
powershell -command "Get-Content neuroinsight.log -Tail 20"

REM Find errors
findstr /i "error failed crash" neuroinsight.log
```

### Check Processes

```powershell
# Check if running
Get-Process | Where-Object { $_.ProcessName -like "*neuroinsight*" }

# Get detailed process info
Get-Process "NeuroInsight" | Select-Object Name, Id, CPU, WorkingSet, Path

# Check backend process
Get-Process | Where-Object { $_.ProcessName -eq "neuroinsight-backend" }

# Stop processes
Stop-Process -Name "NeuroInsight" -Force
Stop-Process -Name "neuroinsight-backend" -Force

# Kill all related processes
Get-Process | Where-Object { $_.ProcessName -like "*neuroinsight*" } | Stop-Process -Force
```

### Check System Resources

```powershell
# Check available memory
Get-CimInstance Win32_OperatingSystem | Select-Object FreePhysicalMemory, TotalVisibleMemorySize

# Convert to GB
$os = Get-CimInstance Win32_OperatingSystem
[math]::Round($os.FreePhysicalMemory/1MB, 2)

# Check disk space
Get-PSDrive C | Select-Object Used, Free

# Monitor process resources
Get-Process "NeuroInsight" | Select-Object Name, @{N="MemoryMB";E={[math]::Round($_.WS/1MB,2)}}, @{N="CPU";E={$_.CPU}}

# Continuous monitoring
while ($true) { 
    Get-Process "NeuroInsight" -ErrorAction SilentlyContinue | Select-Object Name, @{N="MemoryMB";E={[math]::Round($_.WS/1MB,2)}}
    Start-Sleep -Seconds 5 
}
```

### Check Network/Ports

```powershell
# Check if backend port (5000) is in use
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue

# Check all NeuroInsight connections
Get-NetTCPConnection | Where-Object { $_.OwningProcess -in (Get-Process "*neuroinsight*").Id }
```

### Verify Installation Files

```powershell
# Check resources exist
Test-Path "C:\Program Files\NeuroInsight\resources\app.asar"

# Check backend exists
Test-Path "C:\Program Files\NeuroInsight\resources\neuroinsight-backend"

# List backend files
Get-ChildItem "C:\Program Files\NeuroInsight\resources\neuroinsight-backend" | Select-Object Name, Length
```

### Check Event Viewer

```powershell
# Check Windows Event Log for NeuroInsight events
Get-EventLog -LogName Application -Source "NeuroInsight" -Newest 20 -ErrorAction SilentlyContinue

# Check for errors
Get-EventLog -LogName Application -EntryType Error | Where-Object { $_.Source -like "*neuroinsight*" }
```

### Clean Uninstall

```powershell
# Uninstall via Control Panel programmatically
$app = Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -like "*NeuroInsight*" }
$app.Uninstall()

# Or run uninstaller
Start-Process "C:\Program Files\NeuroInsight\Uninstall NeuroInsight.exe" -Wait

# Remove application data
Remove-Item -Path "$env:APPDATA\neuroinsight" -Recurse -Force -ErrorAction SilentlyContinue

# Remove local data
Remove-Item -Path "$env:LOCALAPPDATA\neuroinsight" -Recurse -Force -ErrorAction SilentlyContinue

# Clean registry (as Administrator)
Remove-Item -Path "HKCU:\Software\neuroinsight" -Recurse -Force -ErrorAction SilentlyContinue
```

---

## 🌐 Cross-Platform Tests

### Test 1: Basic Launch Test

**Linux/macOS:**
```bash
# Run and check if window appears
./NeuroInsight-*.AppImage &  # Linux
open /Applications/NeuroInsight.app  # macOS

# Wait a few seconds, then check if running
ps aux | grep -i neuroinsight
```

**Windows:**
```powershell
# Launch
Start-Process "C:\Program Files\NeuroInsight\NeuroInsight.exe"

# Wait and check
Start-Sleep -Seconds 5
Get-Process "NeuroInsight"
```

---

### Test 2: Frontend Loading Test

**Linux:**
```bash
grep "Loading frontend" ~/.config/neuroinsight/logs/neuroinsight.log | tail -1
# Expected: "Loading frontend from: .../frontend/index.html"
```

**macOS:**
```bash
grep "Loading frontend" ~/Library/Logs/NeuroInsight/main.log | tail -1
# Expected: "Loading frontend from: .../frontend/index.html"
```

**Windows:**
```powershell
Select-String -Path "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Pattern "Loading frontend" | Select-Object -Last 1
# Expected: "Loading frontend from: ...\frontend\index.html"
```

---

### Test 3: Backend Status Test

**Linux:**
```bash
grep "Backend" ~/.config/neuroinsight/logs/neuroinsight.log | tail -3
# Expected: "Backend is ready" or "Backend started on port 5000"
```

**macOS:**
```bash
grep "Backend" ~/Library/Logs/NeuroInsight/main.log | tail -3
```

**Windows:**
```powershell
Select-String -Path "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Pattern "Backend" | Select-Object -Last 3
```

---

### Test 4: Error Check Test

**Linux:**
```bash
if [ -s ~/.config/neuroinsight/logs/errors.log ]; then
    echo "❌ Errors found:"
    cat ~/.config/neuroinsight/logs/errors.log
else
    echo "✅ No errors!"
fi
```

**macOS:**
```bash
if [ -s ~/Library/Logs/NeuroInsight/errors.log ]; then
    echo "❌ Errors found:"
    cat ~/Library/Logs/NeuroInsight/errors.log
else
    echo "✅ No errors!"
fi
```

**Windows:**
```powershell
if (Test-Path "$env:APPDATA\neuroinsight\logs\errors.log") {
    $errors = Get-Content "$env:APPDATA\neuroinsight\logs\errors.log"
    if ($errors) {
        Write-Host "❌ Errors found:" -ForegroundColor Red
        $errors
    } else {
        Write-Host "✅ No errors!" -ForegroundColor Green
    }
}
```

---

### Test 5: Memory Check Test

**Linux:**
```bash
# Check if NeuroInsight is using reasonable memory (< 2GB)
ps aux | grep -i neuroinsight | awk '{if($6/1024/1024 < 2) print "✅ Memory OK:", $6/1024/1024 "GB"; else print "⚠️  High memory:", $6/1024/1024 "GB"}'
```

**macOS:**
```bash
# Check memory usage
ps aux | grep -i NeuroInsight | awk '{if($6/1024/1024 < 2) print "✅ Memory OK:", $6/1024/1024 "GB"; else print "⚠️  High memory:", $6/1024/1024 "GB"}'
```

**Windows:**
```powershell
$proc = Get-Process "NeuroInsight" -ErrorAction SilentlyContinue
if ($proc) {
    $memGB = [math]::Round($proc.WS/1GB, 2)
    if ($memGB -lt 2) {
        Write-Host "✅ Memory OK: $memGB GB" -ForegroundColor Green
    } else {
        Write-Host "⚠️  High memory: $memGB GB" -ForegroundColor Yellow
    }
}
```

---

## 📝 Quick Test Checklist

### Automated Test Script

**Linux/macOS:**

```bash
#!/bin/bash
echo "=== NeuroInsight Quick Test ==="
echo ""

# Test 1: Installation
echo "1. Checking installation..."
if [ -f "./NeuroInsight"*.AppImage ] || [ -d "/Applications/NeuroInsight.app" ]; then
    echo "   ✅ Installed"
else
    echo "   ❌ Not found"
fi

# Test 2: Logs exist
echo "2. Checking logs..."
if [ -d ~/.config/neuroinsight/logs/ ] || [ -d ~/Library/Logs/NeuroInsight/ ]; then
    echo "   ✅ Logs directory exists"
else
    echo "   ❌ No logs yet (app not run?)"
fi

# Test 3: Process running
echo "3. Checking if running..."
if ps aux | grep -i "[n]euroinsight" > /dev/null; then
    echo "   ✅ Running"
else
    echo "   ❌ Not running"
fi

# Test 4: Recent errors
echo "4. Checking for errors..."
LOG_DIR=~/.config/neuroinsight/logs/
[ -d ~/Library/Logs/NeuroInsight/ ] && LOG_DIR=~/Library/Logs/NeuroInsight/

if [ -f "$LOG_DIR/errors.log" ] && [ -s "$LOG_DIR/errors.log" ]; then
    echo "   ⚠️  Errors found (check errors.log)"
else
    echo "   ✅ No errors"
fi

echo ""
echo "Test complete!"
```

**Windows:**

```powershell
Write-Host "=== NeuroInsight Quick Test ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Installation
Write-Host "1. Checking installation..."
if (Test-Path "C:\Program Files\NeuroInsight\NeuroInsight.exe") {
    Write-Host "   ✅ Installed" -ForegroundColor Green
} else {
    Write-Host "   ❌ Not found" -ForegroundColor Red
}

# Test 2: Logs exist
Write-Host "2. Checking logs..."
if (Test-Path "$env:APPDATA\neuroinsight\logs") {
    Write-Host "   ✅ Logs directory exists" -ForegroundColor Green
} else {
    Write-Host "   ❌ No logs yet (app not run?)" -ForegroundColor Yellow
}

# Test 3: Process running
Write-Host "3. Checking if running..."
if (Get-Process "NeuroInsight" -ErrorAction SilentlyContinue) {
    Write-Host "   ✅ Running" -ForegroundColor Green
} else {
    Write-Host "   ❌ Not running" -ForegroundColor Yellow
}

# Test 4: Recent errors
Write-Host "4. Checking for errors..."
$errorLog = "$env:APPDATA\neuroinsight\logs\errors.log"
if ((Test-Path $errorLog) -and ((Get-Item $errorLog).Length -gt 0)) {
    Write-Host "   ⚠️  Errors found (check errors.log)" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ No errors" -ForegroundColor Green
}

Write-Host ""
Write-Host "Test complete!" -ForegroundColor Cyan
```

---

## 🎯 Complete Diagnostic Report

### Generate Full Report (Linux/macOS)

```bash
#!/bin/bash
cat << 'EOF' > /tmp/neuroinsight-diagnostic.sh
#!/bin/bash
echo "================================"
echo "NeuroInsight Diagnostic Report"
echo "================================"
echo ""
echo "Date: $(date)"
echo "OS: $(uname -s)"
echo "Version: $(uname -r)"
echo ""

echo "--- Installation ---"
ls -lh ./NeuroInsight*.AppImage 2>/dev/null || ls -lh /Applications/NeuroInsight.app 2>/dev/null || echo "Not found"
echo ""

echo "--- Processes ---"
ps aux | grep -i [n]euroinsight || echo "Not running"
echo ""

echo "--- Logs Directory ---"
ls -lh ~/.config/neuroinsight/logs/ 2>/dev/null || ls -lh ~/Library/Logs/NeuroInsight/ 2>/dev/null || echo "No logs"
echo ""

echo "--- Recent Errors ---"
tail -10 ~/.config/neuroinsight/logs/errors.log 2>/dev/null || tail -10 ~/Library/Logs/NeuroInsight/errors.log 2>/dev/null || echo "No errors"
echo ""

echo "--- System Resources ---"
echo "Memory: $(free -h 2>/dev/null | grep Mem || vm_stat | grep free)"
echo "Disk: $(df -h . | tail -1)"
echo ""

echo "================================"
echo "Report complete!"
EOF

chmod +x /tmp/neuroinsight-diagnostic.sh
/tmp/neuroinsight-diagnostic.sh | tee ~/neuroinsight-diagnostic-report.txt
echo "Report saved to: ~/neuroinsight-diagnostic-report.txt"
```

### Generate Full Report (Windows)

```powershell
$report = @"
================================
NeuroInsight Diagnostic Report
================================

Date: $(Get-Date)
OS: $(Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty Caption)
Build: $(Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty BuildNumber)

--- Installation ---
$(if (Test-Path 'C:\Program Files\NeuroInsight\NeuroInsight.exe') { Get-Item 'C:\Program Files\NeuroInsight\NeuroInsight.exe' | Select-Object Name, Length, LastWriteTime } else { 'Not found' })

--- Processes ---
$(Get-Process | Where-Object { $_.ProcessName -like '*neuroinsight*' } | Format-Table -AutoSize | Out-String)

--- Logs Directory ---
$(if (Test-Path "$env:APPDATA\neuroinsight\logs") { Get-ChildItem "$env:APPDATA\neuroinsight\logs" | Select-Object Name, Length } else { 'No logs' })

--- Recent Errors ---
$(Get-Content "$env:APPDATA\neuroinsight\logs\errors.log" -Tail 10 -ErrorAction SilentlyContinue)

--- System Resources ---
Free Memory: $(Get-CimInstance Win32_OperatingSystem | ForEach-Object { [math]::Round($_.FreePhysicalMemory/1MB,2) }) GB
Free Disk: $(Get-PSDrive C | ForEach-Object { [math]::Round($_.Free/1GB,2) }) GB

================================
Report complete!
"@

$report | Out-File -FilePath "$env:USERPROFILE\Desktop\neuroinsight-diagnostic-report.txt"
Write-Host "Report saved to: $env:USERPROFILE\Desktop\neuroinsight-diagnostic-report.txt" -ForegroundColor Green
```

---

## 🚀 Quick Command Reference Card

### Linux
```bash
./NeuroInsight-*.AppImage              # Launch
tail -30 ~/.config/neuroinsight/logs/neuroinsight.log  # View logs
ps aux | grep neuroinsight             # Check if running
pkill -f NeuroInsight                  # Stop app
```

### macOS
```bash
open /Applications/NeuroInsight.app    # Launch
tail -30 ~/Library/Logs/NeuroInsight/main.log  # View logs
ps aux | grep NeuroInsight             # Check if running
killall NeuroInsight                   # Stop app
```

### Windows
```powershell
& "C:\Program Files\NeuroInsight\NeuroInsight.exe"  # Launch
Get-Content "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Tail 30  # View logs
Get-Process "NeuroInsight"             # Check if running
Stop-Process -Name "NeuroInsight"      # Stop app
```

---

**Last Updated**: November 12, 2025  
**Version**: 1.3.9  
**Platforms**: Linux, macOS, Windows

---

**Happy Testing! 🧪**

