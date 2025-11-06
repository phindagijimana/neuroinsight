# Desktop App Without Docker Desktop Requirement

## The Challenge

Current desktop app requires users to:
1. Install Docker Desktop separately
2. Configure Docker settings
3. Manage Docker service

**Goal:** Create a true standalone installer where users just download and run.

---

## Solutions

### Option 1: Embedded Container Runtime (Complex)

Bundle a container runtime with the application.

#### Approach A: Embedded Docker Engine

**Concept:**
```
NeuroInsight.exe/app
├── Electron UI
├── Embedded Docker Engine
└── Container images (bundled)
```

**Challenges:**
- Docker Engine licensing (Docker Desktop is not free for commercial use)
- Large file size (Docker Engine ~500MB)
- Platform-specific packaging
- Requires elevated permissions
- Complex installation/uninstallation

**Status:** Not recommended due to licensing and complexity

---

#### Approach B: Podman (Daemonless Container Runtime)

**Concept:**
```
NeuroInsight.exe/app
├── Electron UI
├── Embedded Podman runtime
└── Container images
```

**Advantages:**
- Open source (Apache 2.0)
- Daemonless (no background service)
- Docker-compatible
- More embeddable than Docker

**Challenges:**
- Still large (~300-400MB)
- Platform-specific builds
- Windows support limited
- Requires elevated permissions for setup

**Status:** Possible but complex

---

### Option 2: Native Execution (Recommended)

Bundle Python runtime and all dependencies - no containers at all.

#### Architecture

```
NeuroInsight.exe (Windows) / NeuroInsight.app (macOS)
├── Electron UI Shell
├── Embedded Python 3.10
│   ├── FastAPI backend
│   ├── Celery worker
│   ├── PyTorch + FastSurfer
│   └── All dependencies
├── Embedded SQLite database
├── Embedded Redis (or in-memory alternative)
└── FastSurfer model files
```

#### Advantages

**User Experience:**
- Single installer download
- One-click installation
- No prerequisites
- No Docker configuration
- Works immediately after install

**Technical:**
- No container overhead
- Faster startup
- Smaller memory footprint
- Direct system access
- No networking complexity

**Distribution:**
- Simpler licensing
- Smaller download size (1.5-2GB vs 3-4GB with Docker)
- Code signing easier
- App store distribution possible

#### Implementation Path

**1. Bundle Python Backend (PyInstaller/Nuitka)**

```python
# Build script
pyinstaller backend.spec

# Output: backend.exe (Windows) or backend (macOS/Linux)
# Size: ~500MB including PyTorch
```

**2. Bundle FastSurfer Models**

```
models/
├── aparc_vinn_axial_v2.0.0.pkl
├── aparc_vinn_coronal_v2.0.0.pkl
└── aparc_vinn_sagittal_v2.0.0.pkl
# Size: ~400MB
```

**3. Electron Wrapper**

```javascript
// src/main.js
const backendProcess = spawn(backendExecutable, {
  env: {
    DESKTOP_MODE: 'true',
    DATABASE_URL: 'sqlite:///data.db'
  }
});
```

**4. Single Installer**

- **Windows:** NSIS installer (~1.5GB)
- **macOS:** DMG package (~1.5GB)
- **Linux:** AppImage (~1.5GB)

---

### Option 3: Hybrid Approach

Use containers internally but bundle the runtime.

#### Using Embedded Singularity/Apptainer

**Concept:**
```
NeuroInsight.exe
├── Electron UI
├── Singularity runtime (embedded)
└── FastSurfer SIF file (bundled)
```

**Advantages:**
- Container isolation
- Smaller than Docker
- Open source
- No daemon required

**Challenges:**
- Linux-only (limited Windows/macOS support)
- Still requires elevated permissions
- Complex packaging

**Status:** Only viable for Linux distribution

---

## Recommended Approach for NeuroInsight

### Best Solution: Native Python Execution (Option 2)

**Why:**

1. **No External Dependencies**
   - User installs one app, that's it
   - No "Install Docker first" barrier
   - Works immediately

2. **Better User Experience**
   - Faster startup (no container initialization)
   - More responsive
   - Standard desktop app behavior

3. **Simpler Distribution**
   - Standard installers (NSIS, DMG, AppImage)
   - App store compatible
   - Code signing straightforward

4. **Smaller Download**
   - ~1.5-2GB total (vs 3-4GB with Docker)
   - One download, not two (app + Docker Desktop)

5. **Better Performance**
   - No container overhead
   - Direct hardware access
   - Native GPU access easier

---

## Implementation Plan

### Phase 1: Replace PostgreSQL with SQLite

```python
# backend/core/config.py
class DesktopSettings(BaseSettings):
    database_url: str = "sqlite:///neuroinsight.db"
```

**Benefits:**
- No database server needed
- Embedded in application
- Zero configuration

---

### Phase 2: Replace Redis/Celery with In-Process Queue

```python
# For desktop mode
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

def process_job(job_id):
    # Direct execution, no Celery
    result = run_fastsurfer(job_id)
    return result

# Submit job
future = executor.submit(process_job, job_id)
```

**Benefits:**
- No Redis server needed
- Simpler architecture
- Fewer moving parts

---

### Phase 3: Native FastSurfer Execution

