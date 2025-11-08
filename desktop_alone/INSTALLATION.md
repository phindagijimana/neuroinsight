# Installing NeuroInsight Desktop

**Version**: 1.1.0  
**Platforms**: Linux, Windows, macOS

---

## ⚠️ Security Warning Notice

When installing NeuroInsight, you'll see security warnings from your operating system. **This is normal and expected** for research software.

### Why This Happens

NeuroInsight is distributed without commercial code signing certificates, which cost $100-500 per year. As an open-source research project developed at an academic institution, we prioritize free availability over paid certificates.

### Is It Safe?

**YES!** NeuroInsight is safe to use:
- ✅ **Open Source**: Full source code available on GitHub for inspection
- ✅ **Checksum Verified**: Each release includes SHA256 checksums to detect tampering
- ✅ **Academic Software**: Developed for research use at medical institutions
- ✅ **No Telemetry**: All data stays on your computer, nothing sent externally
- ✅ **Trusted Platform**: Hosted on GitHub, a reputable platform

### Similar Software

Many trusted research tools distribute unsigned applications:
- FreeSurfer (brain MRI analysis)
- FSL (neuroimaging tools)
- SPM (statistical parametric mapping)
- 3D Slicer (medical image computing)

This is standard practice in academic software.

---

## 📥 Download

Get the latest release from GitHub:

**https://github.com/phindagijimana/neuroinsight/releases/latest**

Choose the file for your operating system:
- **Linux**: `NeuroInsight-1.0.0.AppImage` (~3.9 GB)
- **Windows**: `NeuroInsight-Setup-1.0.0.exe` (~4.0 GB)
- **macOS**: `NeuroInsight-1.0.0.dmg` (~4.0 GB)

---

## 🐧 Linux Installation

### Requirements
- **OS**: Linux x86_64 (Ubuntu 20.04+, CentOS 8+, Fedora, Debian, etc.)
- **RAM**: 8 GB minimum, 16 GB recommended
- **Disk**: 10 GB free space (for processing)
- **CPU**: 64-bit with AVX support
- **GPU**: Optional (NVIDIA with CUDA for faster processing)

### Installation Steps

1. **Download** the AppImage:
   ```bash
   wget https://github.com/phindagijimana/neuroinsight/releases/download/desktop-v1.1.0/NeuroInsight-1.0.0.AppImage
   ```

2. **Make it executable**:
   ```bash
   chmod +x NeuroInsight-1.0.0.AppImage
   ```

3. **Run the application**:
   ```bash
   ./NeuroInsight-1.0.0.AppImage
   ```

That's it! No installation needed.

### Optional: Add to Applications Menu

To add NeuroInsight to your applications menu:

```bash
# Copy to a permanent location
mv NeuroInsight-1.0.0.AppImage ~/Applications/

# Make it available in menu (optional)
./NeuroInsight-1.0.0.AppImage --appimage-extract
cp squashfs-root/neuroinsight.desktop ~/.local/share/applications/
```

### Verify Download (Recommended)

Check the SHA256 checksum:
```bash
sha256sum NeuroInsight-1.0.0.AppImage
```

Compare with `checksums-linux.txt` from the release.

Expected checksum:
```
0d23ef5aad88ce70c57bae0a233f899e75c9ed49f6a6d9c09a2cda7b6e44e7c0
```

---

## 🪟 Windows Installation

### Requirements
- **OS**: Windows 10 or Windows 11 (64-bit)
- **RAM**: 8 GB minimum, 16 GB recommended
- **Disk**: 10 GB free space (for processing)
- **CPU**: 64-bit Intel or AMD processor
- **GPU**: Optional (NVIDIA with CUDA for faster processing)

### Installation Steps

1. **Download** the installer:
   - Go to GitHub releases page
   - Download `NeuroInsight-Setup-1.0.0.exe`

2. **Run the installer**:
   - Double-click `NeuroInsight-Setup-1.0.0.exe`

