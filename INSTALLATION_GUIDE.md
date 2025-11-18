# NeuroInsight Professional Linux Installation Guide

## Available Packages

### 1. AppImage (Universal)
**File:** `NeuroInsight-*.AppImage`
**Installation:** None required - just make executable and run
**Compatibility:** Works on most Linux distributions

```bash
chmod +x NeuroInsight-*.AppImage
./NeuroInsight-*.AppImage
```

### 2. DEB Package (Debian/Ubuntu)
**File:** `neuroinsight_*_amd64.deb`
**Installation:** Double-click or use package manager

```bash
sudo dpkg -i neuroinsight_*_amd64.deb
sudo apt-get install -f  # Fix any dependencies
```

### 3. RPM Package (RedHat/Fedora)
**File:** `neuroinsight-*.x86_64.rpm`
**Installation:** Use package manager

```bash
sudo rpm -i neuroinsight-*.x86_64.rpm
# or
sudo dnf install neuroinsight-*.x86_64.rpm
```

### 4. Flatpak (Modern Cross-Distribution)
**File:** `neuroinsight-*.flatpak`
**Installation:** Requires Flatpak to be installed

```bash
# Install Flatpak first (if not installed)
sudo apt install flatpak  # Ubuntu/Debian
sudo dnf install flatpak  # Fedora

# Add Flathub repository
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Install NeuroInsight
flatpak install neuroinsight-*.flatpak
```

## System Requirements

- **OS:** Linux (Ubuntu 18.04+, Fedora 30+, or compatible)
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 10GB free space
- **Graphics:** OpenGL compatible GPU

## Post-Installation

After installation, NeuroInsight will:
- Create desktop shortcut
- Set up user directories in `~/Documents/NeuroInsight/`
- Configure proper file permissions

## Troubleshooting

### AppImage Issues
```bash
# Make sure AppImage is executable
chmod +x NeuroInsight-*.AppImage

# If it doesn't start, check dependencies
ldd NeuroInsight-*.AppImage
```

### Package Installation Issues
```bash
# For DEB packages
sudo apt-get update
sudo apt-get install -f

# For RPM packages
sudo dnf check-update
sudo dnf install --refresh neuroinsight-*.rpm
```

### Permission Issues
```bash
# Fix permissions for user directories
chmod -R 755 ~/Documents/NeuroInsight/
```

## Support

For issues or questions:
- Email: support@neuroinsight.app
- GitHub: https://github.com/phindagijimana/neuroinsight

---
Built on: $(date)
Version: 1.3.14
