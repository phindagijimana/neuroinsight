# Development Guide - Standalone Desktop App

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Setup

1. **Install Python dependencies:**
   ```bash
   cd desktop_alone
   pip install -r backend/requirements.txt
   ```

2. **Test backend in desktop mode:**
   ```bash
   export DESKTOP_MODE=true
   python -m backend.main
   ```
   
   Backend should start on http://localhost:8000

3. **Install Electron dependencies:**
   ```bash
   cd electron-app
   npm install
   ```

4. **Test Electron app:**
   ```bash
   npm start
   ```

---

## Development Workflow

### Running in Development

**Terminal 1: Backend**
```bash
cd desktop_alone
export DESKTOP_MODE=true
python -m backend.main
```

**Terminal 2: Electron (if testing Electron wrapper)**
```bash
cd desktop_alone/electron-app
npm start
```

### Testing Changes

**Backend changes:**
```bash
# Make changes to backend code
# Restart backend
# Test at http://localhost:8000
```

**Frontend changes:**
```bash
# Edit frontend files
# Refresh browser
# Changes appear immediately
```

---

## Building

### Build Backend Executable

```bash
cd desktop_alone
bash scripts/build_backend.sh
```

Output: `dist/neuroinsight-backend/`

### Build Desktop App

```bash
cd desktop_alone/electron-app
npm run build
```

Output: `dist/NeuroInsight-*.exe/.dmg/.AppImage`

---

## Testing

### Test Standalone Backend

```bash
cd desktop_alone
export DESKTOP_MODE=true
dist/neuroinsight-backend/neuroinsight-backend
```

Should start without errors.

### Test Desktop App

```bash
cd desktop_alone/electron-app
npm start
```

Should launch Electron window with NeuroInsight UI.

---

## Current Status

**Phase 1: Initial Setup** ✓
- Directory structure created
- Backend code copied
- Pipeline code copied (100% reusable)
- Frontend code copied (100% reusable)
- Base configuration files created

**Phase 2: Backend Adaptation** (Next)
- [ ] Modify config.py for SQLite
- [ ] Update models for SQLite compatibility
- [ ] Implement task_service.py
- [ ] Test desktop mode

**Phase 3: Bundling** (Future)
- [ ] Test PyInstaller build
- [ ] Optimize bundle size
- [ ] Fix any import issues

**Phase 4: Electron Integration** (Future)
- [ ] Complete Electron app
- [ ] Backend process management
- [ ] Error handling

---

## Next Steps

See [../STANDALONE_IMPLEMENTATION_PLAN.md](../STANDALONE_IMPLEMENTATION_PLAN.md) for detailed week-by-week plan.

**Start with:** Week 1, Task 1.1 - SQLite integration

