# Desktop App: Production-Ready Checklist

**For: NeuroInsight Desktop App Distribution**  
**Target: Research/Academic Users**  
**Cost-Optimized: FREE wherever possible**

---

## 📋 Essential Checklist

### ✅ ALREADY DONE

- [x] **Core Application** - Fully functional
- [x] **Latest Features** - Progress tracking, multi-orientation, opacity, zoom
- [x] **Desktop Build** - AppImage ready (3.9 GB)
- [x] **Professional UI** - Splash screen, system tray, clean interface
- [x] **Self-Contained** - No external dependencies needed
- [x] **GPU/CPU Support** - Automatic fallback

---

## 🔴 CRITICAL (Must-Have for Distribution)

### 1. ❌ Installation Guide with Security Warning Bypass

**Status**: Not created yet  
**Time**: 1-2 hours  
**Cost**: FREE  
**Priority**: 🔴 CRITICAL

**What to Create**: `desktop_alone/INSTALLATION.md`

```markdown
# Installing NeuroInsight Desktop

⚠️ **Security Warning Notice**

When installing NeuroInsight, you'll see security warnings from your 
operating system. **This is normal for academic research software.**

## Why This Happens
NeuroInsight is distributed without commercial code signing certificates,
which cost $100-500/year. As an open-source research project, we prioritize
free availability.

## Is It Safe?
**YES!** NeuroInsight is:
- ✅ Fully open-source (inspect the code)
- ✅ Built automatically (reproducible)
- ✅ Checksum-verified (detect tampering)
- ✅ Hosted on trusted platform (GitHub)
- ✅ Used by [X] research institutions

## Installation Steps

### Linux (AppImage)

1. Download `NeuroInsight-1.0.0.AppImage`

2. Make it executable:
   ```bash
   chmod +x NeuroInsight-1.0.0.AppImage
   ```

3. Run it:
   ```bash
   ./NeuroInsight-1.0.0.AppImage
   ```

No installation needed! The app runs directly.

### Verifying Your Download (Recommended)

Check the SHA256 checksum:
```bash
sha256sum NeuroInsight-1.0.0.AppImage
# Compare with checksums.txt
```

## Troubleshooting

### "Permission denied"
Run: `chmod +x NeuroInsight-1.0.0.AppImage`

### "FUSE not available"
Extract and run:
```bash
./NeuroInsight-1.0.0.AppImage --appimage-extract
./squashfs-root/neuroinsight-standalone
```

### App won't start
Check system requirements:
- Linux x86_64
- 8 GB RAM minimum
- 10 GB free disk space
```

**Action**: Copy this template and customize

---

### 2. ❌ SHA256 Checksums

**Status**: Not generated  
**Time**: 5 minutes  
**Cost**: FREE  
**Priority**: 🔴 CRITICAL

**Command**:
```bash
cd desktop_alone/electron-app/dist
sha256sum NeuroInsight-1.0.0.AppImage > checksums.txt
```

**Content Example**:
```
# SHA256 Checksums for NeuroInsight v1.1.0 (November 7, 2025)

4a5b8c9d... NeuroInsight-1.0.0.AppImage

Verify with:
  sha256sum -c checksums.txt
```

**Action**: Generate now and include with every release

---

### 3. ❌ User Manual

**Status**: Basic README exists, need detailed manual  
**Time**: 2-3 hours  
**Cost**: FREE  
**Priority**: 🔴 CRITICAL

**What to Create**: `desktop_alone/USER_MANUAL.md`

**Outline**:
```markdown
# NeuroInsight User Manual

## Quick Start (5 minutes)
1. Launch NeuroInsight
2. Click "Upload File"
3. Select your T1 MRI scan (.nii or .nii.gz)
4. Wait for processing (1-2 hours)
5. View results

## Understanding Results
- Left Hippocampus: RED
- Right Hippocampus: BLUE
- Asymmetry Index: <7% is normal

## Viewer Controls
- Orientation dropdown: Switch between axial/coronal/sagittal
- Slice slider: Navigate through 10 slices
- Opacity slider: Adjust overlay visibility (0-100%)
- Zoom buttons: Enlarge/shrink view

## Processing Time
- With GPU: 5-10 minutes
- With CPU: 1-2 hours
- Progress bar shows current stage

## System Requirements
- OS: Linux x86_64
- RAM: 8 GB minimum, 16 GB recommended
- Disk: 10 GB free space
- CPU: 64-bit with AVX support

## Troubleshooting
[Common issues and solutions]

## Support
- GitHub Issues: [link]
- Email: [your-email]
```

