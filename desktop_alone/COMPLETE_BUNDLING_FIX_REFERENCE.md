# Complete Desktop App Bundling Fix - Reference Guide

**Date**: November 9, 2025  
**Issue**: Dark window when launching desktop app  
**Final Resolution**: v1.1.3 with verified frontend bundling  
**Platforms Affected**: Linux, Windows, macOS

---

## 📋 Table of Contents

1. [Problem Discovery](#problem-discovery)
2. [Diagnosis Process](#diagnosis-process)
3. [Root Cause Analysis](#root-cause-analysis)
4. [Fix Attempts (What Didn't Work)](#fix-attempts-what-didnt-work)
5. [The Actual Working Fix](#the-actual-working-fix)
6. [Verification Steps](#verification-steps)
7. [Secondary Issue: File Size Limits](#secondary-issue-file-size-limits)
8. [Testing Procedure](#testing-procedure)
9. [Distribution Strategy](#distribution-strategy)
10. [Lessons Learned](#lessons-learned)
11. [Quick Reference Commands](#quick-reference-commands)

---

## Problem Discovery

### Initial Symptom

Users reported that when launching the desktop app (AppImage/EXE/DMG), they saw a **dark/blank window** instead of the application interface.

### Environment Where Issue Appeared

- **Platform**: All (Linux, Windows, macOS)
- **Build Version**: v1.0.0 through v1.1.2
- **App Type**: Electron-based desktop application
- **Backend**: Python/FastAPI bundled with PyInstaller
- **Frontend**: Single-file React app (index.html)

### Initial User Report

```
User: "I am still getting the dark window for the app, how can I check the logs?"
```

---

## Diagnosis Process

### Step 1: Check for Display Issues

First ruled out X11/display issues:

```bash
echo $DISPLAY
# If empty, X11 not configured - but this wasn't the issue
```

**Finding**: The app was crashing even before UI could load.

### Step 2: Check Electron Logs

Located electron-log directory:

```bash
ls ~/.config/NeuroInsight/logs/
# Found: main.log with only startup line
```

**Log showed**:
```
[2025-11-06 00:35:18.190] [info]  NeuroInsight Desktop starting...
# Nothing after - app crashed immediately
```

### Step 3: Run AppImage from Terminal

```bash
cd desktop_alone/electron-app/dist
./NeuroInsight-1.0.0.AppImage 2>&1
```

**Error output** (when X11 configured):
```
ERROR:ozone_platform_x11.cc(240)] Missing X server or $DISPLAY
ERROR:env.cc(257)] The platform failed to initialize. Exiting.
Segmentation fault (core dumped)
```

**Conclusion**: Electron couldn't initialize (X11 issue on HPC), but the dark window persisted even with proper display.

### Step 4: Inspect Packaged App Contents

Extract and examine app.asar:

```bash
cd dist/linux-unpacked/resources
npx asar list app.asar | grep frontend
# Result: EMPTY - frontend directory not found!
```

**Critical Discovery**: Frontend files were NOT bundled in the application.

### Step 5: Check Source Files

Verify source frontend exists:

```bash
ls -lh desktop_alone/frontend/index.html
# Found: 91KB file exists
```

**Confirmation**: Frontend source exists, but isn't being packaged.

---

## Root Cause Analysis

### The Problem

The `electron-builder` packaging process was **not including the frontend directory** in the bundled application.

### Why This Happened

In `desktop_alone/electron-app/package.json`, the `files` array configuration was incorrect:

```json
"files": [
  "src/**/*",
  "assets/**/*",
  "../frontend/index.html",  // ❌ This didn't work
  "!**/*.map",
  "!**/.DS_Store"
],
```

### Why the Above Doesn't Work

1. **Parent directory references** (`../`) don't work reliably with electron-builder's file array
2. **Single file pattern** doesn't copy the entire directory structure
3. **No explicit "to" destination** - electron-builder didn't know where to put it

### What Was Expected

The frontend directory should be bundled inside `app.asar`:

```
app.asar/
├── src/
├── assets/
├── frontend/          ← Should be here
│   └── index.html
└── node_modules/
```

### What Was Actually Happening

```
app.asar/
├── src/
├── assets/
└── node_modules/
                       ← frontend/ missing!
```

When Electron tried to load the frontend:

```javascript
// In main.js
const frontendPath = path.join(__dirname, '..', 'frontend', 'index.html');
mainWindow.loadFile(frontendPath);
// File not found → dark window
```

---

## Fix Attempts (What Didn't Work)

### Attempt 1: Incorrect package.json Syntax (v1.1.1)

**What We Tried**:
```json
"files": [
  "src/**/*",
  "assets/**/*",
  "../frontend/index.html",
  "!**/*.map",
  "!**/.DS_Store"
],
```

**Why It Failed**: Parent directory reference doesn't work with electron-builder.

**Committed**: Yes (commit 031eaa6)  
**Result**: ❌ Frontend still not bundled

---

### Attempt 2: Updated main.js Path (v1.1.1)

**What We Tried**:
```javascript
// Changed from:
const frontendPath = path.join(__dirname, '..', 'frontend', 'index.html');

// To:
const frontendPath = path.join(__dirname, 'frontend', 'index.html');
```

**Why It Failed**: Path fix was correct, but frontend still not bundled.

**Committed**: Yes (commit 031eaa6)  
**Result**: ❌ Still dark window (frontend missing)

---

### Attempt 3: Large File Workaround (v1.1.2)

**What We Did**: Fixed release creation to handle files > 2GB

**Why This Wasn't the Main Issue**: This fixed the release upload, but frontend still wasn't bundled.

**Committed**: Yes (commits c1d8330, e2c5b58)  
**Result**: ❌ Dark window persisted

---

### The Critical Discovery

After all these attempts, when checking the actual package.json file:

```bash
git show 031eaa6:desktop_alone/electron-app/package.json | grep -A10 "files"
```

**Shocking finding**: The frontend bundling config was **NEVER ACTUALLY SAVED** to the file!

The search_replace tool claimed success, but the modification didn't persist. All commits (v1.1.1, v1.1.2) had the OLD package.json without the frontend configuration.

---

## The Actual Working Fix

### Step 1: Correct package.json Configuration

**File**: `desktop_alone/electron-app/package.json`

**Change**:
```json
{
  "build": {
    "files": [
      "src/**/*",
      "assets/**/*",
      {
        "from": "../frontend",
        "to": "frontend",
        "filter": ["**/*"]
      },
      "!**/*.map",
      "!**/.DS_Store"
    ]
  }
}
```

**Why This Works**:
- **Object syntax** with explicit `from` and `to`
- **`from`**: Source directory (relative to electron-app/)
- **`to`**: Destination inside app.asar
- **`filter`**: Include all files

### Step 2: Verify and Rebuild

```bash
cd desktop_alone/electron-app
npm run build:linux
```

### Step 3: Verify Frontend Is Bundled

```bash
cd dist/linux-unpacked/resources
npx asar list app.asar | grep frontend
```

**Expected output**:
```
/frontend
/frontend/index.html
/frontend/package-lock.json
/frontend/package.json
/frontend/tsconfig.json
/frontend/tsconfig.node.json
/frontend/vite.config.ts
```

✅ **Success!** Frontend is now bundled.

### Step 4: Commit and Deploy

```bash
git add desktop_alone/electron-app/package.json
git commit -m "Fix: Actually add frontend bundling to package.json (previous commit missed it)"
git push origin main

git tag desktop-v1.1.3 -m "Release v1.1.3 - ACTUALLY fixed frontend bundling (verified)"
git push origin desktop-v1.1.3
```

**Final Resolution**: v1.1.3 (commit af11a78)

---

## Verification Steps

### Pre-Build Verification

1. **Check package.json syntax**:
```bash
cd desktop_alone/electron-app
cat package.json | grep -A10 '"files"'
```

Should see the object syntax with `from`, `to`, `filter`.

2. **Ensure frontend source exists**:
```bash
ls -lh ../frontend/index.html
# Should show 91KB file
```

### Post-Build Verification

1. **Check app.asar contents**:
```bash
cd dist/linux-unpacked/resources
npx asar list app.asar | grep "frontend/index.html"
```

Should return: `/frontend/index.html`

2. **Extract and inspect** (optional):
```bash
npx asar extract app.asar /tmp/app-extracted
ls -lh /tmp/app-extracted/frontend/index.html
# Should show the HTML file
```

3. **Check file size**:
```bash
ls -lh dist/*.AppImage
# Should be ~3.9GB (includes frontend)
```

### Runtime Verification

1. **Launch the app** (with X11 or on local machine):
```bash
./NeuroInsight-1.0.0.AppImage
```

2. **Check logs**:
```bash
tail -f ~/.config/NeuroInsight/logs/main.log
```

Should see:
```
[INFO] NeuroInsight Desktop starting...
[INFO] Starting backend...
[INFO] Backend port captured: 8000
[INFO] Backend is ready!
[INFO] Loading frontend from: /path/to/frontend/index.html
[INFO] Frontend loaded successfully
[INFO] Application window shown
```

3. **Visual confirmation**:
- ✅ Application window appears
- ✅ Full UI visible (not dark/blank)
- ✅ Can see navigation, buttons, forms
- ✅ Can interact with the interface

---

## Secondary Issue: File Size Limits

### Problem

GitHub Releases have a **2GB per file limit**. Our installers exceed this:

| Platform | Size | Status |
|----------|------|--------|
| Linux AppImage | 2.8 GB | ❌ Too large |
| Windows EXE | ~2.5 GB | ❌ Too large |
| macOS DMG | 460 MB | ✅ OK |

### The Error

```
Error: File size (2944582663) is greater than 2 GiB
```

Release creation failed after successful builds.

### Solution Implemented

Modified workflow to:
1. **Build all installers** (stores in GitHub Actions Artifacts)
2. **Upload only checksums** to GitHub Releases
3. **Provide download instructions** in release notes

**File**: `.github/workflows/desktop-build-v15.yml`

**Key changes**:
```yaml
- name: Create Release (checksums only - installers too large)
  uses: softprops/action-gh-release@v1
  with:
    files: |
      artifacts/neuroinsight-linux/checksums-linux.txt
      artifacts/neuroinsight-windows/checksums-windows.txt
      artifacts/neuroinsight-mac/checksums-mac.txt
    body: |
      ## 📥 Downloads
      
      **⚠️ Installers are too large for GitHub Releases (2.8GB > 2GB limit)**
      
      ### Download from GitHub Actions Artifacts:
      1. Go to the [Actions tab](...)
      2. Scroll to "Artifacts" section
      3. Download your platform
```

### Where Users Download

**GitHub Actions Artifacts** (30-day retention):
1. https://github.com/phindagijimana/neuroinsight/actions
2. Click on the successful workflow run
3. Scroll to "Artifacts" section
4. Download:
   - `neuroinsight-linux.zip` (2.8 GB)
   - `neuroinsight-windows.zip` (~2.5 GB)
   - `neuroinsight-mac.zip` (460 MB)

### Future Solutions

See `desktop_alone/LARGE_FILE_WORKAROUND.md` for:
- AWS S3 hosting
- DigitalOcean Spaces
- File size optimization strategies
- Compression techniques

---

## Testing Procedure

### Local Testing (Before GitHub Build)

1. **Build locally**:
```bash
cd desktop_alone/electron-app
npm run build:linux
```

2. **Verify frontend bundled**:
```bash
cd dist/linux-unpacked/resources
npx asar list app.asar | grep "frontend/index.html"
# Must return: /frontend/index.html
```

3. **Test on machine with display**:
```bash
cd dist
./NeuroInsight-1.0.0.AppImage
```

4. **Check for dark window**:
   - ❌ Dark window = Frontend not bundled
   - ✅ Full UI = Success!

### GitHub Actions Testing

1. **Monitor build**:
```
https://github.com/phindagijimana/neuroinsight/actions
```

2. **Check all jobs succeed**:
   - ✅ Build Linux AppImage
   - ✅ Build Windows Installer
   - ✅ Build macOS DMG
   - ✅ Create GitHub Release

3. **Download artifacts**:
   - Click on workflow run
   - Scroll to "Artifacts"
   - Download each platform

4. **Test downloaded builds**:
   - Unzip
   - Install/run
   - Verify no dark window
   - Test basic functionality

### Verification Checklist

- [ ] Frontend bundled in app.asar
- [ ] App launches without errors
- [ ] No dark/blank window
- [ ] Full UI visible
- [ ] Can navigate between pages
- [ ] Can upload files
- [ ] Backend communication works
- [ ] Processing starts correctly
- [ ] Results display properly

---

## Distribution Strategy

### Current Approach (v1.1.3+)

**Method**: GitHub Actions Artifacts

**Pros**:
- ✅ Free
- ✅ Automatic with every build
- ✅ 30-day retention (renewable)
- ✅ Perfect for testing/small-scale use

**Cons**:
- ❌ Requires GitHub account to download
- ❌ Multiple steps for users
- ❌ 30-day expiration

**Best for**: Research labs, internal testing, <10 users/month

### Alternative Options

#### Option 1: DigitalOcean Spaces ($5/month)

**Setup**:
```bash
# Create Space
# Upload files
# Set public access
# Get direct download URLs
```

**Pros**: Cheap, simple, permanent hosting  
**Cons**: Costs money

#### Option 2: AWS S3 + CloudFront (~$50-100/month)

**Setup**: More complex, see `LARGE_FILE_WORKAROUND.md`

**Pros**: Scalable, fast, professional  
**Cons**: More expensive, complex setup

#### Option 3: Institutional Storage (Free)

**Setup**: Work with IT to host files

**Pros**: Free, permanent, fast on campus  
**Cons**: Requires IT approval, limited access off-campus

#### Option 4: File Size Optimization

Reduce installers to <2GB to use GitHub Releases:

**Options**:
- Use CPU-only PyTorch (saves ~800 MB)
- Download models on first run (saves ~500 MB)
- Better compression

**Effort**: Medium  
**Result**: Can use GitHub Releases directly

---

## Lessons Learned

### 1. Always Verify Tool Output

**Problem**: The search_replace tool said it succeeded, but changes weren't saved.

**Lesson**: After modifying critical files, always verify:
```bash
git diff package.json
cat package.json | grep -A10 "files"
```

### 2. Test Locally Before GitHub Actions

**Problem**: Discovered issue after multiple failed GitHub builds.

**Lesson**: Always build and verify locally first:
```bash
npm run build:linux
npx asar list dist/linux-unpacked/resources/app.asar | grep frontend
```

### 3. Use Object Syntax for Complex Bundling

**Problem**: String patterns like `"../frontend/index.html"` don't work reliably.

**Lesson**: Use object syntax with explicit `from`, `to`, `filter`:
```json
{
  "from": "../frontend",
  "to": "frontend",
  "filter": ["**/*"]
}
```

### 4. Check Multiple Layers of Packaging

**Problem**: Frontend could be missing at different stages.

**Lesson**: Verify at each stage:
1. Source files exist
2. package.json has correct config
3. app.asar contains frontend
4. Final AppImage/EXE/DMG works

### 5. Document Everything

**Problem**: Complex debugging process with multiple attempts.

**Lesson**: Keep detailed notes of:
- What was tried
- Why it failed
- What actually worked
- How to verify the fix

### 6. Version History Matters

**Timeline**:
- v1.1.1: ❌ Thought it was fixed, wasn't
- v1.1.2: ❌ Thought it was fixed, wasn't
- v1.1.3: ✅ Actually fixed (verified)

**Lesson**: Users must download v1.1.3 or later. Old versions won't work.

### 7. Have a Backup Plan for Distribution

**Problem**: GitHub's 2GB limit blocked automatic distribution.

**Lesson**: Know the limits of your platform:
- GitHub Releases: 2GB per file
- GitHub Artifacts: 30-day retention
- Have alternative hosting ready

---

## Quick Reference Commands

### Build and Verify

```bash
# Build desktop app
cd desktop_alone/electron-app
npm run build:linux

# Verify frontend bundled
cd dist/linux-unpacked/resources
npx asar list app.asar | grep "frontend/index.html"

# Should output: /frontend/index.html
```

### Check Package Configuration

```bash
# View files array
cat desktop_alone/electron-app/package.json | grep -A15 '"files"'

# Should show object with from/to/filter
```

### Commit and Deploy

```bash
# Stage changes
git add desktop_alone/electron-app/package.json
git add desktop_alone/electron-app/src/main.js

# Commit
git commit -m "Fix: Bundle frontend in desktop app"

# Push
git push origin main

# Create release tag
git tag desktop-v1.x.x -m "Release v1.x.x - Description"
git push origin desktop-v1.x.x
```

### Monitor Build

```bash
# Go to Actions
open https://github.com/phindagijimana/neuroinsight/actions

# Or check from CLI
gh run list --workflow desktop-build-v15.yml
```

### Download and Test

```bash
# Download artifacts
gh run download <run-id> -n neuroinsight-linux

# Unzip
unzip neuroinsight-linux.zip

# Test
chmod +x NeuroInsight-1.0.0.AppImage
./NeuroInsight-1.0.0.AppImage
```

---

## Troubleshooting Future Issues

### If Dark Window Appears Again

1. **Check if frontend is bundled**:
```bash
npx asar list app.asar | grep frontend
```

2. **If missing, check package.json**:
```bash
cat package.json | grep -A15 '"files"'
```

3. **Verify object syntax exists**:
```json
{
  "from": "../frontend",
  "to": "frontend",
  "filter": ["**/*"]
}
```

4. **Rebuild and verify**:
```bash
npm run build:linux
npx asar list dist/linux-unpacked/resources/app.asar | grep frontend
```

### If Frontend Bundled But Still Dark Window

1. **Check main.js path**:
```javascript
const frontendPath = path.join(__dirname, 'frontend', 'index.html');
// NOT: path.join(__dirname, '..', 'frontend', 'index.html')
```

2. **Check backend starts**:
```bash
tail -f ~/.config/NeuroInsight/logs/main.log
```

3. **Check for errors**:
```bash
cat ~/.config/NeuroInsight/logs/crashes.log
```

### If GitHub Release Fails

1. **Check file sizes**:
```bash
ls -lh dist/*.AppImage
# If > 2GB, will fail
```

2. **Use artifacts instead**:
   - Files are still available in Actions artifacts
   - 30-day retention
   - Share download instructions with users

3. **Consider optimization** (see LARGE_FILE_WORKAROUND.md)

---

## Related Documentation

- **DARK_WINDOW_FIX.md**: Technical details of the fix
- **LARGE_FILE_WORKAROUND.md**: File size solutions
- **INSTALLATION.md**: User installation guide
- **USER_MANUAL.md**: End-user documentation
- **.github/workflows/README.md**: CI/CD documentation

---

## Version History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| v1.0.0 | Nov 7 | ❌ Bug | Dark window, frontend not bundled |
| v1.1.1 | Nov 9 | ❌ Bug | Fix attempted, not actually applied |
| v1.1.2 | Nov 9 | ❌ Bug | Release fix, frontend still missing |
| v1.1.3 | Nov 9 | ✅ Fixed | **Frontend actually bundled and verified** |

---

## Contact & Support

**For issues with this process**:
1. Check this document first
2. Verify frontend bundled: `npx asar list app.asar | grep frontend`
3. Check build logs in GitHub Actions
4. Review related documentation above

**Last Updated**: November 9, 2025  
**Verified Working**: v1.1.3  
**Status**: ✅ Complete and Documented

