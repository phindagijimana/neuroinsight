# Desktop App Log Checking Guide

**Quick Reference for Debugging the NeuroInsight Desktop App**

---

## 📍 Log Locations

### Electron Logs
- **Linux**: `~/.config/NeuroInsight/logs/`
- **Windows**: `C:\Users\<user>\AppData\Roaming\NeuroInsight\logs\`
- **macOS**: `~/Library/Logs/NeuroInsight/`

### Log Files
- `main.log` - All application events
- `errors.log` - Errors only
- `crashes.log` - Critical failures

---

## 🔍 Quick Diagnostic Commands

### 1. Check Which Build You're Running
```bash
cd desktop_alone/electron-app/dist
ls -lh NeuroInsight-1.0.0.AppImage

# Look at timestamp:
# Nov 9 01:45 or later = FIXED version
# Earlier = OLD version with bug
```

### 2. Verify Frontend is Bundled
```bash
cd desktop_alone/electron-app/dist/linux-unpacked/resources
npx asar list app.asar | grep "frontend/index.html"

# Expected: /frontend/index.html
# If empty: Frontend NOT bundled
```

### 3. Check Existing Logs
```bash
# List log files
ls -lh ~/.config/NeuroInsight/logs/

# View main log
cat ~/.config/NeuroInsight/logs/main.log

# View errors
cat ~/.config/NeuroInsight/logs/errors.log

# View crashes
cat ~/.config/NeuroInsight/logs/crashes.log

# View last 50 lines
tail -50 ~/.config/NeuroInsight/logs/main.log
```

### 4. Run with Console Output (Best for Debugging)
```bash
cd desktop_alone/electron-app/dist

# Method 1: Show on screen + save to file
./NeuroInsight-1.0.0.AppImage 2>&1 | tee ~/neuroinsight-run.log

# Method 2: Just show on screen
./NeuroInsight-1.0.0.AppImage 2>&1

# Method 3: Save to file only
./NeuroInsight-1.0.0.AppImage > ~/neuroinsight-run.log 2>&1
```

### 5. Check Display Configuration
```bash
echo $DISPLAY

# If empty: No display configured
# If set (e.g., :0): Display available
```

### 6. Check if App is Running
```bash
ps aux | grep neuroinsight

# Shows running processes
```

---

## 🐛 Common Issues & What Logs Show

### Issue 1: Dark Window

**Logs show**:
```
[info] NeuroInsight Desktop starting...
ERROR:ozone_platform_x11.cc(240)] Missing X server or $DISPLAY
Segmentation fault (core dumped)
```

**Cause**: No display server available  
**Solution**: Use X11 forwarding, Open OnDemand, or local machine

---

### Issue 2: Frontend Not Loading

**Logs show**:
```
[info] NeuroInsight Desktop starting...
[info] Starting backend...
[info] Backend is ready!
[error] Failed to load frontend: ENOENT: no such file or directory
```

**Cause**: Frontend not bundled  
**Solution**: Rebuild with correct package.json config

---

### Issue 3: Backend Won't Start

**Logs show**:
```
[info] NeuroInsight Desktop starting...
[info] Starting backend...
[error] Failed to start backend: spawn ENOENT
```

**Cause**: Backend executable missing or not executable  
**Solution**: Check backend exists and is executable

---

### Issue 4: Port Already in Use

**Logs show**:
```
[info] Starting backend...
[error] Backend error: OSError: [Errno 48] Address already in use
```

**Cause**: Port 8000 already in use  
**Solution**: Kill other process or change port

---

## 🔧 Troubleshooting Steps

### Step 1: Verify Build
```bash
# Check timestamp
ls -lh desktop_alone/electron-app/dist/NeuroInsight-1.0.0.AppImage

# Check frontend bundled
cd desktop_alone/electron-app/dist/linux-unpacked/resources
npx asar list app.asar | grep frontend
```

### Step 2: Check Display
```bash
# Check DISPLAY variable
echo $DISPLAY

# If empty, set up X11 or use Open OnDemand
```

### Step 3: Run with Logging
```bash
# Run and capture output
cd desktop_alone/electron-app/dist
./NeuroInsight-1.0.0.AppImage 2>&1 | tee ~/debug.log

# Review the log
cat ~/debug.log
```

### Step 4: Check Electron Logs
```bash
# View logs
cat ~/.config/NeuroInsight/logs/main.log