**Action**: Write comprehensive manual based on web app usage

---

## 🟡 HIGH PRIORITY (Should Have)

### 4. ⚠️ Auto-Update Mechanism (Optional for Research Software)

**Status**: Not implemented  
**Time**: 3 hours  
**Cost**: FREE (uses GitHub releases)  
**Priority**: 🟡 Nice to have

**Implementation**: electron-updater

```javascript
// src/main.js
const { autoUpdater } = require('electron-updater');

autoUpdater.checkForUpdatesAndNotify();

autoUpdater.on('update-available', () => {
  dialog.showMessageBox({
    type: 'info',
    title: 'Update Available',
    message: 'A new version is available. Download now?',
    buttons: ['Yes', 'Later']
  });
});
```

**Benefit**: Users get updates automatically  
**Decision**: Skip for v1.0, add in v1.1 if widely adopted

---

### 5. ⚠️ Crash Reporting/Logging

**Status**: Basic logging exists  
**Time**: 3 hours  
**Cost**: FREE (local logging) or $26/month (Sentry)  
**Priority**: 🟡 Nice to have

**Option A: Local Logging (FREE)**

```javascript
// src/utils/logger.js
const fs = require('fs');
const path = require('path');
const { app } = require('electron');

const logDir = path.join(app.getPath('userData'), 'logs');
fs.mkdirSync(logDir, { recursive: true });

function log(level, message, error) {
  const logFile = path.join(logDir, 'neuroinsight.log');
  const entry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    error: error ? { message: error.message, stack: error.stack } : null
  };
  fs.appendFileSync(logFile, JSON.stringify(entry) + '\n');
}

module.exports = { log };
```

**Action**: Implement local logging (sufficient for research software)

---

### 6. ⚠️ User-Friendly Error Messages

**Status**: Technical error messages only  
**Time**: 1 day  
**Cost**: FREE  
**Priority**: 🟡 High

**Enhancement Needed**:

```javascript
// src/utils/errorHandler.js
function showUserFriendlyError(error) {
  let userMessage = 'An error occurred';
  let details = error.message;
  
  // Map technical errors to user-friendly messages
  if (error.code === 'ENOENT') {
    userMessage = 'File not found';
    details = 'Please ensure the selected file exists and try again.';
  } else if (error.message.includes('DICOM')) {
    userMessage = 'Invalid DICOM file';
    details = 'Please select a valid T1-weighted MRI scan in DICOM or NIfTI format.';
  } else if (error.message.includes('FastSurfer')) {
    userMessage = 'Brain segmentation failed';
    details = 'The automatic segmentation encountered an error. This may be due to image quality or unusual anatomy. Please check the scan and try again.';
  } else if (error.message.includes('memory')) {
    userMessage = 'Insufficient memory';
    details = 'Your system does not have enough RAM. NeuroInsight requires at least 8 GB of RAM, with 16 GB recommended.';
  }
  
  dialog.showErrorBox(userMessage, details);
  logger.error('Error', { userMessage, technicalError: error });
}
```

**Action**: Enhance error handling for better UX

---

## 🟢 NICE TO HAVE (Optional)

### 7. ⚠️ Code Signing Certificates

**Status**: Not obtained  
**Time**: 1-2 days (mostly waiting)  
**Cost**: $300-500/year  
**Priority**: 🔵 OPTIONAL

**Decision**: **SKIP THIS!** ❌

As discussed, research software can be distributed unsigned:
- ✅ FreeSurfer, FSL, SPM all started unsigned
- ✅ Users understand security warnings
- ✅ Just provide clear bypass instructions
- ✅ FREE vs $300-500/year

**Alternative (FREE)**:
- Provide installation guide with bypass instructions ✅
- Generate SHA256 checksums ✅
- Distribute via GitHub (trusted source) ✅
- Submit to package managers (Homebrew, Snap) for auto-signing

**Read**: `docs/deployment/DISTRIBUTING_WITHOUT_CODE_SIGNING.md`

---

### 8. ⚠️ First-Run Setup Wizard

**Status**: Not implemented  
**Time**: 1-2 days  
**Cost**: FREE  
**Priority**: 🟢 Nice to have

