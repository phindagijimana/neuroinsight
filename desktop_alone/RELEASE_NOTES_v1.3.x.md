# Release Notes: v1.3.x Series

This document consolidates release notes for the v1.3.x release series of NeuroInsight Desktop.

---

## v1.3.1 - User Experience: Error Messages & Image Validation (2025-11-11)

### 🎯 Overview
This release dramatically improves the user experience when errors occur, with clear, actionable error messages and automatic T1w image validation.

### ✨ New Features

#### 1. Enhanced Error Message UI
- **Prominent Visual Design**: Error messages now have:
  - Larger, bolder headings with emoji indicators (⚠️, 🐳, ❌)
  - Bright yellow-highlighted "Quick Fix" boxes
  - Clear step-by-step instructions
  - Expandable full error details

#### 2. Docker Error Handling
- **Clear Docker Status Messages**: When Docker Desktop is not running, users see:
  - 🐳 **Docker Desktop is not running** - clear headline
  - Step-by-step instructions to start Docker Desktop
  - Platform-specific guidance (Mac/Windows/Linux)
  - Visual indicators (whale icon) to look for

#### 3. T1w Image Validation
- **Automatic Image Type Detection**: 
  - Validates images before processing
  - Checks NIfTI header for sequence type markers (T2, FLAIR, DWI, etc.)
  - Performs intensity distribution analysis (heuristic)
  
- **User-Friendly Rejection Messages**:
  - ❌ **This is not a T1w image** - clear rejection message
  - ✅ **Accepted sequences**: MPRAGE, SPGR, T1-FLAIR, 3D T1
  - ❌ **NOT supported**: T2-weighted, FLAIR, DWI/DTI
  - 💡 **Helpful tip**: "Look for 'T1' or 'MPRAGE' in your scan series names"

### 🔧 Technical Changes

#### Frontend (`desktop_alone/frontend/index.html`)
- **Improved Error Detection**: More robust pattern matching for error types
  - Docker errors: checks for 'docker' + ('not running' OR 'not installed' OR 'not available')
  - T1w errors: checks for 't1', 't2', 'flair', 'dwi', 'image type', 'sequence'
- **Enhanced Visual Design**:
  - Increased border width (border-2)
  - Larger icons (w-6 h-6)
  - Yellow-highlighted instruction boxes
  - Better spacing and typography

#### Backend (`desktop_alone/pipeline/processors/mri_processor.py`)
- **T1w Validation Method**: `_validate_t1w_image()`
  - Checks NIfTI header description for keywords (t2, flair, dwi, dti, diffusion)
  - Validates intensity distribution (median vs. max)
  - Raises `InvalidImageTypeError` with detailed explanation
  - Integrated into processing pipeline as Step 1.5 (18% progress)

- **Custom Exception**: `InvalidImageTypeError`
  - Includes detected image type (T2, FLAIR, DWI, unknown)
  - Provides detailed instructions on accepted sequences
  - Explains why T1w is required for FastSurfer

### 📝 User-Facing Changes

#### What Users Will See

**For Docker Not Running:**
```
⚠️ Job Failed
🐳 Docker Desktop is not running

NeuroInsight requires Docker to process MRI scans.

🔧 Quick Fix:
1. Open Docker Desktop from your Applications folder
2. Wait for the whale 🐳 icon to appear in your menu bar
3. The icon should be steady (not animating)
4. Return here and upload your MRI file again
```

**For Non-T1w Image:**
```
⚠️ Job Failed
❌ This is not a T1w image

Please upload a T1-weighted MRI scan instead.

✅ Accepted T1w sequences:
• MPRAGE (most common)
• SPGR (Spoiled Gradient Recalled Echo)
• T1-FLAIR
• 3D T1 (volumetric)

❌ NOT supported:
• T2-weighted
• FLAIR (unless T1-FLAIR)
• DWI/DTI

💡 Tip: Look for "T1" or "MPRAGE" in your scan series names
```

### 🎓 Why These Changes Matter

1. **Reduced User Confusion**: Clear error messages eliminate guesswork
2. **Faster Problem Resolution**: Step-by-step instructions get users unblocked quickly
3. **Data Quality Assurance**: T1w validation prevents incorrect results from wrong image types
4. **Professional UX**: Visual design improvements make errors less scary and more actionable

### 🔍 Technical Details

#### T1w Validation Algorithm
The validation uses a two-pronged approach:

1. **Header Keyword Detection** (high confidence):
   - Scans NIfTI header description for sequence markers
   - Detects: 't2', 't2w', 'flair', 'dwi', 'dti', 'diffusion'
   - Rejects if found (unless 't1' also present)

2. **Intensity Distribution Analysis** (low confidence - warning only):
   - Calculates median/max intensity ratio
   - T1w typically has ratio < 0.5 (dark CSF)
   - T2w typically has ratio > 0.6 (bright CSF)
   - Logs warning but doesn't reject (to avoid false positives)

#### Error Message Flow
```
Backend Error → Database (job.error_message) → API Response → Frontend UI
                                                              ↓
                                                    Pattern Matching → Categorized Display
```

### 📦 What's Included in v1.3.1

