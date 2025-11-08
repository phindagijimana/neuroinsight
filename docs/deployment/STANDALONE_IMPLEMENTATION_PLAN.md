# Standalone Desktop App Implementation Plan

Practical plan to convert existing NeuroInsight codebase to standalone desktop application.

**Timeline:** 5-6 weeks  
**Approach:** Reuse 80% of existing code, modify 20%  
**Goal:** One-click installer with no Docker requirement

---

## Current State Analysis

### What We Already Have (Reusable)

**Backend Code (95% reusable):**
```
backend/
├── api/              ✓ Reuse as-is
├── models/           ✓ Reuse (SQLite instead of PostgreSQL)
├── schemas/          ✓ Reuse as-is
├── services/         ✓ Reuse (minor changes)
└── core/             ⚠️ Modify (config, database)

Reusability: 95%
Changes: Configuration for SQLite, remove Redis
```

**Pipeline Code (100% reusable):**
```
pipeline/
├── processors/       ✓ Reuse completely
├── extractors/       ✓ Reuse as-is
└── visualizers/      ✓ Reuse as-is

Reusability: 100%
Changes: None! Already using FastSurfer
```

**Frontend Code (100% reusable):**
```
frontend/
├── index.html        ✓ Reuse as-is
├── styles/           ✓ Reuse as-is
└── assets/           ✓ Reuse as-is

Reusability: 100%
Changes: None needed
```

**What Needs Changing:**

```
workers/              ✗ Replace with threading
docker-compose.yml    ✗ Not needed
Dockerfiles          ✗ Not needed
Redis dependency     ✗ Remove
PostgreSQL           ⚠️ Replace with SQLite
Celery               ✗ Replace with ThreadPoolExecutor
```

---

## Implementation Plan

### Week 1: Backend Simplification

**Goal:** Remove container dependencies, use embedded alternatives

#### Task 1.1: Replace PostgreSQL with SQLite (Day 1-2)

**File:** `backend/core/config.py`

**Changes:**
```python
# BEFORE (current)
class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql://neuroinsight:password@localhost:15432/neuroinsight",
        env="DATABASE_URL"
    )

# AFTER (standalone)
class Settings(BaseSettings):
    # Auto-detect mode
    desktop_mode: bool = Field(default=False, env="DESKTOP_MODE")
    
    @property
    def database_url(self) -> str:
        if self.desktop_mode:
            # Desktop: Use SQLite in user data directory
            import platformdirs
            data_dir = platformdirs.user_data_dir("NeuroInsight")
            os.makedirs(data_dir, exist_ok=True)
            return f"sqlite:///{data_dir}/neuroinsight.db"
        else:
            # Server: Use PostgreSQL
            return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
```

**Why this works:** Same code runs in both modes!

**File:** `backend/models/job.py`

**Changes needed:**
```python
# SQLite doesn't support UUID natively
# Change UUID to String for SQLite compatibility

# BEFORE
from sqlalchemy.dialects.postgresql import UUID
id = Column(UUID(as_uuid=True), primary_key=True)

# AFTER
from sqlalchemy import String
import uuid

id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

# Rest of model unchanged!
```

**Testing:**
```bash
export DESKTOP_MODE=true
python backend/main.py
# Should work with SQLite!
```

**Time:** 1-2 days

---

#### Task 1.2: Replace Celery with Threading (Day 3-4)

**File:** `backend/services/task_service.py` (New file)

**Create abstraction layer:**
```python
"""Task execution abstraction - works with Celery or threads"""
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any

# Auto-detect mode
DESKTOP_MODE = os.getenv("DESKTOP_MODE", "false").lower() == "true"

if DESKTOP_MODE:
    # Desktop: Use thread pool
    executor = ThreadPoolExecutor(max_workers=2)
    
    class TaskResult:
        def __init__(self, future):
            self.future = future
        
        @property
        def id(self):
            return str(id(self.future))
        
        def get(self, timeout=None):
            return self.future.result(timeout=timeout)
    
    def submit_task(func: Callable, *args, **kwargs) -> TaskResult:
        """Submit task to thread pool"""
        future = executor.submit(func, *args, **kwargs)
        return TaskResult(future)

else:
    # Server: Use Celery
    from workers.tasks.processing import process_mri_task
    
    def submit_task(func: Callable, *args, **kwargs):
        """Submit task to Celery"""
        return process_mri_task.delay(*args, **kwargs)
```