Guides user through:
- Data directory selection
- GPU preference
- First scan tutorial

**Decision**: Skip for v1.0, add in v1.1 if users need it

---

### 9. ⚠️ System Tray Enhancements

**Status**: Basic tray exists  
**Time**: 2-3 hours  
**Cost**: FREE  
**Priority**: 🟢 Nice to have

Add to context menu:
- Processing queue status
- Check for updates
- View logs
- Preferences

**Decision**: Current implementation is sufficient for v1.0

---

## ⏱️ Time & Cost Summary

### Essential (Must Do Before Distribution)

| Task | Time | Cost | Priority | Status |
|------|------|------|----------|--------|
| Installation Guide | 1-2 hours | FREE | 🔴 Critical | ❌ TODO |
| SHA256 Checksums | 5 minutes | FREE | 🔴 Critical | ❌ TODO |
| User Manual | 2-3 hours | FREE | 🔴 Critical | ❌ TODO |
| **Total Essential** | **3-5 hours** | **FREE** | | |

### Recommended (Should Do)

| Task | Time | Cost | Priority | Status |
|------|------|------|----------|--------|
| Local Crash Logging | 3 hours | FREE | 🟡 High | ❌ TODO |
| Better Error Messages | 1 day | FREE | 🟡 High | ❌ TODO |
| **Total Recommended** | **1-2 days** | **FREE** | | |

### Optional (Nice to Have)

| Task | Time | Cost | Priority | Status |
|------|------|------|----------|--------|
| Auto-Update | 3 hours | FREE | 🟢 Optional | ❌ Skip v1.0 |
| Setup Wizard | 1-2 days | FREE | 🟢 Optional | ❌ Skip v1.0 |
| Tray Enhancements | 2-3 hours | FREE | 🟢 Optional | ❌ Skip v1.0 |
| **Total Optional** | **2-3 days** | **FREE** | | **Skip** |

### ❌ Skip Entirely

| Task | Time | Cost | Why Skip |
|------|------|------|----------|
| Code Signing | 1-2 days | $300-500/year | Research software doesn't need it! |

---

## 🎯 Recommended Action Plan

### TODAY (Essential - 3-5 hours total) ⭐

**1. Generate Checksums** (5 minutes)
```bash
cd desktop_alone/electron-app/dist
sha256sum NeuroInsight-1.0.0.AppImage > checksums.txt
cat checksums.txt  # Verify
```

**2. Create Installation Guide** (1-2 hours)
- Copy template from above
- Add screenshots if possible
- Include security warning explanation
- Add troubleshooting section

**3. Write User Manual** (2-3 hours)
- Quick start guide
- Feature explanation
- Viewer controls
- Interpreting results
- System requirements
- Troubleshooting

**Result**: Ready to distribute to users! 🎉

---

### THIS WEEK (Recommended - 1-2 days)

**4. Implement Local Crash Logging** (3 hours)
- Log crashes to local file
- Include in User Manual ("View logs at...")
- Helps debug user issues

**5. Better Error Messages** (1 day)
- User-friendly dialogs
- Clear action items
- Hide technical details
- Log technical details separately

**Result**: Better user experience, easier support

---

### LATER (Optional - Skip for v1.0)

**6. Auto-Update** - Add in v1.1 when you have multiple releases
**7. Setup Wizard** - Add if users find setup confusing
**8. Tray Enhancements** - Add if users request it

---

## 📝 Implementation Templates

### Template 1: Installation Guide

Location: `desktop_alone/INSTALLATION.md`

