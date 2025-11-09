# GitHub Actions Workflows

## Active Workflows

### 1. `desktop-build-v15.yml` ⭐ **USE THIS ONE**
**Status**: ✅ Active  
**Purpose**: Build desktop installers for all platforms with FIXED frontend bundling

**What it does:**
- Builds Linux AppImage (~3.9 GB)
- Builds Windows Setup.exe (~4.0 GB)  
- Builds macOS DMG (~4.0 GB)
- Includes frontend HTML in all builds (fixes dark window)
- Generates checksums for verification
- Creates GitHub Release automatically

**Triggers:**
- **Automatic**: When you push tags like `desktop-v1.1.1`, `desktop-v2.0.0`, etc.
- **Manual**: Go to Actions tab → "Desktop Build v15" → "Run workflow"

**How to use:**
```bash
# After committing your changes
git tag desktop-v1.1.1
git push origin desktop-v1.1.1

# Monitor at: https://github.com/phindagijimana/neuroinsight/actions
# Download from: https://github.com/phindagijimana/neuroinsight/releases
```

**Build time**: ~30-60 minutes for all platforms

---

### 2. `release.yml`
**Status**: ✅ Active  
**Purpose**: General release workflow (if applicable)

---

## Workflow History

### Deprecated/Removed:
- ❌ `desktop-build-v14-complete.yml` - Removed (had frontend bundling bug)

---

## Key Fix in v15

### Problem:
Users saw a **dark/blank window** when launching the app because the frontend HTML was not bundled.

### Solution:
- Fixed `electron-app/package.json` to properly bundle frontend directory
- Fixed `electron-app/src/main.js` to use correct path
- Added verification step to confirm frontend is bundled

### Files Affected:
- `desktop_alone/electron-app/package.json`
- `desktop_alone/electron-app/src/main.js`

See `desktop_alone/DARK_WINDOW_FIX.md` for full technical details.

---

## Quick Commands

### Trigger a new build:
```bash
git tag desktop-v1.1.1
git push origin desktop-v1.1.1
```

### Check build status:
```bash
# Go to:
https://github.com/phindagijimana/neuroinsight/actions
```

### Download built installers:
```bash
# Go to:
https://github.com/phindagijimana/neuroinsight/releases
```

### Manual trigger (no tag needed):
1. Go to: https://github.com/phindagijimana/neuroinsight/actions
2. Click "Desktop Build v15 - Fixed"
3. Click "Run workflow" button
4. Select branch (usually `main`)
5. Click "Run workflow"

---

## Troubleshooting

### Build fails on Linux:
- Check PyInstaller can build backend
- Check frontend/index.html exists
- Check npm dependencies install correctly

### Build fails on Windows:
- Usually Python or npm dependency issues
- Check error logs in Actions tab

### Build fails on macOS:
- May need to disable code signing (already done with `CSC_IDENTITY_AUTO_DISCOVERY: false`)
- Check Python dependencies compatible with macOS

### Frontend not bundled (dark window):
- **This is fixed in v15!**
- Old v14 builds had this issue
- Users must download v1.1.1 or later

---

## Contact

Questions about workflows? Check:
- `desktop_alone/DARK_WINDOW_FIX.md` - Technical details of the fix
- `desktop_alone/INSTALLATION.md` - User installation guide
- GitHub Issues - Report problems

---

**Last Updated**: November 9, 2025  
**Current Version**: v15 (Fixed)  
**Status**: ✅ Production Ready

