# Windows Cleanup & Log Commands - Quick Reference

**For testing NeuroInsight Desktop app on Windows**

---

## 🧹 Quick Cleanup Commands (Copy-Paste)

### **1. Complete Cleanup (Fresh Start - Removes ALL data including logs)**
**Run in PowerShell (as Administrator recommended):**

```powershell
# Stop the app
Get-Process -Name "NeuroInsight" -ErrorAction SilentlyContinue | Stop-Process -Force

# Remove app data (settings)
Remove-Item -Path "$env:APPDATA\NeuroInsight" -Recurse -Force -ErrorAction SilentlyContinue

# Remove local app data (includes database & uploads)
Remove-Item -Path "$env:LOCALAPPDATA\NeuroInsight" -Recurse -Force -ErrorAction SilentlyContinue

# Remove logs from previous versions
Remove-Item -Path "$env:USERPROFILE\AppData\Roaming\NeuroInsight" -Recurse -Force -ErrorAction SilentlyContinue

# Remove temp files
Remove-Item -Path "$env:TEMP\NeuroInsight*" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✅ Complete cleanup done! All data & logs removed." -ForegroundColor Green
```

**What this removes:**
- ✅ All logs (main.log, errors.log, crashes.log)
- ✅ Database (neuroinsight.db)
- ✅ Uploaded files
- ✅ Processing outputs
- ✅ User settings
- ✅ Temporary files
- ❌ Does NOT uninstall the app itself

---

### **2. Minimal Cleanup (Keep Logs for Debugging)**
**Clear only test data, preserve logs:**

```powershell
# Stop app
Get-Process -Name "NeuroInsight" -ErrorAction SilentlyContinue | Stop-Process -Force

# Clear database only
Remove-Item "$env:LOCALAPPDATA\NeuroInsight\neuroinsight.db" -Force -ErrorAction SilentlyContinue

# Clear uploads only
Remove-Item "$env:LOCALAPPDATA\NeuroInsight\uploads\*" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✅ Test data cleared (logs preserved)" -ForegroundColor Green
```

**What this keeps:**
- ✅ Logs (useful for debugging)
- ✅ Installed app
- ❌ Removes database (fresh start for testing)
- ❌ Removes uploads (free space)

---

### **3. Logs Only Cleanup (Start with Clean Log File)**
**Remove old logs to see only new session data:**

```powershell
# Stop app
Get-Process -Name "NeuroInsight" -ErrorAction SilentlyContinue | Stop-Process -Force

# Remove all old logs
Remove-Item "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\*.log" -Force -ErrorAction SilentlyContinue

Write-Host "✅ Logs cleared (next run will create fresh log files)" -ForegroundColor Green
```

**When to use this:**
- You want to see only the current test session in logs
- Old logs are too large or confusing
- You're comparing behavior between versions

---

## 📊 **Cleanup Comparison Table**

