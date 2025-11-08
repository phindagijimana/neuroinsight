# NeuroInsight Standalone Desktop App - Migration Plan

**Goal**: Convert from Docker-based hybrid app to true standalone desktop application (like 3D Slicer)

**Timeline**: 3-4 weeks full-time development

**Result**: Single downloadable app, no Docker required, just install and run

---

## Current vs. Target Architecture

### Current (Docker-based)
```
Electron App
  ↓
Docker Desktop
  ↓
Containers:
  - PostgreSQL (database)
  - Redis (queue)
  - MinIO (storage)
  - Celery (workers)
  - FastSurfer (processing)
```

### Target (Standalone)
```
Electron App
  ├── Embedded SQLite (database)
  ├── Local File System (storage)
  ├── Worker Threads (processing)
  └── Bundled FastSurfer (Python subprocess)
```

---

## Phase 1: Backend Simplification (Week 1)

### 1.1 Replace PostgreSQL with SQLite

**Current**: External PostgreSQL in Docker
**Target**: Embedded SQLite database

**Tasks**:
- [ ] Install `better-sqlite3` npm package
- [ ] Create SQLAlchemy → SQLite migration scripts
- [ ] Update all database queries for SQLite compatibility
- [ ] Migrate schema (remove PostgreSQL-specific features)
- [ ] Test all CRUD operations

**Files to modify**:
- `backend/db.py` - Database connection
- `backend/models/*.py` - Model definitions
- All files using `asyncpg` → use `sqlite3`

**Code changes**:
```python
# Before (PostgreSQL)
DATABASE_URL = "postgresql://user:pass@localhost/neuroinsight"

# After (SQLite)
import sqlite3
DATABASE_PATH = app.getPath('userData') + '/neuroinsight.db'
```

**Estimated time**: 2-3 days

---

### 1.2 Replace MinIO with Local File System

**Current**: S3-compatible object storage in Docker
**Target**: Direct file system with organized folders

**Tasks**:
- [ ] Create data directory structure
- [ ] Update file upload/download logic
- [ ] Replace S3 SDK calls with `fs` operations
- [ ] Implement file cleanup/retention
- [ ] Add file compression (optional)

**Directory structure**:
```
~/NeuroInsight/
  ├── data/
  │   ├── uploads/          # Original MRI files
  │   ├── processed/        # FastSurfer outputs
  │   ├── exports/          # User downloads
  │   └── temp/             # Temporary files
  ├── database/
  │   └── neuroinsight.db
  └── logs/
```

**Code changes**:
```javascript
// Before (MinIO)
await minioClient.putObject('bucket', 'file.nii', stream);

// After (File System)
const filePath = path.join(dataDir, 'uploads', 'file.nii');
await fs.promises.writeFile(filePath, buffer);
```

**Estimated time**: 1-2 days

---

### 1.3 Replace Redis + Celery with Worker Threads

**Current**: Redis queue + Celery workers in Docker
**Target**: Node.js worker threads or child processes

**Tasks**:
- [ ] Install `worker_threads` (built-in Node.js)
- [ ] Create job queue system (in-memory or SQLite-backed)
- [ ] Convert Celery tasks to Node.js workers
- [ ] Implement job status tracking
- [ ] Add retry logic and error handling

**Implementation options**:

**Option A: Node.js Worker Threads**
```javascript
const { Worker } = require('worker_threads');

function processJob(jobId, filePath) {
  return new Promise((resolve, reject) => {
    const worker = new Worker('./workers/fastsurfer-worker.js', {
      workerData: { jobId, filePath }
    });
    
    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker stopped with exit code ${code}`));
    });
  });
}
```

**Option B: Python Subprocess (simpler for FastSurfer)**
```javascript
const { spawn } = require('child_process');

