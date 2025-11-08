# One-Click Installation Packaging Guide

This document explains how standalone desktop applications are packaged for one-click installation, with real-world examples and challenges.

---

## How One-Click Installation Works

### The Packaging Process

#### Step 1: Bundle Python Runtime

**Tool:** PyInstaller, Nuitka, or cx_Freeze

**What happens:**
```python
# Input: Your Python application
backend/
├── main.py
├── models/
├── dependencies/
└── requirements.txt

# PyInstaller command
pyinstaller --onefile \
    --add-data "models:models" \
    --hidden-import torch \
    --hidden-import fastapi \
    backend/main.py

# Output: Single executable
dist/
└── backend.exe (or backend on Unix)
    ├── Python interpreter (embedded)
    ├── All Python libraries
    ├── Your code
    └── Data files
```

**Size:** Typically 100-500MB depending on dependencies

---

#### Step 2: Bundle Electron App

**Tool:** electron-builder

**What happens:**
```javascript
// Input: Electron application
electron-app/
├── src/main.js       // Electron code
├── backend.exe       // From Step 1
└── models/           // FastSurfer models

// electron-builder command
electron-builder --win --x64

// Output: Installer
dist/
└── NeuroInsight-Setup-1.0.0.exe
    ├── Electron runtime
    ├── Chromium browser
    ├── Node.js runtime
    ├── Your UI code
    └── Backend executable + models
```

**Size:** 1-2GB including all models and dependencies

---

#### Step 3: Create Platform Installer

**Windows (NSIS):**
```nsis
; Installer script
!define APP_NAME "NeuroInsight"
!define APP_VERSION "1.0.0"

; What it does:
- Copies files to Program Files
- Creates Start Menu shortcuts
- Creates Desktop shortcut
- Adds to Add/Remove Programs
- Sets up file associations (optional)
- Creates uninstaller
```

**macOS (DMG):**
```bash
# Creates disk image with:
- Application bundle (NeuroInsight.app)
- Drag-to-Applications instructions
- Background image
- License agreement
```

**Linux (AppImage):**
```bash
# Creates portable executable:
- No installation required
- Contains entire app
- Double-click to run
- Works on any Linux distro
```

---

## Real-World Examples

### Medical/Scientific Software

#### 1. **Slicer 3D** (Medical Image Analysis)

**How it's packaged:**
- Standalone installer (~500MB)
- Bundles Python + VTK + ITK + Qt
- Windows: NSIS installer
- macOS: DMG with .app bundle
- Linux: tar.gz with launcher script

**No prerequisites required**

**Download:** https://download.slicer.org/

**Similar to:** What we're building for NeuroInsight

---

#### 2. **FIJI/ImageJ** (Image Processing)

**How it's packaged:**
- Bundled with Java Runtime
- Platform-specific installers
- ~300-500MB download
- No Java installation needed

**User experience:**
- Download
- Double-click installer
- Use immediately

**Download:** https://fiji.sc/

---

#### 3. **Meshroom** (3D Reconstruction)

**How it's packaged:**
- Qt + Python application
- Bundled with all dependencies
- ~1-2GB installer
- No Python or Qt installation needed

**Technical stack:**
- Qt for UI
- Python for processing
- Bundled with PyInstaller

**Download:** https://alicevision.org/

---

#### 4. **Anaconda** (Python Distribution)

**How it's packaged:**
- Complete Python environment bundled
- ~500MB-3GB depending on version
- Platform-specific installers
- Includes hundreds of packages

**User experience:**
- One installer
- No prerequisites
- Complete environment ready

**Download:** https://www.anaconda.com/

---

#### 5. **Blender** (3D Modeling)

**How it's packaged:**
- Bundled Python interpreter
- All dependencies included
- ~300MB installer
- Portable or installed versions

**Technical approach:**
- Custom Python build
- Platform-specific optimizations
- No external dependencies

---

### Commercial Medical Software

#### 6. **OsiriX Lite** (DICOM Viewer - macOS)

**Packaging:**
- macOS app bundle
- ~100-200MB
- Mac App Store distribution
- Sandboxed for security

**Prerequisites:** None

---

#### 7. **MicroDicom** (DICOM Viewer - Windows)

**Packaging:**
- Portable .exe (no installation)
- Or traditional installer
- ~50MB
- Zero dependencies

---

#### 8. **Horos** (Medical Imaging - macOS)

**Packaging:**
- DMG installer
- ~100MB
- Includes all frameworks
- No prerequisites

---

### General Desktop Apps Using Similar Approach

#### 9. **Visual Studio Code**

**How it's packaged:**
- Electron-based
- Bundles Chromium + Node.js
- ~100-150MB installer
- No prerequisites

**Similar architecture to what we're building**

---

#### 10. **Slack Desktop**

