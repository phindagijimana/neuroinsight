# macOS Log Commands - Quick Reference

**For checking NeuroInsight Desktop app logs on macOS**

---

## 🚀 Quick Commands (Copy-Paste)

### **1. Run App with Live Console Output**
```bash
/Applications/NeuroInsight.app/Contents/MacOS/NeuroInsight 2>&1 | tee ~/neuroinsight-debug.log
```
*(Press Ctrl+C after 10-15 seconds)*

---

### **2. View the Captured Log**
```bash
cat ~/neuroinsight-debug.log
```

---

### **3. Check for Key Errors**
```bash
cat ~/neuroinsight-debug.log | grep -E "(Loading frontend|Failed to load|ERROR|Backend is ready)"
```

**What to look for:**
```
✅ Backend is ready!                   (Backend started successfully)
✅ Loading frontend from: .../frontend/index.html  (Correct path - v1.1.4+)
❌ Loading frontend from: .../src/frontend/...     (Wrong path - old build)
❌ Failed to load frontend: ERR_FILE_NOT_FOUND     (Frontend not bundled or wrong path)
```

---

### **4. Check Electron Logs (Previous Runs)**
```bash
# View last 30 lines
tail -30 ~/Library/Logs/NeuroInsight/main.log

# View full log
cat ~/Library/Logs/NeuroInsight/main.log

# View errors only
cat ~/Library/Logs/NeuroInsight/errors.log

# View crashes
cat ~/Library/Logs/NeuroInsight/crashes.log
```

---

### **5. Verify Frontend is Bundled**
```bash
cd /Applications/NeuroInsight.app/Contents/Resources
npx asar list app.asar | grep "frontend/index.html"
```

**Expected output:**
```
/frontend/index.html  ✅
```

**If empty:** Frontend NOT bundled!

---

### **6. Check Which Version of main.js**
```bash
cd /tmp
npx asar extract /Applications/NeuroInsight.app/Contents/Resources/app.asar neuroinsight-check
grep "const frontendPath" neuroinsight-check/src/main.js
rm -rf neuroinsight-check
```

**Expected output (v1.1.4+):**
```javascript
const frontendPath = path.join(__dirname, 'frontend', 'index.html');  ✅
```

**Wrong output (old):**
```javascript
const frontendPath = path.join(__dirname, 'src', 'frontend', 'index.html');  ❌
```

---

### **7. Check Backend Status**
```bash
ps aux | grep neuroinsight-backend
```

---

### **8. View Backend Logs (if exists)**
```bash
tail -f ~/Library/Application\ Support/NeuroInsight/backend.log
```

---

### **9. Check macOS System Logs**
```bash
log show --predicate 'process == "NeuroInsight"' --last 5m
```

---

### **10. Clean App Data (Fresh Start)**
```bash
# Remove app
rm -rf /Applications/NeuroInsight.app

# Remove logs
rm -rf ~/Library/Logs/NeuroInsight/

# Remove data
rm -rf ~/Library/Application\ Support/NeuroInsight/

# Remove preferences
rm -rf ~/Library/Preferences/com.neuroinsight.desktop.*
```

---

## 📋 Complete Diagnostic Sequence

Run these in order:

```bash
# 1. Run app and capture output
/Applications/NeuroInsight.app/Contents/MacOS/NeuroInsight 2>&1 | tee ~/debug.log
# (Wait 15 seconds, press Ctrl+C)

# 2. Check frontend loading line
grep "Loading frontend" ~/debug.log

# 3. Check if it succeeded
grep "Frontend loaded successfully" ~/debug.log

# 4. If failed, check error
grep "Failed to load frontend" ~/debug.log

# 5. Verify frontend bundled
cd /Applications/NeuroInsight.app/Contents/Resources
npx asar list app.asar | grep frontend
```

---

## 🎯 Key Indicators

### ✅ **Build is CORRECT if you see:**
```
Loading frontend from: .../app.asar/frontend/index.html
Frontend loaded successfully
Application window shown
```

### ❌ **Build is WRONG if you see:**
```
Loading frontend from: .../app.asar/src/frontend/index.html  ← Has "src/"
Failed to load frontend: ERR_FILE_NOT_FOUND
```

---

## 🔧 Your Current Issue

**Your log shows:**
```
Loading frontend from: .../app.asar/src/frontend/index.html  ❌
```

**This means**: You have an OLD build (v1.1.3 or earlier)

**Solution**:
1. Wait for v1.1.4 build to complete (~30-60 min)
2. Download v1.1.4 macOS artifact from GitHub Actions
3. Install that one
4. The path will be correct!

---

## 📥 Download NEW Build (v1.1.4)

```bash
# 1. Go to Actions
open https://github.com/phindagijimana/neuroinsight/actions

# 2. Look for: "Desktop Build v15" with tag "desktop-v1.1.4"

# 3. Wait for all 3 jobs to complete (green checkmarks)

# 4. Download: neuroinsight-mac.zip from Artifacts section

# 5. Extract and install
unzip neuroinsight-mac.zip
open NeuroInsight-1.0.0-arm64.dmg  # Or regular if Intel Mac
```

---

## ⏰ Build Timeline

| Version | main.js Fixed? | package.json Fixed? | Status |
|---------|----------------|---------------------|---------|
| v1.1.1 | ✅ Yes (031eaa6) | ❌ No | Frontend not bundled |
| v1.1.2 | ✅ Yes | ❌ No | Frontend not bundled |
| v1.1.3 | ❌ No (reverted?) | ✅ Yes (af11a78) | Wrong path |
| v1.1.4 | ✅ Yes | ✅ Yes | **BOTH FIXED!** |

---

## 📝 Summary for Future Reference

**Always use these commands to verify a build:**

```bash
# Command 1: Check frontend path
/Applications/NeuroInsight.app/Contents/MacOS/NeuroInsight 2>&1 | grep "Loading frontend"

# Should show: .../frontend/index.html (no "src/")

# Command 2: Check if frontend bundled
cd /Applications/NeuroInsight.app/Contents/Resources
npx asar list app.asar | grep "frontend/index.html"

# Should output: /frontend/index.html
```

If both pass → Build is good!  
If either fails → Need new build!

---

**Last Updated**: November 10, 2025  
**Current Working Version**: v1.1.4 (building now)  
**ETA**: ~30-60 minutes