function runFastSurfer(inputPath, outputPath) {
  return new Promise((resolve, reject) => {
    const python = spawn('python', [
      'bundled-fastsurfer/run_fastsurfer.py',
      '--input', inputPath,
      '--output', outputPath
    ]);
    
    python.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`FastSurfer failed with code ${code}`));
    });
  });
}
```

**Estimated time**: 3-4 days

---

## Phase 2: Bundle Python + FastSurfer (Week 2)

### 2.1 Embed Python Runtime

**Goal**: Include Python interpreter in the app bundle

**Options**:

**Option A: Python Embedded Distribution (Windows)**
```
Download python-3.11.x-embed-amd64.zip
Extract to: app/resources/python/
```

**Option B: Portable Python (macOS/Linux)**
```bash
# Use pyenv or build Python from source
# Install to app bundle Resources folder
```

**Tasks**:
- [ ] Download/build portable Python for each platform
- [ ] Include in electron-builder `extraResources`
- [ ] Set up PATH to use bundled Python
- [ ] Test Python can find bundled packages

**electron-builder config**:
```json
{
  "extraResources": [
    {
      "from": "python-runtime/",
      "to": "python",
      "filter": ["**/*"]
    }
  ]
}
```

**Estimated time**: 2-3 days

---

### 2.2 Bundle FastSurfer Dependencies

**Goal**: Include all Python packages needed for FastSurfer

**Tasks**:
- [ ] Create requirements.txt for FastSurfer
- [ ] Install packages to bundled Python
- [ ] Bundle PyTorch (CPU or GPU versions)
- [ ] Include FastSurfer model weights
- [ ] Test offline execution

**Approach**:
```bash
# Create virtual environment in bundle
cd app/resources/python
./python -m venv fastsurfer-env

# Install packages
./fastsurfer-env/bin/pip install -r requirements.txt

# Include in app bundle
```

**Bundle size impact**: ~3-5GB (PyTorch + models)

**Estimated time**: 2-3 days

---

### 2.3 Integrate Singularity/Apptainer Alternative

**Challenge**: Singularity doesn't work without Docker

**Solutions**:

**Option A: Pure Python FastSurfer**
- Run FastSurfer directly with bundled Python
- No container needed
- Simpler but requires all dependencies

**Option B: Freeze FastSurfer with PyInstaller**
```bash
pyinstaller --onefile \
  --add-data "models:models" \
  --hidden-import torch \
  run_fastsurfer.py
```

**Recommended**: Option A (pure Python)

**Estimated time**: 2-3 days

---

## Phase 3: Electron App Integration (Week 3)

### 3.1 Update Service Manager

**Current**: Manages Docker containers
**Target**: Manages local processes

**Tasks**:
- [ ] Remove DockerManager.js
- [ ] Create ProcessManager.js
- [ ] Start/stop Python backend as subprocess
- [ ] Monitor process health
- [ ] Handle graceful shutdown

**New ProcessManager**:
```javascript
class ProcessManager {
  constructor() {
    this.processes = {
      backend: null,
      worker: null
    };
  }

  async startBackend() {
    const pythonPath = this.getBundledPython();
    const backendScript = path.join(resourcesPath, 'backend/main.py');
    
    this.processes.backend = spawn(pythonPath, [backendScript], {
      env: {
        ...process.env,
        DATABASE_PATH: this.getDatabasePath(),
        DATA_DIR: this.getDataDir()
      }
    });
    
    this.processes.backend.on('error', (err) => {
      logger.error('Backend process error:', err);
    });
  }

  async startWorker() {
    // Start processing worker
  }

  stopAll() {
    Object.values(this.processes).forEach(proc => {
      if (proc) proc.kill();
    });
  }
}
```

**Estimated time**: 2-3 days

---

### 3.2 Update Backend Server

**Current**: FastAPI expects PostgreSQL, Redis, MinIO
**Target**: FastAPI with SQLite, local files, in-memory queue

**Tasks**:
- [ ] Update FastAPI startup to use SQLite
- [ ] Replace async DB calls with sync (or use aiosqlite)
- [ ] Update file handling endpoints
- [ ] Remove Redis/Celery dependencies
- [ ] Implement simple job queue in memory or SQLite

**Backend changes**:
```python
# main.py
from fastapi import FastAPI
import sqlite3
from pathlib import Path

app = FastAPI()

# Database setup
DB_PATH = os.getenv('DATABASE_PATH', 'neuroinsight.db')
DATA_DIR = os.getenv('DATA_DIR', './data')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Job queue (simple in-memory)
job_queue = []
job_status = {}

