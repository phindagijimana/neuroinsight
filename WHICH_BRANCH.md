# NeuroInsight - Which Branch to Use?

## 🌳 Available Branches

### ✅ `web-app` - **RECOMMENDED FOR USE**

**Use this for:**
- Running NeuroInsight
- Paper publication
- General use
- Sharing with colleagues

**Installation:**
```bash
git clone -b web-app https://github.com/phindagijimana/neuroinsight.git
cd neuroinsight
docker-compose up -d
```

**Documentation:**
- See `README.md` on `web-app` branch
- See `INSTALL.md` for simple 3-step guide
- See `QUICK_REFERENCE.md` for command reference

---

### 🔧 `desktop-app` - **IN DEVELOPMENT**

**Status:** Paused due to macOS PATH issues with Electron + Docker

**Contains:**
- Full Electron desktop application
- All attempted fixes (v1.0.0 - v1.0.5)
- GitHub Actions for automated builds
- Standalone migration plan

**For:**
- Future standalone app development
- Reference for desktop app approach
- Developers interested in Electron + Docker challenges

---

### 📌 `main` - **DEFAULT**

Currently same as `desktop-app`. Will be updated to track recommended branch.

---

## 🚀 Quick Start (Most Users)

```bash
# Clone web-app branch
git clone -b web-app https://github.com/phindagijimana/neuroinsight.git
cd neuroinsight

# Start
docker-compose up -d

# Open
open http://localhost:3000
```

---

## 📚 Full Documentation

See the `web-app` branch:
- https://github.com/phindagijimana/neuroinsight/tree/web-app

---

**Default download** (green "Code" button) gets `main` branch.

**Recommended:** Explicitly clone `web-app` branch as shown above.

