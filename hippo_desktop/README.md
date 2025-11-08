# NeuroInsight Desktop Application

Electron-based desktop application for hippocampal asymmetry analysis.

---

## End Users

**Download:** [GitHub Releases](https://github.com/phindagijimana/neuroinsight/releases)

**Quick Start:** See [QUICK_START.md](QUICK_START.md)

---

## Developers

### Development Setup

```bash
cd hippo_desktop
npm install
npm run dev
```

### Building Installers

```bash
npm run dist          # Current platform
npm run dist:mac      # macOS DMG
npm run dist:win      # Windows NSIS/Portable
npm run dist:linux    # AppImage/deb/rpm
```

### Output

Installers created in `dist/` directory.

---

## Architecture

### Overview

Electron application managing Docker containers for NeuroInsight web application.

### Components

**Main Process** (`src/main.js`)
- Application lifecycle management
- Docker service orchestration
- System tray integration

**Renderer Process**
- Loads NeuroInsight web interface
- Displays processing status

**Docker Manager**
- Auto-starts required services
- Monitors container health

### Workflow

```
Launch Application
    ↓
Verify Docker Desktop
    ↓
Start Services (docker-compose)
    ↓
Load Web Interface
    ↓
Process MRI Scans
```

---

## System Requirements

**Minimum:**
- 4 CPU cores
- 16GB RAM
- 30GB disk space
- Docker Desktop

**Recommended:**
- 8+ CPU cores
- 32GB RAM
- 100GB SSD
- NVIDIA GPU (optional)

---

## Project Structure

```
hippo_desktop/
├── src/
│   ├── main.js           # Main process
│   ├── preload.js        # IPC bridge
│   ├── managers/         # Service managers
│   └── utils/            # System utilities
├── assets/               # Application assets
├── build/                # Platform-specific icons
├── config/               # Configuration files
└── package.json          # Build configuration
```

---

## Production Builds

### Prerequisites

- Node.js 18+
- Docker Desktop (for testing)
- Platform-specific icons (in `build/`)

### Build Process

1. **Verify requirements:**
   ```bash
   npm run check-requirements
   ```

2. **Build installer:**
   ```bash
   npm run dist
   ```

3. **Test on clean system**

4. **Distribute via GitHub Releases**

---

## Automated Builds

GitHub Actions automatically builds installers when release tags are pushed:

```bash
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

Installers uploaded to GitHub Releases automatically.

---

## Platform Support

### Icons

Platform-specific icons in `build/`:
- `icon.icns` - macOS
- `icon.ico` - Windows
- `icons/*.png` - Linux (multiple sizes)

See [ICON_GUIDE.md](ICON_GUIDE.md) for customization.

### Testing

**Note:** Desktop application requires GUI environment. Cannot run on headless servers.

Test on desktop/laptop with Docker Desktop installed.

---

## Customization

### Branding

Edit `package.json`:
```json
{
  "name": "application-name",
  "productName": "Application Display Name",
  "build": {
    "appId": "com.company.application"
  }
}
```

### System Requirements

Edit `src/utils/SystemChecker.js`:
```javascript
this.requirements = {
  minCores: 4,
  minRamGB: 16,
  minDiskGB: 30
};
```

---

## Documentation

- **User Guide:** [QUICK_START.md](QUICK_START.md)
- **Development:** [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- **Icon Creation:** [ICON_GUIDE.md](ICON_GUIDE.md)

---

## Support

**Issues:** [GitHub Issues](https://github.com/phindagijimana/neuroinsight/issues)

**Email:** support@neuroinsight.app

---

**Current Version:** 1.0.5  
**Last Updated:** November 2025
