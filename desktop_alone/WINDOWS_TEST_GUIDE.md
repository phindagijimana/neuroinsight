# Windows Testing Guide - NeuroInsight Desktop

**Complete guide for testing NeuroInsight on Windows PC**

---

## 📥 1. Download the Latest Build

### From GitHub Actions (Latest: v1.3.9)

1. **Go to Actions page**:
   ```
   https://github.com/phindagijimana/neuroinsight/actions
   ```

2. **Find the latest successful workflow**:
   - Look for: "Desktop Build v15 - Fixed (Frontend Bundled)"
   - Status: ✅ Completed
   - Latest: Run #19284629791 (v1.3.9)

3. **Download Windows artifact**:
   - Scroll to bottom of workflow run page
   - Under "Artifacts" section
   - Download: **neuroinsight-windows** (0.20 GB)
   - URL: https://github.com/phindagijimana/neuroinsight/actions/runs/19284629791

4. **Extract the installer**:
   ```powershell
   # In PowerShell or File Explorer
   # Right-click → Extract All
   
   # You'll get TWO files:
   # - NeuroInsight-Setup-1.3.8.exe (the installer)
   # - checksums-windows.txt (for verification) ← Important!
   ```

---

## 🔒 2. Verify Download (REQUIRED - Security Best Practice)

### Where is the Checksum File?

**The checksum file is included in the artifact zip!**

```
neuroinsight-windows.zip
├── NeuroInsight-Setup-1.3.8.exe      ← The installer
└── checksums-windows.txt              ← The checksum file
```

After extracting, you'll have BOTH files in the same folder.

### Check SHA256 Checksum

In PowerShell:

```powershell
# Navigate to download folder
cd ~\Downloads\neuroinsight-windows

# Calculate SHA256
Get-FileHash "NeuroInsight Setup 1.3.8.exe" -Algorithm SHA256

# Or if filename is different:
Get-FileHash NeuroInsight*Setup*.exe -Algorithm SHA256
```

Compare the hash with `checksums-windows.txt` (included in the zip file):

```powershell
# View the expected checksum
Get-Content checksums-windows.txt
```

Hashes should match! ✅

---

## ⚙️ 3. Install NeuroInsight

### Run the Installer

1. **Double-click** the `.exe` file:
   ```
   NeuroInsight-Setup-1.3.8.exe
   ```

2. **Handle Windows SmartScreen warning**:
   
   ⚠️ **You'll see**: "Windows protected your PC"
   
   This is expected for unsigned apps. To proceed:
   - Click **"More info"**
   - Click **"Run anyway"**

3. **Follow installation wizard**:
   - Click "Next"
   - Choose install location (default: `C:\Program Files\NeuroInsight`)
   - Click "Install"
   - Wait for installation (~3-5 minutes)

4. **Launch after install**:
   - Check "Launch NeuroInsight" checkbox
   - Click "Finish"
   - Or launch from Start Menu

---

## 🧪 4. Test the Application

### Basic Functionality Tests

#### Test 1: Application Starts
```powershell
# Launch from Start Menu
# Or from PowerShell:
& "C:\Program Files\NeuroInsight\NeuroInsight.exe"
```

**Expected**:
- ✅ Splash screen appears
- ✅ Main window opens (~5-10 seconds)
- ✅ Three tabs visible: Jobs, Stats, Viewer

**If fails**: See troubleshooting section below

---

#### Test 2: Check Backend Status

**In the app**:
1. The application should show "Backend: Ready" in the status bar
2. If you see "Backend: Starting..." for more than 30 seconds, check logs

---

#### Test 3: Upload Test File

1. **Prepare test data**:
   - Get a T1-weighted MRI scan (`.nii` or `.nii.gz` format)
   - Or use sample data if available

2. **Upload**:
   - Click "Upload File" button
   - Select your MRI file
   - Enter patient info (optional)

3. **Process**:
   - Click "Process" button
   - Watch progress bar
   - Expected time: 5-10 min (GPU) or 1-2 hours (CPU)

**Expected**:
- ✅ Progress bar shows stages (1/11 → 11/11)
- ✅ Status updates in real-time
- ✅ No errors in status messages

---

## 📊 5. View Logs

