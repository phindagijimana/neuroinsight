# Release Strategy - Standalone Desktop App

How installers are organized and distributed separately from web app releases.

---

## Release Organization

### Separate Release Channels

**Desktop Standalone Releases:**
- Tag format: `desktop-v1.0.0`, `desktop-v1.1.0`, etc.
- Branch: `desktop-standalone`
- Artifacts: Windows, macOS, Linux installers
- Target: End users (clinical, research)

**Web App Releases:**
- Tag format: `web-v1.0.0`, `web-v1.1.0`, etc.
- Branch: `web-app`
- Artifacts: Docker images, deployment docs
- Target: HPC, server deployments

---

## File Naming Convention

### Desktop Installers

**Windows:**
```
NeuroInsight-Desktop-1.0.0-Windows-x64.exe
NeuroInsight-Desktop-1.0.0-Windows-x64-Portable.exe (optional)
```

**macOS:**
```
NeuroInsight-Desktop-1.0.0-macOS-Universal.dmg
NeuroInsight-Desktop-1.0.0-macOS-x64.dmg (Intel only)
NeuroInsight-Desktop-1.0.0-macOS-arm64.dmg (Apple Silicon only)
```

**Linux:**
```
NeuroInsight-Desktop-1.0.0-Linux-x64.AppImage
NeuroInsight-Desktop-1.0.0-Linux-x64.deb
NeuroInsight-Desktop-1.0.0-Linux-x64.rpm (optional)
```

---

## GitHub Releases Structure

### Example Release Page

**Release: Desktop v1.0.0**
```
Title: NeuroInsight Desktop v1.0.0
Tag: desktop-v1.0.0
Branch: desktop-standalone
Date: November 15, 2025

Description:
First stable release of NeuroInsight standalone desktop application.

No Docker or external dependencies required.

Installation:
- Windows: Download .exe and run
- macOS: Download .dmg, drag to Applications
- Linux: Download .AppImage, make executable and run

System Requirements:
- 16 GB RAM recommended
- 30 GB free disk space
- Windows 10+, macOS 10.15+, or Linux

Assets:
├── NeuroInsight-Desktop-1.0.0-Windows-x64.exe (1.5 GB)
├── NeuroInsight-Desktop-1.0.0-macOS-Universal.dmg (1.6 GB)
├── NeuroInsight-Desktop-1.0.0-Linux-x64.AppImage (1.5 GB)
├── NeuroInsight-Desktop-1.0.0-Linux-x64.deb (1.5 GB)
├── checksums.txt (SHA256 hashes)
└── RELEASE_NOTES.md (detailed changelog)
```

**Separate from:**
```
Release: Web App v1.0.0
Tag: web-v1.0.0
Branch: web-app

Assets:
├── docker-compose.yml
├── .env.example
├── deployment-guide.pdf
└── Source code (zip/tar.gz)
```

---

## electron-builder Configuration

### Updated package.json for Clear Naming

**File:** `electron-app/package.json`

```json
{
  "name": "neuroinsight-standalone",
  "version": "1.0.0",
  "build": {
    "appId": "com.neuroinsight.desktop",
    "productName": "NeuroInsight Desktop",
    "artifactName": "NeuroInsight-Desktop-${version}-${os}-${arch}.${ext}",
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        }
      ],
      "artifactName": "NeuroInsight-Desktop-${version}-Windows-${arch}.${ext}"
    },
    "mac": {
      "target": [
        {
          "target": "dmg",
          "arch": ["x64", "arm64", "universal"]
        }
      ],
      "artifactName": "NeuroInsight-Desktop-${version}-macOS-${arch}.${ext}"
    },
    "linux": {
      "target": [
        "AppImage",
        "deb"
      ],
      "artifactName": "NeuroInsight-Desktop-${version}-Linux-${arch}.${ext}"
    }
  }
}
```

---

## CI/CD Configuration

### Automated Release Building

**File:** `.github/workflows/build-desktop-release.yml`

