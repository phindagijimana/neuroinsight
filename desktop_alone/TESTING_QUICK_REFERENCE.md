# Testing Quick Reference - NeuroInsight Desktop

**One-page command cheat sheet for testing on all platforms** 🚀

---

## 🎯 Essential Commands

### Linux 🐧

```bash
# Launch
./NeuroInsight-*.AppImage

# Check logs
tail -30 ~/.config/neuroinsight/logs/neuroinsight.log

# Check errors
cat ~/.config/neuroinsight/logs/errors.log

# Check if running
ps aux | grep neuroinsight

# Stop
pkill -f NeuroInsight
```

### macOS 🍎

```bash
# Launch
open /Applications/NeuroInsight.app

# Launch with debug output
/Applications/NeuroInsight.app/Contents/MacOS/NeuroInsight 2>&1 | tee ~/debug.log

# Check logs
tail -30 ~/Library/Logs/NeuroInsight/main.log

# Check errors
cat ~/Library/Logs/NeuroInsight/errors.log

# Check if running
ps aux | grep NeuroInsight

# Verify frontend bundled
cd /Applications/NeuroInsight.app/Contents/Resources
npx asar list app.asar | grep frontend

# Stop
killall NeuroInsight
```

### Windows 🪟

```powershell
# Launch
& "C:\Program Files\NeuroInsight\NeuroInsight.exe"

# Check logs
Get-Content "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Tail 30

# Check errors
Get-Content "$env:APPDATA\neuroinsight\logs\errors.log"

# Check if running
Get-Process | Where-Object { $_.ProcessName -like "*neuroinsight*" }

# Stop
Stop-Process -Name "NeuroInsight" -Force
```

---

## 🔒 Verify Download (IMPORTANT - Do This First!)

### Where to Find Checksums

**Checksums are included in the downloaded artifacts!**

After downloading and extracting the artifact zip:

**Linux:**
```bash
# Extract the artifact
unzip neuroinsight-linux.zip

# You'll see:
# - NeuroInsight-*.AppImage
# - checksums-linux.txt  ← This file!

# Verify checksum
sha256sum NeuroInsight-*.AppImage
cat checksums-linux.txt

# Compare the hashes - they should match!
```

**macOS:**
```bash
# Extract the artifact
unzip neuroinsight-mac.zip

# You'll see:
# - NeuroInsight-*.dmg
# - checksums-mac.txt  ← This file!

# Verify checksum
shasum -a 256 NeuroInsight-*.dmg
cat checksums-mac.txt

# Compare the hashes - they should match!
```

**Windows:**
```powershell
# Extract the artifact
Expand-Archive neuroinsight-windows.zip

# You'll see:
# - NeuroInsight-Setup-*.exe
# - checksums-windows.txt  ← This file!

# Verify checksum
Get-FileHash "NeuroInsight-Setup-*.exe" -Algorithm SHA256
Get-Content checksums-windows.txt

# Compare the hashes - they should match!
```

### Quick Verification One-Liner

**Linux:**
```bash
sha256sum -c checksums-linux.txt
# Output: NeuroInsight-*.AppImage: OK ✅
```

**macOS:**
```bash
shasum -a 256 -c checksums-mac.txt
# Output: NeuroInsight-*.dmg: OK ✅
```

**Windows:**
```powershell
$expected = (Get-Content checksums-windows.txt).Split()[0]
$actual = (Get-FileHash "NeuroInsight-Setup-*.exe" -Algorithm SHA256).Hash
if ($expected -eq $actual) { Write-Host "✅ Checksum matches!" -ForegroundColor Green } else { Write-Host "❌ Checksum MISMATCH!" -ForegroundColor Red }
```

⚠️ **If checksums don't match, DO NOT install! Download again.**

---

## ✅ Quick Test (30 seconds)

### All Platforms

1. **Verify checksum** (see above) ← Do this first!
2. **Launch app**
3. **Wait 10 seconds**
4. **Check**: Window opens with 3 tabs (Jobs, Stats, Viewer)
5. **Verify**: Status bar shows "Backend: Ready"

✅ If yes → Working!  
❌ If no → Check logs

---

## 🔍 Diagnostic Commands

### Check Frontend Loading

**Linux:**
```bash
grep "Loading frontend" ~/.config/neuroinsight/logs/neuroinsight.log | tail -1
```

**macOS:**
```bash
grep "Loading frontend" ~/Library/Logs/NeuroInsight/main.log | tail -1
```

**Windows:**
```powershell
Select-String -Path "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Pattern "Loading frontend" | Select -Last 1
```

**Expected:** `Loading frontend from: .../frontend/index.html` (no "src/" in path)

---

### Check Backend Status

**Linux:**
```bash
grep "Backend" ~/.config/neuroinsight/logs/neuroinsight.log | tail -3
```

**macOS:**
```bash
grep "Backend" ~/Library/Logs/NeuroInsight/main.log | tail -3
```

**Windows:**
```powershell
Select-String -Path "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Pattern "Backend" | Select -Last 3
```

**Expected:** `Backend is ready` or `Backend started on port 5000`

---

### Check for Errors

**Linux:**
```bash
if [ -s ~/.config/neuroinsight/logs/errors.log ]; then
    echo "❌ Errors found"; cat ~/.config/neuroinsight/logs/errors.log
else
    echo "✅ No errors"
fi
```

**macOS:**
```bash
if [ -s ~/Library/Logs/NeuroInsight/errors.log ]; then
    echo "❌ Errors found"; cat ~/Library/Logs/NeuroInsight/errors.log
else
    echo "✅ No errors"
fi
```

