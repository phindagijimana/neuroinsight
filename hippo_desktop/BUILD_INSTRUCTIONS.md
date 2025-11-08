# Building NeuroInsight Desktop Installers

## Prerequisites

### On Your Build Machine

1. **Node.js 18+**
   ```bash
   node --version  # Should be 18.x or higher
   ```

2. **Dependencies installed**
   ```bash
   cd hippo_desktop
   npm install
   ```

3. **Platform-specific requirements**:
   - **Windows**: No special requirements
   - **macOS**: Xcode Command Line Tools
   - **Linux**: `fpm` for deb/rpm (optional)

---

## Build Commands

### Build for Current Platform Only
```bash
cd hippo_desktop
npm run dist
```

**Output**: `hippo_desktop/dist/`
- Creates installer for your current OS
- Fastest option for testing

### Build for Specific Platform

**Windows Installer:**
```bash
npm run dist:win
```
Output: `NeuroInsight-Setup-1.0.5.exe` (~150MB)

**macOS DMG:**
```bash
npm run dist:mac
```
Output: `NeuroInsight-1.0.5.dmg` (~150MB)

**Linux Packages:**
```bash
npm run dist:linux
```
Output:
- `NeuroInsight-1.0.5.AppImage` (universal)
- `neuroinsight_1.0.5_amd64.deb` (Ubuntu/Debian)
- `neuroinsight-1.0.5.x86_64.rpm` (Fedora/RHEL)

### Build for All Platforms
```bash
npm run dist -- --mac --win --linux
```
⚠️ **Note**: Cross-platform builds have limitations:
- Can't build macOS installers on Windows/Linux
- Can build Windows installers on macOS/Linux (with wine)
- Can build Linux on any platform

---

## What Gets Built

### Application Size
- **Electron app**: ~150MB (includes Node.js runtime)
- **Docker images** (downloaded on first run):
  - FastSurfer: ~15GB
  - PostgreSQL: ~350MB
  - Redis: ~50MB
  - MinIO: ~100MB
  - **Total first download**: ~15GB

### What's Included in Installer
```
NeuroInsight-Setup.exe (150MB)
├── Electron runtime
├── Application code (src/)
├── Icons and assets
├── Docker Compose files
└── Setup scripts
```

### What's Downloaded Later
- Docker Desktop (if not installed)
- Container images (~15GB, one-time)

---

## Testing the Build

### 1. Install on Clean System
- Use a VM or fresh machine
- Verify Docker Desktop installs correctly
- Check first-run experience

### 2. Check System Requirements Detection
The app checks:
- CPU cores (minimum 4)
- RAM (minimum 16GB)
- Disk space (minimum 30GB)
- Docker availability

### 3. Verify Core Functions
- Upload MRI scan
- Process scan (check both CPU and GPU modes)
- View results
- Export data
- System tray controls

---

## Distribution Options

### Option 1: GitHub Releases (Recommended)

**Manual Upload:**
1. Create release on GitHub:
   ```bash
   git tag -a v1.0.5 -m "Release v1.0.5"
   git push origin v1.0.5
   ```

2. Upload installers to release page
3. Users download from: `https://github.com/yourusername/neuroinsight/releases`

**Automatic (GitHub Actions):**
- Already configured in `.github/workflows/build.yml`
- Push a tag → installers build automatically
- ~20 minutes build time
- All platforms built in parallel

### Option 2: Self-Hosted

**Web Server:**
```bash
# Upload to your server
scp dist/NeuroInsight-Setup-*.exe user@yourserver.com:/var/www/downloads/

# Create download page
https://yoursite.com/downloads
├── NeuroInsight-Setup-1.0.5.exe
├── NeuroInsight-1.0.5.dmg
└── NeuroInsight-1.0.5.AppImage
```

### Option 3: Professional Distribution

**For wider distribution, consider:**

1. **Code Signing** (removes "unknown publisher" warnings)
   - **Windows**: Get Authenticode certificate (~$200/year)
   - **macOS**: Apple Developer account ($99/year)
   - Update `package.json` with certificate info

2. **Auto-Updates**
   - Add `electron-updater` to check for updates
   - Host update manifest on your server
   - App notifies users of new versions

3. **Analytics** (optional)
   - Add anonymous usage tracking
   - Track crash reports
   - Monitor adoption

---

## Build Troubleshooting

### "ENOENT: no such file or directory"
**Cause**: Missing icons or assets
**Fix**:
```bash
cd hippo_desktop
ls build/icon.icns  # macOS icon should exist
ls build/icon.ico   # Windows icon should exist
ls build/icons/     # Linux icons should exist
```

### "Cannot build for macOS on Windows"
**Cause**: macOS builds require macOS or CI
**Fix**: Use GitHub Actions or build on a Mac

### "Code signing failed"
**Cause**: No code signing certificate configured
**Fix**: Either:
- Get a certificate and configure it
- Disable signing: `package.json` → `"sign": null`

### Build is Very Slow
**Normal**: First build downloads dependencies (~200MB)
**Faster builds**: Subsequent builds use cache

---

## Recommended Build Process

### For Testing (Quick)
```bash
# Build for your platform only
npm run dist
```

### For Release (Complete)
```bash
# 1. Update version
npm version patch  # or minor, or major

# 2. Commit changes
git add package.json package-lock.json
git commit -m "Bump version to 1.0.6"

# 3. Create tag
git tag -a v1.0.6 -m "Release v1.0.6 - Bug fixes"

# 4. Push
git push && git push --tags

# 5. GitHub Actions builds automatically
# Check: https://github.com/yourusername/neuroinsight/actions

# 6. Download from Releases tab when done
```

---

## Advanced: Custom Branding

### Change App Name
Edit `package.json`:
```json
{
  "name": "your-app-name",
  "productName": "Your Product Name",
  "build": {
    "appId": "com.yourcompany.yourapp"
  }
}
```

### Custom Icons
Replace:
- `build/icon.icns` (macOS)
- `build/icon.ico` (Windows)
- `build/icons/*.png` (Linux)

See `ICON_GUIDE.md` for icon creation.

### Custom Installer
- **Windows**: Edit `nsis` section in `package.json`
- **macOS**: Edit `dmg` section
- **Linux**: Edit `linux` section

---

## Size Optimization

### Reduce App Size
Currently ~150MB. Hard to reduce much because:
- Electron runtime: ~80MB (required)
- Node modules: ~50MB
- Your code: ~20MB

### Reduce Download Size
The 15GB Docker images are the main size concern:
- **Can't reduce much**: FastSurfer model is inherently large
- **One-time download**: Cached after first install
- **Consider**: Cloud processing option for users with slow internet

---

## Next Steps

1. ✅ Build installer: `npm run dist`
2. ✅ Test on clean system
3. ✅ Create GitHub release
4. 📢 Share download link with users
5. 📊 Gather feedback
6. 🔄 Iterate and release updates

**Questions?** Check the main README.md or open an issue.