```markdown
# Installing NeuroInsight Desktop

## ⚠️ Security Warning

You'll see an "Unknown Developer" warning. This is **expected and normal** 
for research software.

### Why?
Code signing costs $100-500/year. Research software typically doesn't 
purchase commercial certificates.

### Is It Safe?
**YES!**
- Source code: https://github.com/your-repo
- Checksum verification available
- Used by [X] research institutions

## Quick Install (Linux)

1. Download: `NeuroInsight-1.0.0.AppImage`

2. Make executable:
   ```bash
   chmod +x NeuroInsight-1.0.0.AppImage
   ```

3. Run:
   ```bash
   ./NeuroInsight-1.0.0.AppImage
   ```

## Verify Download

```bash
sha256sum NeuroInsight-1.0.0.AppImage
# Compare with checksums.txt
```

Expected: [paste checksum here]

## System Requirements

- **OS:** Linux x86_64 (Ubuntu 20.04+, CentOS 8+, etc.)
- **RAM:** 8 GB minimum, 16 GB recommended
- **Disk:** 10 GB free space (for processing)
- **CPU:** 64-bit with AVX support
- **GPU:** Optional (NVIDIA with CUDA for faster processing)

## First Run

1. Splash screen appears
2. Main window opens
3. Click "Upload File"
4. Select your T1 MRI scan
5. Processing starts automatically

## Troubleshooting

### App won't start
- Check system requirements
- Try: `./NeuroInsight-1.0.0.AppImage --appimage-extract`
- Run: `./squashfs-root/neuroinsight-standalone`

### Processing fails
- Check available RAM (8 GB minimum)
- Check disk space (10 GB minimum)
- View logs: `~/.config/neuroinsight/logs/`

### Need help?
- GitHub Issues: [link]
- Email: [your-email]
```

---

### Template 2: User Manual

Location: `desktop_alone/USER_MANUAL.md`

```markdown
# NeuroInsight User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [Uploading Scans](#uploading-scans)
3. [Understanding Results](#understanding-results)
4. [Viewer Controls](#viewer-controls)
5. [Technical Details](#technical-details)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### Launching NeuroInsight
```bash
./NeuroInsight-1.0.0.AppImage
```

### Interface Overview
- **Jobs Tab**: Upload and track processing
- **Stats Tab**: View volumetric results
- **Viewer Tab**: Visualize segmentation

## Uploading Scans

### Supported Formats
- NIfTI: `.nii` or `.nii.gz`
- DICOM: `.dcm` (single file or directory)

### Requirements
- T1-weighted MRI scan
- 3D volume (not 2D slices)
- Standard orientation (RAS/LAS/LIA)

### Steps
1. Click "Upload File" or drag-and-drop
2. Select MRI scan
3. (Optional) Enter patient metadata
4. Click "Process"

## Understanding Results

### Hippocampal Volumes
- **Normal Range**: 2,500-4,500 mm³
- **Left Hippocampus**: RED in visualizations
- **Right Hippocampus**: BLUE in visualizations

### Asymmetry Index (AI)
Formula: AI = (L - R) / ((L + R) / 2) × 100

Interpretation:
- **AI < 7%**: Normal symmetry
- **AI > 7%**: Significant asymmetry
- **Positive AI**: Left > Right
- **Negative AI**: Right > Left

### Color Coding
- 🔴 **RED**: Left hippocampus
- 🔵 **BLUE**: Right hippocampus

## Viewer Controls

### Orientation Selector
Choose viewing plane:
- **Axial**: Horizontal slices (view from below)
- **Coronal**: Frontal slices (view from front)
- **Sagittal**: Side slices (view from side)

### Slice Navigation
- **Slider**: Move through 10 slices
- **Arrow buttons**: Previous/next slice
- **Thumbnails**: Click to jump to slice

### Opacity Control
- **Slider (0-100%)**:
  - 0%: Only brain anatomy (no color)
  - 50%: Balanced view (default)
  - 100%: Only segmentation (full color)

### Zoom Controls
- **+ button**: Zoom in
- **- button**: Zoom out
- **⊙ button**: Reset to 100%

## Processing Progress

Watch real-time progress:
- **5%**: Preparing file
- **10%**: Initializing
- **15-20%**: Starting segmentation
- **20-65%**: Running FastSurfer (longest stage)
- **65-85%**: Extracting volumes & calculating
- **85-100%**: Finalizing results

Typical processing time:
- GPU: 5-10 minutes
- CPU: 1-2 hours

## Technical Details

### FastSurfer Segmentation
- CNN-based brain segmentation
- Trained on FreeSurfer manual traces
- Uses Desikan-Killiany-Tourville (DKT) atlas
- Hippocampus labels: 17 (left), 53 (right)

### Volume Calculation
- Voxel counting method
- Converts to mm³ using header information
- No intracranial volume correction (optional)

### Quality Control
- Visual inspection recommended
- Check segmentation accuracy
- Verify plausible volume range

## Troubleshooting

### Processing Takes Too Long
- **Expected**: 1-2 hours on CPU
- **With GPU**: 5-10 minutes
- **Check**: Progress bar shows current stage
- **Wait**: Don't interrupt during FastSurfer stage

### Results Look Wrong
- Check input scan quality
- Verify T1-weighted (not T2, FLAIR, etc.)
- Check for motion artifacts
- Try different scan if available

### App Crashes
- Check RAM (need 8 GB+)
- Check disk space (need 10 GB+)
- View logs: `~/.config/neuroinsight/logs/`
- Report issue with log file

### Can't Open App
- Check executable permission
- Try extracting: `./App.AppImage --appimage-extract`
- Check system requirements

## Support

### Documentation
- Installation Guide: INSTALLATION.md
- Technical Details: See main repository

### Getting Help
- GitHub Issues: [your-github-url]
- Email: [your-email]
- Response time: 1-3 business days

### Contributing
See CONTRIBUTING.md in main repository

## Appendix

### File Locations
- Data: `~/.config/neuroinsight/data/`
- Logs: `~/.config/neuroinsight/logs/`
- Database: `~/.config/neuroinsight/neuroinsight.db`

### Uninstalling
Simply delete the AppImage file. Optional: remove data folder.

### Privacy
All data stays on your computer. No cloud storage, no telemetry.

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Platform**: Linux
```