# Look for errors
grep -i error ~/.config/NeuroInsight/logs/main.log
```

### Step 5: Check Backend Logs
```bash
# If backend started, check its logs
tail -f ~/.local/share/NeuroInsight/backend.log
```

---

## 📊 Log Analysis Patterns

### Successful Startup
```
[info] NeuroInsight Desktop starting...
[info] Starting backend...
[info] Backend port captured: 8000
[info] Backend is ready!
[info] Loading frontend from: /path/to/frontend/index.html
[info] Frontend loaded successfully
[info] Application window shown
```

### Missing Display (HPC)
```
[info] NeuroInsight Desktop starting...
ERROR:ozone_platform_x11.cc(240)] Missing X server or $DISPLAY
Segmentation fault (core dumped)
```

### Missing Frontend
```
[info] NeuroInsight Desktop starting...
[info] Backend is ready!
[error] Failed to load: Error: ENOENT: no such file or directory
```

### Backend Failure
```
[info] NeuroInsight Desktop starting...
[info] Starting backend...
[error] Backend process exited with code 1
[crash] Failed to start backend process
```

---

## 🎯 Quick Diagnosis Checklist

Run these commands in order:

```bash
# 1. Check build date
ls -lh desktop_alone/electron-app/dist/NeuroInsight-1.0.0.AppImage

# 2. Check frontend bundled
cd desktop_alone/electron-app/dist/linux-unpacked/resources && npx asar list app.asar | grep frontend

# 3. Check display
echo $DISPLAY

# 4. Check logs
cat ~/.config/NeuroInsight/logs/main.log

# 5. Run with output
cd ../../.. && ./NeuroInsight-1.0.0.AppImage 2>&1 | head -20
```

---

## 🖥️ Testing on Different Environments

### HPC/Server (No Display)
```bash
# Option 1: X11 forwarding
ssh -X user@server
./NeuroInsight-1.0.0.AppImage

# Option 2: Open OnDemand
# Use web interface to launch desktop
# Run app in that desktop

# Option 3: Virtual display (headless)
xvfb-run ./NeuroInsight-1.0.0.AppImage
```

### Local Linux Machine
```bash
# Should work directly
./NeuroInsight-1.0.0.AppImage

# Check logs if issues
cat ~/.config/NeuroInsight/logs/main.log
```

### Windows
```powershell
# Run installer
.\NeuroInsight-Setup-1.0.0.exe

# Check logs at
%APPDATA%\NeuroInsight\logs\main.log
```

### macOS
```bash
# Open DMG and install
# Run from Applications

# Check logs at
~/Library/Logs/NeuroInsight/main.log
```

---

## 🆘 When to Check Each Log

**main.log**:
- General debugging
- Startup issues
- See application flow

**errors.log**:
- Error messages
- Failed operations
- API errors

**crashes.log**:
- App crashes
- Fatal errors
- Unexpected exits

**Console output** (running with 2>&1):
- Real-time debugging
- See exactly what's happening
- Backend startup issues

---

## 📝 Saving Logs for Bug Reports

### Collect All Logs
```bash
# Create archive
cd ~/.config/NeuroInsight
tar -czf ~/neuroinsight-logs-$(date +%Y%m%d).tar.gz logs/

# Or copy individual logs
cp logs/main.log ~/neuroinsight-main-$(date +%Y%m%d).log
cp logs/errors.log ~/neuroinsight-errors-$(date +%Y%m%d).log
```

### Run and Capture Session
```bash
# Capture entire session
cd desktop_alone/electron-app/dist
script ~/neuroinsight-session-$(date +%Y%m%d).log
./NeuroInsight-1.0.0.AppImage
# Press Ctrl+D when done
```

### What to Include in Bug Report
1. **Build info**: Output of `ls -lh NeuroInsight-1.0.0.AppImage`
2. **Environment**: Output of `echo $DISPLAY` and `uname -a`
3. **Logs**: Attach main.log, errors.log, crashes.log
4. **Console output**: If available
5. **Steps to reproduce**: What you did before the error

---

## 🔗 Related Documentation

- **DESKTOP_APP_MASTER_REFERENCE.md** - Complete app documentation
- **COMPLETE_BUNDLING_FIX_REFERENCE.md** - Dark window fix details
- **LOGS_AND_TROUBLESHOOTING.md** - Detailed troubleshooting guide

---

**Last Updated**: November 9, 2025  
**Version**: v1.1.3+

