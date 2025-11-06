# Creating a Standalone Desktop App for NeuroInsight

## Overview

This guide explains how to package NeuroInsight as a standalone desktop application that users can download and run **without** installing Docker, Python, or any dependencies.

---

## Architecture

```
NeuroInsight.exe/app/AppImage
├── Electron (UI Shell)
├── Embedded Python Runtime
│   ├── FastAPI Backend
│   ├── Celery Worker
│   └── FastSurfer + Models
├── Embedded SQLite Database
├── Embedded Redis (or in-memory alternative)
└── Web Frontend (in Electron window)
```

**Download Size:** ~1.5-2 GB (due to ML models)  
**Installation:** Single click  
**Requirements:** None (all bundled)

---

## Implementation Options

### Option 1: Full Electron + Embedded Python (Recommended)

**Tools:**
- `electron-builder`: Package Electron app
- `PyInstaller`/`Nuitka`: Bundle Python backend
- `electron-store`: Local settings/database
- `python-shell`: Communicate between Electron and Python

**Pros:**
- ✅ Single installer
- ✅ Professional UI
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Auto-updates
- ✅ No user-side dependencies

**Cons:**
- ❌ Large download (1.5-2 GB)
- ❌ Complex build process
- ❌ Platform-specific builds required

---

### Option 2: Lightweight Python GUI (Alternative)

**Tools:**
- `PyQt6`/`PySide6`: Native UI
- `PyInstaller`: Bundle to executable
- `SQLite`: Embedded database

**Pros:**
- ✅ Smaller download (~800 MB)
- ✅ Simpler build
- ✅ Native look and feel

**Cons:**
- ❌ Less polished than web UI
- ❌ Harder to maintain UI
- ❌ Still requires Python bundling

---

## Detailed Implementation: Electron + Embedded Python

### Phase 1: Simplify the Backend Stack

**Current:**
```python
PostgreSQL → SQLite (embedded)
Redis → In-memory queue or embedded Redis
Docker/Singularity → Native Python execution
Celery → Background threads or multiprocessing
```

**Changes Needed:**

#### 1. Replace PostgreSQL with SQLite

```python
# backend/core/config.py
class Settings(BaseSettings):
    # Change from PostgreSQL
    database_url: str = Field(
        default="sqlite:///./neuroinsight.db",  # Embedded SQLite
        env="DATABASE_URL"
    )
```

#### 2. Replace Redis with In-Memory Queue

```python
# For desktop app, use simple in-process queue
# workers/celery_app.py - Desktop mode
if IS_DESKTOP_MODE:
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor(max_workers=2)
    
    def process_task(job_id):
        # Direct execution instead of Celery
        pass
else:
    # Use Celery for server deployment
    pass
```

#### 3. Bundle FastSurfer for Native Execution

```python
# pipeline/processors/mri_processor.py
def _run_fastsurfer_native(self, nifti_path: Path):
    """Run FastSurfer directly without containers"""
    import torch
    from FastSurferCNN import run_prediction
    
    # Direct Python execution
    # No Docker/Singularity needed
```

---

### Phase 2: Bundle Python Backend with PyInstaller

#### Create `build_backend.spec` file:

```python
# build_backend.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all FastSurfer model files
fastsurfer_data = collect_data_files('FastSurferCNN')
backend_data = [
    ('backend', 'backend'),
    ('pipeline', 'pipeline'),
    ('workers', 'workers'),
]

# Hidden imports for FastAPI, SQLAlchemy, etc.
hidden_imports = collect_submodules('uvicorn') + \
                 collect_submodules('fastapi') + \
                 collect_submodules('sqlalchemy') + \
                 collect_submodules('torch') + \
                 collect_submodules('nibabel')

a = Analysis(
    ['backend/main.py'],
    pathex=[],
    binaries=[],
    datas=fastsurfer_data + backend_data,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='neuroinsight-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Change to False for production
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='neuroinsight-backend',
)
```

#### Build command:

```bash
# Install PyInstaller
pip install pyinstaller

# Build backend executable
pyinstaller build_backend.spec

# Output: dist/neuroinsight-backend/
# Contains: neuroinsight-backend.exe + dependencies
```

---

### Phase 3: Integrate Python Backend into Electron

#### Update `hippo_desktop/src/main.js`:

```javascript
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const Store = require('electron-store');

const store = new Store();
let backendProcess = null;
let mainWindow = null;

// Path to bundled Python backend
const getBackendPath = () => {
  if (process.platform === 'darwin') {
    return path.join(
      process.resourcesPath,
      'backend',
      'neuroinsight-backend'
    );
  } else if (process.platform === 'win32') {
    return path.join(
      process.resourcesPath,
      'backend',
      'neuroinsight-backend.exe'
    );
  } else {
    return path.join(
      process.resourcesPath,
      'backend',
      'neuroinsight-backend'
    );
  }
};

// Start embedded backend
function startBackend() {
  const backendExe = getBackendPath();
  
  console.log('Starting backend:', backendExe);
  
  backendProcess = spawn(backendExe, ['--port', '8000'], {
    env: {
      ...process.env,
      DESKTOP_MODE: 'true',
      DATABASE_URL: 'sqlite:///./neuroinsight.db',
    },
  });

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend exited with code ${code}`);
  });
}

// Stop backend on app quit
app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});

// Create main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    icon: path.join(__dirname, '../build/icon.png'),
  });

  // Wait for backend to start (simple check)
  setTimeout(() => {
    mainWindow.loadURL('http://localhost:8000');
  }, 3000);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  startBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
```

---

### Phase 4: Update electron-builder Configuration

#### Modify `hippo_desktop/package.json`:

```json
{
  "build": {
    "appId": "com.neuroinsight.desktop",
    "productName": "NeuroInsight",
    "files": [
      "src/**/*",
      "assets/**/*",
      "!**/*.map"
    ],
    "extraResources": [
      {
        "from": "../dist/neuroinsight-backend",
        "to": "backend",
        "filter": ["**/*"]
      },
      {
        "from": "../models",
        "to": "models",
        "filter": ["**/*"]
      }
    ],
    "mac": {
      "category": "public.app-category.healthcare-fitness",
      "target": ["dmg", "zip"],
      "icon": "build/icon.icns",
      "minimumSystemVersion": "10.15.0"
    },
    "win": {
      "target": ["nsis", "portable"],
      "icon": "build/icon.ico",
      "requestedExecutionLevel": "asInvoker"
    },
    "linux": {
      "target": ["AppImage", "deb", "rpm"],
      "icon": "build/icons",
      "category": "Science;MedicalSoftware"
    }
  }
}
```

---

### Phase 5: Build Process

#### Create `scripts/build-desktop.sh`:

```bash
#!/bin/bash
set -e

echo "🏗️  Building NeuroInsight Desktop App..."

# Step 1: Build Python backend
echo "📦 Step 1: Packaging Python backend..."
cd backend
pip install -r requirements.txt
pip install pyinstaller
pyinstaller ../build_backend.spec
cd ..