### Access Logs - Method 1 (Through App)

1. In NeuroInsight: **Help** → **View Logs**
2. Or press: `Ctrl+L`
3. Log folder opens in File Explorer

### Access Logs - Method 2 (PowerShell)

```powershell
# Navigate to logs directory
cd "$env:APPDATA\neuroinsight\logs"

# List log files
Get-ChildItem

# View main log (last 30 lines)
Get-Content neuroinsight.log -Tail 30

# View errors only
Get-Content errors.log

# View crashes (if any)
Get-Content crashes.log
```

### Access Logs - Method 3 (File Explorer)

1. Press `Win+R`
2. Type: `%APPDATA%\neuroinsight\logs`
3. Press Enter

**Log files you'll find**:
```
C:\Users\[YourUsername]\AppData\Roaming\neuroinsight\logs\
├── neuroinsight.log  (Main log - all events)
├── errors.log        (Errors only)
└── crashes.log       (Critical failures)
```

---

## 🔍 6. Debugging Commands

### Check if Backend is Running

```powershell
# Check for backend process
Get-Process | Where-Object { $_.ProcessName -like "*neuroinsight*" }
```

**Expected output**:
```
NPM(K)    PM(M)      WS(M)     CPU(s)     Id  SI ProcessName
------    -----      -----     ------     --  -- -----------
    0    250.00     280.00       0.50   1234   1 neuroinsight-backend
    0    180.00     220.00       1.20   5678   1 NeuroInsight
```

### Check Backend Logs

```powershell
# View backend log
Get-Content "$env:APPDATA\neuroinsight\backend.log" -Tail 50
```

### Check for Key Errors in Logs

```powershell
# Search for critical errors
Select-String -Path "$env:APPDATA\neuroinsight\logs\*.log" -Pattern "ERROR|CRASH|Failed" | Select-Object -Last 10
```

### Check Frontend Loading

```powershell
# Search for frontend loading messages
Select-String -Path "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Pattern "Loading frontend|Frontend loaded|Failed to load"
```

**What to look for**:
```
✅ "Loading frontend from: ...\\frontend\\index.html"
✅ "Frontend loaded successfully"
✅ "Application window shown"

❌ "Failed to load frontend: ERR_FILE_NOT_FOUND"
❌ "Loading frontend from: ...\\src\\frontend\\..."  (wrong path!)
```

### Verify Installation Integrity

```powershell
# Check if all required files exist
cd "C:\Program Files\NeuroInsight"

# Check main executable
Test-Path "NeuroInsight.exe"

# Check resources
Test-Path "resources\app.asar"

# Check if backend is bundled
Test-Path "resources\neuroinsight-backend"
```

All should return `True` ✅

---

## 🛠️ 7. Troubleshooting

### Issue 1: Application Won't Start

**Symptoms**:
- Double-click does nothing
- Window briefly appears then closes
- "Application Error" message

**Solutions**:

1. **Run as Administrator**:
   ```powershell
   # Right-click NeuroInsight.exe → Run as administrator
   ```

2. **Check Windows Defender**:
   ```powershell
   # Add exclusion in Windows Security
   # Settings → Update & Security → Windows Security → Virus & threat protection
   # → Manage settings → Add exclusion → Folder
   # Add: C:\Program Files\NeuroInsight
   ```

3. **Check logs for errors**:
   ```powershell
   Get-Content "$env:APPDATA\neuroinsight\logs\crashes.log"
   ```

4. **Run from PowerShell to see errors**:
   ```powershell
   & "C:\Program Files\NeuroInsight\NeuroInsight.exe"
   # Watch for any error messages in console
   ```

---

### Issue 2: Dark/Black Window (Frontend Not Loading)

**Symptoms**:
- Window opens but shows black/dark screen
- No UI elements visible
- Title bar shows "NeuroInsight" but content is blank

**Diagnosis**:

```powershell
# Check if frontend is loaded
Select-String -Path "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Pattern "Loading frontend"
```

**If you see**:
```
Loading frontend from: ...\\src\\frontend\\index.html  ❌ WRONG PATH
```

**Solution**: This is an old build. Download the **latest build** (v1.3.9 or later) which has the frontend path fixed.