| What Gets Removed | Complete Cleanup (#1) | Minimal Cleanup (#2) | Logs Only (#3) |
|-------------------|:---------------------:|:--------------------:|:--------------:|
| **Logs** (main.log, errors.log) | ✅ YES | ❌ NO (kept) | ✅ YES |
| **Database** (neuroinsight.db) | ✅ YES | ✅ YES | ❌ NO |
| **Uploads** (uploaded MRI files) | ✅ YES | ✅ YES | ❌ NO |
| **Outputs** (processing results) | ✅ YES | ❌ NO | ❌ NO |
| **Settings** (config.json) | ✅ YES | ❌ NO | ❌ NO |
| **Temp Files** | ✅ YES | ❌ NO | ❌ NO |
| **Installed App** | ❌ NO | ❌ NO | ❌ NO |

**Recommendation for testing new versions:**
- Use **Complete Cleanup (#1)** before installing new version
- Use **Logs Only (#3)** to get clean log output for each test session

---

### **4. Check Current Logs**
**View the main application log:**

```powershell
# View last 50 lines
Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" -Tail 50

# View full log
Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log"

# Search for errors
Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" | Select-String -Pattern "error|ERROR|failed|Failed"

# Search for upload issues
Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" | Select-String -Pattern "upload|400|validation"
```

---

### **5. Check What's Installed**

```powershell
# Check installed version
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | 
    Where-Object { $_.DisplayName -like "*NeuroInsight*" } | 
    Select-Object DisplayName, DisplayVersion, InstallLocation

# Check if app is running
Get-Process | Where-Object { $_.ProcessName -like "*NeuroInsight*" }

# Check backend process
Get-Process | Where-Object { $_.ProcessName -like "*neuroinsight-backend*" }
```

---

### **6. Check Data Storage Size**

```powershell
# Check how much space is being used
Get-ChildItem -Path "$env:LOCALAPPDATA\NeuroInsight" -Recurse -ErrorAction SilentlyContinue | 
    Measure-Object -Property Length -Sum | 
    Select-Object @{Name="Size(MB)"; Expression={[math]::Round($_.Sum / 1MB, 2)}}

# List all data files
Get-ChildItem -Path "$env:LOCALAPPDATA\NeuroInsight" -Recurse -ErrorAction SilentlyContinue | 
    Select-Object FullName, @{Name="Size(MB)"; Expression={[math]::Round($_.Length / 1MB, 2)}}
```

---

### **7. Verify Installation**

```powershell
# Check if executable exists
Test-Path "$env:LOCALAPPDATA\Programs\NeuroInsight\NeuroInsight.exe"

# Check backend bundle
Test-Path "$env:LOCALAPPDATA\Programs\NeuroInsight\resources\backend\neuroinsight-backend.exe"

# Check frontend files
Test-Path "$env:LOCALAPPDATA\Programs\NeuroInsight\resources\frontend\index.html"
```

---

## 📋 Complete Diagnostic Sequence

Run these in order to diagnose issues:

```powershell
# 1. Check what version is installed
$app = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | 
    Where-Object { $_.DisplayName -like "*NeuroInsight*" }
Write-Host "Installed Version: $($app.DisplayVersion)" -ForegroundColor Cyan

# 2. Check if app is running
$proc = Get-Process -Name "NeuroInsight" -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "✓ App is running (PID: $($proc.Id))" -ForegroundColor Green
} else {
    Write-Host "✗ App is NOT running" -ForegroundColor Red
}

# 3. Check backend process
$backend = Get-Process -Name "neuroinsight-backend" -ErrorAction SilentlyContinue
if ($backend) {
    Write-Host "✓ Backend is running (PID: $($backend.Id))" -ForegroundColor Green
} else {
    Write-Host "✗ Backend is NOT running" -ForegroundColor Yellow
}

# 4. Check logs for upload errors
Write-Host "`nChecking logs for upload errors..." -ForegroundColor Cyan
Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" -ErrorAction SilentlyContinue | 
    Select-String -Pattern "upload_received|400 Bad Request|validation" | 
    Select-Object -Last 10

# 5. Check database
if (Test-Path "$env:LOCALAPPDATA\NeuroInsight\neuroinsight.db") {
    $dbSize = (Get-Item "$env:LOCALAPPDATA\NeuroInsight\neuroinsight.db").Length / 1KB
    Write-Host "✓ Database exists ($([math]::Round($dbSize, 2)) KB)" -ForegroundColor Green
} else {
    Write-Host "✗ Database NOT found" -ForegroundColor Red
}
```

---

## 🎯 Key Indicators

### ✅ **App is WORKING if you see:**
```
Backend is ready!
Loading frontend from: ...resources\frontend\index.html
Frontend loaded successfully
Application window shown
```

### ❌ **App has ISSUES if you see:**
```
Failed to load frontend: ERR_FILE_NOT_FOUND
Backend failed to start
upload_received ... 400 Bad Request  ← Upload validation failing
```

---

## 🔧 Your Current Issue

**From your logs:**
```
upload_received filename=sub-268_T1w.nii size_bytes=44564832
INFO: 127.0.0.1:54239 - "POST /upload/ HTTP/1.1" 400 Bad Request
```

**This means:**
- ✅ Backend is running
- ✅ Upload endpoint is receiving files
- ❌ Validation is rejecting them (silently - no error details)
- ❌ You need v1.3.10+ to see WHY it's failing

---

## 📥 Download & Install Latest Build

### **Step 1: Check for v1.3.10 build**

```powershell
# Open GitHub Actions in browser
Start-Process "https://github.com/phindagijimana/neuroinsight/actions"
```

Look for: **desktop-v1.3.10** tag

### **Step 2: Download from Actions Artifacts**

1. Click on the workflow run with `desktop-v1.3.10` tag
2. Scroll to "Artifacts" section
3. Download: `neuroinsight-windows.zip`

### **Step 3: Extract and Install**

```powershell
# Extract downloaded zip
Expand-Archive -Path "Downloads\neuroinsight-windows.zip" -DestinationPath ".\neuroinsight-v1.3.10" -Force

# List contents
Get-ChildItem ".\neuroinsight-v1.3.10"

# Run installer
& ".\neuroinsight-v1.3.10\NeuroInsight Setup 1.3.10.exe"
```

---

## ⏰ Version Timeline

| Version | Upload Validation | Error Logging | Status |
|---------|-------------------|---------------|---------|
| v1.3.9 | ❌ Complex (fails silently) | ❌ No details | Your current build |
| v1.3.10 | ✅ Simple (filename-based) | ✅ Full details | **NEED THIS!** |

---

## 🚀 Complete Fresh Install Process

### **Option A: Quick Cleanup Script**

Save as `cleanup-neuroinsight.ps1`:

```powershell
$ErrorActionPreference = "SilentlyContinue"

Write-Host "`n🧹 NeuroInsight Cleanup Tool" -ForegroundColor Yellow
Write-Host "================================`n" -ForegroundColor Yellow

# Stop process
Write-Host "Stopping NeuroInsight process..." -ForegroundColor Cyan
Get-Process -Name "NeuroInsight" | Stop-Process -Force
Start-Sleep -Seconds 2
Write-Host "✓ Process stopped" -ForegroundColor Green

# Remove data directories
Write-Host "`nRemoving data directories..." -ForegroundColor Cyan

$paths = @(
    @{Path="$env:APPDATA\NeuroInsight"; Name="App Data"},
    @{Path="$env:LOCALAPPDATA\NeuroInsight"; Name="Local App Data (Database & Uploads)"},
    @{Path="$env:USERPROFILE\AppData\Roaming\NeuroInsight"; Name="Logs"},
    @{Path="$env:TEMP\NeuroInsight*"; Name="Temp Files"}
)

foreach ($item in $paths) {
    if (Test-Path $item.Path) {
        $size = (Get-ChildItem -Path $item.Path -Recurse -File -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum).Sum / 1MB
        Remove-Item -Path $item.Path -Recurse -Force
        Write-Host "✓ Removed: $($item.Name) ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
    } else {
        Write-Host "○ Not found: $($item.Name)" -ForegroundColor Gray
    }
}

Write-Host "`n✅ Cleanup complete! Ready for new build.`n" -ForegroundColor Green
```

**Run it:**
```powershell
.\cleanup-neuroinsight.ps1
```

### **Option B: One-Liner**

```powershell
Get-Process NeuroInsight -ErrorAction SilentlyContinue | Stop-Process -Force; Remove-Item -Path "$env:APPDATA\NeuroInsight","$env:LOCALAPPDATA\NeuroInsight","$env:USERPROFILE\AppData\Roaming\NeuroInsight" -Recurse -Force -ErrorAction SilentlyContinue; Write-Host "✅ Done" -ForegroundColor Green
```

---

## 📊 What Gets Cleaned

| Location | What's Stored | Typical Size |
|----------|---------------|--------------|
| `%APPDATA%\NeuroInsight` | User preferences, settings | ~1 KB |
| `%LOCALAPPDATA%\NeuroInsight` | SQLite database, uploads, processing data | 100 MB - 10 GB |
| `%USERPROFILE%\AppData\Roaming\NeuroInsight\logs` | Application logs (main.log, errors.log) | ~500 KB |
| `%TEMP%\NeuroInsight*` | Temporary processing files | Variable |
| `C:\Users\[user]\AppData\Local\Programs\NeuroInsight` | **Installed app** (DO NOT DELETE unless uninstalling) | ~7 GB |

---

## 🔍 Troubleshooting Current Build

### **Check Which Version You're Testing**

```powershell
# Method 1: Check installer name
# The installer you ran should have version in filename:
# "NeuroInsight Setup 1.3.9.exe" or "NeuroInsight Setup 1.3.10.exe"

# Method 2: Check package.json in installed app (advanced)
# This requires extracting from app.asar
```

### **Your Current Issue: Upload Validation Failing**

**What we know from your logs:**
- ✅ Backend starts successfully
- ✅ Frontend loads
- ✅ Database initialized
- ✅ Job polling works
- ❌ Upload validation rejects all files
- ❌ No error details logged

**File attempts:**
1. `sub-1_T1w.nii` (210 bytes) ← Too small, invalid file
2. `sub-268_T1w.nii` (44.5 MB) ← **VALID FILE SIZE** but still rejected!

**Why the valid file is rejected (in v1.3.9 and earlier):**
- Complex NIfTI validation tries to parse the file
- Checks voxel spacing (must be 0.2-5.0mm)
- Checks T1 markers in headers
- If ANY check fails, it rejects with no details logged

**Solution:**
- ✅ Use v1.3.10+ which has simple filename-based validation
- ✅ v1.3.10+ logs the actual error message

---

## 🚨 Critical: File to Test With

Your `sub-268_T1w.nii` (44.5 MB) **should work** with v1.3.10 because:
- ✅ Filename contains "T1" (case-insensitive)
- ✅ Has `.nii` extension
- ✅ File size is reasonable

**DO NOT use `sub-1_T1w.nii` (210 bytes)** - this file is corrupted or invalid!

---

## 📝 Testing Workflow

### **Before Each Test Session:**

```powershell
# 1. Clean up old data
Get-Process NeuroInsight -ErrorAction SilentlyContinue | Stop-Process -Force
Remove-Item "$env:LOCALAPPDATA\NeuroInsight\neuroinsight.db" -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\NeuroInsight\uploads\*" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Start fresh
& "$env:LOCALAPPDATA\Programs\NeuroInsight\NeuroInsight.exe"

# 3. Wait 10 seconds for startup
Start-Sleep -Seconds 10

# 4. Check logs
Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" -Tail 20 | 
    Select-String -Pattern "Backend is ready|Frontend loaded|ERROR|Failed"
```

### **After Upload Attempt:**

```powershell
# Check for upload errors (shows last 5 upload attempts)
Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" | 
    Select-String -Pattern "upload_received" -Context 0,2 | 
    Select-Object -Last 5
```

**Expected in v1.3.10+:**
```
upload_received filename=sub-268_T1w.nii size_bytes=44564832
upload_validation_failed detail="..." ← SHOULD SEE THIS!
INFO: 127.0.0.1:54239 - "POST /upload/ HTTP/1.1" 400 Bad Request
```

**Current in v1.3.9 and earlier:**
```
upload_received filename=sub-268_T1w.nii size_bytes=44564832
INFO: 127.0.0.1:54239 - "POST /upload/ HTTP/1.1" 400 Bad Request
```
*(Missing error details!)*

---

## 🎯 What to Check After Installing v1.3.10

### **1. Verify New Version**
```powershell
# Check version in installer filename
# Should be: "NeuroInsight Setup 1.3.10.exe"

# Or check in installed app
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | 
    Where-Object { $_.DisplayName -like "*NeuroInsight*" } | 
    Select-Object DisplayVersion
```

### **2. Test Upload with Valid File**
Use: `sub-268_T1w.nii` (44.5 MB) ✅

### **3. Check for Detailed Error (if it still fails)**
```powershell
# Look for the new error logging
Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" | 
    Select-String -Pattern "upload_validation_failed"
```

**Expected output:**
```
upload_validation_failed filename=sub-268_T1w.nii status_code=400 detail="[specific reason]"
```

Now you'll see the ACTUAL reason!

---

## 🛠️ Advanced Diagnostics

### **Check Backend API Directly**

```powershell
# Get backend port from logs
$port = (Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" | 
         Select-String -Pattern "Backend port captured: (\d+)" | 
         Select-Object -Last 1).Matches.Groups[1].Value

Write-Host "Backend running on port: $port" -ForegroundColor Cyan

# Test health endpoint
Invoke-RestMethod -Uri "http://127.0.0.1:$port/health" -Method Get

# Test jobs endpoint
Invoke-RestMethod -Uri "http://127.0.0.1:$port/jobs/" -Method Get
```

### **Monitor Logs in Real-Time**

```powershell
# Watch logs as they're written (like tail -f)
Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" -Wait -Tail 20
```

---

## 📁 Windows File Locations Reference

```
Installation:
C:\Users\[user]\AppData\Local\Programs\NeuroInsight\
  ├── NeuroInsight.exe                        (Main app)
  └── resources\
      ├── backend\
      │   └── neuroinsight-backend.exe       (Python backend ~30MB)
      └── frontend\
          └── index.html                      (Frontend files)

Data & Logs:
C:\Users\[user]\AppData\Local\NeuroInsight\
  ├── neuroinsight.db                         (SQLite database)
  ├── uploads\                                (Uploaded MRI files)
  └── outputs\                                (Processing results)

Logs:
C:\Users\[user]\AppData\Roaming\NeuroInsight\logs\
  ├── main.log                                (Main application log)
  ├── errors.log                              (Error log)
  └── crashes.log                             (Crash reports)

Settings:
C:\Users\[user]\AppData\Roaming\NeuroInsight\
  └── config.json                             (User preferences)
```

---

## 🔄 Complete Reinstall Process

### **Step 1: Full Uninstall**

```powershell
# Uninstall via Settings
Start-Process "ms-settings:appsfeatures"
# Then: Search "NeuroInsight" → Uninstall

# OR uninstall via PowerShell
$app = Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* | 
       Where-Object { $_.DisplayName -like "*NeuroInsight*" }
if ($app.UninstallString) {
    Start-Process -FilePath $app.UninstallString -Wait
}
```

### **Step 2: Clean All Data**

```powershell
# Remove all NeuroInsight data
Remove-Item -Path "$env:APPDATA\NeuroInsight" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\NeuroInsight" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:LOCALAPPDATA\Programs\NeuroInsight" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:USERPROFILE\AppData\Roaming\NeuroInsight" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:TEMP\NeuroInsight*" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "✅ Complete cleanup done" -ForegroundColor Green
```

### **Step 3: Install New Version**

```powershell
# Navigate to downloaded installer
cd ~\Downloads\neuroinsight-v1.3.10

# Run installer
& ".\NeuroInsight Setup 1.3.10.exe"
```

### **Step 4: Verify Clean Install**

```powershell
# After installing and running, check it's fresh
$dbExists = Test-Path "$env:LOCALAPPDATA\NeuroInsight\neuroinsight.db"
if ($dbExists) {
    $db = Get-Item "$env:LOCALAPPDATA\NeuroInsight\neuroinsight.db"
    $age = (Get-Date) - $db.CreationTime
    if ($age.TotalMinutes -lt 5) {
        Write-Host "✅ Fresh database created $([math]::Round($age.TotalSeconds, 0)) seconds ago" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Database is $([math]::Round($age.TotalMinutes, 1)) minutes old (may not be fresh)" -ForegroundColor Yellow
    }
}
```

---

## 📝 Quick Copy-Paste Commands

### **Cleanup Before Testing:**
```powershell
Get-Process NeuroInsight -ErrorAction SilentlyContinue | Stop-Process -Force; Remove-Item "$env:LOCALAPPDATA\NeuroInsight\neuroinsight.db","$env:LOCALAPPDATA\NeuroInsight\uploads" -Recurse -Force -ErrorAction SilentlyContinue; Write-Host "✅ Ready for test"
```

### **Check Last Upload Error:**
```powershell
Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" | Select-String -Pattern "upload|400" | Select-Object -Last 5
```

### **Check Backend Status:**
```powershell
Get-Process neuroinsight-backend -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, CPU, WorkingSet
```

### **Find Backend Port:**
```powershell
Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" | Select-String -Pattern "Backend port captured: (\d+)" | Select-Object -Last 1
```

---

## 🎓 Understanding Your Logs

### **Normal Startup Sequence:**
```
[info] NeuroInsight Desktop starting...
[info] App ready, starting backend...
[info] Backend process started (PID: XXXXX)
[info] Backend port captured: XXXXX
[info] Backend is ready!
[info] Loading frontend from: ...\resources\frontend\index.html
[info] Frontend loaded successfully
[info] Application window shown
```

### **Upload Failure Pattern (v1.3.9):**
```
[info] upload_received filename=sub-268_T1w.nii size_bytes=44564832
INFO: 127.0.0.1:XXXXX - "POST /upload/ HTTP/1.1" 400 Bad Request
```
**Problem:** No error details!

### **Upload Failure Pattern (v1.3.10+):**
```
[info] upload_received filename=sub-268_T1w.nii size_bytes=44564832
[error] upload_validation_failed filename=sub-268_T1w.nii status_code=400 detail="[reason here]"
INFO: 127.0.0.1:XXXXX - "POST /upload/ HTTP/1.1" 400 Bad Request
```
**Fixed:** Now you see WHY it failed!

---

## 📞 Common Issues & Solutions

### **Issue: Upload always fails with 400**
**Solution:**
1. Upgrade to v1.3.10+ to see error details
2. Ensure filename contains "T1" (case-insensitive)
3. Ensure file has `.nii` or `.nii.gz` extension
4. Check file is not corrupted (should be 10-50 MB typically)

### **Issue: Backend doesn't start**
**Solution:**
```powershell
# Check if backend executable exists
Test-Path "$env:LOCALAPPDATA\Programs\NeuroInsight\resources\backend\neuroinsight-backend.exe"

# Try running backend manually to see errors
& "$env:LOCALAPPDATA\Programs\NeuroInsight\resources\backend\neuroinsight-backend.exe"
```

### **Issue: Frontend shows blank/dark screen**
**Solution:**
```powershell
# Check if frontend files exist
Test-Path "$env:LOCALAPPDATA\Programs\NeuroInsight\resources\frontend\index.html"

# Check logs for frontend loading
Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" | 
    Select-String -Pattern "Loading frontend|Frontend loaded|ERR_FILE_NOT_FOUND"
```

---

## ⚡ Next Steps for Your Testing

1. **Clean up current installation:**
   ```powershell
   Get-Process NeuroInsight -ErrorAction SilentlyContinue | Stop-Process -Force
   Remove-Item "$env:LOCALAPPDATA\NeuroInsight" -Recurse -Force
   ```

2. **Check if v1.3.10 Windows build exists:**
   - Go to: https://github.com/phindagijimana/neuroinsight/actions
   - Look for workflow run with `desktop-v1.3.10` tag
   - Download `neuroinsight-windows` artifact

3. **Install v1.3.10 and test with `sub-268_T1w.nii` (44.5 MB file)**

4. **Check logs for detailed error message:**
   ```powershell
   Get-Content "$env:USERPROFILE\AppData\Roaming\NeuroInsight\logs\main.log" | 
       Select-String -Pattern "upload_validation_failed"
   ```

---

**Last Updated**: November 12, 2025  
**Current Build Tested**: v1.3.9 (upload validation failing)  
**Recommended Version**: v1.3.10+ (has error logging)  
**Next Action**: Download v1.3.10 Windows build from GitHub Actions