```yaml
name: Build Desktop Release

on:
  push:
    tags:
      - 'desktop-v*'

jobs:
  build-backend:
    name: Build Python Backend
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd desktop_alone
          pip install -r backend/requirements.txt
          pip install pyinstaller
      
      - name: Build backend with PyInstaller
        run: |
          cd desktop_alone
          pyinstaller build.spec --clean
      
      - name: Upload backend artifact
        uses: actions/upload-artifact@v3
        with:
          name: backend-bundle
          path: desktop_alone/dist/neuroinsight-backend/
          retention-days: 1

  build-windows:
    name: Build Windows Installer
    needs: build-backend
    runs-on: windows-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Download backend bundle
        uses: actions/download-artifact@v3
        with:
          name: backend-bundle
          path: desktop_alone/dist/neuroinsight-backend
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Build Electron app
        run: |
          cd desktop_alone/electron-app
          npm install
          npm run build:win
      
      - name: Upload Windows installer
        uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: desktop_alone/electron-app/dist/*.exe
          retention-days: 1

  build-macos:
    name: Build macOS Installer
    needs: build-backend
    runs-on: macos-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Download backend bundle
        uses: actions/download-artifact@v3
        with:
          name: backend-bundle
          path: desktop_alone/dist/neuroinsight-backend
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Build Electron app
        run: |
          cd desktop_alone/electron-app
          npm install
          npm run build:mac
        env:
          # Code signing (when certificates configured)
          # CSC_LINK: ${{ secrets.MAC_CERTIFICATE }}
          # CSC_KEY_PASSWORD: ${{ secrets.MAC_CERTIFICATE_PASSWORD }}
      
      - name: Upload macOS installer
        uses: actions/upload-artifact@v3
        with:
          name: macos-installer
          path: desktop_alone/electron-app/dist/*.dmg
          retention-days: 1

  build-linux:
    name: Build Linux Installers
    needs: build-backend
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Download backend bundle
        uses: actions/download-artifact@v3
        with:
          name: backend-bundle
          path: desktop_alone/dist/neuroinsight-backend
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Build Electron app
        run: |
          cd desktop_alone/electron-app
          npm install
          npm run build:linux
      
      - name: Upload Linux installers
        uses: actions/upload-artifact@v3
        with:
          name: linux-installers
          path: |
            desktop_alone/electron-app/dist/*.AppImage
            desktop_alone/electron-app/dist/*.deb
          retention-days: 1

  create-release:
    name: Create GitHub Release
    needs: [build-windows, build-macos, build-linux]
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Download all installers
        uses: actions/download-artifact@v3
        with:
          path: installers
      
      - name: Generate checksums
        run: |
          cd installers
          find . -type f \( -name "*.exe" -o -name "*.dmg" -o -name "*.AppImage" -o -name "*.deb" \) \
            -exec sha256sum {} \; > checksums.txt
      
      - name: Create Release Notes
        run: |
          cat > RELEASE_NOTES.md << 'EOF'
          # NeuroInsight Desktop ${GITHUB_REF_NAME}
          
          ## Installation
          
          ### Windows
          Download and run: `NeuroInsight-Desktop-*-Windows-x64.exe`
          
          ### macOS
          Download, open, and drag to Applications: `NeuroInsight-Desktop-*-macOS-*.dmg`
          
          ### Linux
          Download and make executable: `NeuroInsight-Desktop-*-Linux-x64.AppImage`
          Or install DEB package: `sudo dpkg -i NeuroInsight-Desktop-*-Linux-x64.deb`
          
          ## System Requirements
          - 16 GB RAM (minimum), 32 GB recommended
          - 30 GB free disk space
          - Windows 10+, macOS 10.15+, or Linux
          
          ## What's New
          - First stable release
          - No Docker required
          - One-click installation
          - Auto-updates enabled
          
          ## Checksums
          See checksums.txt for SHA256 verification
          EOF
      
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          name: NeuroInsight Desktop ${{ github.ref_name }}
          body_path: RELEASE_NOTES.md
          draft: false
          prerelease: false
          files: |
            installers/windows-installer/*.exe
            installers/macos-installer/*.dmg
            installers/linux-installers/*.AppImage
            installers/linux-installers/*.deb
            installers/checksums.txt
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Release Process

### Creating a New Release

**Step 1: Update version**
```bash
cd desktop_alone/electron-app

# Update package.json version
# "version": "1.1.0"

git commit -am "Bump desktop version to 1.1.0"
```

**Step 2: Create tag**
```bash
git tag -a desktop-v1.1.0 -m "Desktop release 1.1.0

New features:
- Feature A
- Feature B

Bug fixes:
- Fix X
- Fix Y
"

git push origin desktop-v1.1.0
```

**Step 3: Automated build**
```
GitHub Actions automatically:
1. Builds backend with PyInstaller
2. Builds Windows installer
3. Builds macOS installer  
4. Builds Linux installers
5. Creates GitHub release
6. Uploads all installers
7. Generates checksums