---

### Issue 3: Backend Fails to Start

**Symptoms**:
- Status bar shows "Backend: Failed" or "Backend: Error"
- Processing doesn't work
- Errors about "Cannot connect to backend"

**Solutions**:

1. **Check if Python dependencies are missing**:
   ```powershell
   # View backend log
   Get-Content "$env:APPDATA\neuroinsight\backend.log" -Tail 50
   ```

2. **Check antivirus blocking**:
   - Windows Defender might block the backend executable
   - Add exclusion for `neuroinsight-backend.exe`

3. **Check port conflict**:
   ```powershell
   # Check if port 5000 is in use
   Get-NetTCPConnection -LocalPort 5000
   ```
   If something else is using port 5000, close that application.

4. **Restart the application**:
   - Close NeuroInsight completely
   - End all processes:
   ```powershell
   Stop-Process -Name "NeuroInsight" -Force
   Stop-Process -Name "neuroinsight-backend" -Force
   ```
   - Relaunch

---

### Issue 4: Processing Fails or Crashes

**Symptoms**:
- Progress bar gets stuck
- "Processing failed" error
- Application crashes during processing

**Check**:

1. **Memory available**:
   ```powershell
   # Check free memory
   Get-CimInstance Win32_OperatingSystem | Select-Object FreePhysicalMemory, TotalVisibleMemorySize
   ```
   Need at least **8 GB free** (8388608 KB)

2. **Disk space**:
   ```powershell
   # Check free disk space
   Get-PSDrive C
   ```
   Need at least **10 GB free**

3. **Input file validity**:
   - Ensure file is T1-weighted MRI
   - Check file isn't corrupted
   - Try with a different scan

4. **View processing errors**:
   ```powershell
   Select-String -Path "$env:APPDATA\neuroinsight\logs\errors.log" -Pattern "Processing|FastSurfer|Failed"
   ```

---

### Issue 5: Slow Performance

**Expected times**:
- **With GPU**: 5-10 minutes
- **With CPU only**: 1-2 hours

**Check GPU availability**:

```powershell
# Check if NVIDIA GPU detected
nvidia-smi
```

If GPU not found or CUDA not available, processing will use CPU (much slower).

---

## 📋 8. Complete Diagnostic Sequence

Run these commands in PowerShell to diagnose issues:

```powershell
# 1. Check if app is installed
Test-Path "C:\Program Files\NeuroInsight\NeuroInsight.exe"

# 2. Check log directory exists
Test-Path "$env:APPDATA\neuroinsight\logs"

# 3. View recent errors
Get-Content "$env:APPDATA\neuroinsight\logs\errors.log" -Tail 20

# 4. Check running processes
Get-Process | Where-Object { $_.ProcessName -like "*neuroinsight*" }

# 5. Check frontend loading
Select-String -Path "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Pattern "Loading frontend" | Select-Object -Last 1

# 6. Check backend status
Select-String -Path "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Pattern "Backend is ready|Backend failed" | Select-Object -Last 1

# 7. Check memory
Get-CimInstance Win32_OperatingSystem | Select-Object @{Name="FreeMemoryGB";Expression={[math]::Round($_.FreePhysicalMemory/1MB,2)}}

# 8. Check disk space
Get-PSDrive C | Select-Object Used,Free
```

---

## 📤 9. Reporting Test Results

### If Everything Works ✅

Report success with:
1. ✅ Version tested: v1.3.9
2. ✅ Windows version: (run `winver`)
3. ✅ Installation: Successful
4. ✅ Application starts: Yes
5. ✅ Backend status: Ready
6. ✅ Processing test: (if you ran one) Successful

### If Issues Occur ❌

**Collect diagnostic information**:

