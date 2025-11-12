# Platform Testing Checklist
## Windows, macOS, Linux Compatibility Verification

**Version:** 1.3.12+  
**Purpose:** Ensure desktop app works correctly on all platforms  
**Last Updated:** November 12, 2025

---

## 🎯 **Testing Strategy**

### **Automated Testing (CI/CD)**
✅ GitHub Actions builds on all 3 platforms automatically  
✅ Each platform builds on its native OS  
✅ Build artifacts tested for correct structure  

### **Manual Testing Required**
- [ ] Windows 10/11 (x64)
- [ ] macOS Intel (x64)
- [ ] macOS Apple Silicon (ARM64)
- [ ] Linux Ubuntu 20.04+ (x64)

---

## 🪟 **Windows Testing (v1.3.12)**

### **Environment Setup**
- [ ] Windows 10 or 11 (64-bit)
- [ ] Docker Desktop installed and running
- [ ] Clean system (no previous versions)

### **Installation**
- [ ] Download `NeuroInsight Setup 1.3.12.exe` from GitHub Actions
- [ ] Run installer (NSIS)
- [ ] Installer completes without errors
- [ ] Desktop shortcut created
- [ ] Start Menu entry created
- [ ] App installed to `C:\Users\<user>\AppData\Local\Programs\NeuroInsight`

### **Launch**
- [ ] Double-click app icon
- [ ] No Windows Defender/antivirus warnings
- [ ] Splash screen appears
- [ ] Backend starts (check Task Manager for `neuroinsight-backend.exe`)
- [ ] Main window appears within 30 seconds
- [ ] No error dialogs

### **Backend Verification**
```powershell
# Check backend process
Get-Process | Where-Object {$_.ProcessName -like "*neuroinsight*"}

# Check logs
Get-Content "$env:APPDATA\NeuroInsight\logs\main.log" -Tail 20

# Verify paths exist
Test-Path "$env:USERPROFILE\Documents\NeuroInsight\uploads"
Test-Path "$env:USERPROFILE\Documents\NeuroInsight\outputs"
```

- [ ] Backend process running
- [ ] No errors in `main.log`
- [ ] Upload/output directories created
- [ ] Database file exists: `%APPDATA%\NeuroInsight\neuroinsight.db`

### **Upload Test**
- [ ] Select T1-weighted MRI file (e.g., `sub-268_T1w.nii`)
- [ ] Upload starts immediately
- [ ] Progress bar shows uploading
- [ ] File saves to `Documents\NeuroInsight\uploads\`

### **Processing Test (CRITICAL for v1.3.12)**
```powershell
# Watch logs during processing
Get-Content "$env:APPDATA\NeuroInsight\logs\main.log" -Wait | 
    Select-String -Pattern "desktop_mode_paths|fastsurfer|mock_data"
```

**Expected behavior:**
- [ ] Log shows: `desktop_mode_paths` with Windows paths (C:\Users\...)
- [ ] Log shows: `fastsurfer_image_downloaded` or existing image
- [ ] Log shows: `executing_fastsurfer` with Docker command
- [ ] **NO** `using_mock_data` error
- [ ] **NO** `module 'os' has no attribute` errors
- [ ] Progress updates: 20% → 65% → 70% → 100%
- [ ] Job completes with status "COMPLETED"

### **Results Verification**
- [ ] Metrics displayed in UI
- [ ] Left/Right volumes are NOT 3500/3800 (mock data)
- [ ] Asymmetry index calculated
- [ ] Results saved to `Documents\NeuroInsight\outputs\<job-id>\`
- [ ] CSV and JSON files created

### **Cleanup Test**
```powershell
# Close app
Get-Process NeuroInsight | Stop-Process

