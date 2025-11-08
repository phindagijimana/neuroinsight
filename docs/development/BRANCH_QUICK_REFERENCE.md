# NeuroInsight - Branch Quick Reference

## 🌳 Available Branches

### 1. `desktop-app` - Electron Desktop Application
```bash
git checkout desktop-app
```

**What's Preserved:**
- ✅ Complete Electron app (`hippo_desktop/` folder)
- ✅ All source code (React UI, Node.js backend integration)
- ✅ Package.json with all dependencies
- ✅ GitHub Actions workflow (`.github/workflows/release.yml`)
- ✅ All PATH fixes we attempted (v1.0.1 - v1.0.5)
- ✅ Docker integration code
- ✅ Service management (DockerManager, ServiceManager)
- ✅ System checker utilities
- ✅ macOS install scripts
- ✅ Icon files (icns, ico, png)
- ✅ Documentation (QUICK_START.md, etc.)
- ✅ Build configuration (electron-builder)
- ✅ Migration plan (STANDALONE_MIGRATION_PLAN.md)

**To Resume Desktop Development:**
```bash
git checkout desktop-app
cd hippo_desktop
npm install
npm start  # Test locally
npm run dist:mac  # Build for macOS
```

**Future Options:**
1. Continue fixing Docker PATH issues
2. Migrate to standalone (STANDALONE_MIGRATION_PLAN.md)
3. Try hybrid approach (bundled Python)

---

### 2. `web-app` - Docker Compose Web Application
```bash
git checkout web-app
```

**What's Here:**
- ✅ Simplified deployment (docker-compose only)
- ✅ All backend services (unchanged)
- ✅ Web frontend (unchanged)
- ✅ Clean documentation
- ✅ Paper-ready approach

**To Use:**
```bash
git checkout web-app
docker-compose up -d
open http://localhost:3000
```

**Recommended For:**
- Paper publication
- Research use
- HPC/cluster deployment
- Reliable, proven approach

---

### 3. `main` - Default Branch
```bash
git checkout main
```

**Current Status:** Same as `desktop-app` (has all desktop work)

**Will Become:** We can point this to `web-app` for stable release

---

## 🔄 Switching Between Branches

### View All Branches
```bash
git branch -a

# Output:
  desktop-app
  main
  web-app
* (current branch highlighted)
```

### Switch to Desktop App
```bash
git checkout desktop-app
# Now you have all desktop code
ls hippo_desktop/  # See all files
```

### Switch to Web App
```bash
git checkout web-app
# Simplified version
docker-compose up -d
```

### Compare Branches
```bash
# See what's different between branches
git diff desktop-app web-app

# See files only in desktop-app
git diff --name-only desktop-app web-app
```

---

## 📋 What's in Each Branch

### Files in `desktop-app` (NOT in `web-app`)
```
hippo_desktop/
├── src/
│   ├── main.js (Electron main process with PATH fixes)
│   ├── preload.js
│   ├── setup.html
│   ├── managers/ (DockerManager, ServiceManager)
│   └── utils/ (SystemChecker, ComposeWrapper, logger)
├── assets/ (icons, images)
├── scripts/ (check-requirements, setup)
├── package.json (Electron + dependencies)
├── QUICK_START.md
├── STANDALONE_MIGRATION_PLAN.md
└── install-macos.sh

.github/workflows/release.yml (automated builds)
```

### Files in Both Branches
```
backend/ (FastAPI, all unchanged)
frontend/ (React web UI, all unchanged)
data/ (uploads, outputs)
docker-compose.yml (unchanged)
README.md
CONTRIBUTING.md
```

---

## 🎯 Recommendations by Use Case

### For Your Paper (Submit Soon)
```bash
git checkout web-app
# Use this - it works reliably
```

### To Continue Desktop Development
```bash
git checkout desktop-app
# All your work is here
# Can continue anytime
```

### To Start Standalone Migration (v2.0)
```bash
git checkout -b standalone-migration desktop-app
# Start from desktop-app code
# Follow STANDALONE_MIGRATION_PLAN.md
```

---

## 💾 Everything is Saved!

**Nothing is lost!** All the work on:
- PATH fixes (5 versions worth)
- Docker integration
- Electron configuration
- GitHub Actions
- Documentation

Is safely preserved in the `desktop-app` branch.

You can:
- ✅ Come back to it anytime
- ✅ Continue development
- ✅ Create new branches from it
- ✅ Merge improvements back
- ✅ Compare with web-app approach

---

## 🔍 Quick Commands

### See Current Branch
```bash
git branch --show-current
```

### See All Commits in Desktop Branch
```bash
git log --oneline desktop-app
```

### See What Changed in Last Commit
```bash
git show desktop-app
```

### Create New Branch from Desktop
```bash
git checkout -b my-new-feature desktop-app
```

---

## 📞 Quick Decision Guide

**"I want to publish my paper soon"**
→ Use `web-app` branch

**"I want to continue desktop app work"**
→ Use `desktop-app` branch

**"I want to build standalone app (no Docker)"**
→ Create branch from `desktop-app`, follow migration plan

**"I want to see all the PATH fixes we tried"**
→ `git checkout desktop-app && git log --oneline`

**"I want to compare approaches"**
→ `git diff desktop-app web-app`

---

*All branches are on GitHub at:*
*https://github.com/phindagijimana/neuroinsight*

