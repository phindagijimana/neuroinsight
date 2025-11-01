# NeuroInsight Desktop

Desktop application for NeuroInsight - Advanced Hippocampal Asymmetry Analysis.

## Overview

This folder contains the desktop application version of NeuroInsight, packaged as a standalone application similar to 3D Slicer. It uses Electron to provide a native desktop experience while running the web-based NeuroInsight application locally via Docker containers.

## Architecture

```
┌─────────────────────────────────────┐
│   Electron Shell (Native App)       │
│   - Window management               │
│   - System tray                     │
│   - Auto-start Docker               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Docker Desktop                     │
│   ┌───────────────────────────────┐ │
│   │ PostgreSQL                    │ │
│   │ Redis                         │ │
│   │ MinIO                         │ │
│   │ FastAPI Backend               │ │
│   │ Celery Worker                 │ │
│   │ React Frontend                │ │
│   └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

## System Requirements

### Minimum Requirements
- **OS**: Windows 10 (64-bit), macOS 10.15+, or Ubuntu 20.04+
- **CPU**: 4 cores (Intel i5/AMD Ryzen 5 or better)
- **RAM**: 16GB
- **Storage**: 30GB free space
- **Docker Desktop**: Required (will be installed during setup)

### Recommended Requirements
- **CPU**: 8+ cores
- **RAM**: 32GB
- **Storage**: 100GB SSD
- **GPU**: NVIDIA GPU with 8GB+ VRAM (for 10-20x faster processing)

## Development Setup

### Prerequisites

1. Install Node.js 18+ and npm
2. Install Docker Desktop

### Installation

```bash
# Navigate to hippo_desktop folder
cd hippo_desktop

# Install dependencies
npm install

# Run in development mode
npm run dev
```

### Building

```bash
# Build for current platform
npm run dist

# Build for specific platforms
npm run dist:mac      # macOS (DMG + ZIP)
npm run dist:win      # Windows (NSIS installer + portable)
npm run dist:linux    # Linux (AppImage, deb, rpm)
```

## Project Structure

```
hippo_desktop/
├── src/
│   ├── main.js                 # Main Electron process
│   ├── preload.js              # IPC bridge
│   ├── setup.html              # First-run setup wizard
│   ├── managers/
│   │   ├── DockerManager.js    # Docker Desktop integration
│   │   └── ServiceManager.js   # Service orchestration
│   └── utils/
│       ├── SystemChecker.js    # Requirements checking
│       └── logger.js           # Logging utility
├── assets/
│   ├── icon.png                # App icon
│   ├── tray-icon.png           # System tray icon
│   └── dmg-background.png      # macOS DMG background
├── build/
│   ├── icon.icns               # macOS icon
│   ├── icon.ico                # Windows icon
│   ├── icons/                  # Linux icons (various sizes)
│   └── entitlements.mac.plist  # macOS code signing
├── installers/
│   ├── windows/
│   │   └── installer.nsh       # NSIS installer script
│   └── macos/
│       └── dmg-spec.json       # DMG configuration
├── scripts/
│   ├── check-requirements.js   # Pre-install checker
│   └── setup.js                # Post-install setup
├── config/
│   └── env.template            # Environment template
├── package.json                # npm configuration
└── README.md                   # This file
```

## Key Features

### 🚀 Easy Installation
- One-click installer for Windows, macOS, and Linux
- Automatic Docker Desktop integration
- First-run setup wizard
- System requirements checking

### 🎯 User-Friendly
- Native desktop application (not a browser window)
- System tray icon for quick access
- Auto-start on login (optional)
- Desktop shortcut

### 🔧 Service Management
- Automatic Docker container management
- Health monitoring
- One-click restart
- Log viewer

### 📊 Performance
- GPU acceleration support (10-20x faster)
- Optimized for minimum system requirements
- Background processing

### 🔒 Privacy
- Fully local processing (no cloud)
- No internet required after installation
- Data stays on your machine

## Distribution

### Creating Installers

The build process creates platform-specific installers:

#### macOS
- **DMG**: Drag-and-drop installer with custom background
- **ZIP**: Portable version
- **Architectures**: x64 (Intel) and arm64 (Apple Silicon)

```bash
npm run dist:mac
# Output: dist/NeuroInsight-1.0.0.dmg
#         dist/NeuroInsight-1.0.0-mac.zip
```

#### Windows
- **NSIS Installer**: Traditional Windows installer with wizard
- **Portable**: Standalone .exe (no installation required)

```bash
npm run dist:win
# Output: dist/NeuroInsight Setup 1.0.0.exe
#         dist/NeuroInsight 1.0.0.exe (portable)
```

#### Linux
- **AppImage**: Universal Linux package (works everywhere)
- **deb**: Debian/Ubuntu package
- **rpm**: Red Hat/Fedora package

```bash
npm run dist:linux
# Output: dist/NeuroInsight-1.0.0.AppImage
#         dist/neuroinsight_1.0.0_amd64.deb
#         dist/neuroinsight-1.0.0.x86_64.rpm
```

### Code Signing (for production)

#### macOS
1. Get an Apple Developer account
2. Create certificates in Xcode
3. Set environment variables:
```bash
export CSC_LINK=/path/to/certificate.p12
export CSC_KEY_PASSWORD=your_password
export APPLE_ID=your@email.com
export APPLE_APP_SPECIFIC_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

#### Windows
1. Get a code signing certificate
2. Set environment variables:
```bash
export CSC_LINK=/path/to/certificate.pfx
export CSC_KEY_PASSWORD=your_password
```

## Testing

### Pre-flight Checks

Before building, run the requirements checker:

```bash
npm run check-requirements
```

This will verify:
- ✓ Node.js version
- ✓ Docker Desktop installed
- ✓ Build tools available
- ✓ Code signing certificates (if configured)

### Manual Testing

1. **Development Mode**:
```bash
npm run dev
```

2. **Packaged Mode** (without installer):
```bash
npm run pack
# Test from: dist/mac/NeuroInsight.app (macOS)
#           dist/win-unpacked/NeuroInsight.exe (Windows)
```

3. **Full Installer**:
```bash
npm run dist
# Install and test the actual installer
```

## Deployment

### Release Checklist

- [ ] Update version in `package.json`
- [ ] Test on all platforms
- [ ] Update `CHANGELOG.md`
- [ ] Create git tag
- [ ] Build installers for all platforms
- [ ] Code sign applications
- [ ] Test installers on clean systems
- [ ] Upload to distribution server
- [ ] Update auto-updater configuration
- [ ] Announce release

### Auto-Updates

Auto-update configuration can be added using `electron-updater`:

```javascript
// In main.js
const { autoUpdater } = require('electron-updater');

autoUpdater.checkForUpdatesAndNotify();
```

## Troubleshooting

### Docker Not Starting

**Error**: "Docker Desktop is not running"

**Solution**:
1. Install Docker Desktop from https://docker.com
2. Start Docker Desktop manually
3. Restart NeuroInsight

### Insufficient Memory

**Error**: "Not enough RAM"

**Solution**:
- Close other applications
- Upgrade to 16GB+ RAM
- Use Docker Desktop memory settings to limit usage

### Build Errors

**Error**: "Cannot find module 'electron'"

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

## Support

- **Issues**: https://github.com/neuroinsight/desktop/issues
- **Docs**: https://neuroinsight.app/docs
- **Email**: support@neuroinsight.app

## License

See LICENSE file in project root.

## Credits

Built with:
- [Electron](https://www.electronjs.org/)
- [Docker](https://www.docker.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [FastSurfer](https://deep-mi.org/research/fastsurfer/)


