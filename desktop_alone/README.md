# NeuroInsight Standalone Desktop Application

Standalone desktop version of NeuroInsight with no Docker requirement.

---

## Overview

This directory contains the standalone desktop application version of NeuroInsight that can be packaged as a single-click installer for Windows, macOS, and Linux.

**Key differences from main version:**
- No Docker/container dependencies
- SQLite instead of PostgreSQL
- Threading instead of Celery/Redis
- Bundled with PyInstaller + Electron
- Single installer for end users

---

## Directory Structure

```
desktop_alone/
├── backend/           # Backend code (FastAPI, adapted for SQLite)
├── pipeline/          # Processing pipeline (FastSurfer, unchanged)
├── frontend/          # Web UI (unchanged)
├── electron-app/      # Electron wrapper
├── models/            # FastSurfer model files (to be added)
├── scripts/           # Build and packaging scripts
├── build.spec         # PyInstaller configuration
└── README.md          # This file
```

---

## Development Status

**Phase 1: Backend Simplification** (In Progress)
- [ ] SQLite integration
- [ ] Threading instead of Celery
- [ ] Desktop mode configuration
- [ ] Remove Redis dependencies

**Phase 2: PyInstaller Bundling** (Pending)
- [ ] Create PyInstaller spec
- [ ] Test bundled backend
- [ ] Optimize bundle size

**Phase 3: Electron Integration** (Pending)
- [ ] Electron app setup
- [ ] Backend process management
- [ ] Auto-updater integration

**Phase 4: Packaging** (Pending)
- [ ] Windows installer (NSIS)
- [ ] macOS installer (DMG)
- [ ] Linux installer (AppImage)

---

## Quick Start (Development)

### Running Standalone Backend

```bash
cd desktop_alone

# Install dependencies
pip install -r backend/requirements.txt

# Run in desktop mode
export DESKTOP_MODE=true
python -m backend.main
```

### Building Standalone Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build backend
pyinstaller build.spec

# Test
dist/neuroinsight-backend/neuroinsight-backend
```

### Building Desktop App

```bash
cd electron-app
npm install
npm run build
```

---

## Documentation

**Implementation Plan:** [../STANDALONE_IMPLEMENTATION_PLAN.md](../STANDALONE_IMPLEMENTATION_PLAN.md)

**Quick Summary:** [../STANDALONE_QUICK_SUMMARY.md](../STANDALONE_QUICK_SUMMARY.md)

---

## Current vs Standalone

| Aspect | Current (main) | Standalone (desktop_alone) |
|--------|---------------|---------------------------|
| **Database** | PostgreSQL | SQLite |
| **Task Queue** | Celery + Redis | Threading |
| **Distribution** | Docker Compose | Single installer |
| **Target** | Servers, HPC | Desktop users |
| **Prerequisites** | Docker | None |

---

**Note:** This is a work in progress. See implementation plan for detailed roadmap.

