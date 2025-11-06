# Installation Guide

## Linux Installation

### AppImage (Recommended)

1. **Download** `NeuroInsight-1.0.0.AppImage`
2. **Make executable:**
   ```bash
   chmod +x NeuroInsight-1.0.0.AppImage
   ```
3. **Run:**
   ```bash
   ./NeuroInsight-1.0.0.AppImage
   ```

The AppImage is self-contained and requires no installation.

### Debian/Ubuntu Package

1. **Download** `neuroinsight-standalone_1.0.0_amd64.deb`
2. **Install:**
   ```bash
   sudo dpkg -i neuroinsight-standalone_1.0.0_amd64.deb
   ```
3. **Run from application menu** or:
   ```bash
   neuroinsight-standalone
   ```

## Windows Installation

1. **Download** `NeuroInsight-Setup-1.0.0.exe`
2. **Run installer** (double-click)
3. **Follow setup wizard**
4. **Launch from Start Menu**

Note: Windows may show SmartScreen warning for unsigned apps. Click "More info" → "Run anyway"

## macOS Installation

### DMG (Universal)

1. **Download** `NeuroInsight-1.0.0.dmg`
2. **Open DMG file**
3. **Drag NeuroInsight to Applications folder**
4. **Launch from Applications**

First launch:
- Right-click app → "Open" (for unsigned apps)
- Or: System Preferences → Security & Privacy → "Open Anyway"

## Verify Installation

After installation, verify checksums:

### Linux
```bash
sha256sum -c checksums-linux.txt
```

### Windows (PowerShell)
```powershell
Get-FileHash NeuroInsight-Setup-1.0.0.exe -Algorithm SHA256
```

### macOS
```bash
shasum -a 256 NeuroInsight-1.0.0.dmg
```

## System Requirements

- **OS:** Linux (Ubuntu 20.04+), Windows 10+, macOS 11+
- **RAM:** 8 GB minimum, 16 GB recommended
- **Disk:** 10 GB free space
- **CPU:** 64-bit processor with AVX support

## Troubleshooting

### Linux: AppImage won't run
```bash
# Install FUSE (if needed)
sudo apt install libfuse2  # Ubuntu/Debian
sudo dnf install fuse-libs  # Fedora/RHEL
```

### Windows: SmartScreen warning
This appears for unsigned applications. The app is safe to run.

### macOS: "damaged" error
```bash
# Clear quarantine attribute
xattr -cr /Applications/NeuroInsight.app
```

### App won't start
Check logs:
- **Linux:** `~/.config/NeuroInsight/logs/`
- **Windows:** `%APPDATA%\NeuroInsight\logs\`
- **macOS:** `~/Library/Logs/NeuroInsight/`

## First Run

1. **Launch app** - splash screen appears during startup
2. **Wait 10-30 seconds** for backend initialization
3. **Main window opens** automatically
4. **Upload MRI scan** to start analysis

## Updates

The app will notify you of new versions. Download and install as above.

## Uninstallation

### Linux AppImage
Simply delete the `.AppImage` file.

### Linux DEB
```bash
sudo apt remove neuroinsight-standalone
```

### Windows
Settings → Apps → NeuroInsight → Uninstall

### macOS
Drag app from Applications to Trash.

## Support

- Issues: https://github.com/phindagijimana/neuroinsight/issues
- Email: support@neuroinsight.app