**Windows:**
```powershell
if (Test-Path "$env:APPDATA\neuroinsight\logs\errors.log") {
    $e = Get-Content "$env:APPDATA\neuroinsight\logs\errors.log"
    if ($e) { Write-Host "❌ Errors found"; $e } else { Write-Host "✅ No errors" }
}
```

---

## 📊 System Checks

### Memory Check

**Linux:**
```bash
free -h | grep Mem
```

**macOS:**
```bash
vm_stat | grep "Pages free"
```

**Windows:**
```powershell
Get-CimInstance Win32_OperatingSystem | Select @{N="FreeMemoryGB";E={[math]::Round($_.FreePhysicalMemory/1MB,2)}}
```

**Need:** At least 8 GB free

---

### Disk Space Check

**Linux:**
```bash
df -h ~/.config/neuroinsight/
```

**macOS:**
```bash
df -h ~/Library/Application\ Support/NeuroInsight/
```

**Windows:**
```powershell
Get-PSDrive C | Select Used, Free
```

**Need:** At least 10 GB free

---

## 🧪 Automated Test Script

### Linux/macOS One-Liner

```bash
curl -s https://raw.githubusercontent.com/phindagijimana/neuroinsight/main/desktop_alone/test-script.sh | bash
```

Or copy this script:

```bash
#!/bin/bash
echo "Testing NeuroInsight..."
APP_RUNNING=$(ps aux | grep -i "[n]euroinsight" | wc -l)
LOG_DIR=~/.config/neuroinsight/logs/
[ -d ~/Library/Logs/NeuroInsight/ ] && LOG_DIR=~/Library/Logs/NeuroInsight/
HAS_ERRORS=$([ -s "$LOG_DIR/errors.log" ] && echo "YES" || echo "NO")

echo "✓ Running: $([[ $APP_RUNNING -gt 0 ]] && echo YES || echo NO)"
echo "✓ Errors: $HAS_ERRORS"
echo "Done!"
```

### Windows One-Liner

```powershell
iwr -useb https://raw.githubusercontent.com/phindagijimana/neuroinsight/main/desktop_alone/test-script.ps1 | iex
```

Or copy this script:

```powershell
Write-Host "Testing NeuroInsight..." -ForegroundColor Cyan
$running = Get-Process "NeuroInsight" -ErrorAction SilentlyContinue
$hasErrors = Test-Path "$env:APPDATA\neuroinsight\logs\errors.log"

Write-Host "✓ Running: $(if($running){'YES'}else{'NO'})" -ForegroundColor $(if($running){'Green'}else{'Red'})
Write-Host "✓ Errors: $(if($hasErrors){'YES'}else{'NO'})" -ForegroundColor $(if(!$hasErrors){'Green'}else{'Red'})
Write-Host "Done!" -ForegroundColor Cyan
```

---

## 📥 Download Latest Build

**Direct Links:**

- **Linux**: [Download](https://github.com/phindagijimana/neuroinsight/actions/runs/19284629791) (2.74 GB)
- **macOS**: [Download](https://github.com/phindagijimana/neuroinsight/actions/runs/19284629791) (0.45 GB)
- **Windows**: [Download](https://github.com/phindagijimana/neuroinsight/actions/runs/19284629791) (0.20 GB)

**Latest Version**: v1.3.9 ✅  
**Status**: All platforms successful  
**Built**: November 12, 2025

---

## 📚 Full Documentation

| Document | Purpose |
|----------|---------|
| **DESKTOP_TESTING_COMMANDS.md** | Complete command reference (all platforms) |
| **WINDOWS_TEST_GUIDE.md** | Full Windows testing guide |
| **MACOS_LOG_COMMANDS.md** | macOS-specific commands |
| **QUICK_START_WINDOWS.md** | Fast Windows setup |
| **INSTALLATION.md** | Installation for all platforms |
| **USER_MANUAL.md** | User guide |
| **LOGS_AND_TROUBLESHOOTING.md** | Troubleshooting help |

---

## 🎯 Common Issues & Quick Fixes

### Black/Dark Window
**Cause**: Old build with wrong frontend path  
**Fix**: Download latest build (v1.3.9+)

### Backend Won't Start
**Cause**: Port 5000 in use or antivirus blocking  
**Fix**: Close other apps on port 5000, add to antivirus exclusions

### SmartScreen Warning (Windows)
**Cause**: Unsigned application  
**Fix**: Click "More info" → "Run anyway" (safe!)

### Gatekeeper Block (macOS)
**Cause**: Unsigned application  
**Fix**: Right-click app → "Open" → "Open" (or use `xattr -rd`)

### Processing Slow
**Expected**: 5-10 min with GPU, 1-2 hours with CPU  
**Fix**: Be patient, or get NVIDIA GPU for faster processing

---

## 🔗 Quick Links

- **Actions**: https://github.com/phindagijimana/neuroinsight/actions
- **Releases**: https://github.com/phindagijimana/neuroinsight/releases
- **Issues**: https://github.com/phindagijimana/neuroinsight/issues
- **Repo**: https://github.com/phindagijimana/neuroinsight

---

## 📞 Report Results

**Working? ✅**
- Say: "Tested v1.3.9 on [OS], works perfectly!"

**Not Working? ❌**
- Run diagnostic command (see above)
- Collect logs
- Share in GitHub Issues with:
  - OS version
  - Error logs
  - Screenshots

---

**Last Updated**: November 12, 2025  
**Version**: 1.3.9  
**Status**: All platforms tested ✅

---

**Print this page for quick reference during testing! 📄**

