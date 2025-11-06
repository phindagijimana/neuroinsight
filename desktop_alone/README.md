# NeuroInsight Desktop Standalone

One-click desktop application for hippocampal asymmetry analysis. No Docker or prerequisites required.

**Branch:** `desktop-standalone`  
**Status:** In Development  
**Target Release:** 6 weeks

---

## What This Is

Standalone desktop application that bundles everything needed:
- Python backend with FastAPI
- PyTorch + FastSurfer models
- Web-based UI in Electron window
- SQLite database (no PostgreSQL)
- Threading (no Celery/Redis)

**Result:** Download → Install → Use (like Cursor or Slack)

---

## For End Users (When Ready)

**Installation:**
1. Download installer for your platform
2. Run installer
3. Launch NeuroInsight
4. Upload MRI scan and process

**No Docker, Python, or configuration needed.**

---

## For Developers

### Quick Start

```bash
# Run backend in desktop mode
cd desktop_alone
export DESKTOP_MODE=true
python -m backend.main
```

Backend starts on http://localhost:8000

### Build Backend Bundle

```bash
bash scripts/build_backend.sh
```

Creates: `dist/neuroinsight-backend/`

### Build Desktop App

```bash
cd electron-app
npm install
npm run build
```

Creates platform installers in `electron-app/dist/`

---

## Project Structure

```
desktop_alone/
├── backend/         # FastAPI backend (adapted for SQLite)
├── pipeline/        # FastSurfer processing (unchanged)
├── frontend/        # Web UI (unchanged)
├── electron-app/    # Electron wrapper + icons
├── scripts/         # Build automation
├── build.spec       # PyInstaller config
└── models/          # FastSurfer models (to add)
```

---

## Key Differences from Main Version

| Aspect | Main (web-app) | Desktop (this) |
|--------|---------------|----------------|
| Database | PostgreSQL | SQLite |
| Tasks | Celery + Redis | Threading |
| Distribution | Docker Compose | Single installer |
| Target | Servers, HPC | Desktop users |

**Code reuse:** 85-90% shared with main version

---

## Development Status

**Week 1:** Backend adaptation (current)  
**Week 2:** PyInstaller bundling  
**Week 3:** Electron integration  
**Week 4:** Testing  
**Week 5:** Packaging  
**Week 6:** Release

See [GETTING_STARTED.md](GETTING_STARTED.md) for current tasks.

---

## System Requirements

**For built application:**
- 16 GB RAM (minimum), 32 GB recommended
- 30 GB free disk space
- Windows 10+, macOS 10.15+, or Linux

**For development:**
- Python 3.10+
- Node.js 18+
- PyInstaller

---

## Documentation

**Start here:**
- [README_FIRST.md](README_FIRST.md) - Orientation
- [GETTING_STARTED.md](GETTING_STARTED.md) - Next steps
- [DEVELOPMENT.md](DEVELOPMENT.md) - Dev workflow
- [STATUS.md](STATUS.md) - Progress

**Reference:**
- [../STANDALONE_IMPLEMENTATION_PLAN.md](../STANDALONE_IMPLEMENTATION_PLAN.md) - Full plan
- [RELEASE_STRATEGY.md](RELEASE_STRATEGY.md) - How releases work
- [BRANDING.md](BRANDING.md) - Icons and branding

---

## Building Installers

### Windows
```bash
cd electron-app && npm run build:win
```
Output: `NeuroInsight-Desktop-1.0.0-Windows-x64.exe`

### macOS
```bash
cd electron-app && npm run build:mac
```
Output: `NeuroInsight-Desktop-1.0.0-macOS-Universal.dmg`

### Linux
```bash
cd electron-app && npm run build:linux
```
Output: `NeuroInsight-Desktop-1.0.0-Linux-x64.AppImage`

---

## Contributing

**Development happens in:** `desktop-standalone` branch

**To contribute:**
1. Work in `desktop_alone/` directory
2. Test changes locally
3. Commit to `desktop-standalone` branch
4. Create PR when ready

---

**Goal:** Professional medical software with simple installation for clinical and research users.