**Files Changed:**
- `desktop_alone/frontend/index.html` - Enhanced error message UI
- `desktop_alone/pipeline/processors/mri_processor.py` - T1w validation already present
- `desktop_alone/electron-app/package.json` - Version bump to 1.3.1
- `desktop_alone/RELEASE_NOTES_v1.3.x.md` - This file (consolidated release notes)

**Build Artifacts:**
- ✅ macOS: `NeuroInsight-1.3.1-arm64.dmg` (Apple Silicon), `NeuroInsight-1.3.1-x64.dmg` (Intel)
- ✅ Windows: `NeuroInsight-Setup-1.3.1.exe`
- ✅ Linux: `NeuroInsight-1.3.1.AppImage`

### 🚀 Deployment

**GitHub Actions Workflow:**
- Triggered by tag: `desktop-v1.3.1`
- Multi-platform builds (macOS, Windows, Linux)
- Automated artifact upload to release page

**Installation:**
1. Download the appropriate installer for your platform from the [Releases](https://github.com/phindagijimana/neuroinsight/releases) page
2. macOS: Drag NeuroInsight.app to Applications folder
3. Windows: Run the installer
4. Linux: Make AppImage executable and run

### 🐛 Bug Fixes (from v1.3.0)
- ✅ Fixed: Jobs failing immediately with `UnboundLocalError: local variable 'subprocess' referenced before assignment`
- ✅ Fixed: Duplicate import statements in mri_processor.py
- ✅ Fixed: Correct file path now used for desktop builds (`desktop_alone/pipeline/processors/mri_processor.py`)

### 🔄 Upgrade Path

**From v1.3.0:**
- Direct upgrade - no breaking changes
- Enhanced UX only - all existing functionality preserved

**From v1.2.x or earlier:**
- Direct upgrade - includes subprocess bug fix from v1.3.0
- All previously saved data remains accessible

---

## v1.3.0 - Critical Fix: Subprocess Bug (2025-11-11)

### 🐛 Bug Fixes

#### Fixed: Jobs Failing Immediately with UnboundLocalError
**Issue**: Jobs were failing immediately on all platforms with:
```
UnboundLocalError: local variable 'subprocess' referenced before assignment
```

**Root Cause**: 
- Duplicate `import subprocess` statements within a try-catch block
- The imports were being shadowed, causing the variable to be unbound
- Affected file: `desktop_alone/pipeline/processors/mri_processor.py`

**Solution**:
- Removed duplicate imports from inside the try block
- Ensured imports are at the module level
- Fixed in the correct file for desktop builds

**Files Changed:**
- `desktop_alone/pipeline/processors/mri_processor.py` - Removed duplicate imports

### 📝 Lessons Learned

1. **Two File Copies**: The repository has two copies of the processor:
   - `pipeline/processors/mri_processor.py` (web/HPC version)
   - `desktop_alone/pipeline/processors/mri_processor.py` (desktop version)
   - Desktop builds use the `desktop_alone/` copy

2. **Testing Across Platforms**: Bug appeared consistently across macOS, Windows, and Linux
   - Initial builds v1.2.8 and v1.2.9 applied fix to wrong file
   - v1.3.0 applied fix to correct file

### 🚀 Deployment

**Build Versions:**
- v1.2.8 (incorrect fix) - DEPRECATED
- v1.2.9 (incorrect fix) - DEPRECATED
- v1.3.0 (correct fix) - **STABLE**

---

## Version History Summary

| Version | Date | Status | Key Changes |
|---------|------|--------|-------------|
| v1.3.1 | 2025-11-11 | **Latest** | Enhanced error messages, T1w validation UI |
| v1.3.0 | 2025-11-11 | Stable | Fixed subprocess UnboundLocalError |
| v1.2.9 | 2025-11-11 | Deprecated | Incorrect fix location |
| v1.2.8 | 2025-11-11 | Deprecated | Incorrect fix location |
| v1.1.7 | 2025-11-11 | Broken | Original bug present |

---

## For Developers

### Building from Source

```bash
# From repository root
cd desktop_alone

# Install dependencies
cd electron-app && npm install && cd ..

# Build Python backend (one-time)
./build_desktop.sh

# Test locally
cd electron-app && npm start

# Build for distribution
cd electron-app && npm run build:mac  # or build:win, build:linux, build:all
```

### Running Tests

```bash
# Test with a sample T1w image
# The app should process successfully

# Test with a T2 image
# The app should reject with clear error message

# Test without Docker running
# The app should show Docker error message
```

### Debugging

```bash
# macOS: Run from terminal to see logs
/Applications/NeuroInsight.app/Contents/MacOS/NeuroInsight 2>&1 | tee ~/neuroinsight-debug.log

# Windows: Check logs in
%APPDATA%\NeuroInsight\logs\

# Linux: Run from terminal
./NeuroInsight.AppImage 2>&1 | tee ~/neuroinsight-debug.log
```

---

## Support

For issues, questions, or feedback:
- 📧 Email: support@neuroinsight.app
- 🐛 Issues: https://github.com/phindagijimana/neuroinsight/issues
- 📖 Documentation: https://github.com/phindagijimana/neuroinsight/wiki

---

**End of Release Notes for v1.3.x Series**