@app.post("/upload")
async def upload_scan(file: UploadFile):
    # Save to local file system
    file_path = Path(DATA_DIR) / 'uploads' / file.filename
    with open(file_path, 'wb') as f:
        f.write(await file.read())
    
    # Add to queue
    job_id = str(uuid.uuid4())
    job_queue.append({
        'id': job_id,
        'file_path': str(file_path),
        'status': 'queued'
    })
    
    return {'job_id': job_id}
```

**Estimated time**: 3-4 days

---

### 3.3 Worker Process

**Goal**: Background processing without Celery

**Implementation**:
```python
# worker.py
import sys
import json
from pathlib import Path
from processing.fastsurfer_runner import run_fastsurfer

def process_job(job_data):
    job_id = job_data['id']
    input_path = job_data['file_path']
    output_path = Path(DATA_DIR) / 'processed' / job_id
    
    # Update status
    update_job_status(job_id, 'running')
    
    try:
        # Run FastSurfer
        run_fastsurfer(input_path, output_path)
        
        # Calculate metrics
        metrics = calculate_metrics(output_path)
        
        # Save to database
        save_results(job_id, metrics)
        
        update_job_status(job_id, 'completed')
    except Exception as e:
        update_job_status(job_id, 'failed', str(e))

if __name__ == '__main__':
    # Poll for jobs or listen on IPC
    while True:
        job = get_next_job()
        if job:
            process_job(job)
        time.sleep(5)
```

**Estimated time**: 2-3 days

---

## Phase 4: Build & Package (Week 4)

### 4.1 electron-builder Configuration

**Goal**: Bundle everything into standalone installers

**Updated package.json**:
```json
{
  "build": {
    "extraResources": [
      {
        "from": "bundled-python/",
        "to": "python"
      },
      {
        "from": "backend/",
        "to": "backend"
      },
      {
        "from": "fastsurfer/",
        "to": "fastsurfer"
      }
    ],
    "files": [
      "src/**/*",
      "!**/node_modules/**/*"
    ],
    "mac": {
      "target": ["dmg", "zip"],
      "icon": "build/icon.icns"
    },
    "win": {
      "target": ["nsis", "portable"],
      "icon": "build/icon.ico"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "icon": "build/icons"
    }
  }
}
```

**Estimated time**: 1-2 days

---

### 4.2 Platform-Specific Builds

**macOS**:
```bash
# Bundle Python + FastSurfer
npm run bundle:mac

# Build DMG
npm run dist:mac
```

**Windows**:
```bash
# Include embedded Python
npm run bundle:win

# Build installer
npm run dist:win
```

**Linux**:
```bash
# Use system Python or bundle
npm run bundle:linux

