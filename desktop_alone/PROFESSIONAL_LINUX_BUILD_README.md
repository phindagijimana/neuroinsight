# NeuroInsight Professional Linux Build System

This document describes the professional Linux packaging system for NeuroInsight, providing multiple installation formats for maximum compatibility across Linux distributions.

## 🎯 Overview

The NeuroInsight Linux build system creates **four different package formats** to ensure users on any Linux distribution can install the application with a **single click**:

1. **AppImage** - Universal portable format (works on most Linux distros)
2. **DEB packages** - Native Debian/Ubuntu installer
3. **RPM packages** - Native RedHat/Fedora installer
4. **Flatpak** - Modern sandboxed cross-distribution format

## 🚀 Quick Start

### Prerequisites

```bash
# Install Node.js (required)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install electron-builder globally
sudo npm install -g electron-builder

# Optional: Install Flatpak for Flatpak builds
sudo apt install flatpak flatpak-builder
```

### Build All Packages

```bash
cd desktop_alone
./scripts/build_linux_installers.sh
```

This single command will:
- ✅ Check all prerequisites
- ✅ Install Node.js dependencies
- ✅ Build all four package formats
- ✅ Generate installation guide

## 📦 Package Formats Explained

### AppImage (Recommended for Universal Compatibility)

**Best for:** Users who want a portable, no-installation solution

```bash
# Just make executable and run
chmod +x NeuroInsight-*.AppImage
./NeuroInsight-*.AppImage
```

**Pros:**
- Works on any Linux distribution
- No installation required
- Portable (can run from USB drives)
- Self-contained with all dependencies

**Cons:**
- Slightly larger file size
- Not integrated with system package manager

### DEB Packages (Recommended for Debian/Ubuntu)

**Best for:** Ubuntu, Debian, Linux Mint users

```bash
# Double-click the .deb file or use:
sudo dpkg -i neuroinsight_*_amd64.deb
sudo apt-get install -f  # Fix dependencies
```

**Pros:**
- Native system integration
- Automatic dependency management
- Easy uninstallation
- System updates integration

### RPM Packages (Recommended for RedHat/Fedora)

**Best for:** Fedora, CentOS, RHEL, SUSE users

```bash
# Use package manager
sudo dnf install neuroinsight-*.x86_64.rpm
# or
sudo rpm -i neuroinsight-*.x86_64.rpm
```

### Flatpak (Recommended for Modern Linux)

**Best for:** Users wanting sandboxed, modern packaging

```bash
# Install Flatpak first
sudo apt install flatpak  # Ubuntu/Debian
sudo dnf install flatpak  # Fedora

# Install NeuroInsight
flatpak install neuroinsight-*.flatpak
```

**Pros:**
- Sandboxed (enhanced security)
- Automatic updates
- Cross-distribution compatibility
- Modern packaging standard

## 🏗️ Build System Architecture

### Directory Structure

```
desktop_alone/
├── electron-app/           # Main Electron application
│   ├── package.json       # Updated with multi-format config
│   ├── scripts/           # Post-install scripts
│   │   ├── postinst.sh    # Post-installation setup
│   │   └── postrm.sh      # Post-removal cleanup
│   ├── build/
│   │   └── flatpak/       # Flatpak manifest
│   └── dist/              # Output directory
└── scripts/
    └── build_linux_installers.sh  # Main build script
```

### Build Process

1. **Preparation**: Check prerequisites and install dependencies
2. **Electron Build**: Use electron-builder to create base application
3. **Packaging**: Generate AppImage, DEB, RPM, and Flatpak packages
4. **Documentation**: Create installation guides and checksums

## 🛠️ Manual Build Options

### Build Specific Formats

```bash
cd desktop_alone/electron-app

# AppImage only
npx electron-builder --linux AppImage

# DEB only
npx electron-builder --linux deb

# RPM only
npx electron-builder --linux rpm

# Flatpak only
npx electron-builder --linux flatpak
```

### Custom Build Configuration

Edit `electron-app/package.json` to customize:

- Package dependencies
- Desktop integration
- File associations
- Build targets

## 📋 System Requirements

### Build System Requirements

- **Node.js**: 16.x or higher
- **Python**: 3.8+ (for backend)
- **System Dependencies**:
  ```bash
  sudo apt install build-essential libnss3-dev libatk-bridge2.0-dev libdrm2-dev libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2
  ```

### Runtime Requirements

- **OS**: Linux (kernel 3.10+)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **Graphics**: OpenGL 2.0+ compatible GPU

## 🔍 Troubleshooting

### Build Issues

**Missing dependencies:**
```bash
# Install all required system packages
sudo apt install build-essential libnss3-dev libatk-bridge2.0-dev libdrm2-dev libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2
```

**Flatpak build fails:**
```bash
# Install Flatpak and add Flathub
sudo apt install flatpak flatpak-builder
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
```

### Runtime Issues

**AppImage won't start:**
```bash
# Check if executable
ls -la NeuroInsight-*.AppImage
chmod +x NeuroInsight-*.AppImage

# Check missing libraries
ldd NeuroInsight-*.AppImage
```

**Package installation fails:**
```bash
# Clean package cache
sudo apt clean && sudo apt autoclean
sudo apt update

# For DEB
sudo dpkg --configure -a
sudo apt-get install -f
```

## 📊 Distribution Strategy

### Recommended Approach

1. **Primary**: Provide AppImage for universal compatibility
2. **Secondary**: DEB/RPM packages for major distributions
3. **Tertiary**: Flatpak for modern Linux users

### Hosting and Distribution

- **GitHub Releases**: Upload all package formats
- **Website**: Provide download links with system detection
- **Package Repositories**: Submit to official repos (future)

## 🔐 Security Considerations

- All packages are code-signed (when certificates are available)
- Flatpak provides sandboxing
- AppImage includes integrity verification
- DEB/RPM packages follow system security policies

## 📈 Performance Optimization

- Packages include optimized binaries
- Minimal runtime dependencies
- Compressed assets
- Lazy loading where possible

## 🐛 Testing

### Automated Testing

```bash
# Run the smoke test
cd ../..
python tests/smoke_test.py --backend-exe dist/neuroinsight-backend/neuroinsight-backend
```

### Manual Testing

1. Install each package format
2. Test basic functionality
3. Verify file operations
4. Check system integration

## 📚 Additional Resources

- [Electron Builder Documentation](https://www.electron.build/)
- [AppImage Documentation](https://docs.appimage.org/)
- [Flatpak Documentation](https://docs.flatpak.org/)
- [Linux Package Guidelines](https://refspecs.linuxfoundation.org/)

## 🤝 Contributing

When modifying the build system:

1. Test all package formats
2. Update this documentation
3. Verify on multiple Linux distributions
4. Update version numbers appropriately

---

**Built with ❤️ for the scientific community**

For support: support@neuroinsight.app
GitHub: https://github.com/phindagijimana/neuroinsight