Time: 30-60 minutes
```

**Step 4: Release is live**
```
Users can download from:
https://github.com/yourorg/neuroinsight/releases/tag/desktop-v1.1.0
```

---

## Download Page Organization

### GitHub Releases View

**Visitors see:**

```
Releases
├── Desktop v1.1.0 (Latest Desktop)
│   ├── NeuroInsight-Desktop-1.1.0-Windows-x64.exe
│   ├── NeuroInsight-Desktop-1.1.0-macOS-Universal.dmg
│   ├── NeuroInsight-Desktop-1.1.0-Linux-x64.AppImage
│   ├── NeuroInsight-Desktop-1.1.0-Linux-x64.deb
│   └── checksums.txt
│
├── Desktop v1.0.0
│   └── Previous desktop installers...
│
├── Web v2.0.0 (Latest Web)
│   ├── Source code (zip)
│   ├── Source code (tar.gz)
│   └── deployment-guide.pdf
│
└── Web v1.0.0
    └── Previous web releases...
```

**Clear separation:** Users easily find the right version

---

## Custom Download Page

### Optional: Dedicated Download Site

**Create:** `docs/DOWNLOAD.md` in repository

```markdown
# Download NeuroInsight

## Desktop Application (Recommended for Most Users)

No installation of Docker or other prerequisites required.

### Latest Version: Desktop v1.0.0