# Build AppImage
npm run dist:linux
```

**Estimated time**: 2-3 days

---

### 4.3 Testing

**Test matrix**:
- [ ] macOS Intel
- [ ] macOS Apple Silicon
- [ ] Windows 10/11
- [ ] Ubuntu 20.04/22.04
- [ ] Fedora

**Test scenarios**:
- [ ] Fresh install (no Docker)
- [ ] Upload and process scan
- [ ] GPU detection (if available)
- [ ] CPU fallback
- [ ] Results visualization
- [ ] Export functionality
- [ ] App restart persistence

**Estimated time**: 2-3 days

---

## Phase 5: Optimization (Optional)

### 5.1 Reduce Bundle Size

**Current estimated size**: ~8-12GB

**Optimizations**:
- [ ] Use Python 3.11+ (smaller runtime)
- [ ] Strip debug symbols from binaries
- [ ] Compress model weights
- [ ] Lazy-load PyTorch (download on demand)
- [ ] Use lighter alternative to PyTorch (TensorFlow Lite?)

**Target size**: ~3-5GB

---

### 5.2 Performance Improvements

- [ ] Preload models on app startup
- [ ] Implement job caching
- [ ] Optimize database queries
- [ ] Add progress streaming
- [ ] Implement partial processing

---

## Summary: Effort Breakdown

### Week 1: Backend Simplification
- SQLite migration: 2-3 days
- Local file system: 1-2 days
- Worker threads: 3-4 days

### Week 2: Python Bundling
- Embed Python runtime: 2-3 days
- Bundle FastSurfer: 2-3 days
- Integration testing: 2-3 days

### Week 3: Electron Integration
- Process manager: 2-3 days
- Backend updates: 3-4 days
- Worker process: 2-3 days

### Week 4: Build & Test
- electron-builder config: 1-2 days
- Platform builds: 2-3 days
- Testing: 2-3 days

**Total**: 20-28 days (3-4 weeks full-time)

---

## Technical Challenges & Solutions

### Challenge 1: FastSurfer GPU Support

**Problem**: FastSurfer expects CUDA/PyTorch with GPU
**Solution**: 
- Bundle both CPU and GPU versions of PyTorch
- Detect GPU at runtime
- Download GPU version on demand if available

### Challenge 2: Large Bundle Size

**Problem**: Python + PyTorch + models = ~8GB
**Solution**:
- Initial download: Small installer (~200MB)
- On first run: Download Python/FastSurfer components
- Similar to 3D Slicer's extension manager

### Challenge 3: Cross-Platform Python

**Problem**: Different Python builds for each OS
**Solution**:
- Use GitHub Actions matrix builds
- Separate builds for macOS (Intel + ARM), Windows, Linux
- Test on all platforms

### Challenge 4: Database Migrations

**Problem**: Users upgrading from Docker version
**Solution**:
- Provide migration tool
- Export from PostgreSQL → Import to SQLite
- Auto-detect old installation

---

## Migration Strategy for Existing Users

### Option A: Clean Install
- Backup data
- Uninstall Docker version
- Install standalone version
- Import data

### Option B: In-App Migration
- Detect Docker version
- Offer to migrate data
- Export from PostgreSQL
- Import to SQLite
- Switch to standalone

---

## File Structure (Standalone)

```
NeuroInsight.app/
├── Contents/
│   ├── MacOS/
│   │   └── NeuroInsight                    # Electron executable
│   ├── Resources/
│   │   ├── app/                            # Electron app code
│   │   │   ├── src/                        # Main/renderer processes
│   │   │   ├── assets/                     # Icons, images
│   │   │   └── frontend/                   # React app (built)
│   │   ├── python/                         # Bundled Python
│   │   │   ├── bin/python3.11
│   │   │   ├── lib/
│   │   │   └── site-packages/
│   │   ├── backend/                        # FastAPI app
│   │   │   ├── main.py
│   │   │   ├── models/
│   │   │   ├── routes/
│   │   │   └── processing/
│   │   └── fastsurfer/                     # FastSurfer code + models
│   │       ├── run_fastsurfer.py
│   │       └── models/
│   └── Info.plist
└── (User Data - outside app)
    ~/Library/Application Support/NeuroInsight/
    ├── database/
    │   └── neuroinsight.db
    ├── data/
    │   ├── uploads/
    │   └── processed/
    └── logs/
```

---

## Benefits vs. Current Approach

### Benefits
✅ No Docker required
✅ Simpler installation
✅ Smaller total footprint (~5GB vs ~16GB)
✅ Faster startup
✅ Better for locked-down systems
✅ True offline operation
✅ Enterprise-friendly

### Tradeoffs
⚠️ Larger initial development (3-4 weeks)
⚠️ More complex build process
⚠️ Platform-specific Python bundling
⚠️ Need to maintain embedded components

---

## Next Steps

### Immediate (Week 1)
1. Create new branch: `standalone-migration`
2. Start with SQLite migration
3. Test basic database operations

### Short-term (Weeks 2-3)
4. Bundle Python runtime
5. Integrate FastSurfer
6. Update Electron app

### Medium-term (Week 4)
7. Build installers
8. Test on all platforms
9. Create migration guide

### Long-term
10. Deprecate Docker version (optional)
11. Maintain both versions (hybrid + standalone)

---

## Recommendation

**For your paper/research**: Current Docker version is fine

**For wider adoption**: Standalone version is essential

**Best approach**: 
1. Publish paper with current version (mention Docker requirement)
2. Develop standalone version as v2.0
3. Offer both versions going forward

This gives you:
- ✅ Working solution now for paper
- ✅ Professional standalone version for clinical use
- ✅ Flexibility for different user needs

---

**Would you like me to start implementing Phase 1 (SQLite migration)?**

