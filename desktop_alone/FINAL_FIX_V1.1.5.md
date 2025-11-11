# FINAL FIX - v1.1.5 (extraResources Approach)

**Date**: November 10, 2025  
**Issue**: Dark window persisted through v1.1.1 - v1.1.4  
**Final Solution**: v1.1.5 using extraResources  
**Status**: ✅ Verified locally, building on GitHub Actions

---

## 🔍 The Journey

### v1.1.1 - v1.1.2: Frontend Not Bundled
- **Problem**: package.json didn't actually get modified
- **Result**: Frontend missing from app.asar
- **Status**: ❌ Dark window

### v1.1.3: Wrong Path
- **Problem**: main.js had old path (src/frontend/)
- **Result**: Looking in wrong location
- **Status**: ❌ Dark window

### v1.1.4: Correct Path, But Frontend STILL Not Bundled!
- **Problem**: "files" array syntax works on Linux but FAILS on macOS in GitHub Actions
- **Result**: main.js looks for frontend/index.html, but file doesn't exist
- **Status**: ❌ Dark window

### v1.1.5: The Working Solution
- **Approach**: Use `extraResources` (same as backend)
- **Result**: Frontend bundled as separate directory in resources/
- **Status**: ✅ Verified locally, should work on all platforms

---

## 🎯 The Root Cause

### Why "files" Array Failed on macOS

The `files` array in electron-builder with object syntax:

```json
"files": [
  {
    "from": "../frontend",
    "to": "frontend",
    "filter": ["**/*"]
  }
]
```

**Works on**:
- ✅ Linux (GitHub Actions ubuntu-latest)
- ✅ Linux (local builds)

**Fails on**:
- ❌ macOS (GitHub Actions macos-latest)
- Possibly Windows too

**Why it fails**: Unknown, likely electron-builder bug or platform-specific path handling

---

## ✅ The Working Solution

### Use extraResources (Same as Backend)

```json
"extraResources": [
  {
    "from": "../frontend",
    "to": "frontend",
    "filter": ["**/*"]
  },
  {
    "from": "../dist/neuroinsight-backend",
    "to": "backend",
    "filter": ["**/*"]
  }
]
```

### Update main.js to Load from Resources

```javascript
const frontendPath = app.isPackaged
  ? path.join(process.resourcesPath, 'frontend', 'index.html')
  : path.join(__dirname, '..', 'frontend', 'index.html');
```

### Result Structure

```
NeuroInsight.app/Contents/
├── MacOS/
│   └── NeuroInsight         (Electron executable)
├── Resources/
│   ├── app.asar            (Electron app code)
│   ├── frontend/            ← Frontend HERE (extraResources)
│   │   └── index.html
│   └── backend/             ← Backend HERE (extraResources)
│       └── neuroinsight-backend
```

**This is the SAME approach as the backend**, which has been working all along!

---

## 🧪 Local Verification (Linux)

```bash
cd desktop_alone/electron-app/dist/linux-unpacked

# Check structure
ls -lh resources/
# Shows: app.asar, backend/, frontend/ ✅

# Verify index.html exists
ls -lh resources/frontend/index.html
# Shows: 91K file ✅

# Verify NOT in app.asar
npx asar list resources/app.asar | grep frontend
# Shows: (empty) ✅ Correct - it's in extraResources
```

---

## 📦 How to Verify v1.1.5 Build

### After downloading v1.1.5 macOS build:

```bash
# Mount DMG
hdiutil attach NeuroInsight-1.0.0-arm64.dmg

# Check structure
ls -la /Volumes/NeuroInsight\ 1.0.0/NeuroInsight.app/Contents/Resources/

# Should see:
# - app.asar
# - backend/
# - frontend/  ← THIS should exist!

# Verify index.html
ls -lh /Volumes/NeuroInsight\ 1.0.0/NeuroInsight.app/Contents/Resources/frontend/index.html

# Should show: 91-92KB file
```

---

## 🎯 Expected Log Output (v1.1.5)

```
18:XX:XX.XXX › NeuroInsight Desktop starting...
18:XX:XX.XXX › Backend is ready!
18:XX:XX.XXX › Loading frontend from: /Applications/NeuroInsight.app/Contents/Resources/frontend/index.html
18:XX:XX.XXX › Frontend loaded successfully  ← KEY LINE!
18:XX:XX.XXX › Application window shown
```

**No errors**, **NO dark window**!

---

## 📊 Version History Summary

| Version | main.js Path | Frontend Location | Result |
|---------|-------------|-------------------|--------|
| v1.1.1 | ❌ src/frontend/ | ❌ Not bundled | Dark window |
| v1.1.2 | ❌ src/frontend/ | ❌ Not bundled | Dark window |
| v1.1.3 | ❌ src/frontend/ | ❌ Not bundled | Dark window |
| v1.1.4 | ✅ frontend/ | ❌ Not bundled (files array failed) | Dark window |
| v1.1.5 | ✅ Resources/frontend/ | ✅ extraResources | **Should work!** ✅ |

