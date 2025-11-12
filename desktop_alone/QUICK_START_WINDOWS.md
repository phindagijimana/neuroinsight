# Quick Start - Testing on Windows PC

**Fast guide to test NeuroInsight Desktop on Windows** 🚀

---

## 🎯 3-Minute Quick Test

### Step 1: Download (2 minutes)

```powershell
# Go to this URL in your browser:
https://github.com/phindagijimana/neuroinsight/actions/runs/19284629791

# Scroll down to "Artifacts" section
# Download: neuroinsight-windows (0.20 GB)
# Extract the zip file

# You'll get TWO files:
# - NeuroInsight-Setup-1.3.8.exe (the installer)
# - checksums-windows.txt (for verification)
```

### Step 1.5: Verify Checksum (30 seconds) ✅

**IMPORTANT: Always verify before installing!**

```powershell
# In PowerShell, navigate to extracted folder:
cd ~\Downloads\neuroinsight-windows

# Verify checksum (automatic)
$expected = (Get-Content checksums-windows.txt).Split()[0]
$actual = (Get-FileHash "NeuroInsight-Setup-*.exe" -Algorithm SHA256).Hash
if ($expected -eq $actual) { 
    Write-Host "✅ Checksum verified! Safe to install." -ForegroundColor Green 
} else { 
    Write-Host "❌ Checksum MISMATCH! Do not install!" -ForegroundColor Red 
}
```

**OR manual verification:**
```powershell
# Calculate hash
Get-FileHash "NeuroInsight-Setup-1.3.8.exe" -Algorithm SHA256

# View expected hash
Get-Content checksums-windows.txt

# Compare manually - they should match!
```

### Step 2: Install (1 minute)

1. **Run** `NeuroInsight-Setup-1.3.8.exe` (or latest version)
2. **When SmartScreen appears**: Click "More info" → "Run anyway"
3. **Follow installer** → Click "Next" → "Install" → "Finish"

### Step 3: Test (30 seconds)

1. **Launch** from Start Menu: "NeuroInsight"
2. **Check**: Main window opens with 3 tabs (Jobs, Stats, Viewer)
3. **Verify**: Status bar shows "Backend: Ready"

✅ **If all 3 work → Installation successful!**

---

## 📊 Full Testing (10 minutes)

### Test 1: Launch App
```powershell
# From PowerShell
& "C:\Program Files\NeuroInsight\NeuroInsight.exe"
```
**Expected**: Window opens, 3 tabs visible

### Test 2: Check Logs
Press `Ctrl+L` in the app
**Expected**: Log folder opens

### Test 3: Verify Backend
Look at status bar (bottom of window)
**Expected**: "Backend: Ready" (green)

### Test 4: Upload Test File (Optional)
1. Click "Upload File"
2. Select a `.nii` or `.nii.gz` MRI scan
3. Click "Process"
**Expected**: Progress bar shows stages

---

## 🔍 Quick Diagnostics

### Check Installation
```powershell
# Is it installed?
Test-Path "C:\Program Files\NeuroInsight\NeuroInsight.exe"
```

### Check Logs
```powershell
# View recent errors
Get-Content "$env:APPDATA\neuroinsight\logs\errors.log" -Tail 10
```

### Check Processes
```powershell
# Is it running?
Get-Process | Where-Object { $_.ProcessName -like "*neuroinsight*" }
```

---

## ❌ Common Issues & Quick Fixes

### Issue: SmartScreen blocks installer
**Fix**: Click "More info" → "Run anyway"

### Issue: Black/dark window
**Fix**: Download latest build (v1.3.9+)

### Issue: Backend won't start
**Fix**: Add to Windows Defender exclusions:
```
Settings → Update & Security → Windows Security 
→ Virus & threat protection → Add exclusion 
→ C:\Program Files\NeuroInsight
```

### Issue: Processing slow
**Expected**:
- With GPU: 5-10 minutes
- Without GPU: 1-2 hours (CPU only)

---

## 📝 Report Results

### If Working ✅
Say: "Tested v1.3.9 on Windows [version], everything works!"

### If Not Working ❌
Run this diagnostic:
```powershell
# Quick diagnostic report
@"
Version: v1.3.9
Windows: $(Get-CimInstance Win32_OperatingSystem | Select -ExpandProperty Caption)
App Starts: $(Test-Path 'C:\Program Files\NeuroInsight\NeuroInsight.exe')
Recent Error: $(Get-Content "$env:APPDATA\neuroinsight\logs\errors.log" -Tail 1 -ErrorAction SilentlyContinue)
"@ | Out-File "$env:USERPROFILE\Desktop\test-report.txt"

# Then share the test-report.txt from your Desktop
```

---

## 📚 Full Documentation

- **Complete Testing Guide**: `WINDOWS_TEST_GUIDE.md`
- **Installation Manual**: `INSTALLATION.md`
- **User Manual**: `USER_MANUAL.md`
- **Troubleshooting**: `LOGS_AND_TROUBLESHOOTING.md`

---

## 🔗 Download Links

| Version | Status | Download |
|---------|--------|----------|
| **v1.3.9** | ✅ Latest | [Download](https://github.com/phindagijimana/neuroinsight/actions/runs/19284629791) |
| v1.3.8 | ✅ Stable | [Download](https://github.com/phindagijimana/neuroinsight/actions/runs/19284222305) |
| All Releases | - | [View All](https://github.com/phindagijimana/neuroinsight/releases) |

---

**That's it!** 🎉

For detailed troubleshooting, see the full **WINDOWS_TEST_GUIDE.md**

---

**Last Updated**: November 12, 2025  
**Latest Build**: v1.3.9 ✅