**Windows (Windows 10/11):**
[Download NeuroInsight-Desktop-1.0.0-Windows-x64.exe](https://github.com/yourorg/neuroinsight/releases/download/desktop-v1.0.0/NeuroInsight-Desktop-1.0.0-Windows-x64.exe) (1.5 GB)

**macOS (10.15+):**
[Download NeuroInsight-Desktop-1.0.0-macOS-Universal.dmg](https://github.com/yourorg/neuroinsight/releases/download/desktop-v1.0.0/NeuroInsight-Desktop-1.0.0-macOS-Universal.dmg) (1.6 GB)

**Linux (Ubuntu, Fedora, etc.):**
[Download NeuroInsight-Desktop-1.0.0-Linux-x64.AppImage](https://github.com/yourorg/neuroinsight/releases/download/desktop-v1.0.0/NeuroInsight-Desktop-1.0.0-Linux-x64.AppImage) (1.5 GB)

[Download NeuroInsight-Desktop-1.0.0-Linux-x64.deb](https://github.com/yourorg/neuroinsight/releases/download/desktop-v1.0.0/NeuroInsight-Desktop-1.0.0-Linux-x64.deb) (1.5 GB)

---

## Server Deployment (For Administrators)

Docker-based deployment for HPC and servers.

[See Web App Releases](https://github.com/yourorg/neuroinsight/releases?q=web-v)
```

**Benefits:**
- Clear download links
- Auto-detects user's OS (with JavaScript)
- Direct links to latest version
- Separated by use case

---

## Tagging Strategy

### Desktop Tags

```bash
# Major release
git tag -a desktop-v1.0.0 -m "Desktop 1.0.0 - First stable release"

# Minor release (new features)
git tag -a desktop-v1.1.0 -m "Desktop 1.1.0 - Add batch processing"

# Patch release (bug fixes)
git tag -a desktop-v1.0.1 -m "Desktop 1.0.1 - Fix upload bug"

# Beta releases
git tag -a desktop-v1.1.0-beta.1 -m "Desktop 1.1.0 Beta 1"

# Push tags
git push origin desktop-v1.0.0
```

### Web App Tags

```bash
# Separate versioning
git tag -a web-v2.0.0 -m "Web 2.0.0 - GPU support"
git push origin web-v2.0.0
```

**Independent versioning:** Desktop and web can have different version numbers

---

## Auto-Update Configuration

### electron-updater Setup

**File:** `electron-app/src/updater.js` (Create)

```javascript
const { autoUpdater } = require('electron-updater');
const log = require('electron-log');

// Configure for desktop releases only
autoUpdater.channel = 'latest';
autoUpdater.allowPrerelease = false;

// Only check desktop-v* tags
autoUpdater.setFeedURL({
  provider: 'github',
  owner: 'yourorg',
  repo: 'neuroinsight',
  // Only desktop releases
  releaseType: 'release',
  updaterCacheDirName: 'neuroinsight-desktop-updater'
});

// Check for updates
function checkForUpdates() {
  autoUpdater.checkForUpdatesAndNotify();
}

// Update available
autoUpdater.on('update-available', (info) => {
  log.info('Update available:', info.version);
  // Show notification to user
});

// Download complete
autoUpdater.on('update-downloaded', (info) => {
  log.info('Update downloaded:', info.version);
  // Prompt user to restart
});

module.exports = { checkForUpdates };
```

**Update will only find desktop-v* releases** due to filtering

---

## Release Artifacts Structure

### What Gets Published

**For each desktop release:**

```
GitHub Release: desktop-v1.0.0
├── Installers/
│   ├── NeuroInsight-Desktop-1.0.0-Windows-x64.exe
│   ├── NeuroInsight-Desktop-1.0.0-macOS-Universal.dmg
│   ├── NeuroInsight-Desktop-1.0.0-macOS-x64.dmg
│   ├── NeuroInsight-Desktop-1.0.0-macOS-arm64.dmg
│   ├── NeuroInsight-Desktop-1.0.0-Linux-x64.AppImage
│   └── NeuroInsight-Desktop-1.0.0-Linux-x64.deb
│
├── Verification/
│   ├── checksums.txt (SHA256 hashes)
│   └── checksums.txt.sig (GPG signature, optional)
│
├── Documentation/
│   ├── RELEASE_NOTES.md
│   ├── INSTALLATION_GUIDE.pdf
│   └── CHANGELOG.md
│
└── Metadata/
    ├── latest.yml (for auto-updater)
    ├── latest-mac.yml
    └── latest-linux.yml
```

**electron-builder generates latest*.yml automatically for auto-updater**

---

## Separate Beta/Stable Channels

### Beta Releases

**For testing before stable:**

```bash
# Create beta tag
git tag -a desktop-v1.1.0-beta.1 -m "Desktop 1.1.0 Beta 1"
git push origin desktop-v1.1.0-beta.1

# Release marked as "Pre-release" on GitHub
# Different download section
# Auto-updater won't notify stable users
```

**Beta users opt-in:**
```javascript
// In app settings
autoUpdater.allowPrerelease = true;
autoUpdater.channel = 'beta';
```

---

## Release Checklist

### Before Creating Release

```
Version Management:
□ Update version in electron-app/package.json
□ Update CHANGELOG.md
□ Commit version bump

Testing:
□ Test on Windows 10/11
□ Test on macOS (Intel + Apple Silicon)
□ Test on Ubuntu/Fedora
□ Verify all features work
□ Check for memory leaks

Documentation:
□ Update README if needed
□ Prepare release notes
□ Update installation guide

Build:
□ Create git tag (desktop-v*)
□ Push tag to trigger CI/CD
□ Wait for builds to complete
□ Download and verify installers
□ Test installers on clean systems

Release:
□ Edit release description
□ Add installation instructions
□ Attach additional docs if needed
□ Publish release
```

---

## Version Numbering

### Semantic Versioning

**Format:** `MAJOR.MINOR.PATCH`

**Desktop releases:**
```
desktop-v1.0.0 - First stable
desktop-v1.0.1 - Bug fix
desktop-v1.1.0 - New features
desktop-v2.0.0 - Major changes
```

**Web releases:**
```
web-v1.0.0 - First stable
web-v1.5.0 - New features
web-v2.0.0 - Major update
```

**Independent:** Desktop v1.0.0 != Web v1.0.0

---

## Download Statistics

### Tracking Downloads

**GitHub provides:**
- Download count per asset
- Download count per release
- Traffic analytics

**View:**
```
Repository → Insights → Traffic → Releases
```

**Useful for:**
- Understanding user base
- Platform distribution (Windows vs Mac vs Linux)
- Update adoption rates

---

## Summary

### Organized Release Structure

**Desktop releases:**
- Tags: `desktop-v*`
- Branch: `desktop-standalone`
- Artifacts: Installers for all platforms
- Naming: `NeuroInsight-Desktop-VERSION-OS-ARCH.ext`
- Auto-updates: Only checks desktop releases

**Web releases:**
- Tags: `web-v*`
- Branch: `web-app`
- Artifacts: Docker images, docs
- Separate versioning

**Benefits:**
```
✓ Clear separation
✓ Easy to find correct version
✓ Independent version numbers
✓ Automated builds
✓ Professional presentation
✓ Auto-update isolation
```

**User experience:**
```
Clinical user:
1. Goes to GitHub releases
2. Sees "Desktop v1.0.0" (clear label)
3. Downloads for their OS
4. No confusion with web releases

IT admin:
1. Goes to GitHub releases
2. Sees "Web v2.0.0" (clear label)
3. Gets Docker deployment files
4. No confusion with desktop releases
```

---

**All installers will be clearly separated and organized!**

