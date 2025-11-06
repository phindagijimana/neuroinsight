# Where to Find Desktop Releases

## Current Status

**No releases yet** - The desktop_alone app is in development.

**What exists now:**
- ✓ Code and infrastructure
- ✓ Build configuration
- ✓ Documentation

**What doesn't exist yet:**
- ✗ Built installers
- ✗ Published releases

**Timeline:** First release in ~6 weeks after implementation

---

## Where Releases Will Be

### GitHub Releases Page

**URL:** https://github.com/phindagijimana/neuroinsight/releases

**Desktop releases will be tagged:**
```
desktop-v1.0.0
desktop-v1.0.1
desktop-v1.1.0
etc.
```

**Example release page:**
```
NeuroInsight Desktop v1.0.0
Tag: desktop-v1.0.0
Branch: desktop-standalone
Published: [Date]

Assets:
├── NeuroInsight-Desktop-1.0.0-Windows-x64.exe (1.5 GB)
├── NeuroInsight-Desktop-1.0.0-macOS-Universal.dmg (1.6 GB)
├── NeuroInsight-Desktop-1.0.0-Linux-x64.AppImage (1.5 GB)
├── NeuroInsight-Desktop-1.0.0-Linux-x64.deb (1.5 GB)
└── checksums.txt
```

---

## How to Access

### Direct Links (When Available)

**Latest desktop release:**
```
https://github.com/phindagijimana/neuroinsight/releases/latest
```

**Specific desktop version:**
```
https://github.com/phindagijimana/neuroinsight/releases/tag/desktop-v1.0.0
```

**All desktop releases:**
```
https://github.com/phindagijimana/neuroinsight/releases
(Filter by "desktop-v" tags)
```

---

### From Repository

**Step 1:** Go to GitHub repository
```
https://github.com/phindagijimana/neuroinsight
```

**Step 2:** Click "Releases" (right sidebar)

**Step 3:** Look for tags starting with `desktop-v*`
```
Releases:
├── desktop-v1.0.0  ← Desktop installers
├── web-v2.0.0      ← Web/Docker version (different)
└── desktop-v0.9.0  ← Previous desktop version
```

**Step 4:** Click desktop release you want

**Step 5:** Download installer for your platform

---

## Current Development Versions

### Building Locally (For Testing)

**If you want to test now (before official release):**

```bash
# 1. Clone repository
git clone https://github.com/phindagijimana/neuroinsight
cd neuroinsight

# 2. Switch to desktop-standalone branch
git checkout desktop-standalone

# 3. Build backend
cd desktop_alone
bash scripts/build_backend.sh

# 4. Build desktop app
cd electron-app
npm install
npm run build

# 5. Installers created in:
cd dist/
# NeuroInsight-Desktop-1.0.0-[Platform].exe/.dmg/.AppImage
```

**Note:** These are development builds, not official releases

---

## When First Release Will Be Available

### Timeline

**Development phases:**
```
Week 1: Backend adaptation (6 days remaining)
Week 2: PyInstaller bundling
Week 3: Electron integration
Week 4: Testing
Week 5: Create installers
Week 6: Code signing & polish

First release: ~6 weeks from now
```

**When ready:**
1. Create tag: `desktop-v1.0.0`
2. Push to GitHub
3. CI/CD builds installers automatically
4. Release published on GitHub
5. Users can download

---

## Release Notification

### How to Know When Released

**GitHub Watch:**
```
1. Go to: https://github.com/phindagijimana/neuroinsight
2. Click "Watch" (top right)
3. Choose "Custom" → "Releases"
4. Get notified when desktop-v* released
```

**Check Releases Page:**
```
https://github.com/phindagijimana/neuroinsight/releases
```

**Subscribe to Updates:**
- Star the repository
- Check releases periodically

---

## Future Release Structure

### When Multiple Versions Exist

**GitHub Releases page will show:**

```
NeuroInsight Releases

Desktop Releases:
├── desktop-v1.2.0 (Latest Desktop) ★
│   └── Windows, macOS, Linux installers
├── desktop-v1.1.0
└── desktop-v1.0.0

Web App Releases:
├── web-v2.5.0 (Latest Web) ★
│   └── Docker deployment files
├── web-v2.0.0
└── web-v1.0.0
```

**Filtering:**
- Search for "desktop" to see only desktop releases
- Search for "web" to see only web releases

---

## Direct Download Links (Future)

### Latest Version URLs

**When released, these URLs will work:**

**Windows (latest):**
```
https://github.com/phindagijimana/neuroinsight/releases/download/desktop-v1.0.0/NeuroInsight-Desktop-1.0.0-Windows-x64.exe
```

**macOS (latest):**
```
https://github.com/phindagijimana/neuroinsight/releases/download/desktop-v1.0.0/NeuroInsight-Desktop-1.0.0-macOS-Universal.dmg
```

**Linux (latest):**
```
https://github.com/phindagijimana/neuroinsight/releases/download/desktop-v1.0.0/NeuroInsight-Desktop-1.0.0-Linux-x64.AppImage
```

**These can be used for:**
- Direct download links
- Documentation
- Installation scripts
- Website download buttons

---

## Alternative Distribution (Future)

### Microsoft Store

**When submitted:**
```
Search: "NeuroInsight"
Publisher: NeuroInsight Team
Platform: Windows only

Separate from GitHub releases
Auto-updates through Microsoft Store
```

### Snap Store

**When submitted:**
```
Command: snap install neuroinsight
Platform: Linux only

Separate from GitHub releases
Auto-updates through Snap
```

---

## Summary

**Current Status:**
- No releases yet (in development)
- Code infrastructure ready
- Release strategy defined

**Where releases will be:**
- GitHub: https://github.com/phindagijimana/neuroinsight/releases
- Tagged: desktop-v1.0.0, desktop-v1.1.0, etc.
- Separate from web-v* releases

**How to access:**
- Go to releases page
- Look for "desktop-v*" tags
- Download installer for your platform

**When available:**
- ~6 weeks (after development)
- First tag: desktop-v1.0.0
- You'll see desktop installers clearly separated

**Current option:**
- Build locally from desktop-standalone branch
- For development and testing only

---

**Once released, desktop installers will be easy to find with clear "desktop-v" tags, completely separate from web app releases!**