**Packaging:**
- Electron application
- ~150MB installer
- Bundled runtime
- Auto-updates

---

#### 11. **Discord**

**Packaging:**
- Electron + Native modules
- ~100MB installer
- Cross-platform
- One-click installation

---

#### 12. **Atom Editor** (Before sunsetting)

**Packaging:**
- Electron application
- Bundled dependencies
- ~200MB
- PyInstaller for Python packages

---

## Detailed Packaging Steps for NeuroInsight

### Phase 1: Prepare Backend

```bash
# Install PyInstaller
pip install pyinstaller

# Create spec file
pyi-makespec backend/main.py \
    --name neuroinsight-backend \
    --onefile \
    --add-data "models:models" \
    --hidden-import torch \
    --hidden-import fastapi \
    --hidden-import uvicorn
```

**Edit spec file to add:**
```python
a = Analysis(
    ['backend/main.py'],
    datas=[
        ('models/', 'models/'),
        ('backend/static/', 'static/'),
    ],
    hiddenimports=[
        'torch', 'torchvision', 
        'fastapi', 'uvicorn',
        'sqlalchemy', 'alembic',
        'nibabel', 'numpy', 'scipy'
    ],
    excludes=['matplotlib', 'pandas'],  # Reduce size
)
```

**Build:**
```bash
pyinstaller neuroinsight-backend.spec
# Output: dist/neuroinsight-backend.exe (~500MB)
```

---

### Phase 2: Prepare Electron Wrapper

```javascript
// package.json
{
  "name": "neuroinsight",
  "version": "1.0.0",
  "main": "src/main.js",
  "build": {
    "appId": "com.neuroinsight.app",
    "productName": "NeuroInsight",
    "files": [
      "src/**/*",
      "assets/**/*"
    ],
    "extraResources": [
      {
        "from": "dist/neuroinsight-backend.exe",
        "to": "backend/"
      },
      {
        "from": "models/",
        "to": "models/"
      }
    ],
    "win": {
      "target": "nsis",
      "icon": "assets/icon.ico"
    },
    "mac": {
      "target": "dmg",
      "icon": "assets/icon.icns"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "icon": "assets/icon.png"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true
    }
  }
}
```

**Build command:**
```bash
npm run build  # or electron-builder
```

---

### Phase 3: Create Installers

#### Windows (NSIS)

**What electron-builder creates:**
```
NeuroInsight-Setup-1.0.0.exe
├── NSIS installer wrapper (~1MB)
├── Application files (compressed)
│   ├── NeuroInsight.exe (Electron)
│   ├── resources/
│   │   ├── app.asar (your code)
│   │   └── backend/
│   │       └── neuroinsight-backend.exe
│   └── models/
└── Uninstaller
```

**Installation process:**
1. User double-clicks setup.exe
2. NSIS extracts to temp
3. Shows installation wizard
4. User chooses install location
5. Files copied to Program Files
6. Shortcuts created
7. Registry entries added
8. Uninstaller created
9. Launch option shown

**Result:** Start menu entry, desktop shortcut, ready to use

---

#### macOS (DMG)

**What electron-builder creates:**
```
NeuroInsight-1.0.0.dmg
└── Contents:
    ├── NeuroInsight.app/
    │   ├── Contents/
    │   │   ├── MacOS/
    │   │   │   └── NeuroInsight (executable)
    │   │   ├── Resources/
    │   │   │   ├── app.asar
    │   │   │   ├── backend/
    │   │   │   └── models/
    │   │   └── Info.plist
    └── Applications (symlink)
```

**Installation process:**
1. User double-clicks DMG
2. DMG mounts as virtual disk
3. User drags app to Applications folder
4. Eject DMG
5. Launch from Applications

**Result:** App in Applications folder, launch like any Mac app

---

#### Linux (AppImage)

**What electron-builder creates:**
```
NeuroInsight-1.0.0.AppImage
├── AppImage runtime
└── Squashfs filesystem containing:
    ├── NeuroInsight executable
    ├── resources/
    ├── backend/
    └── models/
```

**Installation process:**
1. User downloads AppImage
2. Makes it executable: `chmod +x NeuroInsight-1.0.0.AppImage`
3. Double-click to run
4. No actual installation needed (portable)

**Optional:** Integrate with desktop using AppImageLauncher

---

## Challenges and Solutions

### Challenge 1: Large File Size

**Problem:**
- PyTorch: ~500MB
- Electron + Chromium: ~200MB
- FastSurfer models: ~400MB
- Total: 1.5-2GB download

**Solutions:**

**A. Differential Updates**
```javascript
// Only download changed files
const { autoUpdater } = require('electron-updater');

autoUpdater.on('download-progress', (progress) => {
  // Only downloads changed files, not full 2GB
  console.log(`Downloaded ${progress.percent}%`);
});
```

