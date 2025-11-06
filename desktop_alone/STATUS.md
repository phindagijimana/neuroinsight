# Standalone Desktop App - Current Status

**Created:** November 6, 2025  
**Phase:** Initial Setup Complete

---

## What Exists Now

### Directory Structure

```
desktop_alone/
├── backend/           ✓ Copied from main codebase
├── pipeline/          ✓ Copied from main (100% reusable)
├── frontend/          ✓ Copied from main (100% reusable)
├── electron-app/      ✓ Created (Electron wrapper)
├── models/            ✓ Created (for FastSurfer models)
├── scripts/           ✓ Created (build scripts)
└── Configuration files ✓ Created
```

### Key Files Created

**Configuration:**
- `backend/core/config_desktop.py` - Desktop-specific settings (SQLite, user directories)
- `backend/requirements.txt` - Python dependencies
- `build.spec` - PyInstaller configuration
- `.gitignore` - Git ignore rules

**Service Layer:**
- `backend/services/task_service.py` - Threading abstraction (replaces Celery)

**Electron App:**
- `electron-app/package.json` - Electron configuration
- `electron-app/src/main.js` - Main process (backend management)

**Build Tools:**
- `scripts/build_backend.sh` - Backend build script

**Documentation:**
- `README.md` - Overview
- `DEVELOPMENT.md` - Development guide
- `GETTING_STARTED.md` - Next steps
- `STATUS.md` - This file

---

## What Works

**Already functional:**
- ✓ Backend code present
- ✓ Pipeline code present (FastSurfer integration)
- ✓ Frontend code present (Web UI)
- ✓ Desktop configuration created
- ✓ Task service abstraction created
- ✓ Build infrastructure in place

**Ready for:**
- Code adaptation (SQLite, threading)
- Testing in desktop mode
- PyInstaller bundling

---

## What Needs Work

### Phase 1: Backend Adaptation (Week 1)

**To Do:**
```
1. backend/core/config.py
   - Use config_desktop when DESKTOP_MODE=true
   
2. backend/models/*.py
   - Change UUID to String(36) for SQLite
   
3. backend/api/upload.py
   - Use task_service instead of Celery
   
4. backend/main.py
   - Remove Celery references
   - Serve frontend static files
   
5. Test in desktop mode
```

---

## Next Actions

### Immediate (Today/Tomorrow)

**Test current backend in desktop mode:**
```bash
cd desktop_alone
pip install -r backend/requirements.txt
export DESKTOP_MODE=true
python -m backend.main
```

**Expected:** May have errors (that's OK - we'll fix them)

**Goal:** Identify what needs changing

---

### This Week

**Adapt backend for standalone:**
1. Integrate desktop config
2. Make SQLite compatible
3. Remove Celery dependencies
4. Test each change

**Deliverable:** Backend runs without Docker/PostgreSQL/Redis

---

## Progress Tracking

**Phase 1: Backend Simplification**
- [x] Directory structure created
- [x] Code copied
- [x] Configuration files created
- [ ] Config integration
- [ ] SQLite compatibility  
- [ ] Threading implementation
- [ ] Testing

**Phase 2: PyInstaller Bundling**
- [ ] Build backend with PyInstaller
- [ ] Test bundled backend
- [ ] Optimize bundle size

**Phase 3: Electron Integration**
- [ ] Complete Electron app
- [ ] Backend process management
- [ ] Testing

**Phase 4-6:** See [STANDALONE_IMPLEMENTATION_PLAN.md](../STANDALONE_IMPLEMENTATION_PLAN.md)

---

## Current State

**Code reuse:** 85-90% (as planned)

**New code created:**
- config_desktop.py (80 lines)
- task_service.py (100 lines)
- main.js (150 lines)
- Build scripts (100 lines)
- Total new code: ~430 lines

**Modifications needed:** ~500 more lines across 10 files

**Total new/modified code:** ~930 lines (vs 50,000+ existing lines = <2%)

---

## Success Criteria

**Phase 1 complete when:**
- [ ] Backend starts with `DESKTOP_MODE=true`
- [ ] SQLite database created automatically
- [ ] No PostgreSQL/Redis needed
- [ ] Can upload MRI file
- [ ] Processing works (even if slow)
- [ ] Results stored in SQLite

**Testing command:**
```bash
export DESKTOP_MODE=true
python -m backend.main &
sleep 5
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

---

## Timeline

**Week 1 (Current):** Backend adaptation  
**Weeks 2-6:** Bundling, Electron, packaging, polish

**End goal:** One-click installers for Windows, macOS, Linux

---

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed next steps.