```powershell
# Create a diagnostic report
$report = @"
=== NeuroInsight Test Report ===
Date: $(Get-Date)
Windows Version: $(Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty Caption)
Build: $(Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty BuildNumber)

=== Installation ===
Install Path: C:\Program Files\NeuroInsight
Installed: $(Test-Path 'C:\Program Files\NeuroInsight\NeuroInsight.exe')

=== Processes ===
$(Get-Process | Where-Object { $_.ProcessName -like '*neuroinsight*' } | Format-Table -AutoSize | Out-String)

=== Recent Errors ===
$(Get-Content "$env:APPDATA\neuroinsight\logs\errors.log" -Tail 20 -ErrorAction SilentlyContinue)

=== Frontend Status ===
$(Select-String -Path "$env:APPDATA\neuroinsight\logs\neuroinsight.log" -Pattern "Loading frontend|Frontend loaded|Failed to load" -ErrorAction SilentlyContinue | Select-Object -Last 5 | Out-String)

=== System Resources ===
Free Memory: $(Get-CimInstance Win32_OperatingSystem | ForEach-Object { [math]::Round($_.FreePhysicalMemory/1MB,2) }) GB
Free Disk: $(Get-PSDrive C | ForEach-Object { [math]::Round($_.Free/1GB,2) }) GB
"@

# Save report
$report | Out-File -FilePath "$env:USERPROFILE\Desktop\neuroinsight-test-report.txt"

Write-Host "Report saved to Desktop: neuroinsight-test-report.txt"
```

**Then share**:
1. The diagnostic report
2. The log files from `%APPDATA%\neuroinsight\logs\`
3. Screenshots of any error messages

---

## 🔗 10. Useful Links

| Resource | URL |
|----------|-----|
| **Latest Build** | https://github.com/phindagijimana/neuroinsight/actions/runs/19284629791 |
| **All Releases** | https://github.com/phindagijimana/neuroinsight/releases |
| **Report Issues** | https://github.com/phindagijimana/neuroinsight/issues |
| **Installation Guide** | `desktop_alone/INSTALLATION.md` |
| **User Manual** | `desktop_alone/USER_MANUAL.md` |

---

## 🎯 Quick Test Checklist

Use this checklist for quick testing:

- [ ] Downloaded Windows artifact (neuroinsight-windows.zip)
- [ ] Verified SHA256 checksum matches
- [ ] Ran installer (bypassed SmartScreen if needed)
- [ ] Application launches successfully
- [ ] Main window appears (3 tabs visible)
- [ ] Backend status shows "Ready"
- [ ] Frontend loads (not black screen)
- [ ] Can upload a file
- [ ] Can start processing (optional - takes time)
- [ ] Logs are accessible via Ctrl+L
- [ ] No critical errors in error logs

---

## 💡 Pro Tips

### Tip 1: Test on Clean System
- Test on a Windows VM or clean install
- Ensures no dependency conflicts
- Mimics end-user experience

### Tip 2: Test Without GPU
- Test on system without NVIDIA GPU
- Ensures CPU fallback works
- Many users won't have GPU

### Tip 3: Monitor Resource Usage
```powershell
# Watch memory usage during processing
while ($true) { 
    Get-Process "neuroinsight*" | Select-Object Name, @{N="MemoryMB";E={[math]::Round($_.WS/1MB,2)}}
    Start-Sleep -Seconds 5 
}
```

### Tip 4: Keep Logs
- Save logs from successful AND failed runs
- Compare to identify patterns
- Archive with build version number

---

## 🧹 11. Clean Uninstall (If Needed)

### Complete Removal

```powershell
# 1. Uninstall via Control Panel
# Settings → Apps → NeuroInsight → Uninstall

# 2. Or uninstall via PowerShell
$uninstaller = "C:\Program Files\NeuroInsight\Uninstall NeuroInsight.exe"
if (Test-Path $uninstaller) {
    Start-Process -FilePath $uninstaller -Wait
}

# 3. Remove application data
Remove-Item -Path "$env:APPDATA\neuroinsight" -Recurse -Force -ErrorAction SilentlyContinue

# 4. Remove local data
Remove-Item -Path "$env:LOCALAPPDATA\neuroinsight" -Recurse -Force -ErrorAction SilentlyContinue

# 5. Clean registry (optional - advanced)
# Run as Administrator
Remove-Item -Path "HKCU:\Software\neuroinsight" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "NeuroInsight completely removed!" -ForegroundColor Green
```

---

**Last Updated**: November 12, 2025  
**Latest Version**: v1.3.9  
**Platform**: Windows 10/11 (64-bit)

---

**Happy Testing! 🧪🖥️**

