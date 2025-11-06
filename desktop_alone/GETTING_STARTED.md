# Getting Started - Desktop Standalone Build

## What Was Created

The `desktop_alone/` directory contains a standalone version of NeuroInsight:

```
desktop_alone/
├── backend/                    # Copied from main, will be adapted
├── pipeline/                   # Copied as-is (100% reusable)
├── frontend/                   # Copied as-is (100% reusable)
├── electron-app/               # New Electron wrapper
│   ├── src/main.js            # Main process (created)
│   └── package.json           # Build config (created)
├── scripts/
│   └── build_backend.sh       # Build script (created)
├── build.spec                  # PyInstaller config (created)
├── backend/requirements.txt    # Dependencies (created)
├── backend/core/config_desktop.py  # Desktop config (created)
├── backend/services/task_service.py  # Threading abstraction (created)
├── .gitignore                  # Ignore rules (created)
├── README.md                   # Overview (created)
├── DEVELOPMENT.md              # Dev guide (created)
└── GETTING_STARTED.md          # This file
```

---

## What's Been Done

**✓ Directory structure created**
**✓ Backend code copied** (needs adaptation)
**✓ Pipeline code copied** (ready to use)
**✓ Frontend code copied** (ready to use)
**✓ Desktop configuration created**
**✓ Task service abstraction created**
**✓ PyInstaller spec file created**
**✓ Electron app skeleton created**
**✓ Build scripts created**

---

## Next Steps (Week 1)

### Step 1: Adapt Backend for SQLite

**Files to modify:**

1. **backend/core/config.py**
   - Import and use DesktopSettings
   - Auto-detect desktop mode
   
2. **backend/models/job.py** (and other models)
   - Change UUID to String(36) for SQLite compatibility
   
3. **backend/core/database.py**
   - Ensure SQLite compatibility

4. **backend/api/upload.py**
   - Use task_service instead of Celery

**Estimated time:** 2-3 days

---

### Step 2: Remove Docker/Celery Dependencies

**Files to modify:**

1. **backend/main.py**
   - Serve frontend static files
   - Remove Celery imports
   - Use desktop config

2. **workers/tasks/processing.py** → **backend/services/processing_service.py**
   - Extract core processing function
   - Make it work without Celery decorators

**Estimated time:** 2 days

---

### Step 3: Test Desktop Mode

**Commands:**
```bash
export DESKTOP_MODE=true
python -m backend.main

# In another terminal:
curl http://localhost:8000/health
curl http://localhost:8000/jobs/

# Test upload (prepare a test .nii file)
curl -F "file=@test.nii" http://localhost:8000/upload/
```

**Expected:**
- Backend starts without PostgreSQL/Redis
- Creates SQLite database in user directory
- Can upload and process files
- Results stored locally

**Estimated time:** 1 day

---

## Quick Commands

### Development

```bash
# Run backend in desktop mode
cd desktop_alone
export DESKTOP_MODE=true
python -m backend.main
```

### Build Backend Bundle

```bash
cd desktop_alone
bash scripts/build_backend.sh
```

### Build Desktop App

```bash
cd desktop_alone/electron-app
npm install
npm run build
```

---

## Troubleshooting

### "Module not found" errors

**Solution:** Add to `build.spec` hiddenimports

### "Database error" 

**Solution:** Check SQLite compatibility in models

### "Backend won't start"

**Solution:** Check logs, ensure DESKTOP_MODE=true

---

## Documentation

**Full plan:** [../STANDALONE_IMPLEMENTATION_PLAN.md](../STANDALONE_IMPLEMENTATION_PLAN.md)

**Summary:** [../STANDALONE_QUICK_SUMMARY.md](../STANDALONE_QUICK_SUMMARY.md)

---

## Current Focus

**Working on:** Phase 1 - Backend Simplification

**Goal:** Make backend work without Docker, PostgreSQL, Redis, or Celery

**Timeline:** Week 1 of 6-week plan

---

Ready to start! Begin with modifying `backend/core/config.py` to use SQLite.