**Savings:** Updates typically <100MB

**B. Model Download on Demand**
```javascript
// Don't bundle models in installer
// Download on first run
async function downloadModels() {
  if (!modelsExist()) {
    showProgress("Downloading models...");
    await downloadFromServer();
  }
}
```

**Savings:** Installer reduced to ~800MB

**C. Compression**
```javascript
// electron-builder automatically compresses
compression: 'maximum'  // LZMA compression
```

**Savings:** 20-30% size reduction

**D. Exclude Unnecessary Dependencies**
```python
# PyInstaller - exclude what you don't need
excludes=[
    'matplotlib',  # If not used
    'pandas',      # If not used
    'PIL',         # If not used
]
```

**Savings:** 100-200MB

---

### Challenge 2: Code Signing

**Problem:**
- Windows SmartScreen blocks unsigned apps
- macOS Gatekeeper blocks unsigned apps
- Users see scary warnings

**Solutions:**

**Windows:**
```bash
# Purchase code signing certificate (~$100-400/year)
# Sign the installer
signtool sign /f certificate.pfx \
    /p password \
    /tr http://timestamp.digicert.com \
    /td sha256 \
    NeuroInsight-Setup.exe
```

**macOS:**
```bash
# Apple Developer account required ($99/year)
# Sign the app
codesign --deep --force --verify --verbose \
    --sign "Developer ID Application: Your Name" \
    NeuroInsight.app

# Notarize with Apple
xcrun altool --notarize-app \
    --primary-bundle-id com.neuroinsight.app \
    --username your@email.com \
    --password @keychain:AC_PASSWORD \
    --file NeuroInsight.dmg
```

**Linux:**
- Code signing less critical
- GPG signatures optional

**Workarounds for Testing:**
- Self-signing (users must trust manually)
- Institutional certificates (if available)
- Clear documentation on security warnings

---

### Challenge 3: Platform-Specific Builds

**Problem:**
- Must build on each platform
- Can't cross-compile native modules
- Different file structures

**Solutions:**

**A. CI/CD Pipeline (GitHub Actions)**
```yaml
# .github/workflows/build.yml
name: Build Installers

on: [push]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Windows
        run: npm run build:win
      
  build-mac:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build macOS
        run: npm run build:mac
      
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build Linux
        run: npm run build:linux
```

**Benefits:**
- Automatic builds on each commit
- All platforms built simultaneously
- Consistent build environment

**B. Virtual Machines**
- Windows VM for Windows builds
- macOS machine (or cloud service) for Mac builds
- Linux VM for Linux builds

---

### Challenge 4: Auto-Updates

**Problem:**
- Users need latest version
- Manual updates are painful
- Security updates critical

**Solutions:**

**electron-updater:**
```javascript
const { autoUpdater } = require('electron-updater');

// Check for updates
autoUpdater.checkForUpdatesAndNotify();

// When update available
autoUpdater.on('update-available', () => {
  dialog.showMessageBox({
    message: 'New version available. Download?'
  });
});

// Download and install
autoUpdater.on('update-downloaded', () => {
  autoUpdater.quitAndInstall();
});
```

**Update server options:**
- GitHub Releases (free)
- S3 bucket
- Custom server
- Institutional server

---

### Challenge 5: GPU Support

**Problem:**
- GPU drivers platform-specific
- CUDA versions vary
- PyTorch GPU builds are large

**Solutions:**

**A. CPU-only Default**
```python
# Bundle CPU version (smaller)
# Detect GPU at runtime
if torch.cuda.is_available():
    download_gpu_libraries()
```

**B. Separate GPU Installer**
```
NeuroInsight-CPU-1.0.0.exe (1.2GB)
NeuroInsight-GPU-1.0.0.exe (2.5GB)  # Optional
```

**C. Runtime Detection**
```python
# Install CPU version
# If GPU detected, download GPU libs on demand
if has_nvidia_gpu():
    install_cuda_libraries()
```

---

### Challenge 6: First-Run Performance

**Problem:**
- Backend takes time to start first time
- Model loading is slow
- Database initialization

**Solutions:**

**A. Splash Screen**
```javascript
// Show splash while backend starts
const splash = new BrowserWindow({
  width: 400,
  height: 300,
  transparent: true,
  frame: false
});

splash.loadFile('splash.html');

// Hide when ready
backend.on('ready', () => {
  splash.close();
  mainWindow.show();
});
```

**B. Lazy Loading**
```python
# Don't load models until needed
models = None

def process_image(path):
    global models
    if models is None:
        models = load_models()  # First time only
    return models.predict(path)
```

**C. Precomputed Cache**
```python
# Pre-compile Python on install
python -m compileall .
```

---

### Challenge 7: Permissions

