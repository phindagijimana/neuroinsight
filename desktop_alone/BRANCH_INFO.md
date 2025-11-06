# Desktop Standalone Branch

**Branch:** `desktop-standalone`  
**Created:** November 6, 2025  
**Purpose:** Develop standalone desktop application without Docker dependencies

---

## Repository Structure

### Branches

**`web-app`** - Main branch
- Docker Compose deployment
- HPC/Server version
- Current production system

**`desktop-standalone`** - This branch
- Standalone desktop application
- No Docker requirement
- End-user distribution

**`desktop-app`** - Old Docker manager
- Electron app that manages Docker
- Legacy approach

---

## What's in This Branch

### New Directory: `desktop_alone/`

Complete standalone application codebase:

```
desktop_alone/
├── backend/         # Adapted for SQLite + threading
├── pipeline/        # Reused 100% from web-app
├── frontend/        # Reused 100% from web-app
├── electron-app/    # New Electron wrapper
├── scripts/         # Build automation
├── models/          # FastSurfer models (to add)
├── build.spec       # PyInstaller config
└── docs/            # Development guides
```

### Also in This Branch

All comprehensive documentation:
- `STANDALONE_IMPLEMENTATION_PLAN.md`
- `STANDALONE_QUICK_SUMMARY.md`
- `docs/3D_SLICER_ARCHITECTURE.md`
- `docs/MODERN_APP_PACKAGING.md`
- `docs/ONE_CLICK_PACKAGING_GUIDE.md`
- `docs/DOCKER_VS_STANDALONE_COMPARISON.md`
- `docs/APP_STORE_DISTRIBUTION.md`
- And more...

---

## Development Workflow

### Working on Standalone

```bash
# Switch to standalone branch
git checkout desktop-standalone

# Work in desktop_alone directory
cd desktop_alone

# Make changes
# Test
# Commit

git add .
git commit -m "Your changes"
git push origin desktop-standalone
```

### Pulling Updates from web-app

```bash
# If web-app branch gets updates
git checkout desktop-standalone
git merge web-app

# Resolve conflicts if any
# Usually in main codebase files, not desktop_alone/
```

---

## Branch Purpose

### desktop-standalone (This Branch)

**Purpose:**
- Develop standalone desktop application
- Experiment with PyInstaller + Electron
- Test without affecting production

**Key directories:**
- `desktop_alone/` - Standalone version
- Documentation about standalone approach

**Deploy:** End-user desktop installers

---

### web-app (Main Branch)

**Purpose:**
- Production HPC deployment
- Docker-based server version
- Current working system

**Key directories:**
- Root backend/, frontend/, pipeline/
- docker-compose.yml
- Deployment scripts

**Deploy:** HPC, servers, Docker environments

---

## Keeping Branches in Sync

### Strategy

**Common code (pipeline, frontend):**
```
Changes in web-app:
- Update in web-app branch
- Merge into desktop-standalone
- Copy to desktop_alone/ if needed

Changes in desktop-standalone:
- If generally useful, port to web-app
```

**Separate code:**
```
desktop_alone/ - Only in desktop-standalone
docker-compose.yml - Only in web-app
```

---

## Why Separate Branch?

**Benefits:**
1. **Non-disruptive:** web-app continues working
2. **Experimental:** Can test freely
3. **Organized:** Clear separation
4. **Reviewable:** Can create PR when ready
5. **Reversible:** Can abandon if doesn't work

---

## Merging Back

**When standalone is ready:**
```bash
# Option 1: Keep both versions
git checkout web-app
# Both versions exist in repository

# Option 2: Merge standalone as subdirectory
git checkout web-app
git merge desktop-standalone
# Now web-app has desktop_alone/ too
```

---

## Current Status

**Branch created:** ✓  
**Directory structure:** ✓  
**Base files:** ✓  
**Documentation:** ✓  
**Ready for development:** ✓

**Next:** Begin Week 1 implementation

---

## Quick Links

**This Branch:**
- `desktop_alone/` - Standalone app code
- `desktop_alone/STATUS.md` - Development progress
- `desktop_alone/GETTING_STARTED.md` - Next steps

**Documentation:**
- `STANDALONE_IMPLEMENTATION_PLAN.md` - Full 6-week plan
- `STANDALONE_QUICK_SUMMARY.md` - One-page overview

**GitHub:**
https://github.com/phindagijimana/neuroinsight/tree/desktop-standalone