3. **Handle SmartScreen warning**:
   
   ⚠️ You'll see: **"Windows protected your PC"**
   
   This is expected. To proceed:
   - Click **"More info"**
   - Click **"Run anyway"**
   
   ![Windows SmartScreen](https://via.placeholder.com/600x300?text=SmartScreen+More+Info)

4. **Follow installer prompts**:
   - Click "Next" through the installation wizard
   - Choose installation location (default is fine)
   - Click "Install"

5. **Launch NeuroInsight**:
   - From Start Menu
   - Or from Desktop shortcut

### Verify Download (Recommended)

In PowerShell:
```powershell
Get-FileHash NeuroInsight-Setup-1.0.0.exe -Algorithm SHA256
```

Compare with `checksums-windows.txt` from the release.

---

## 🍎 macOS Installation

### Requirements
- **OS**: macOS 10.13 (High Sierra) or later
- **RAM**: 8 GB minimum, 16 GB recommended
- **Disk**: 10 GB free space (for processing)
- **CPU**: Intel or Apple Silicon (M1/M2)
- **Architecture**: Universal binary (runs on both Intel and ARM)

### Installation Steps

1. **Download** the disk image:
   - Go to GitHub releases page
   - Download `NeuroInsight-1.0.0.dmg`

2. **Open the DMG**:
   - Double-click `NeuroInsight-1.0.0.dmg`
   - A window will open

3. **Install the app**:
   - Drag `NeuroInsight.app` to the `Applications` folder
   - Eject the DMG

4. **First launch - Handle Gatekeeper**:
   
   ⚠️ You'll see: **"NeuroInsight.app cannot be opened because the developer cannot be verified"**
   
   This is expected. To open the app:
   
   **Method 1** (Recommended):
   - Right-click (or Ctrl+click) on `NeuroInsight.app` in Applications
   - Select **"Open"** from the menu
   - Click **"Open"** in the dialog
   - The app will launch (only need to do this once)
   
   **Method 2** (Terminal):
   ```bash
   sudo xattr -rd com.apple.quarantine /Applications/NeuroInsight.app
   ```
   
   Then launch normally.

5. **Subsequent launches**:
   - Just double-click the app
   - No more warnings!

### Verify Download (Recommended)

In Terminal:
```bash
shasum -a 256 NeuroInsight-1.0.0.dmg
```

Compare with `checksums-mac.txt` from the release.

---

## 🚀 First Run

After installation, when you first launch NeuroInsight:

1. **Splash screen** appears (loading...)
2. **Main window** opens
3. **Three tabs** visible:
   - Jobs (upload & process scans)
   - Stats (view results)
   - Viewer (visualize overlays)

### Upload Your First Scan

1. Click **"Upload File"** button
2. Select a T1-weighted MRI scan:
   - `.nii` or `.nii.gz` (NIfTI format)
   - DICOM files (`.dcm`)
3. (Optional) Enter patient metadata
4. Click **"Process"**
5. Watch progress bar (5-10 min with GPU, 1-2 hours with CPU)
6. View results when complete!

---

## 🗂️ Where Are Files Stored?

### Linux
```
~/.config/neuroinsight/
├── neuroinsight.db         (Database)
├── data/                   (Uploaded scans & results)
└── logs/                   (Application logs)
```

### Windows
```
C:\Users\[YourUsername]\AppData\Roaming\neuroinsight\
├── neuroinsight.db         (Database)
├── data\                   (Uploaded scans & results)
└── logs\                   (Application logs)
```

### macOS
```
~/Library/Application Support/neuroinsight/
├── neuroinsight.db         (Database)
├── data/                   (Uploaded scans & results)
└── logs/                   (Application logs)
```

**Logs are useful for troubleshooting!**

Access logs:
- **Linux/macOS**: Press `Ctrl+L` or `Cmd+L`
- **Windows**: Press `Ctrl+L`
- Or: Help → View Logs

---

## 🔧 Troubleshooting

### App Won't Start

**Linux**:
```bash
# Check if FUSE is available
fusermount --version

# If not, extract and run manually:
./NeuroInsight-1.0.0.AppImage --appimage-extract
./squashfs-root/neuroinsight-standalone
```

**Windows**:
- Check antivirus isn't blocking it
- Run as Administrator (right-click → Run as administrator)
- Check Windows Defender exclusions

**macOS**:
- Try removing quarantine attribute:
  ```bash
  sudo xattr -rd com.apple.quarantine /Applications/NeuroInsight.app
  ```

### Processing Fails

Check:
- ✅ Input is T1-weighted MRI (not T2, FLAIR, etc.)
- ✅ File is valid NIfTI or DICOM
- ✅ At least 8 GB RAM available
- ✅ 10 GB free disk space
- ✅ Scan is not corrupted

View logs for detailed error:
- Help → View Logs
- Check `errors.log` for details

### Out of Memory

If processing fails with "out of memory":
- Close other applications
- Restart NeuroInsight
- Try on a machine with 16+ GB RAM
- Check logs: `~/.config/neuroinsight/logs/errors.log`

### Slow Processing

**With GPU**: 5-10 minutes  
**With CPU**: 1-2 hours

If taking longer:
- Check Task Manager/Activity Monitor (CPU should be high)
- Progress bar should show current step
- Be patient during "Running FastSurfer" stage (longest)

### App Crashes

1. Check logs: Help → View Logs
2. Look in `crashes.log` for details
3. Include log file when reporting issues

---

## 🆘 Getting Help

### Documentation
- **User Manual**: See [USER_MANUAL.md](USER_MANUAL.md)
- **Troubleshooting**: See [LOGS_AND_TROUBLESHOOTING.md](LOGS_AND_TROUBLESHOOTING.md)
- **Technical Details**: See repository README

### Support
- **GitHub Issues**: https://github.com/phindagijimana/neuroinsight/issues
- **Email**: neuroinsight@example.com
- **Response Time**: 1-3 business days

### When Reporting Issues

Please include:
1. **Your OS** and version
2. **NeuroInsight version**
3. **Steps to reproduce** the issue
4. **Log files** from `~/.config/neuroinsight/logs/`
   - Especially `errors.log` or `crashes.log`
5. **Error messages** you saw

To get log files:
- Press `Ctrl+L` / `Cmd+L` in the app
- Or: Help → View Logs
- Zip the `logs/` folder and attach to issue

---

## 🔄 Updating

### Check for Updates

NeuroInsight will notify you when updates are available (future feature).

For now, check GitHub releases manually:
- https://github.com/phindagijimana/neuroinsight/releases

### Install Update

**Linux**:
- Download new AppImage
- Replace old file
- Done!

**Windows**:
- Download new installer
- Run it (will upgrade existing installation)

**macOS**:
- Download new DMG
- Replace app in Applications folder

Your data is preserved (stored separately in config folder).

---

## 🗑️ Uninstalling

### Linux
```bash
# Just delete the AppImage
rm NeuroInsight-1.0.0.AppImage

# (Optional) Remove data
rm -rf ~/.config/neuroinsight/
```

### Windows
- Control Panel → Programs → Uninstall NeuroInsight
- (Optional) Delete: `C:\Users\[You]\AppData\Roaming\neuroinsight\`

### macOS
```bash
# Delete the app
rm -rf /Applications/NeuroInsight.app

# (Optional) Remove data
rm -rf ~/Library/Application\ Support/neuroinsight/
```

---

## 🔒 Privacy & Security

### Data Storage
- ✅ All data stored **locally** on your computer
- ✅ **No cloud storage** or external servers
- ✅ **No telemetry** or analytics
- ✅ **No internet connection** required (after installation)

### What NeuroInsight Does NOT Do
- ❌ Send your data anywhere
- ❌ Track your usage
- ❌ Collect personal information
- ❌ Require registration or login
- ❌ Display ads

### Open Source
- Full source code: https://github.com/phindagijimana/neuroinsight
- Inspect and audit anytime
- Contribute improvements

---

## 📜 License

NeuroInsight is open-source software licensed under [LICENSE TYPE].

See [LICENSE](../LICENSE) file for details.

---

## 🙏 Acknowledgments

NeuroInsight uses:
- **FastSurfer**: Brain segmentation (Henschel et al., 2020)
- **Electron**: Desktop framework
- **PyTorch**: Deep learning
- **FreeSurfer**: MRI analysis tools

Developed for research use at University of Rochester Medical Center.

---

**Last Updated**: November 2025  
**Version**: 1.1.0  
**Platform**: Linux, Windows, macOS
