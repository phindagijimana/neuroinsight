# Simple Windows Testing Commands

**Easy copy-paste commands for testing NeuroInsight on Windows** 🪟

---

## 📥 1. Download & Verify

### Download
1. Go to: https://github.com/phindagijimana/neuroinsight/actions/runs/19284629791
2. Scroll down → "Artifacts" → Download **neuroinsight-windows**
3. Extract the zip file

### Verify Checksum (Copy-Paste in PowerShell)
```powershell
cd ~\Downloads\neuroinsight-windows
$expected = (Get-Content checksums-windows.txt).Split()[0]
$actual = (Get-FileHash "NeuroInsight-Setup-*.exe" -Algorithm SHA256).Hash
if ($expected -eq $actual) { Write-Host "✅ Safe to install" -ForegroundColor Green } else { Write-Host "❌ DO NOT INSTALL!" -ForegroundColor Red }
```

---

## ⚙️ 2. Install
```powershell
# Run the installer
.\NeuroInsight-Setup-1.3.8.exe

# Click "More info" → "Run anyway" when SmartScreen appears
# Follow installer prompts
```

---

## 🚀 3. Launch App
```powershell
# Start the app
& "C:\Program Files\NeuroInsight\NeuroInsight.exe"
```

---

## ✅ 4. Quick Tests

### Check if Running
```powershell
Get-Process | Where-Object { $_.ProcessName -like "*neuroinsight*" }
```

**Expected:** Should show NeuroInsight and neuroinsight-backend processes

### Check Logs
```powershell
# View last 20 lines of main log
Get-Content "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Tail 20
```

### Check for Errors
```powershell
# View errors (if any)
Get-Content "$env:APPDATA\neuroinsight\logs\errors.log"
```

### Open Log Folder
```powershell
# Open logs in Explorer
explorer "$env:APPDATA\neuroinsight\logs"
```

---

## 🔍 5. Verify It's Working

### Check Frontend Loaded
```powershell
Select-String -Path "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Pattern "Loading frontend" | Select-Object -Last 1
```