# Verify clean shutdown
Get-Process | Where-Object {$_.ProcessName -like "*neuroinsight*"}
```

- [ ] App closes gracefully
- [ ] Backend process terminates
- [ ] No zombie processes
- [ ] Logs show normal shutdown

---

## 🍎 **macOS Testing**

### **Environment Setup**
- [ ] macOS 10.15+ (Catalina or newer)
- [ ] Docker Desktop installed and running
- [ ] Test on Intel (x64) if possible
- [ ] Test on Apple Silicon (ARM64) if possible

### **Installation**
- [ ] Download `NeuroInsight-1.3.12.dmg` from GitHub Actions
- [ ] Open DMG file
- [ ] Drag to Applications folder
- [ ] Eject DMG
- [ ] First launch: Right-click → Open (bypass Gatekeeper)
- [ ] Click "Open" on security dialog

### **Launch**
- [ ] App opens from Applications folder
- [ ] No "App is damaged" error
- [ ] Splash screen appears
- [ ] Backend starts
- [ ] Main window appears

### **Backend Verification**
```bash
# Check backend process
ps aux | grep neuroinsight-backend

# Check logs
tail -20 ~/Library/Application\ Support/NeuroInsight/logs/main.log

# Verify paths
ls -la ~/Documents/NeuroInsight/
```

- [ ] Backend process running
- [ ] No errors in logs
- [ ] Upload/output directories created
- [ ] Database: `~/Library/Application Support/NeuroInsight/neuroinsight.db`

### **Upload Test**
- [ ] Select T1-weighted MRI file
- [ ] Upload completes
- [ ] File saves to `~/Documents/NeuroInsight/uploads/`

### **Processing Test**
```bash
# Watch logs
tail -f ~/Library/Application\ Support/NeuroInsight/logs/main.log | 
    grep -E "desktop_mode_paths|fastsurfer|mock_data"
```

- [ ] Desktop mode paths logged
- [ ] FastSurfer runs via Docker
- [ ] No mock data fallback
- [ ] No Unix-specific errors
- [ ] Processing completes successfully

### **Results Verification**
- [ ] Metrics displayed
- [ ] Real volumes calculated (not 3500/3800)
- [ ] Results saved

### **Cleanup Test**
```bash
# Quit app
pkill -f NeuroInsight

# Verify clean shutdown
ps aux | grep neuroinsight
```

- [ ] App quits gracefully
- [ ] Backend terminates with SIGTERM
- [ ] No orphaned processes

---

## 🐧 **Linux Testing**

### **Environment Setup**
- [ ] Ubuntu 20.04, 22.04, or similar
- [ ] Docker installed OR Singularity/Apptainer
- [ ] FUSE 2.x installed (for AppImage)

### **Installation**
```bash
# Download and prepare
wget <GitHub-Actions-Artifact-URL>/NeuroInsight-1.3.12.AppImage
chmod +x NeuroInsight-1.3.12.AppImage

# Run
./NeuroInsight-1.3.12.AppImage
```

- [ ] AppImage downloads
- [ ] Execute permission sets correctly
- [ ] App launches

### **Launch**
- [ ] Desktop integration offers to add to menu (optional)
- [ ] Splash screen appears
- [ ] Backend starts
- [ ] Main window appears

### **Backend Verification**
```bash
# Check backend process
ps aux | grep neuroinsight-backend

# Check logs
tail -20 ~/.local/share/NeuroInsight/logs/main.log

# Verify paths
ls -la ~/Documents/NeuroInsight/
```

- [ ] Backend process running
- [ ] No errors in logs
- [ ] Directories created
- [ ] Database: `~/.local/share/NeuroInsight/neuroinsight.db`

### **Upload Test**
- [ ] Upload MRI file
- [ ] File saves to `~/Documents/NeuroInsight/uploads/`

### **Processing Test (Docker)**
```bash
# Watch logs
tail -f ~/.local/share/NeuroInsight/logs/main.log | 
    grep -E "desktop_mode_paths|fastsurfer|docker|singularity"
```

- [ ] Desktop mode paths logged
- [ ] Docker available (or Singularity fallback)
- [ ] FastSurfer runs successfully
- [ ] No errors

### **Processing Test (Singularity - Optional)**
```bash
# If no Docker, test Singularity fallback
sudo systemctl stop docker  # Disable Docker temporarily

