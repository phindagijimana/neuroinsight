# Building NeuroInsight Windows Installer

## Prerequisites

### Required Software (Windows Machine)
- **Windows 10/11** (64-bit)
- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Git** (with Git LFS support)
- **PowerShell** (built-in on Windows)

### Optional (for full functionality)
- **Docker Desktop for Windows**

## Build Process

### Option 1: Automated Script (Recommended)

1. **Clone/download the repository** to a Windows machine
2. **Open PowerShell as Administrator**
3. **Navigate to the project directory**
4. **Run the build script**:
   ```powershell
   .\build-windows-installer.ps1
   ```

The script will:
- ✅ Check prerequisites
- ✅ Install Python dependencies
- ✅ Build PyInstaller backend executable
- ✅ Install Electron dependencies
- ✅ Build NSIS installer (.exe)
- ✅ Generate SHA256 checksums
- ✅ Create installation documentation

### Option 2: Manual Build

If you prefer manual control:

```powershell
# 1. Install dependencies
pip install -r desktop_alone/requirements.txt
pip install pyinstaller requests

# 2. Build backend
cd desktop_alone
pyinstaller build.spec --clean --noconfirm

# 3. Build Electron app
cd electron-app
npm install
npm run build:win
```

## Output Files

After successful build, you'll find in `desktop_alone/electron-app/dist/`:

- `NeuroInsight-*.exe` - NSIS installer (main file)
- `checksums-windows.txt` - SHA256 checksums
- `README-Windows.md` - Installation guide
- `builder-debug.yml` - Build log

## Testing the Installer

### On Clean Windows Machine:
1. Copy the `.exe` installer to a test machine
2. Run the installer (may require admin privileges)
3. Test with sample MRI data
4. Verify Docker detection works

### Test Scenarios:
- ✅ **With Docker**: Full FastSurfer functionality
- ✅ **Without Docker**: Smoke mode fallback
- ✅ **Different Windows versions**: Win10, Win11
- ✅ **Antivirus compatibility**: May flag as unknown publisher

## Distribution

### GitHub Releases:
1. Go to repository → Releases → Create new release
2. Upload the installer `.exe` file
3. Include checksums and README
4. Add release notes

### File Structure for Distribution:
```
NeuroInsight-v1.3.14-Windows/
├── NeuroInsight-Setup-1.3.14.exe
├── checksums-windows.txt
└── README-Windows.md
```

## Troubleshooting

### Common Issues:

**"Execution Policy" Error in PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**PyInstaller Build Fails:**
- Ensure all Python dependencies installed
- Check antivirus isn't blocking
- Try running as Administrator

**Electron Build Fails:**
- Clear npm cache: `npm cache clean --force`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version`

**Large File Sizes:**
- Backend executable: ~200-300MB (expected due to PyTorch)
- Complete installer: ~1-2GB (includes all dependencies)

### Build Time:
- **Total time**: 15-30 minutes
- **Backend build**: 5-10 minutes
- **Electron build**: 5-15 minutes
- **Disk space needed**: 10GB free

## Security Considerations

### Code Signing (Optional but Recommended):
For production distribution, consider:
- **Windows Code Signing Certificate** ($200-500/year)
- **EV Certificate** for Microsoft SmartScreen bypass
- **Timestamping** to prevent expiration

### Without Code Signing:
- Users will see "Unknown Publisher" warning
- SmartScreen may block initial download
- Users can bypass by clicking "Run anyway"

## Advanced Configuration

### Custom Build Options:
Edit `desktop_alone/electron-app/package.json`:
```json
"win": {
  "target": "nsis",
  "certificateFile": "path/to/cert.p12",
  "certificatePassword": "cert_password"
}
```

### Environment Variables:
```powershell
$env:DEBUG="*"
$env:PYINSTALLER_VERBOSE="1"
```

## Support

If builds fail:
1. Check the `builder-debug.yml` log file
2. Verify all prerequisites are installed
3. Try on a different Windows machine
4. Check GitHub Issues for similar problems

---
**Last Updated**: November 15, 2025
**Tested On**: Windows 10/11, Python 3.9+, Node.js 18+