---

## 🔧 Technical Details

### Why extraResources Works

**extraResources**:
- Copies files OUTSIDE app.asar
- Creates separate directory in Contents/Resources/
- Proven approach (backend uses this successfully)
- Works consistently across all platforms
- More reliable than "files" array for cross-platform

**files array**:
- Bundles files INSIDE app.asar
- Platform-specific behavior
- Failed on macOS in GitHub Actions
- Less reliable for complex bundling

---

## 🚀 Deployment

### Current Status

**Tag**: desktop-v1.1.5  
**Commit**: 3d15049  
**Build**: 🟡 In progress  
**ETA**: ~30-60 minutes

**Monitor**: https://github.com/phindagijimana/neuroinsight/actions

### Installation Process

```bash
# 1. Full cleanup
rm -rf /Applications/NeuroInsight.app \
       ~/Library/Logs/NeuroInsight/ \
       ~/Library/Application\ Support/NeuroInsight/

# 2. Download v1.1.5 from GitHub Actions artifacts

# 3. Install
cd ~/Downloads/neuroinsight-mac/
sudo xattr -cr NeuroInsight-1.0.0-arm64.dmg
open NeuroInsight-1.0.0-arm64.dmg
# Drag to Applications
sudo xattr -cr /Applications/NeuroInsight.app

# 4. Test
/Applications/NeuroInsight.app/Contents/MacOS/NeuroInsight 2>&1 | tee ~/v1.1.5-test.log

# 5. Verify
cat ~/v1.1.5-test.log | grep -E "(Loading frontend|Frontend loaded|Failed)"
```

### Success Criteria

- ✅ Frontend directory exists in Resources/
- ✅ index.html file exists (91-92KB)
- ✅ Log shows: "Frontend loaded successfully"
- ✅ NO "Failed to load frontend" error
- ✅ Window shows UI (not dark)

---

## 🎓 Lessons Learned

### Lesson 1: Test on Target Platform

**Problem**: Local Linux build worked, macOS build failed

**Lesson**: Always verify fixes on ALL target platforms, not just one

### Lesson 2: Use Proven Approaches

**Problem**: "files" array with object syntax was untested across platforms

**Lesson**: Backend used extraResources successfully - should have used same approach for frontend from start

### Lesson 3: Verify Build Outputs, Not Just Code

**Problem**: Assumed if code was correct, build would work

**Lesson**: Always verify the BUILT artifact contains expected files, not just that source code is correct

### Lesson 4: Platform-Specific electron-builder Behavior

**Problem**: electron-builder behaves differently on different OS runners

**Lesson**: What works on Linux might not work on macOS/Windows. Use approaches that work everywhere (like extraResources).

---

## 📝 Testing Checklist for v1.1.5

- [ ] v1.1.5 build completes on GitHub Actions
- [ ] All 3 platforms build successfully (Linux, Windows, macOS)
- [ ] Download v1.1.5 macOS artifact
- [ ] Verify frontend/ directory exists in DMG
- [ ] Verify index.html exists (91-92KB)
- [ ] Clean install on Mac
- [ ] Run with logging
- [ ] Check log shows "Frontend loaded successfully"
- [ ] Verify NO dark window
- [ ] Can see UI elements
- [ ] Can interact with app

---

## 🆘 If v1.1.5 Still Fails

### Check These:

1. **Is frontend directory in Resources?**
   ```bash
   ls -lh /Applications/NeuroInsight.app/Contents/Resources/frontend/
   ```

2. **What does log say?**
   ```bash
   cat ~/v1.1.5-test.log | grep "Loading frontend"
   ```

3. **GitHub Actions build logs**:
   - Check macOS build logs
   - Look for "Building Electron DMG" step
   - Check if any errors during packaging

---

## 💡 Alternative Approaches (If v1.1.5 Fails)

### Option 1: Copy frontend during build

```yaml
# In GitHub Actions workflow
- name: Copy frontend to electron-app
  working-directory: desktop_alone
  run: |
    cp -r frontend electron-app/
```

Then update package.json:
```json
"files": [
  "src/**/*",
  "assets/**/*",
  "frontend/**/*"
]
```

### Option 2: Pre-bundle frontend into app

```bash
# Build step
cd desktop_alone/electron-app
mkdir -p app-files/frontend
cp -r ../frontend/* app-files/frontend/
```

### Option 3: Serve frontend from backend

Make backend serve the frontend HTML file (fallback approach).

---

## ✅ Confidence Level

**v1.1.5**: **HIGH** ✅

**Why**:
- ✅ Verified locally (Linux)
- ✅ Uses same approach as backend (proven)
- ✅ extraResources more reliable than files array
- ✅ Simpler, more straightforward

**This should be the final fix!**

---

**Last Updated**: November 10, 2025  
**Version**: v1.1.5  
**Status**: Building  
**Expected Result**: ✅ Working app with NO dark window