**File:** `backend/api/upload.py`

**Modify to use abstraction:**
```python
# BEFORE
from workers.tasks.processing import process_mri_task
task = process_mri_task.delay(str(job.id))

# AFTER
from backend.services.task_service import submit_task
from workers.tasks.processing import process_mri

task = submit_task(process_mri, str(job.id))
```

**File:** `workers/tasks/processing.py`

**Extract core processing function:**
```python
# Separate Celery decorator from actual work

# Keep this (actual work)
def process_mri(job_id: str) -> dict:
    """Core processing logic - works without Celery"""
    # ... existing processing code ...
    return result

# This becomes optional wrapper
@celery_app.task(name="workers.tasks.processing.process_mri_task")
def process_mri_task(job_id: str) -> dict:
    """Celery wrapper - only used in server mode"""
    return process_mri(job_id)
```

**Testing:**
```bash
export DESKTOP_MODE=true
python -c "
from workers.tasks.processing import process_mri
result = process_mri('test-id')
print(result)
"
# Should work without Celery!
```

**Time:** 2 days

---

#### Task 1.3: Remove Redis Dependency (Day 5)

**No changes needed if using threading approach above!**

**For configuration clarity:**

**File:** `backend/core/config.py`

```python
@property
def use_celery(self) -> bool:
    """Use Celery only in server mode"""
    return not self.desktop_mode

@property
def celery_broker_url(self) -> str:
    if self.use_celery:
        return f"redis://{self.redis_host}:{self.redis_port}/0"
    else:
        return None  # Not used in desktop mode
```

**Time:** 1 day

---

### Week 2: PyInstaller Bundling

**Goal:** Create standalone Python executable

#### Task 2.1: Create PyInstaller Spec (Day 6-7)

**File:** `build_standalone.spec` (New file)

```python
# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all backend data files
backend_data = [
    ('backend', 'backend'),
    ('pipeline', 'pipeline'),
    ('frontend', 'frontend'),
]

# Collect FastSurfer model files
model_data = [
    ('singularity-images/fastsurfer-models', 'models'),
]

# Hidden imports (packages PyInstaller might miss)
hidden_imports = [
    # FastAPI and dependencies
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    
    # SQLAlchemy
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.ext.declarative',
    
    # FastSurfer dependencies
    'torch',
    'nibabel',
    'numpy',
    'scipy',
    
    # Other
    'platformdirs',
]

# Analysis
a = Analysis(
    ['backend/main.py'],
    pathex=[],
    binaries=[],
    datas=backend_data + model_data,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude dev dependencies
        'pytest',
        'black',
        'flake8',
        # Exclude if not using
        'matplotlib',
        'pandas',
    ],
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
    console=False,  # No console window
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

**Build and test:**
```bash
# Install PyInstaller
pip install pyinstaller

# Build
pyinstaller build_standalone.spec

# Test
cd dist/neuroinsight-backend
export DESKTOP_MODE=true
./neuroinsight-backend

# Should start backend on port 8000
```

**Time:** 2 days (including testing and fixes)

---

#### Task 2.2: Test Backend Bundle (Day 8-9)

**Create test script:**
```bash
#!/bin/bash
# test_standalone_backend.sh

echo "Testing standalone backend..."

# Set desktop mode
export DESKTOP_MODE=true

# Start backend
dist/neuroinsight-backend/neuroinsight-backend &
BACKEND_PID=$!

# Wait for startup
sleep 5

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/jobs/

# Test upload (if working)
# curl -F "file=@test.nii" http://localhost:8000/upload/

# Stop backend
kill $BACKEND_PID

echo "Tests complete!"
```

**Fix any issues:**
- Missing imports (add to hidden_imports)
- Missing data files (add to datas)
- Path issues (use resource paths)

**Time:** 2 days

---

### Week 3: Electron Integration

**Goal:** Wrap backend in Electron app

#### Task 3.1: Update Electron App (Day 10-11)

**File:** `hippo_desktop/src/main.js`

**Modify to launch bundled backend:**
```javascript
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const waitOn = require('wait-on');

let backendProcess = null;
let mainWindow = null;