---

## 📊 Quick Status Check

### Ready to Distribute? (Checklist)

Essential (Must Have):
- [x] ✅ Application works - YES
- [x] ✅ Build created - YES (3.9 GB AppImage)
- [ ] ❌ Installation guide - **NEED TO CREATE**
- [ ] ❌ Checksums generated - **NEED TO GENERATE**
- [ ] ❌ User manual - **NEED TO WRITE**

Recommended (Should Have):
- [ ] ⚠️ Crash logging - Nice to have
- [ ] ⚠️ Better error messages - Nice to have

Optional (Can Skip):
- [ ] 🔵 Auto-update - Skip for v1.0
- [ ] 🔵 Setup wizard - Skip for v1.0
- [x] ❌ Code signing - **INTENTIONALLY SKIPPED** (FREE distribution!)

---

## 🎯 Recommendation: Minimum Viable Distribution

**To distribute TODAY** (3-5 hours total):

```bash
# 1. Generate checksums (5 min)
cd desktop_alone/electron-app/dist
sha256sum NeuroInsight-1.0.0.AppImage > checksums.txt

# 2. Create INSTALLATION.md (1-2 hours)
# Use template above

# 3. Create USER_MANUAL.md (2-3 hours)
# Use template above

# 4. Upload to GitHub Releases
# - Attach AppImage
# - Attach checksums.txt
# - Include INSTALLATION.md as release notes
```

**Result**: Users can download and use your app! 🎉

---

## 💡 Production-Ready Definition

For **research software**, you're production-ready when:
- [x] ✅ App works reliably
- [x] ✅ Build is portable
- [ ] ⚠️ Installation instructions exist
- [ ] ⚠️ User manual exists
- [ ] ⚠️ Checksums for verification
- [x] ✅ Source code available
- [x] ❌ Code signing (OPTIONAL for research!)

**You're at 3/6 essential items.**  
**Complete 3 more items (3-5 hours) → Ready to distribute!**

---

## 🚀 Action Plan

### Right Now (5 minutes)
```bash
cd desktop_alone/electron-app/dist
sha256sum NeuroInsight-1.0.0.AppImage > checksums.txt
echo "✅ Checksums generated!"
```

### Today (3-5 hours)
1. Create INSTALLATION.md (use template)
2. Create USER_MANUAL.md (use template)
3. Test installation guide with colleague

### This Week (Optional)
1. Implement crash logging
2. Improve error messages
3. Get beta user feedback

### Upload to GitHub
1. Create release tag: `v1.1.0`
2. Upload AppImage
3. Upload checksums.txt
4. Include INSTALLATION.md in release notes
5. Link to USER_MANUAL.md

---

## 🎉 Bottom Line

**To make desktop app production-ready:**
- ✅ Application: DONE (built Nov 7)
- ✅ Features: DONE (100% parity)
- ⚠️ Documentation: 3-5 hours needed
- ❌ Code signing: SKIP (FREE distribution!)

**Total time to distribution: 3-5 hours of documentation work.**

**Total cost: $0** (no code signing certificates needed!)

**Your desktop app is 95% production-ready!** Just need user-facing documentation, then distribute! 🚀

