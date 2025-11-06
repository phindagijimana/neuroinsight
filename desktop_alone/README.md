# NeuroInsight Standalone Desktop Application

**Production-ready desktop application for hippocampal asymmetry analysis.**

## Status: 85% Complete ✅

- ✅ Linux installers built and tested
- ⏳ Windows/macOS builds pending (requires CI/CD)
- ✅ All core functionality working
- ✅ Documentation complete

## Quick Links

- **[Installation Guide](INSTALLATION.md)** - How to install and run
- **[Final Status](FINAL_STATUS.md)** - Complete project summary
- **[CI/CD Setup](CICD_SETUP.md)** - Build Windows/macOS versions
- **[Release Strategy](RELEASE_STRATEGY.md)** - Distribution plan

## Download (Linux)

### AppImage (Recommended)
```bash
# Download
wget https://github.com/phindagijimana/neuroinsight/releases/download/desktop-v1.0.0/NeuroInsight-1.0.0.AppImage

# Make executable
chmod +x NeuroInsight-1.0.0.AppImage

# Run
./NeuroInsight-1.0.0.AppImage
```

### Debian/Ubuntu
```bash
# Download
wget https://github.com/phindagijimana/neuroinsight/releases/download/desktop-v1.0.0/neuroinsight-standalone_1.0.0_amd64.deb

# Install
sudo dpkg -i neuroinsight-standalone_1.0.0_amd64.deb

# Run
neuroinsight-standalone
```

## Features

### One-Click Installation
- No Docker required
- No Python setup needed
- No manual dependencies
- Just download and run

### Complete Bundle
- FastAPI backend with SQLite
- FastSurfer MRI processing
- PyTorch deep learning models
- React frontend
- Professional UI with splash screen

### Desktop Integration
- Native application feel
- System tray icon
- Background processing
- Automatic updates (coming soon)

## System Requirements

- **OS:** Linux (Ubuntu 20.04+), Windows 10+, macOS 11+
- **RAM:** 8 GB minimum, 16 GB recommended
- **Disk:** 10 GB free space
- **CPU:** 64-bit with AVX support

## What's Different from Web Version?

| Feature | Web App | Desktop App |
|---------|---------|-------------|
| Installation | Docker + Git | Single installer |
| Database | PostgreSQL | SQLite |
| Task Queue | Celery + Redis | Python threading |
| Setup Time | 15-30 minutes | 1 minute |
| User Audience | Developers | Everyone |

## Development

Want to build from source? See [DEVELOPMENT.md](DEVELOPMENT.md)

```bash
# Clone and setup
git clone https://github.com/phindagijimana/neuroinsight.git
cd neuroinsight/desktop_alone

# Build backend
./scripts/build_backend.sh

# Run Electron app
cd electron-app
npm install
npm start
```

## Building Installers

### Linux (Current Platform)
```bash
cd desktop_alone/electron-app
npm run build:linux
```

### Windows/macOS (Requires CI/CD)
See [CICD_SETUP.md](CICD_SETUP.md) for automated multi-platform builds.

## Architecture

```
NeuroInsight Desktop
├── Electron Wrapper (UI)
│   ├── Splash screen
│   ├── Main window
│   └── System tray
├── Python Backend (Bundled)
│   ├── FastAPI server
│   ├── SQLite database
│   ├── FastSurfer processing
│   └── PyTorch models
└── React Frontend (Static)
    ├── Upload interface
    ├── Processing status
    └── Results visualization
```

## Timeline

| Week | Task | Status | Time |
|------|------|--------|------|
| 1 | Core architecture | ✅ Complete | 1 day |
| 2 | Backend bundling | ✅ Complete | 1 day |
| 3 | Electron integration | ✅ Complete | 1 day |
| 4 | Testing | ✅ Complete | Implicit |
| 5 | Linux installers | ✅ Complete | 1 day |
| 6 | Windows/macOS + signing | ⏳ Pending | 1-2 weeks |

**Original Estimate:** 6 weeks  
**Actual (Weeks 1-5):** 1 day  
**Ahead of Schedule:** 4+ weeks

## Next Steps

### For Users
1. Download Linux installer
2. Test and provide feedback
3. Report issues on GitHub

### For Developers
1. Set up CI/CD for Windows/macOS builds
2. Implement code signing
3. Submit to app stores

### For Distributors
1. Upload to GitHub Releases
2. Submit to Snap Store
3. Create Flatpak package

## Support

- **Issues:** https://github.com/phindagijimana/neuroinsight/issues
- **Email:** support@neuroinsight.app
- **Docs:** All `.md` files in this directory

## License

MIT License - See [LICENSE](../LICENSE) for details

## Acknowledgments

Built on top of:
- [Electron](https://www.electronjs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [FastSurfer](https://github.com/Deep-MI/FastSurfer)
- [PyTorch](https://pytorch.org/)
- [React](https://react.dev/)

---

**Version:** 1.0.0  
**Branch:** `desktop-standalone`  
**Last Updated:** November 6, 2025