// Get path to bundled backend
function getBackendPath() {
  if (app.isPackaged) {
    // Production: backend bundled in resources
    const resources = process.resourcesPath;
    
    if (process.platform === 'win32') {
      return path.join(resources, 'backend', 'neuroinsight-backend.exe');
    } else if (process.platform === 'darwin') {
      return path.join(resources, 'backend', 'neuroinsight-backend');
    } else {
      return path.join(resources, 'backend', 'neuroinsight-backend');
    }
  } else {
    // Development: use local build
    return path.join(__dirname, '../../../dist/neuroinsight-backend/neuroinsight-backend');
  }
}

// Start backend process
function startBackend() {
  const backendPath = getBackendPath();
  
  console.log('Starting backend:', backendPath);
  
  backendProcess = spawn(backendPath, [], {
    env: {
      ...process.env,
      DESKTOP_MODE: 'true',
      PORT: '8000',
    },
  });

  backendProcess.stdout.on('data', (data) => {
    console.log(`[Backend] ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`[Backend Error] ${data}`);
  });

  backendProcess.on('error', (error) => {
    console.error('Failed to start backend:', error);
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
async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    show: false,  // Don't show until backend ready
  });

  // Wait for backend to be ready
  try {
    await waitOn({
      resources: ['http://localhost:8000/health'],
      timeout: 30000,
    });
    
    // Backend ready, load UI
    mainWindow.loadURL('http://localhost:8000');
    mainWindow.show();
    
  } catch (error) {
    console.error('Backend failed to start:', error);
    // Show error dialog
  }
}

// App lifecycle
app.whenReady().then(async () => {
  startBackend();
  await createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
```

**File:** `hippo_desktop/package.json`

**Update build configuration:**
```json
{
  "name": "neuroinsight-desktop",
  "version": "1.0.0",
  "main": "src/main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder"
  },
  "dependencies": {
    "electron": "^28.0.0",
    "wait-on": "^7.0.1"
  },
  "devDependencies": {
    "electron-builder": "^24.9.1"
  },
  "build": {
    "appId": "com.neuroinsight.desktop",
    "productName": "NeuroInsight",
    "files": [
      "src/**/*",
      "assets/**/*"
    ],
    "extraResources": [
      {
        "from": "../dist/neuroinsight-backend",
        "to": "backend",
        "filter": ["**/*"]
      }
    ],
    "win": {
      "target": "nsis",
      "icon": "build/icon.ico"
    },
    "mac": {
      "target": "dmg",
      "icon": "build/icon.icns",
      "category": "public.app-category.healthcare-fitness"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "icon": "build/icons",
      "category": "Science;MedicalSoftware"
    }
  }
}
```

**Time:** 2 days

---

#### Task 3.2: Serve Frontend from Backend (Day 12)

**File:** `backend/main.py`

**Add static file serving:**
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# Serve frontend
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

# API routes
app.include_router(jobs_router)
app.include_router(upload_router)
# etc.
```

**Now frontend served directly from backend - no separate server needed!**

**Time:** 1 day

---

### Week 4: Testing & Bug Fixes

**Goal:** Ensure standalone backend works perfectly

#### Task 4.1: Test All Features (Day 13-15)

**Create test checklist:**
```
Test standalone backend:
□ Upload MRI file
□ Process with FastSurfer
□ View results
□ Export data
□ Delete job
□ Multiple jobs in sequence
□ Database persistence
□ Error handling
```

**Common issues to fix:**
- Path issues (use `__file__` for relative paths)
- Missing imports (add to spec file)
- Database migrations (ensure work with SQLite)
- File permissions (user data directory)

**Time:** 3 days

---

#### Task 4.2: Optimize Build (Day 16-17)

**Reduce bundle size:**

```python
# build_standalone.spec

# Exclude unnecessary packages
excludes=[
    'tkinter',  # GUI toolkit not used
    'matplotlib',  # If not used
    'pandas',  # If not used
    'pytest',  # Testing only
    'IPython',  # Development only
]

# Use UPX compression
upx=True
upx_exclude=[
    'vcruntime140.dll',  # Windows
    'python*.dll',  # Can cause issues
]
```

**Test bundle size:**
```bash
# Before optimization: ~1.2 GB
# After optimization: ~800 MB target
```

**Time:** 2 days

---

### Week 5: Electron Packaging

**Goal:** Create installers for all platforms

#### Task 5.1: Build Platform Installers (Day 18-20)

**Windows build:**
```bash
cd hippo_desktop
npm install
npm run build:win

# Output: dist/NeuroInsight-Setup-1.0.0.exe
# Size: ~1.5-2 GB
```

**macOS build (needs Mac):**
```bash
npm run build:mac

# Output: dist/NeuroInsight-1.0.0.dmg
# Size: ~1.5-2 GB
```

**Linux build:**
```bash
npm run build:linux

# Output:
# dist/NeuroInsight-1.0.0.AppImage
# dist/neuroinsight_1.0.0_amd64.deb
```

**Time:** 3 days (including CI/CD setup)

---

#### Task 5.2: Set Up CI/CD (Day 21-22)

**File:** `.github/workflows/build-desktop.yml` (New)

```yaml
name: Build Desktop Installers

on:
  push:
    tags:
      - 'v*'

jobs:
  build-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pyinstaller
      
      - name: Build backend
        run: pyinstaller build_standalone.spec
      
      - name: Upload backend artifact
        uses: actions/upload-artifact@v3
        with:
          name: backend
          path: dist/neuroinsight-backend/

  build-windows:
    needs: build-backend
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Download backend
        uses: actions/download-artifact@v3
        with:
          name: backend
          path: dist/neuroinsight-backend
      
      - name: Build Electron app
        run: |
          cd hippo_desktop
          npm install
          npm run build:win
      
      - name: Upload installer
        uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: hippo_desktop/dist/*.exe

  build-mac:
    needs: build-backend
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Download backend
        uses: actions/download-artifact@v3
        with:
          name: backend
          path: dist/neuroinsight-backend
      
      - name: Build Electron app
        run: |
          cd hippo_desktop
          npm install
          npm run build:mac
      
      - name: Upload installer
        uses: actions/upload-artifact@v3
        with:
          name: mac-installer
          path: hippo_desktop/dist/*.dmg

  build-linux:
    needs: build-backend
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Download backend
        uses: actions/download-artifact@v3
        with:
          name: backend
          path: dist/neuroinsight-backend
      
      - name: Build Electron app
        run: |
          cd hippo_desktop
          npm install
          npm run build:linux
      
      - name: Upload installer
        uses: actions/upload-artifact@v3
        with:
          name: linux-installer
          path: hippo_desktop/dist/*.AppImage

  release:
    needs: [build-windows, build-mac, build-linux]
    runs-on: ubuntu-latest
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v3
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            windows-installer/*
            mac-installer/*
            linux-installer/*
```

**Testing:**
```bash
# Create test tag
git tag v1.0.0-test
git push origin v1.0.0-test

# GitHub Actions will build all platforms
# Wait 30-60 minutes
# Check Releases page for installers
```

**Time:** 2 days

---

### Week 6: Polish & Distribution

**Goal:** Professional finish, ready to distribute

#### Task 6.1: Code Signing (Day 23-25)

**Windows:**
```bash
# Purchase certificate
# From: DigiCert, Sectigo, SSL.com
# Cost: $300-500/year

# Sign executable
signtool sign /f certificate.pfx \
  /p password \
  /fd sha256 \
  /tr http://timestamp.digicert.com \
  /td sha256 \
  "NeuroInsight-Setup.exe"
```

**macOS:**
```bash
# Apple Developer account ($99/year)

# Sign app
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  --options runtime \
  NeuroInsight.app

# Notarize
xcrun notarytool submit NeuroInsight.dmg \
  --apple-id your@email.com \
  --team-id TEAMID \
  --password @keychain:AC_PASSWORD

# Staple
xcrun stapler staple NeuroInsight.dmg
```

**Linux:**
```bash
# Optional: GPG signing
gpg --detach-sign NeuroInsight.AppImage
```

**Time:** 3 days (including certificate purchase)

---

#### Task 6.2: Documentation & Testing (Day 26-28)

**User documentation:**
```
Create:
- Installation guide
- User manual
- Troubleshooting guide
- Video tutorial (optional)
```

**Testing on clean systems:**
```
Test installation on:
□ Fresh Windows 10
□ Fresh Windows 11
□ macOS 12, 13, 14
□ Ubuntu 22.04, 24.04
□ Fedora latest
```

**Time:** 3 days

---

## Code Changes Summary

### Files to Modify (10 files)

```
1. backend/core/config.py
   - Add DESKTOP_MODE support
   - SQLite database URL
   - Conditional configuration

2. backend/core/database.py
   - SQLite-compatible UUID handling
   - Platform-specific data directory

3. backend/models/job.py
   - UUID → String(36) for SQLite
   - Same for other models

4. backend/services/task_service.py (NEW)
   - Abstraction layer
   - ThreadPoolExecutor for desktop
   - Celery for server

5. backend/api/upload.py
   - Use task_service abstraction
   - Remove direct Celery imports

6. backend/main.py
   - Serve frontend static files
   - Desktop mode detection

7. workers/tasks/processing.py
   - Extract core function from Celery task
   - Make Celery wrapper optional

8. hippo_desktop/src/main.js
   - Launch bundled backend
   - Wait for backend ready
   - Lifecycle management

9. hippo_desktop/package.json
   - Update build configuration
   - Include backend in bundle

10. build_standalone.spec (NEW)
    - PyInstaller configuration
    - Hidden imports
    - Data files
```

### Files to Create (5 files)

```
1. build_standalone.spec
   - PyInstaller spec

2. backend/services/task_service.py
   - Task abstraction layer

3. scripts/build_desktop.sh
   - Automated build script

4. .github/workflows/build-desktop.yml
   - CI/CD automation

5. test_standalone_backend.sh
   - Testing script
```

### Files Unchanged (Most of codebase!)

```
✓ pipeline/ (100% reusable)
✓ frontend/ (100% reusable)
✓ backend/api/ (95% reusable)
✓ backend/schemas/ (100% reusable)
✓ Most of backend/services/ (90% reusable)
```

**Total code reuse: 85-90%**

---

## Detailed Timeline

### Week-by-Week Breakdown

**Week 1: Backend Simplification**
```
Day 1-2: SQLite integration
Day 3-4: Threading instead of Celery
Day 5: Remove Redis dependencies
Goal: Backend works without Docker

Deliverable: Standalone backend runs locally
```

**Week 2: PyInstaller Bundling**
```
Day 6-7: Create PyInstaller spec
Day 8-9: Test and fix bundled backend
Goal: Single executable backend

Deliverable: backend.exe works standalone
```

**Week 3: Electron Integration**
```
Day 10-11: Update Electron app
Day 12: Frontend integration
Day 13-14: Testing
Goal: Electron launches backend

Deliverable: Desktop app works locally
```

**Week 4: Testing & Optimization**
```
Day 15-17: Feature testing
Day 18-19: Bug fixes
Day 20-21: Optimization
Goal: Production-ready app

Deliverable: Fully functional desktop app
```

**Week 5: Packaging**
```
Day 22-24: Platform builds
Day 25-26: CI/CD setup
Day 27-28: Cross-platform testing
Goal: Installers for all platforms

Deliverable: .exe, .dmg, .AppImage installers
```

**Week 6: Polish & Release**
```
Day 29-31: Code signing
Day 32-34: Documentation
Day 35: Release preparation
Goal: Professional release

Deliverable: Signed installers ready for distribution
```

---

## Quick Start Script

**File:** `scripts/build_desktop.sh` (Create this)

```bash
#!/bin/bash
set -e

echo "=================================="
echo "Building NeuroInsight Desktop App"
echo "=================================="

# Step 1: Build Python backend
echo ""
echo "[1/4] Building Python backend..."
cd "$(dirname "$0")/.."

pip install -r backend/requirements.txt
pip install pyinstaller

pyinstaller build_standalone.spec
echo "✓ Backend built: dist/neuroinsight-backend/"

# Step 2: Install Electron dependencies
echo ""
echo "[2/4] Installing Electron dependencies..."
cd hippo_desktop
npm install
echo "✓ Dependencies installed"

# Step 3: Build Electron app
echo ""
echo "[3/4] Building Electron app..."
npm run build
echo "✓ Electron app built"

# Step 4: Create installers
echo ""
echo "[4/4] Creating installers..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    npm run build:mac
    echo "✓ macOS installer: hippo_desktop/dist/*.dmg"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    npm run build:linux
    echo "✓ Linux installer: hippo_desktop/dist/*.AppImage"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    npm run build:win
    echo "✓ Windows installer: hippo_desktop/dist/*.exe"
fi

echo ""
echo "=================================="
echo "✓ Build Complete!"
echo "=================================="
echo ""
echo "Installers in: hippo_desktop/dist/"
echo ""
```

**Usage:**
```bash
chmod +x scripts/build_desktop.sh
./scripts/build_desktop.sh
```

---

## Testing Checklist

### Functionality Tests

**Desktop Mode:**
```
□ Backend starts automatically
□ No Docker/PostgreSQL/Redis needed
□ SQLite database created
□ Frontend loads in Electron window
□ Upload works
□ Processing works (FastSurfer)
□ Results display correctly
□ Export functions work
□ App closes cleanly
□ Data persists between sessions
```

**Cross-Platform:**
```
□ Windows 10 installation
□ Windows 11 installation
□ macOS 12+ installation (Intel)
□ macOS 12+ installation (Apple Silicon)
□ Ubuntu 22.04 installation
□ Fedora latest installation
```

**Performance:**
```
□ Startup < 10 seconds
□ Processing works (40-60 min CPU)
□ Memory < 6 GB peak
□ No crashes during processing
□ Clean shutdown
```

---

## Migration for Existing Users

### Backward Compatibility

**Server deployment (current):**
```bash
# Still works exactly as before!
docker-compose up -d
# Uses PostgreSQL, Redis, Celery

# Set server mode explicitly
export DESKTOP_MODE=false
```

**Desktop deployment (new):**
```bash
# Just run executable
./NeuroInsight.app
# Automatically uses SQLite, threading

# Or explicit
export DESKTOP_MODE=true
```

**Same codebase, auto-detects mode!**

---

## Risk Mitigation

### Potential Issues & Solutions

**Issue 1: PyInstaller missing imports**
```
Symptom: "ModuleNotFoundError" at runtime
Solution: Add to hiddenimports in spec file
Prevention: Thorough testing
```

**Issue 2: FastSurfer models not found**
```
Symptom: "Model file not found"
Solution: Ensure models in datas list
Prevention: Test bundled paths
```

**Issue 3: SQLite UUID incompatibility**
```
Symptom: Database errors
Solution: Use String(36) instead of UUID type
Prevention: Migration script
```

**Issue 4: File paths in bundled app**
```
Symptom: "File not found" errors
Solution: Use sys._MEIPASS for resource paths
Prevention: Use path helpers
```

**Issue 5: Large installer size**
```
Symptom: Users complain about download
Solution: Optimize, exclude unused packages
Mitigation: Progressive download, or CDN
```

---

## Success Criteria

### Definition of Done

**Functional:**
```
✓ User downloads single installer
✓ Installs with one click
✓ Launches without configuration
✓ Processes MRI scans correctly
✓ Results match server version
✓ No external dependencies
```

**Technical:**
```
✓ Installer < 2 GB
✓ Code signed (no warnings)
✓ Works on clean systems
✓ Memory < 6 GB peak
✓ Startup < 10 seconds
```

**Professional:**
```
✓ User documentation complete
✓ Error messages helpful
✓ Installer looks professional
✓ Auto-updater working
```

---

## Budget & Resources

### Time Investment

```
Developer time: 6 weeks (1 person)
Or: 3 weeks (2 developers)

Breakdown:
- Backend changes: 1 week
- PyInstaller setup: 1 week
- Electron integration: 1 week
- Testing: 1 week
- Packaging: 1 week
- Polish: 1 week
```

### Financial Investment

```
Code signing certificates:
- Windows: $300-500/year
- macOS: $99/year
- Total: $399-599/year

Development:
- If contractor: $10,000-15,000
- If staff: 6 weeks time

Total first year: $10,399-15,599
Annual ongoing: $399-599 (just certificates)
```

---

## SUMMARY

### What You Need to Do

**Code Changes:**
```
Modify: 10 files (~500 lines of code)
Create: 5 new files (~800 lines)
Reuse: 85-90% of existing codebase
Total effort: 6 weeks
```

**Build Process:**
```
1. Run: pip install pyinstaller
2. Run: pyinstaller build_standalone.spec
3. Run: cd hippo_desktop && npm run build
4. Get: Installers in hippo_desktop/dist/
```

**Result:**
```
One-click installers:
- NeuroInsight-Setup.exe (Windows)
- NeuroInsight.dmg (macOS)
- NeuroInsight.AppImage (Linux)

No Docker, No Python, No dependencies
Just like Cursor or Slack
```

---

**Next Step:** Start with Week 1, Task 1.1 - Replace PostgreSQL with SQLite. Want me to help implement the first changes?