**Expected:** Should show path ending with `\frontend\index.html` (not `\src\frontend\`)

### Check Backend Started
```powershell
Select-String -Path "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Pattern "Backend" | Select-Object -Last 3
```

**Expected:** Should see "Backend is ready" or "Backend started on port 5000"

---

## 📊 6. System Checks

### Check Available Memory
```powershell
$mem = Get-CimInstance Win32_OperatingSystem
[math]::Round($mem.FreePhysicalMemory/1MB, 2)
```

**Need:** At least 8 GB free

### Check Disk Space
```powershell
Get-PSDrive C | Select-Object @{N="Free (GB)";E={[math]::Round($_.Free/1GB, 2)}}
```

**Need:** At least 10 GB free

### Check App Memory Usage
```powershell
Get-Process "NeuroInsight" -ErrorAction SilentlyContinue | Select-Object Name, @{N="Memory (MB)";E={[math]::Round($_.WS/1MB, 2)}}
```

---

## 🛑 7. Stop/Restart

### Stop App
```powershell
Stop-Process -Name "NeuroInsight" -Force
Stop-Process -Name "neuroinsight-backend" -Force -ErrorAction SilentlyContinue
```

### Restart App
```powershell
& "C:\Program Files\NeuroInsight\NeuroInsight.exe"
```

---

## 🧪 8. Complete Test (Copy All)

```powershell
Write-Host "`n=== NeuroInsight Windows Test ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Installation
Write-Host "1. Checking installation..." -ForegroundColor Yellow
if (Test-Path "C:\Program Files\NeuroInsight\NeuroInsight.exe") {
    Write-Host "   ✅ Installed" -ForegroundColor Green
} else {
    Write-Host "   ❌ Not installed" -ForegroundColor Red
}

# Test 2: Logs
Write-Host "`n2. Checking logs..." -ForegroundColor Yellow
if (Test-Path "$env:APPDATA\neuroinsight\logs") {
    Write-Host "   ✅ Logs exist" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  No logs (app not run yet?)" -ForegroundColor Yellow
}

# Test 3: Running
Write-Host "`n3. Checking if running..." -ForegroundColor Yellow
$running = Get-Process "NeuroInsight" -ErrorAction SilentlyContinue
if ($running) {
    Write-Host "   ✅ Running (PID: $($running.Id))" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Not running" -ForegroundColor Yellow
}

# Test 4: Errors
Write-Host "`n4. Checking for errors..." -ForegroundColor Yellow
$errorLog = "$env:APPDATA\neuroinsight\logs\errors.log"
if (Test-Path $errorLog) {
    $errors = Get-Content $errorLog -ErrorAction SilentlyContinue
    if ($errors) {
        Write-Host "   ⚠️  Errors found:" -ForegroundColor Yellow
        $errors | Select-Object -Last 3
    } else {
        Write-Host "   ✅ No errors" -ForegroundColor Green
    }
} else {
    Write-Host "   ✅ No error log" -ForegroundColor Green
}

# Test 5: Memory
Write-Host "`n5. Checking memory..." -ForegroundColor Yellow
$freeMem = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB, 2)
Write-Host "   Free Memory: $freeMem GB" -ForegroundColor Cyan
if ($freeMem -gt 8) {
    Write-Host "   ✅ Sufficient memory" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Low memory" -ForegroundColor Yellow
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""
```

---

## 🗑️ 9. Uninstall (if needed)

```powershell
# Uninstall via Windows Settings
start ms-settings:appsfeatures

# Or via Control Panel
appwiz.cpl

# Then manually remove data:
Remove-Item -Path "$env:APPDATA\neuroinsight" -Recurse -Force -ErrorAction SilentlyContinue
```

---

## 📝 10. Generate Diagnostic Report

```powershell
$report = @"
=== NeuroInsight Diagnostic Report ===
Date: $(Get-Date)
Windows: $(Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty Caption)

--- Installation ---
Installed: $(Test-Path 'C:\Program Files\NeuroInsight\NeuroInsight.exe')

--- Running ---
$(Get-Process | Where-Object { $_.ProcessName -like '*neuroinsight*' } | Format-Table Name, Id, @{N='Memory(MB)';E={[math]::Round($_.WS/1MB,2)}} | Out-String)

--- Recent Log (Last 10 lines) ---
$(Get-Content "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Tail 10 -ErrorAction SilentlyContinue)

--- Errors (Last 5 lines) ---
$(Get-Content "$env:APPDATA\neuroinsight\logs\errors.log" -Tail 5 -ErrorAction SilentlyContinue)

--- System Resources ---
Free Memory: $([math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)) GB
Free Disk: $((Get-PSDrive C).Free / 1GB -as [int]) GB

=== End Report ===
"@

$report | Out-File -FilePath "$env:USERPROFILE\Desktop\neuroinsight-report.txt"
Write-Host "Report saved to Desktop\neuroinsight-report.txt" -ForegroundColor Green
```

---

## 🎯 Common Issues & Quick Fixes

### App Won't Start
```powershell
# Add Windows Defender exclusion
Add-MpPreference -ExclusionPath "C:\Program Files\NeuroInsight"
```

### Black Window (Frontend Not Loading)
```powershell
# Check frontend path
Select-String -Path "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Pattern "Loading frontend" | Select-Object -Last 1
```
If it shows `\src\frontend\`, download latest version (v1.3.9+)

### Backend Won't Start
```powershell
# Check if port 5000 is in use
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
```
If something is using it, close that app

---

## 📋 Quick Test Checklist

```powershell
# Copy-paste this entire block:
Write-Host "`n📋 Quick Checklist:" -ForegroundColor Cyan
Write-Host "[ ] Downloaded artifact from GitHub Actions"
Write-Host "[ ] Verified checksum (ran verification command)"
Write-Host "[ ] Installed successfully"
Write-Host "[ ] App launches"
Write-Host "[ ] Main window shows 3 tabs"
Write-Host "[ ] Status bar says 'Backend: Ready'"
Write-Host "[ ] No black/dark window"
Write-Host "[ ] Logs accessible (check command above)"
Write-Host "[ ] No errors in error log"
Write-Host ""
```

---

## 🔗 Quick Links

- **Latest Build**: https://github.com/phindagijimana/neuroinsight/actions/runs/19284629791
- **All Actions**: https://github.com/phindagijimana/neuroinsight/actions
- **Releases**: https://github.com/phindagijimana/neuroinsight/releases

---

## 💡 Pro Tips

1. **Run PowerShell as Administrator** for some commands
2. **Use Tab completion** - type `Get-Pro` and press Tab
3. **Copy whole code blocks** - they're tested and work
4. **Save the diagnostic report** - useful for bug reports

---

**Last Updated**: November 12, 2025  
**Version**: 1.3.9  
**All commands tested on Windows 10/11**

---

**Print this page for quick reference! 📄**