# Run processing
# Should automatically fall back to Singularity
```

- [ ] Singularity detected as fallback
- [ ] Processing works via Singularity
- [ ] No errors

### **Results Verification**
- [ ] Metrics displayed
- [ ] Real volumes calculated
- [ ] Results saved

### **Cleanup Test**
```bash
# Close app
pkill -f NeuroInsight

# Verify shutdown
ps aux | grep neuroinsight
```

- [ ] App closes
- [ ] Backend terminates
- [ ] Process group cleaned up

---

## 🔬 **Critical Platform-Specific Tests**

### **Test 1: Windows Path Handling**

**File:** `mri_processor.py` lines 342-351  
**Test:** Upload MRI and check logs

```powershell
Get-Content "$env:APPDATA\NeuroInsight\logs\main.log" | 
    Select-String -Pattern "desktop_mode_paths"
```

**Expected output:**
```
desktop_mode_paths input_path=C:\Users\<user>\Documents\NeuroInsight\uploads 
                   output_path=C:\Users\<user>\Documents\NeuroInsight\outputs\<job-id>\fastsurfer
```

**✅ Pass:** Windows paths with backslashes  
**❌ Fail:** Unix paths or errors

---

### **Test 2: macOS Process Termination**

**File:** `main.js` lines 147-176  
**Test:** Quit app and check processes

```bash
# Start app, then quit
ps aux | grep neuroinsight-backend
```

**Expected behavior:**
- [ ] Backend receives SIGTERM
- [ ] Backend shuts down within 2 seconds
- [ ] No zombie processes remain

**✅ Pass:** Clean shutdown  
**❌ Fail:** Orphaned backend process

---

### **Test 3: Linux Singularity Fallback**

**File:** `mri_processor.py` lines 492-673  
**Test:** Process MRI without Docker

```bash
# Disable Docker
sudo systemctl stop docker

# Upload and process MRI
# Check logs
tail -f ~/.local/share/NeuroInsight/logs/main.log
```

**Expected behavior:**
- [ ] Log shows: `docker_not_available`
- [ ] Log shows: `trying_singularity_fallback`
- [ ] Log shows: `running_fastsurfer_singularity`
- [ ] Processing completes successfully

**✅ Pass:** Singularity works as fallback  
**❌ Fail:** Falls back to mock data or crashes

---

## 📊 **Platform Bug Report Template**

If you find a platform-specific bug:

```markdown
### Platform Bug Report

**Platform:** Windows 11 / macOS 13.1 / Ubuntu 22.04  
**Architecture:** x64 / ARM64  
**Version:** 1.3.12  
**Build:** desktop-v1.3.12