**Problem:**
- Writing to Program Files requires admin
- macOS sandboxing restrictions
- Antivirus false positives

**Solutions:**

**A. User Directory for Data**
```javascript
// Don't write to install directory
const userDataPath = app.getPath('userData');
// C:/Users/Name/AppData/Roaming/NeuroInsight (Windows)
// ~/Library/Application Support/NeuroInsight (macOS)
// ~/.config/NeuroInsight (Linux)

database_path = path.join(userDataPath, 'data.db');
```

**B. Request Permissions Appropriately**
```javascript
// macOS - request permissions when needed
const { systemPreferences } = require('electron');

async function requestFileAccess() {
  const status = await systemPreferences.getMediaAccessStatus('camera');
  if (status !== 'granted') {
    await systemPreferences.askForMediaAccess('camera');
  }
}
```

**C. Antivirus Whitelisting**
```
Documentation for users:
"If antivirus blocks, add exception for NeuroInsight"
Submit to antivirus vendors for whitelisting
```

---

### Challenge 8: Uninstallation

**Problem:**
- Need to clean up properly
- Remove all files
- Don't leave orphaned data

**Solutions:**

**Windows (NSIS):**
```nsis
Section "Uninstall"
  ; Remove files
  Delete "$INSTDIR\*.*"
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$DESKTOP\NeuroInsight.lnk"
  Delete "$SMPROGRAMS\NeuroInsight\*.*"
  
  ; Remove registry entries
  DeleteRegKey HKLM "Software\NeuroInsight"
  
  ; Ask about user data
  MessageBox MB_YESNO "Remove user data?" IDYES RemoveData
  Goto Done
  
  RemoveData:
    RMDir /r "$APPDATA\NeuroInsight"
  
  Done:
SectionEnd
```

**macOS:**
```bash
# User drags to trash
# Clear app data manually or with cleanup app
```

---

## Testing One-Click Installation

### Test Checklist

**Fresh System Testing:**
- [ ] Install on clean Windows 10/11
- [ ] Install on clean macOS (multiple versions)
- [ ] Install on Ubuntu/Fedora/etc.
- [ ] No prerequisites installed
- [ ] Limited user account (not admin)

**Installation Testing:**
- [ ] Download completes successfully
- [ ] Installer runs without errors
- [ ] Can choose install location
- [ ] Shortcuts created correctly
- [ ] Uninstaller works properly

**First Run Testing:**
- [ ] Application starts without errors
- [ ] No missing dependencies
- [ ] Database initializes
- [ ] All features work
- [ ] GPU detected if available

**Update Testing:**
- [ ] Auto-update notification works
- [ ] Update downloads successfully
- [ ] Update installs without issues
- [ ] Data preserved after update

---

## Distribution Strategies

### Option 1: GitHub Releases (Free)

```bash
# Build creates installers
# Upload to GitHub Releases
# electron-updater automatically checks GitHub

# Users download from:
https://github.com/yourorg/neuroinsight/releases/latest
```

**Pros:** Free, automatic updates, version history

**Cons:** Public (can make private repo), bandwidth limits

---

### Option 2: Institutional Server

```bash
# Host on university server
https://institution.edu/software/neuroinsight/

NeuroInsight-Setup-1.0.0.exe
NeuroInsight-1.0.0.dmg
NeuroInsight-1.0.0.AppImage
```

**Pros:** Institutional control, private, no limits

**Cons:** Must maintain server, manual updates

---

### Option 3: App Stores

**Microsoft Store:**
- Automated installation
- Auto-updates built-in
- $19 one-time fee

**Mac App Store:**
- $99/year Apple Developer account
- Strict sandboxing requirements
- Review process

**Linux Snap/Flatpak:**
- Free
- Automatic updates
- Cross-distro

---

## Summary

### How It Works
1. **Bundle Python** with PyInstaller → ~500MB executable
2. **Wrap in Electron** → Add UI layer
3. **Create Installer** with electron-builder → Platform-specific installers
4. **Distribute** → Users download and install

### Real Examples
- Slicer 3D, FIJI, Meshroom (medical/scientific)
- VS Code, Slack, Discord (Electron apps)
- All work exactly this way

### Main Challenges
1. Large file size (1.5-2GB) → Compression, lazy loading
2. Code signing → Costs $100-500/year
3. Platform builds → CI/CD automation
4. Auto-updates → electron-updater
5. GPU support → Separate builds or runtime download

### Timeline
- 5-6 weeks for complete implementation
- Worth it for professional medical software distribution

### Recommendation
**Absolutely feasible** for NeuroInsight. Many medical software packages use this exact approach successfully.

---

**Next Steps:** See [docs/DESKTOP_APP_WITHOUT_DOCKER.md](DESKTOP_APP_WITHOUT_DOCKER.md) for implementation details.

