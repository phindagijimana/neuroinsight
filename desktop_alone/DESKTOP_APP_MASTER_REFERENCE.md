# NeuroInsight Desktop App - Complete Master Reference

**Date**: November 9, 2025  
**Version**: v1.1.3+  
**Status**: Production Ready  
**Type**: Standalone Electron Desktop Application

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Technology Stack](#technology-stack)
5. [Build System](#build-system)
6. [Development Setup](#development-setup)
7. [Building Installers](#building-installers)
8. [CI/CD Pipeline](#cicd-pipeline)
9. [Configuration Files](#configuration-files)
10. [Key Components](#key-components)
11. [Common Issues & Solutions](#common-issues--solutions)
12. [Deployment](#deployment)
13. [Testing](#testing)
14. [Maintenance](#maintenance)
15. [Troubleshooting](#troubleshooting)
16. [Related Documentation](#related-documentation)

---

## Overview

### What Is This?

NeuroInsight Desktop is a **standalone desktop application** for automated hippocampal asymmetry analysis from T1-weighted MRI scans.

### Key Features

- ✅ **Automated brain segmentation** with FastSurfer
- ✅ **Hippocampal volume calculation** and asymmetry index
- ✅ **Multi-orientation viewer** (axial, coronal, sagittal)
- ✅ **Real-time progress tracking** (11 stages)
- ✅ **Crash logging** for debugging
- ✅ **GPU/CPU automatic fallback**
- ✅ **No Docker required** - fully standalone

### Target Platforms

- **Linux**: AppImage (Ubuntu, Debian, Fedora, etc.)
- **Windows**: NSIS Installer (.exe)
- **macOS**: DMG (x64 and arm64)

### Use Cases

- **Research labs**: Process MRI scans without cloud dependencies
- **Clinical settings**: Offline processing with patient data privacy
- **Remote locations**: No internet connection required
- **Teaching**: Demonstrate hippocampal analysis workflows

---

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────┐
│           Electron Shell (UI Process)           │
│  - Window management                            │
│  - Splash screen                                │
│  - Logging                                      │
└────────────┬────────────────────────────────────┘
             │ IPC
             ▼
┌─────────────────────────────────────────────────┐
│         Frontend (React + TypeScript)           │
│  - Single-file HTML (no build needed)           │
│  - Tailwind CSS styling                         │
│  - Recharts for visualizations                  │
└────────────┬────────────────────────────────────┘
             │ HTTP (localhost:PORT)
             ▼
┌─────────────────────────────────────────────────┐
│         Backend (Python FastAPI)                │
│  - REST API                                     │
│  - Job management                               │
│  - SQLite database                              │
│  - File storage                                 │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│      Processing Pipeline (FastSurfer)           │
│  - Brain segmentation                           │
│  - Hippocampal volume extraction                │
│  - Asymmetry calculations                       │
│  - Visualization generation                     │
└─────────────────────────────────────────────────┘
```

### Component Layers

1. **Electron Shell**: Native desktop wrapper
2. **Frontend**: React-based UI loaded in Electron window
3. **Backend**: FastAPI server spawned as subprocess
4. **Pipeline**: MRI processing with FastSurfer

### Communication Flow

```
User → Electron UI → Frontend (React) → Backend API → Processing Pipeline
                                               ↓
                                          SQLite DB
                                               ↓
                                         File Storage
```

---

## Project Structure

```
desktop_alone/
│
├── backend/                    # Python FastAPI backend
│   ├── api/                   # REST API endpoints
│   │   ├── jobs.py           # Job management
│   │   ├── upload.py         # File uploads
│   │   ├── metrics.py        # Metrics/results
│   │   └── visualizations.py # Image serving
│   ├── core/                 # Core functionality
│   │   ├── config_desktop.py # Desktop-specific config
│   │   ├── database.py       # SQLite setup
│   │   └── logging.py        # Logging setup
│   ├── models/               # Database models
│   │   ├── job.py           # Job model
│   │   └── metric.py        # Metrics model
│   ├── services/             # Business logic
│   │   ├── job_service.py   # Job management
│   │   ├── storage_service.py # File storage
│   │   └── task_service.py  # Task execution
│   ├── main.py              # FastAPI app entry point
│   └── requirements.txt      # Python dependencies
│
├── electron-app/              # Electron wrapper
│   ├── src/                  # Source code
│   │   ├── main.js          # Main process (Electron)
│   │   ├── splash.html      # Splash screen
│   │   └── utils/
│   │       └── logger.js    # Custom logging
│   ├── assets/              # App icons
│   ├── build/               # Build resources
│   ├── dist/                # Built installers (output)
│   ├── package.json         # Electron config
│   └── node_modules/        # Node dependencies
│
├── frontend/                  # React frontend
│   ├── index.html           # Single-file React app
│   ├── package.json         # Frontend dependencies
│   └── vite.config.ts       # Vite config (dev only)
│
├── pipeline/                  # Processing pipeline
│   ├── processors/
│   │   └── mri_processor.py # MRI processing
│   └── utils/
│       ├── asymmetry.py     # Asymmetry calculations
│       ├── segmentation.py  # Segmentation helpers
│       └── visualization.py # Image generation
│
├── workers/                   # Background tasks
│   └── tasks/
│       └── processing.py    # Async job processing
│
├── models/                    # Shared models
├── build.spec                # PyInstaller spec
├── requirements.txt          # Python dependencies
│
└── Documentation/            # All documentation
    ├── COMPLETE_BUNDLING_FIX_REFERENCE.md
    ├── DARK_WINDOW_FIX.md
    ├── LARGE_FILE_WORKAROUND.md
    ├── INSTALLATION.md
    ├── USER_MANUAL.md
    └── LOGS_AND_TROUBLESHOOTING.md
```

---

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18 | UI framework |
| Tailwind CSS | 3.x | Styling |
| Recharts | 2.10 | Data visualization |
| Babel Standalone | Latest | JSX transpilation |

**Note**: Frontend is a **single HTML file** with inline React. No build step required!

### Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10 | Backend language |
| FastAPI | Latest | REST API framework |
| SQLite | 3 | Database |
| Uvicorn | Latest | ASGI server |
| PyTorch | 2.x | ML framework |
| FastSurfer | Latest | Brain segmentation |

### Electron

| Technology | Version | Purpose |
|-----------|---------|---------|
| Electron | 28.x | Desktop wrapper |
| electron-builder | 24.x | Packaging tool |
| electron-log | 5.x | Logging |
| wait-on | 7.x | Wait for backend startup |

### Build Tools

| Tool | Purpose |
|------|---------|
| PyInstaller | Bundle Python backend into executable |
| electron-builder | Create platform installers |
| npm | Node package management |
| pip | Python package management |

---

## Build System

### Overview

The build process has **two stages**:

1. **Backend Build**: PyInstaller bundles Python → single executable
2. **Frontend Build**: electron-builder packages everything → installer

### Stage 1: Backend Build (PyInstaller)

**File**: `desktop_alone/build.spec`

**What it does**:
- Collects Python code and dependencies
- Bundles PyTorch, FastSurfer, FastAPI
- Creates standalone executable: `neuroinsight-backend`
- Output: `dist/neuroinsight-backend/`

**Command**:
```bash
cd desktop_alone
pyinstaller build.spec --clean --noconfirm
```

**Key Configuration**:
```python
# build.spec
a = Analysis(
    ['backend/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend/alembic', 'alembic'),
        ('models', 'models'),
        ('pipeline', 'pipeline'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'fastapi',
        # ... more imports
    ],
)
```

### Stage 2: Frontend Build (electron-builder)

**File**: `desktop_alone/electron-app/package.json`

**What it does**:
- Packages Electron app
- Bundles backend executable
- Bundles frontend HTML
- Creates platform installers (AppImage/EXE/DMG)

**Command**:
```bash
cd desktop_alone/electron-app
npm run build:linux    # Linux AppImage
npm run build:win      # Windows installer
npm run build:mac      # macOS DMG
```

**Key Configuration**:
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
      }
    ],
    "extraResources": [
      {
        "from": "../dist/neuroinsight-backend",
        "to": "backend",
        "filter": ["**/*"]
      }
    ]
  }
}
```

### Build Output

**Linux**:
```
desktop_alone/electron-app/dist/
├── NeuroInsight-1.0.0.AppImage  (~3.9 GB)
├── linux-unpacked/              (extracted files)
└── checksums-linux.txt
```

**Windows**:
```
desktop_alone/electron-app/dist/
├── NeuroInsight-Setup-1.0.0.exe (~4.0 GB)
└── checksums-windows.txt
```

**macOS**:
```
desktop_alone/electron-app/dist/
├── NeuroInsight-1.0.0.dmg       (232 MB x64)
├── NeuroInsight-1.0.0-arm64.dmg (228 MB arm64)
└── checksums-mac.txt
```

---

## Development Setup

### Prerequisites

**System Requirements**:
- **Linux**: Ubuntu 20.04+ or similar
- **RAM**: 16 GB minimum (for building)
- **Disk**: 20 GB free space
- **Python**: 3.10
- **Node.js**: 18.x

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/phindagijimana/neuroinsight.git
cd neuroinsight/desktop_alone

# 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller

# 3. Set up Node.js
cd electron-app
npm install

# 4. Verify frontend exists
ls -lh ../frontend/index.html
# Should show 91KB file
```

### Development Mode

**Terminal 1 - Backend**:
```bash
cd desktop_alone
source venv/bin/activate
export DESKTOP_MODE=true
python backend/main.py
# Backend runs on http://127.0.0.1:8000
```

**Terminal 2 - Frontend (Dev Server)**:
```bash
cd desktop_alone/frontend
npm run dev
# Frontend runs on http://localhost:5173
```

**Terminal 3 - Electron (Dev Mode)**:
```bash
cd desktop_alone/electron-app
npm run dev
# Electron window opens
```

**Or use Electron directly** (loads production frontend):
```bash
cd desktop_alone/electron-app
npm start
# Starts backend + opens Electron
```

---

## Building Installers

### Local Build (All Platforms)

**Prerequisites**:
- Linux: Any recent distribution
- Windows: Windows 10+ or WSL2
- macOS: macOS 10.15+

**Step 1: Build Backend**:
```bash
cd desktop_alone
source venv/bin/activate
pyinstaller build.spec --clean --noconfirm
# Output: dist/neuroinsight-backend/
```

**Step 2: Build Installer**:
```bash
cd electron-app

# Linux
npm run build:linux
# Output: dist/NeuroInsight-1.0.0.AppImage

# Windows (on Windows or with Wine)
npm run build:win
# Output: dist/NeuroInsight-Setup-1.0.0.exe

# macOS (on macOS only)
npm run build:mac
# Output: dist/NeuroInsight-1.0.0.dmg
```

**Step 3: Verify Build**:
```bash
# Check file size
ls -lh dist/*.AppImage  # Should be ~3.9 GB

# Verify frontend bundled
cd dist/linux-unpacked/resources
npx asar list app.asar | grep "frontend/index.html"
# Should output: /frontend/index.html
```

### Cross-Platform Build (GitHub Actions)

See [CI/CD Pipeline](#cicd-pipeline) section.

---

## CI/CD Pipeline

### GitHub Actions Workflow

**File**: `.github/workflows/desktop-build-v15.yml`

### Workflow Structure

```yaml
name: Desktop Build v15 - Fixed (Frontend Bundled)

on:
  push:
    tags:
      - 'desktop-v*'
  workflow_dispatch:

jobs:
  build-linux:      # Builds on ubuntu-latest
  build-windows:    # Builds on windows-latest
  build-macos:      # Builds on macos-latest
  create-release:   # Creates GitHub Release
```

### Build Process

**Each platform job does**:
1. Checkout code
2. Setup Node.js 18 + Python 3.10
3. Install dependencies
4. Build backend with PyInstaller
5. Build Electron installer
6. Generate SHA256 checksums
7. Upload artifacts (30-day retention)

**Final job**:
- Downloads all artifacts
- Creates GitHub Release (checksums only)
- Provides download instructions

### Triggering a Build

**Method 1: Tag Push (Automatic)**
```bash
git tag desktop-v1.1.3 -m "Release v1.1.3"
git push origin desktop-v1.1.3
```

**Method 2: Manual Trigger**
1. Go to https://github.com/phindagijimana/neuroinsight/actions
2. Click "Desktop Build v15"
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

### Monitoring Builds

**Actions Page**:
```
https://github.com/phindagijimana/neuroinsight/actions
```

**Expected Build Time**:
- Linux: ~20 minutes
- Windows: ~30 minutes
- macOS: ~30 minutes
- **Total**: ~30-60 minutes (parallel)

### Downloading Build Artifacts

1. Go to Actions → Click on workflow run
2. Scroll to "Artifacts" section
3. Download:
   - `neuroinsight-linux.zip` (2.8 GB)
   - `neuroinsight-windows.zip` (~2.5 GB)
   - `neuroinsight-mac.zip` (460 MB)

**Note**: Artifacts expire after 30 days. Re-run workflow to regenerate.

---

## Configuration Files

### Backend Configuration

**File**: `desktop_alone/backend/core/config_desktop.py`

**Key Settings**:
```python
class DesktopSettings(BaseSettings):
    desktop_mode: bool = True
    
    # Database
    @property
    def database_url(self) -> str:
        return f"sqlite:///{user_data_dir}/neuroinsight.db"
    
    # Storage
    @property
    def upload_dir(self) -> Path:
        return Path(user_documents_dir) / "NeuroInsight" / "uploads"
    
    # Server
    host: str = "127.0.0.1"  # Localhost only
    port: int = 8000
    
    # Processing
    use_celery: bool = False
    task_mode: str = "threading"
    max_concurrent_jobs: int = 1  # One job at a time
```

**User Data Locations**:
- **Linux**: `~/.local/share/NeuroInsight/`
- **Windows**: `C:\Users\<user>\AppData\Roaming\NeuroInsight\`
- **macOS**: `~/Library/Application Support/NeuroInsight/`

**User Documents**:
- **Linux**: `~/Documents/NeuroInsight/`
- **Windows**: `C:\Users\<user>\Documents\NeuroInsight\`
- **macOS**: `~/Documents/NeuroInsight/`

### Electron Configuration

**File**: `desktop_alone/electron-app/src/main.js`

**Key Settings**:
```javascript
// Backend startup
const env = {
  DESKTOP_MODE: 'true',
  PORT: String(BACKEND_PORT),  // 0 = OS assigns port
  HOST: '127.0.0.1',
};

// Window configuration
mainWindow = new BrowserWindow({
  width: 1400,
  height: 900,
  minWidth: 1000,
  minHeight: 700,
  webPreferences: {
    nodeIntegration: false,
    contextIsolation: true,
    sandbox: true,
  },
  show: false,
  backgroundColor: '#1a1a1a',
  title: 'NeuroInsight',
});

// Frontend loading
const frontendPath = path.join(__dirname, 'frontend', 'index.html');
mainWindow.loadFile(frontendPath);
```

### PyInstaller Configuration

**File**: `desktop_alone/build.spec`

**Key Settings**:
```python
a = Analysis(
    ['backend/main.py'],
    binaries=[],
    datas=[
        ('backend/alembic', 'alembic'),
        ('models', 'models'),
        ('pipeline', 'pipeline'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.lifespan',
        # ... more
    ],
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='neuroinsight-backend',
    console=True,  # Shows console for debugging
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='neuroinsight-backend',
)
```

### electron-builder Configuration

**File**: `desktop_alone/electron-app/package.json`

**Critical Section** (Frontend Bundling):
```json
{
  "build": {
    "appId": "com.neuroinsight.desktop",
    "productName": "NeuroInsight",
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
    ],
    "extraResources": [
      {
        "from": "../dist/neuroinsight-backend",
        "to": "backend",
        "filter": ["**/*"]
      }
    ],
    "linux": {
      "target": ["AppImage"],
      "category": "Science;MedicalSoftware;Education"
    },
    "win": {
      "target": "nsis"
    },
    "mac": {
      "target": ["dmg"],
      "category": "public.app-category.healthcare-fitness"
    }
  }
}
```

---

## Key Components

### 1. Electron Main Process

**File**: `desktop_alone/electron-app/src/main.js`

**Responsibilities**:
- Application lifecycle management
- Backend process spawning
- Window creation
- IPC communication
- Logging

**Key Functions**:
```javascript
// Start backend
function startBackend() {
  const backendPath = getBackendPath();
  backendProcess = spawn(backendPath, [], { env, stdio });
  // Capture port from stdout
}

// Create window
async function createWindow() {
  // Wait for backend ready
  await waitOn({
    resources: [`http://127.0.0.1:${BACKEND_PORT}/health`],
    timeout: 30000,
  });
  
  // Load frontend
  mainWindow.loadFile(frontendPath);
}
```

### 2. Frontend React App

**File**: `desktop_alone/frontend/index.html`

**Structure**:
- Single HTML file (~2000 lines)
- Inline React components
- Inline CSS (Tailwind)
- No build step required

**Key Components**:
```javascript
// Main App
function App() {
  const [page, setPage] = useState('home');
  // ... state management
}

// Job Upload
function UploadPage() {
  // File upload UI
}

// Job List
function JobsPage() {
  // Display processing jobs
}

// Results Viewer
function ViewerPage() {
  // 3D brain visualization
}
```

**API Communication**:
```javascript
// Backend URL set by Electron
const API_BASE = window.BACKEND_URL || 'http://localhost:8000';

// API calls
async function uploadScan(file) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    body: formData,
  });
  return response.json();
}
```

### 3. Backend API Server

**File**: `desktop_alone/backend/main.py`

**Main Entry Point**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config_desktop import get_desktop_settings
from backend.api import jobs, upload, metrics, visualizations

app = FastAPI(title="NeuroInsight Desktop API")

# CORS for Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(visualizations.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    settings = get_desktop_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)
```

**Key Endpoints**:
```python
# Upload scan
POST /api/upload

# List jobs
GET /api/jobs

# Get job details
GET /api/jobs/{job_id}

# Get metrics
GET /api/metrics/{job_id}

# Get visualizations
GET /api/visualizations/{job_id}/{filename}
```

### 4. Processing Pipeline

**File**: `desktop_alone/pipeline/processors/mri_processor.py`

**Processing Steps**:
1. **File validation**: Check format, size
2. **FastSurfer segmentation**: Run brain segmentation
3. **Volume extraction**: Calculate hippocampal volumes
4. **Asymmetry calculation**: Compute asymmetry index
5. **Visualization generation**: Create brain images
6. **Result storage**: Save to database

**Key Function**:
```python
async def process_mri_scan(job_id: str, file_path: Path):
    # 1. Validate input
    validate_nifti_file(file_path)
    
    # 2. Run FastSurfer
    segmentation = await run_fastsurfer(file_path)
    
    # 3. Extract volumes
    volumes = extract_hippocampal_volumes(segmentation)
    
    # 4. Calculate asymmetry
    asymmetry = calculate_asymmetry_index(volumes)
    
    # 5. Generate visualizations
    create_brain_visualizations(segmentation, output_dir)
    
    # 6. Save results
    save_metrics_to_db(job_id, volumes, asymmetry)
```

### 5. Logging System

**File**: `desktop_alone/electron-app/src/utils/logger.js`

**Log Locations**:
- **Linux**: `~/.config/NeuroInsight/logs/`
- **Windows**: `C:\Users\<user>\AppData\Roaming\NeuroInsight\logs\`
- **macOS**: `~/Library/Logs/NeuroInsight/`

**Log Files**:
- `main.log`: All application events
- `errors.log`: Errors only
- `crashes.log`: Critical failures

**Usage**:
```javascript
// In Electron
log.info('Application started');
log.error('Backend failed to start', error);
logger.crash('Renderer process crashed', error, details);
```

---

## Common Issues & Solutions

### Issue 1: Dark Window on Launch

**Symptom**: App opens but shows blank/dark window

**Cause**: Frontend not bundled in installer

**Solution**: Verify frontend is bundled:
```bash
cd dist/linux-unpacked/resources
npx asar list app.asar | grep "frontend/index.html"
```

**If missing**, check `package.json`:
```json
{
  "files": [
    {
      "from": "../frontend",
      "to": "frontend",
      "filter": ["**/*"]
    }
  ]
}
```

**Reference**: `COMPLETE_BUNDLING_FIX_REFERENCE.md`

---

### Issue 2: Backend Won't Start

**Symptom**: Electron opens but backend doesn't respond

**Check logs**:
```bash
tail -f ~/.config/NeuroInsight/logs/main.log
```

**Common causes**:
1. **Port already in use**: Another process using port 8000
2. **Missing dependencies**: PyTorch not bundled correctly
3. **Permission denied**: Backend executable not marked executable

**Solutions**:
```bash
# 1. Check port
lsof -i :8000

# 2. Check backend exists
ls -lh resources/backend/neuroinsight-backend

# 3. Make executable
chmod +x resources/backend/neuroinsight-backend
```

---

### Issue 3: Build Fails (PyInstaller)

**Symptom**: PyInstaller build fails with import errors

**Common errors**:
```
ModuleNotFoundError: No module named 'torch'
ModuleNotFoundError: No module named 'uvicorn.logging'
```

**Solution**: Add to `hiddenimports` in `build.spec`:
```python
hiddenimports=[
    'torch',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.lifespan',
    # ... add missing modules
]
```

---

### Issue 4: electron-builder Fails

**Symptom**: electron-builder fails during packaging

**Common error**:
```
Cannot find module '../dist/neuroinsight-backend'
```

**Solution**: Build backend first:
```bash
cd desktop_alone
pyinstaller build.spec
# Then build Electron
cd electron-app
npm run build:linux
```

---

### Issue 5: AppImage > 2GB Release Failure

**Symptom**: GitHub Release creation fails

**Error**:
```
Error: File size (2944582663) is greater than 2 GiB
```

**Solution**: Download from Actions Artifacts instead of Releases

**Reference**: `LARGE_FILE_WORKAROUND.md`

---

### Issue 6: X11 Display Error (HPC)

**Symptom**: `Missing X server or $DISPLAY`

**Cause**: Running on headless server without display

**Solutions**:
1. **X11 forwarding**: `ssh -X user@server`
2. **Open OnDemand**: Use interactive desktop
3. **Test on local machine**: Download to laptop/desktop

---

## Deployment

### Distribution Methods

#### Method 1: GitHub Actions Artifacts (Current)

**Best for**: Small-scale, testing, internal use

**Process**:
1. Push tag: `git tag desktop-v1.x.x && git push origin desktop-v1.x.x`
2. Wait for build: ~30-60 minutes
3. Download from Actions artifacts
4. Share with users

**Retention**: 30 days (renewable by re-running workflow)

**Pros**: Free, automatic  
**Cons**: Requires GitHub account, temporary

---

#### Method 2: External Hosting (Future)

**Best for**: Production, public distribution

**Options**:
- AWS S3 + CloudFront (~$50-100/month)
- DigitalOcean Spaces (~$5/month)
- Institutional storage (free if available)

**Reference**: `LARGE_FILE_WORKAROUND.md`

---

### User Installation

**Linux**:
```bash
chmod +x NeuroInsight-1.0.0.AppImage
./NeuroInsight-1.0.0.AppImage
```

**Windows**:
- Run `NeuroInsight-Setup-1.0.0.exe`
- Follow installer prompts
- Launch from Start Menu

**macOS**:
- Open `.dmg` file
- Drag to Applications folder
- Right-click → Open (first time only, bypasses Gatekeeper)

**Reference**: `INSTALLATION.md`

---

## Testing

### Pre-Release Testing Checklist

**Build Verification**:
- [ ] Backend builds without errors
- [ ] Frontend bundled in app.asar
- [ ] AppImage/EXE/DMG created successfully
- [ ] File sizes reasonable (~3-4 GB)
- [ ] Checksums generated

**Functional Testing**:
- [ ] App launches without errors
- [ ] No dark/blank window
- [ ] Backend starts and responds
- [ ] Can upload MRI scan
- [ ] Processing starts
- [ ] Progress tracking works
- [ ] Results display correctly
- [ ] Can download results
- [ ] Logs are generated

**Platform Testing**:
- [ ] Tested on Linux
- [ ] Tested on Windows
- [ ] Tested on macOS (x64 and arm64 if possible)

**Performance**:
- [ ] Startup time < 10 seconds
- [ ] Processing completes successfully
- [ ] Memory usage reasonable
- [ ] No memory leaks after multiple jobs

**Error Handling**:
- [ ] Invalid file upload rejected
- [ ] Errors logged properly
- [ ] Crash recovery works
- [ ] User-friendly error messages

---

## Maintenance

### Regular Tasks

**Monthly**:
- [ ] Check for dependency updates
- [ ] Review and address GitHub Issues
- [ ] Update documentation if needed
- [ ] Test on latest OS versions

**As Needed**:
- [ ] Re-run workflows if artifacts expire (30 days)
- [ ] Create new release tags for updates
- [ ] Respond to user bug reports

### Updating Dependencies

**Backend**:
```bash
cd desktop_alone
pip install --upgrade -r requirements.txt
# Test thoroughly before committing
```

**Frontend**:
```bash
cd desktop_alone/frontend
npm update
# Check for breaking changes
```

**Electron**:
```bash
cd desktop_alone/electron-app
npm update
# Test app launches correctly
```

### Version Numbering

Follow semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes

**Current**: v1.1.3

---

## Troubleshooting

### Debug Mode

**Enable verbose logging**:
```bash
# Backend
export LOG_LEVEL=DEBUG
python backend/main.py

# Electron (in package.json)
"start": "electron . --dev --verbose"
```

### Common Commands

**Check if app is running**:
```bash
ps aux | grep neuroinsight
```

**Check logs**:
```bash
# Linux
tail -f ~/.config/NeuroInsight/logs/main.log

# Check all logs
ls -lh ~/.config/NeuroInsight/logs/
```

**Clear app data**:
```bash
# Linux
rm -rf ~/.config/NeuroInsight/
rm -rf ~/.local/share/NeuroInsight/
rm -rf ~/Documents/NeuroInsight/
```

**Rebuild from scratch**:
```bash
cd desktop_alone

# Clean old builds
rm -rf dist/ build/ electron-app/dist/

# Rebuild backend
pyinstaller build.spec --clean --noconfirm

# Rebuild Electron
cd electron-app
npm run build:linux
```

---

## Related Documentation

### Core Documentation

1. **COMPLETE_BUNDLING_FIX_REFERENCE.md** (824 lines)
   - Complete fix history for dark window issue
   - Diagnosis, solution, verification
   - Lessons learned

2. **DARK_WINDOW_FIX.md**
   - Quick technical summary of the fix
   - Before/after comparison

3. **LARGE_FILE_WORKAROUND.md**
   - GitHub's 2GB limit explanation
   - Current workaround (Artifacts)
   - Future hosting solutions

4. **INSTALLATION.md**
   - User installation instructions
   - Per-platform steps
   - Gatekeeper/SmartScreen bypass

5. **USER_MANUAL.md**
   - End-user guide
   - How to use the application
   - Feature walkthrough

6. **LOGS_AND_TROUBLESHOOTING.md**
   - Log locations
   - How to read logs
   - Common issues

7. **.github/workflows/README.md**
   - CI/CD workflow documentation
   - How to trigger builds
   - Troubleshooting builds

---

## Quick Command Reference

```bash
# ============================================
# Development
# ============================================

# Start backend (dev)
cd desktop_alone && python backend/main.py

# Start frontend (dev)
cd desktop_alone/frontend && npm run dev

# Start Electron (dev)
cd desktop_alone/electron-app && npm start


# ============================================
# Building
# ============================================

# Build backend
cd desktop_alone && pyinstaller build.spec --clean

# Build Linux AppImage
cd desktop_alone/electron-app && npm run build:linux

# Build Windows installer (on Windows)
cd desktop_alone/electron-app && npm run build:win

# Build macOS DMG (on macOS)
cd desktop_alone/electron-app && npm run build:mac


# ============================================
# Verification
# ============================================

# Check frontend bundled
cd dist/linux-unpacked/resources
npx asar list app.asar | grep frontend

# Check file size
ls -lh dist/*.AppImage

# Test locally
./dist/NeuroInsight-1.0.0.AppImage


# ============================================
# Deployment
# ============================================

# Create release tag
git tag desktop-v1.x.x -m "Release vX.X.X"
git push origin desktop-v1.x.x

# Monitor build
open https://github.com/phindagijimana/neuroinsight/actions


# ============================================
# Troubleshooting
# ============================================

# Check logs
tail -f ~/.config/NeuroInsight/logs/main.log

# Check if running
ps aux | grep neuroinsight

# Clean everything
rm -rf dist/ build/ electron-app/dist/
```

---

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                     User's Computer                         │
│                                                             │
│  ┌───────────────────────────────────────────────────┐    │
│  │              NeuroInsight.AppImage                 │    │
│  │                                                     │    │
│  │  ┌──────────────────────────────────────────┐    │    │
│  │  │         Electron Main Process            │    │    │
│  │  │  - Spawns backend subprocess             │    │    │
│  │  │  - Creates BrowserWindow                 │    │    │
│  │  │  - Manages lifecycle                     │    │    │
│  │  └────────┬─────────────────────────────────┘    │    │
│  │           │                                       │    │
│  │           │ spawns                               │    │
│  │           ▼                                       │    │
│  │  ┌──────────────────────────────────────────┐    │    │
│  │  │    Backend (neuroinsight-backend)        │    │    │
│  │  │    - FastAPI server                      │    │    │
│  │  │    - Listens on 127.0.0.1:8000          │    │    │
│  │  │    - SQLite database                     │    │    │
│  │  │    - FastSurfer processing               │    │    │
│  │  └────────▲─────────────────────────────────┘    │    │
│  │           │ HTTP                                  │    │
│  │           │                                       │    │
│  │  ┌────────┴─────────────────────────────────┐    │    │
│  │  │         Frontend (React SPA)             │    │    │
│  │  │    - Loaded in BrowserWindow             │    │    │
│  │  │    - Single HTML file                    │    │    │
│  │  │    - Communicates via fetch()            │    │    │
│  │  └──────────────────────────────────────────┘    │    │
│  │                                                     │    │
│  └───────────────────────────────────────────────────┘    │
│                                                             │
│  User Data:                                                │
│  ~/.local/share/NeuroInsight/     (database)              │
│  ~/Documents/NeuroInsight/         (uploads, outputs)      │
│  ~/.config/NeuroInsight/logs/      (logs)                 │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## Summary

This desktop application is a **standalone, self-contained Electron app** that:

1. **Bundles everything**: Python backend + React frontend + ML models
2. **Runs offline**: No internet or Docker required
3. **Cross-platform**: Linux, Windows, macOS
4. **Easy to distribute**: Single installer file per platform
5. **User-friendly**: Double-click to launch

**Key Technologies**:
- Electron (desktop wrapper)
- Python + FastAPI (backend)
- React (frontend)
- PyInstaller (backend bundling)
- electron-builder (app packaging)
- FastSurfer (brain segmentation)

**Build Process**:
1. PyInstaller → Python executable
2. electron-builder → Platform installer

**Distribution**:
- GitHub Actions builds for all platforms
- Download from Actions artifacts
- 30-day retention, renewable

**Current Status**: ✅ Production Ready (v1.1.3+)

---

**Last Updated**: November 9, 2025  
**Current Version**: v1.1.3  
**Status**: Complete and Fully Documented  
**Maintainer**: Development Team

---

## Need Help?

1. **Check this document first** - Most answers are here
2. **Review related documentation** - See [Related Documentation](#related-documentation)
3. **Check logs** - `~/.config/NeuroInsight/logs/`
4. **GitHub Issues** - https://github.com/phindagijimana/neuroinsight/issues
5. **Contact**: neuroinsight@example.com

**This document is your complete reference.** Bookmark it! 📚



