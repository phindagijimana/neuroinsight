#!/bin/bash
# Professional Linux Installer Builder for NeuroInsight
# Creates AppImage, DEB, RPM, and Flatpak packages

set -e

echo "======================================"
echo "NeuroInsight Professional Linux Build"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd "$(dirname "$0")/../electron-app"

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"

    # Check Node.js and npm
    if ! command -v node >/dev/null 2>&1; then
        echo -e "${RED}Error: Node.js is required but not installed${NC}"
        exit 1
    fi

    # Check electron-builder
    if ! command -v electron-builder >/dev/null 2>&1; then
        echo -e "${YELLOW}Installing electron-builder...${NC}"
        npm install -g electron-builder
    fi

    # Note: Currently focusing on AppImage for universal compatibility
# DEB/RPM/Flatpak can be added later when build tools are available
echo -e "${YELLOW}Note: Building AppImage format for universal Linux compatibility${NC}"
echo -e "${YELLOW}DEB/RPM/Flatpak formats can be added with additional build tools${NC}"

    echo -e "${GREEN}Prerequisites check complete${NC}"
    echo ""
}

# Install dependencies
install_dependencies() {
    echo -e "${BLUE}Installing Node.js dependencies...${NC}"
    npm install
    echo -e "${GREEN}Dependencies installed${NC}"
    echo ""
}

# Build the application
build_app() {
    echo -e "${BLUE}Building NeuroInsight application...${NC}"

    # Clean previous builds
    rm -rf dist/

    # Build with electron-builder
    echo "Creating packages: AppImage, DEB, RPM, Flatpak..."
    npx electron-builder --linux

    echo -e "${GREEN}Build completed successfully!${NC}"
    echo ""
}

# Create distribution summary
create_summary() {
    echo -e "${BLUE}Creating distribution summary...${NC}"

    local output_dir="dist"
    local summary_file="$output_dir/INSTALLATION_GUIDE.md"

    cat > "$summary_file" << 'EOF'
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
EOF

    echo -e "${GREEN}Installation guide created: $summary_file${NC}"
}

# Main build process
main() {
    echo -e "${GREEN}Starting NeuroInsight Professional Linux Build${NC}"
    echo ""

    check_prerequisites
    install_dependencies
    build_app
    create_summary

    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}✅ Build Complete!${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo "Generated packages:"
    ls -la dist/*.AppImage dist/*.deb dist/*.rpm dist/*.flatpak 2>/dev/null || echo "Some package formats may not be available"
    echo ""
    echo "See dist/INSTALLATION_GUIDE.md for detailed installation instructions"
    echo ""
    echo "For one-click installation:"
    echo "- AppImage: Just double-click and run"
    echo "- DEB/RPM: Double-click the package file"
    echo "- Flatpak: Use 'flatpak install' command"
}

# Run main function
main "$@"