```python
# No Docker, direct Python execution
import torch
from FastSurferCNN import run_prediction

def process_mri(input_path, output_path):
    # Direct PyTorch execution
    model = load_fastsurfer_model()
    result = model.predict(input_path)
    save_results(result, output_path)
```

**Benefits:**
- No container runtime needed
- Direct GPU access
- Faster execution

---

### Phase 4: Bundle Everything with PyInstaller

```python
# build.spec
a = Analysis(
    ['backend/main.py'],
    datas=[
        ('models/', 'models/'),  # FastSurfer models
        ('frontend/', 'frontend/'),  # Web UI
    ],
    hiddenimports=[
        'torch', 'FastSurferCNN', 'nibabel', 
        'uvicorn', 'fastapi', 'sqlalchemy'
    ]
)

exe = EXE(
    pyz, a.scripts,
    exclude_binaries=True,
    name='neuroinsight-backend'
)
```

**Output:** Single executable with all dependencies

---

### Phase 5: Electron Wrapper

```javascript
// Electron manages Python backend
function startBackend() {
  const backend = spawn('./backend/neuroinsight-backend');
  
  backend.on('ready', () => {
    // Open UI when backend ready
    mainWindow.loadURL('http://localhost:8000');
  });
}
```

---

### Phase 6: Create Installers

**Windows:**
```bash
electron-builder --win
# Output: NeuroInsight-Setup-1.0.0.exe
```

**macOS:**
```bash
electron-builder --mac
# Output: NeuroInsight-1.0.0.dmg
```

**Linux:**
```bash
electron-builder --linux
# Output: NeuroInsight-1.0.0.AppImage
```

---

## Comparison Matrix

| Aspect | Docker Desktop | Embedded Container | Native Python |
|--------|---------------|-------------------|---------------|
| **User Installation** | 2 steps | 1 step | 1 step |
| **Download Size** | 500MB + 2GB | ~2.5GB | ~1.5GB |
| **Prerequisites** | Docker Desktop | None | None |
| **Startup Time** | 30-60s | 20-30s | 5-10s |
| **Memory Usage** | 4-8GB | 3-5GB | 2-4GB |
| **GPU Access** | Complex | Complex | Direct |
| **Development Complexity** | Low | High | Medium |
| **Platform Support** | Good | Limited | Excellent |
| **App Store Compatible** | No | No | Yes |
| **Code Signing** | N/A | Complex | Standard |

---

## Timeline Estimate

### Native Python Approach

**Phase 1-3:** Backend simplification (2-3 weeks)
- Replace PostgreSQL with SQLite
- Replace Celery with ThreadPoolExecutor
- Remove Docker dependencies

**Phase 4:** Python bundling (1 week)
- Configure PyInstaller
- Test bundled backend
- Optimize size

**Phase 5:** Electron integration (1 week)
- Backend process management
- IPC communication
- Error handling

**Phase 6:** Installer creation (1 week)
- Platform-specific builds
- Code signing
- Testing on clean systems

**Total:** 5-6 weeks for complete standalone app

---

## User Experience Comparison

### Current (Docker Desktop Required)

```
User Journey:
1. Install Docker Desktop (15 min)
2. Configure Docker memory (5 min)
3. Download NeuroInsight app (5 min)
4. Install NeuroInsight (2 min)
5. Start Docker Desktop
6. Launch NeuroInsight
7. Wait for services (30-60s)
8. Use application

Total setup: 30+ minutes
Prerequisites: Technical knowledge
```

### Proposed (Native Standalone)

```
User Journey:
1. Download NeuroInsight (5 min)
2. Install NeuroInsight (2 min)
3. Launch NeuroInsight
4. Use application

Total setup: 7 minutes
Prerequisites: None
```

---

## Recommendation

**For NeuroInsight, implement Native Python Execution (Option 2):**

**Reasons:**

1. **Clinical/Research Software Expectations**
   - Medical software should "just work"
   - Minimal technical barriers
   - Professional appearance

2. **User Base**
   - Non-technical users (clinicians, researchers)
   - One-click installation expected
   - No IT support for Docker troubleshooting

3. **Distribution**
   - Can distribute via institutional channels
   - App store distribution possible
   - Standard installation process

4. **Maintenance**
   - Users don't need to update Docker
   - Simpler support
   - Fewer failure points

5. **Performance**
   - Faster startup
   - Lower memory usage
   - Better for laptop use

---

## Next Steps

See [docs/STANDALONE_DESKTOP_APP.md](STANDALONE_DESKTOP_APP.md) for detailed implementation guide.

**Quick start:**

```bash
# Prepare for standalone build
bash scripts/prepare-desktop-build.sh

# This creates:
# - Desktop-specific configuration
# - PyInstaller spec files
# - Build scripts
```

---

## Questions?

**Can it really work without containers?**

Yes. Containers are convenient for development and deployment, but not required. Python can run natively with all dependencies bundled.

**What about FastSurfer's Docker image?**

FastSurfer is Python code. We extract it and bundle with our app. No container needed.

**Will it be as reliable?**

More reliable - fewer components to fail, simpler architecture.

**Can we still use Docker for development?**

Yes. Development uses Docker Compose. Production desktop app uses native execution. Best of both worlds.

---

**Bottom Line:** Native Python execution is the best path for a true standalone desktop application that users can download and run without installing Docker Desktop.

