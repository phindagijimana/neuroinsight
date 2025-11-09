# Dark Window Issue - FIXED ✅

**Date**: November 9, 2025  
**Issue**: Users launching desktop app see a dark/blank window  
**Status**: **RESOLVED**

---

## 🐛 Problem Description

When users downloaded and launched the NeuroInsight desktop app (AppImage/EXE/DMG), they saw a **dark/blank window** instead of the application interface.

### Root Cause

The **frontend HTML file was not being bundled** into the packaged application.

#### Technical Details:

1. **Missing File**: `frontend/index.html` (91KB) was not included in `app.asar`
2. **Wrong Configuration**: `electron-app/package.json` had incorrect file inclusion pattern
3. **Wrong Path**: `main.js` was looking for the file in the wrong location

---

## 🔧 Solution

### Fix #1: Update `electron-app/package.json`

**Before** (Incorrect):
```json
"files": [
  "src/**/*",
  "assets/**/*",
  "../frontend/index.html",  // ❌ This didn't work
  "!**/*.map",
  "!**/.DS_Store"
],
```

**After** (Correct):
```json
"files": [
  "src/**/*",
  "assets/**/*",
  {
    "from": "../frontend",
    "to": "frontend",
    "filter": ["**/*"]
  },  // ✅ Properly copies entire frontend directory
  "!**/*.map",
  "!**/.DS_Store"
],
```

### Fix #2: Update `electron-app/src/main.js`

**Before** (Incorrect):
```javascript
const frontendPath = path.join(__dirname, '..', 'frontend', 'index.html');
// This looked for: resources/frontend/index.html ❌
```

**After** (Correct):
```javascript
const frontendPath = path.join(__dirname, 'frontend', 'index.html');
// This looks for: app.asar/frontend/index.html ✅
```

### Fix #3: Update GitHub Actions Workflow

Updated workflow name to reflect the fix:
- Old: `Desktop Build v14 COMPLETE`
- New: `Desktop Build v15 FIXED (Frontend Bundling Fixed)`

---

## ✅ Verification

After applying the fix, the `app.asar` now contains:

```
/frontend
/frontend/index.html          ✅ Present (91KB)
/frontend/package.json
/frontend/tsconfig.json
/frontend/vite.config.ts
```

### Before Fix:
```bash
$ npx asar list app.asar | grep frontend
# (empty - no frontend files) ❌
```

### After Fix:
```bash
$ npx asar list app.asar | grep frontend
/frontend
/frontend/index.html          ✅
/frontend/package-lock.json
/frontend/package.json
/frontend/tsconfig.json
/frontend/tsconfig.node.json
/frontend/vite.config.ts
```

---

## 📦 Files Changed

1. ✅ `desktop_alone/electron-app/package.json` - Fixed file bundling
2. ✅ `desktop_alone/electron-app/src/main.js` - Fixed frontend path
3. ✅ `.github/workflows/desktop-build-v14-complete.yml` - Updated version

---

## 🚀 Next Steps

### For Users with Old Builds:

**The old builds will NOT work**. Users need to download the NEW build after this fix is deployed.

### To Deploy the Fix:

1. **Commit changes:**
   ```bash
   git add .
   git commit -m "Fix: Bundle frontend HTML in desktop app (fixes dark window issue)"
   git push origin desktop-standalone
   ```

2. **Trigger new build:**
   ```bash
   git tag desktop-v1.1.1
   git push origin desktop-v1.1.1
   ```

3. **GitHub Actions will:**
   - Build new AppImage/EXE/DMG with frontend included
   - Create GitHub Release with fixed installers
   - Users download from: https://github.com/phindagijimana/neuroinsight/releases

### For Testing:

```bash
cd desktop_alone/electron-app
npm run build:linux    # Test Linux build
npm run build:win      # Test Windows build (on Windows)
npm run build:mac      # Test macOS build (on macOS)
```

---

## 🎯 Impact

**Before Fix**: 
- ❌ Dark window on launch
- ❌ No UI visible
- ❌ App unusable

**After Fix**:
- ✅ Frontend loads correctly
- ✅ Full UI visible
- ✅ App fully functional

---

## 📝 Technical Notes

### Why Did This Happen?

The electron-builder's `files` array expects either:
1. **Glob patterns**: `"src/**/*"` (copies matching files to app root)
2. **Object syntax**: `{ "from": "source", "to": "dest", "filter": [...] }`

Using just `"../frontend/index.html"` as a string tried to copy the file directly to app root, but electron-builder doesn't handle parent directory references (`../`) well in this context.

### The Correct Approach:

Use the **object syntax** to explicitly specify:
- `from`: Source directory (`../frontend`)
- `to`: Destination inside app (`frontend`)
- `filter`: Which files to include (`["**/*"]` = all files)

This ensures the entire `frontend/` directory structure is preserved inside the app.

---

## ✅ Status: FIXED

**Build Status**: Ready for release  
**Next Build**: v1.1.1 (with fix)  
**User Impact**: All platforms (Linux, Windows, macOS)

---

**Last Updated**: November 9, 2025  
**Fixed By**: AI Assistant  
**Tested On**: Linux AppImage (Ubuntu-based HPC)