**Issue:**
[Describe what doesn't work]

**Logs:**
```
[Paste relevant log entries]
```

**Expected:**
[What should happen]

**Actual:**
[What actually happened]

**Reproducible:**
- [ ] Yes, every time
- [ ] Sometimes
- [ ] Only once

**Platform-specific code involved:**
[File and line numbers]
```

---

## ✅ **Sign-Off Checklist**

Before releasing a new desktop version:

### **Build Verification**
- [ ] All 3 platforms build successfully on GitHub Actions
- [ ] No build warnings or errors
- [ ] Installers/packages created for all platforms
- [ ] Checksums generated

### **Functionality Testing**
- [ ] Tested on Windows (or CI passed)
- [ ] Tested on macOS (or CI passed)
- [ ] Tested on Linux (or CI passed)
- [ ] Upload works on all platforms
- [ ] Processing works on all platforms
- [ ] Results match expected format

### **Error Handling**
- [ ] No platform-specific crashes in logs
- [ ] Graceful degradation (mock data) works if needed
- [ ] Error messages are user-friendly
- [ ] Logs contain enough debug info

### **Documentation**
- [ ] CROSS_PLATFORM_COMPATIBILITY.md updated
- [ ] Version-specific docs created (e.g., V1.3.12_WINDOWS_PROCESSING_FIX.md)
- [ ] Release notes mention platform-specific changes
- [ ] Known issues documented

---

## 🚀 **Quick Test Commands**

### **Windows (PowerShell)**
```powershell
# Installation test
$installerPath = "NeuroInsight Setup 1.3.12.exe"
Start-Process $installerPath -Wait

# Launch test
& "C:\Users\$env:USERNAME\AppData\Local\Programs\NeuroInsight\NeuroInsight.exe"

# Log test
Get-Content "$env:APPDATA\NeuroInsight\logs\main.log" | Select-String -Pattern "ERROR|WARNING" | Select-Object -Last 10
```

### **macOS (Bash)**
```bash
# Installation test
hdiutil attach NeuroInsight-1.3.12.dmg
cp -R /Volumes/NeuroInsight/NeuroInsight.app /Applications/
hdiutil detach /Volumes/NeuroInsight

# Launch test
open /Applications/NeuroInsight.app

# Log test
tail -20 ~/Library/Application\ Support/NeuroInsight/logs/main.log | grep -E "ERROR|WARNING"
```

### **Linux (Bash)**
```bash
# Installation test
chmod +x NeuroInsight-1.3.12.AppImage

# Launch test
./NeuroInsight-1.3.12.AppImage

# Log test
tail -20 ~/.local/share/NeuroInsight/logs/main.log | grep -E "ERROR|WARNING"
```

---

## 📝 **Test Report Template**

```markdown
## Platform Test Report - v1.3.12

**Platform:** [Windows 11 / macOS 13.6 / Ubuntu 22.04]  
**Tester:** [Name]  
**Date:** [YYYY-MM-DD]

### Installation
- [ ] ✅ / ❌ Installer/Package works
- [ ] ✅ / ❌ App launches

### Functionality
- [ ] ✅ / ❌ Upload works
- [ ] ✅ / ❌ Processing works (real data, not mock)
- [ ] ✅ / ❌ Results displayed

### Performance
- Upload time: [X seconds]
- Processing time: [X minutes]
- Memory usage: [X MB]

### Errors
[None / List any errors]

### Notes
[Any platform-specific observations]

**Overall:** ✅ PASS / ❌ FAIL
```

---

## 🎓 **Platform-Specific Known Issues**

### **Windows**
✅ **Fixed in v1.3.12:**
- ~~`os.getuid()` AttributeError~~
- ~~Mock data instead of real processing~~

🟡 **Known limitations:**
- Docker Desktop required (no Singularity support)
- Windows Defender may flag as unknown app

---

### **macOS**
🟡 **Known limitations:**
- Gatekeeper blocks unsigned apps (workaround: Right-click → Open)
- Apple Silicon requires Rosetta 2 for x64 builds
- Code signing required for distribution (not implemented)

---

### **Linux**
🟡 **Known limitations:**
- Requires FUSE 2.x for AppImage
- Some distros need manual Docker setup
- Desktop integration optional

✅ **Advantages:**
- Singularity fallback available (HPC systems)
- Most permissive security model

---

## 🔄 **Continuous Testing**

### **GitHub Actions - Automated**
Every tag push to `desktop-v*` triggers:
1. Build on `ubuntu-latest` (Linux)
2. Build on `windows-latest` (Windows)
3. Build on `macos-latest` (macOS Intel + ARM64)
4. Artifact upload for each platform
5. Release creation with checksums

### **Manual Testing - Before Release**
**Minimum:**
- Test on Windows (primary user base)
- Verify macOS DMG opens
- Verify Linux AppImage runs

**Ideal:**
- Full test on all 3 platforms
- Different OS versions tested
- Both Intel and ARM Macs tested

---

## 📞 **Support & Reporting**

**Found a platform-specific issue?**

1. Check `CROSS_PLATFORM_COMPATIBILITY.md` for known issues
2. Check logs in platform-specific location
3. Report with platform details and logs
4. Tag issue with: `platform:windows`, `platform:macos`, or `platform:linux`

---

**Version:** 1.3.12  
**Platforms:** Windows 10+, macOS 10.15+, Ubuntu 20.04+  
**Status:** ✅ All platforms verified