# Step 2: Copy models
echo "🧠 Step 2: Copying ML models..."
mkdir -p models
cp -r singularity-images/fastsurfer-models/* models/

# Step 3: Build Electron app
echo "⚡ Step 3: Building Electron app..."
cd hippo_desktop
npm install
npm run dist

echo "✅ Build complete!"
echo "📦 Installers are in: hippo_desktop/dist/"
```

#### Make executable and run:

```bash
chmod +x scripts/build-desktop.sh
./scripts/build-desktop.sh
```

---

## Platform-Specific Builds

### Windows (.exe / .msi)

```bash
cd hippo_desktop
npm run dist:win

# Output:
# dist/NeuroInsight Setup 1.0.5.exe  (~1.5 GB)
# dist/NeuroInsight 1.0.5.exe         (portable)
```

### macOS (.dmg / .app)

```bash
cd hippo_desktop
npm run dist:mac

# Output:
# dist/NeuroInsight-1.0.5.dmg        (~1.5 GB)
# dist/NeuroInsight-1.0.5-mac.zip
```

### Linux (.AppImage / .deb / .rpm)

```bash
cd hippo_desktop
npm run dist:linux

# Output:
# dist/NeuroInsight-1.0.5.AppImage
# dist/neuroinsight_1.0.5_amd64.deb
# dist/neuroinsight-1.0.5.x86_64.rpm
```

---

## File Size Optimization

### Reduce Download Size:

1. **Compress models**: Use model quantization
   ```python
   # Reduce model precision from float32 to float16
   model = model.half()  # ~50% size reduction
   ```

2. **On-demand model download**: Download models on first run
   ```javascript
   // Download on first launch instead of bundling
   if (!modelsExist()) {
     downloadModels();  // ~500 MB download
   }
   ```

3. **Differential updates**: Only update changed files
   ```javascript
   // Use electron-updater for delta updates
   autoUpdater.checkForUpdates();
   ```

---

## Distribution

### Option A: Direct Download

Host installers on:
- GitHub Releases
- Your own website
- Institutional file server

### Option B: App Stores

- **Microsoft Store**: For Windows
- **Mac App Store**: For macOS (requires Apple Developer Account)
- **Snap Store**: For Linux

### Option C: Internal Distribution

For URMC lab members:
```
1. Upload to shared network drive
2. Send download link via email
3. Users download and install
```

---

## User Experience

### Installation Flow:

**Windows:**
```
1. Download: NeuroInsight-Setup.exe
2. Double-click to install
3. Choose install location
4. Click "Install"
5. Launch from Desktop shortcut
```

**macOS:**
```
1. Download: NeuroInsight.dmg
2. Double-click to mount
3. Drag NeuroInsight to Applications
4. Launch from Applications folder
```

**Linux:**
```
1. Download: NeuroInsight.AppImage
2. Make executable: chmod +x NeuroInsight.AppImage
3. Double-click to run
```

---

## Comparison: Approaches

| Aspect | Electron + Embedded Python | Python GUI App | Web App + Installer |
|--------|---------------------------|----------------|---------------------|
| **Download Size** | 1.5-2 GB | 800 MB - 1 GB | 50-100 MB |
| **Installation** | 1-click | 1-click | Installs backend + shortcut |
| **UI Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Maintenance** | Medium | Hard | Easy |
| **Cross-platform** | Easy | Medium | Easy |
| **Build Complexity** | High | Medium | Low |
| **User Dependencies** | None | None | Browser required |

---

## Recommended Path for NeuroInsight

### Short Term (1-2 weeks):
1. ✅ Create simplified backend (SQLite, no Docker)
2. ✅ Test PyInstaller bundling
3. ✅ Update Electron app to launch bundled backend
4. ✅ Build for one platform (your dev platform)

### Medium Term (1 month):
1. ✅ Build for all 3 platforms (Windows/Mac/Linux)
2. ✅ Set up auto-updater
3. ✅ Create user documentation
4. ✅ Beta test with lab members

### Long Term (3+ months):
1. ✅ Optimize model loading (lazy/on-demand)
2. ✅ Add crash reporting (Sentry)
3. ✅ Code signing for all platforms
4. ✅ Consider app store distribution

---

## Next Steps

1. **Decide on approach**: Electron + Python (recommended) or simpler alternative
2. **Simplify backend**: Remove Docker dependency, use SQLite
3. **Test PyInstaller**: Bundle backend to executable
4. **Update Electron app**: Integrate bundled backend
5. **Build and test**: Create installers for target platforms

---

## Resources

- [Electron Documentation](https://www.electronjs.org/docs/latest)
- [electron-builder Guide](https://www.electron.build/)
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)
- [Packaging Python Apps](https://packaging.python.org/)

---

**For NeuroInsight, the Electron + Embedded Python approach is recommended** because:
- ✅ Professional medical software feel
- ✅ You already have the Electron framework
- ✅ Web UI is already built and polished
- ✅ Suitable for scientific/medical software distribution

