# NeuroInsight Desktop

Professional desktop application for hippocampal asymmetry analysis.

## For End Users

**Download**: https://github.com/phindagijimana/neuroinsight/releases

See **QUICK_START.md** for installation instructions.

## For Developers

### Development

```bash
cd hippo_desktop
npm install
npm run dev
```

### Building Installers

```bash
npm run dist          # Current platform
npm run dist:mac      # macOS DMG
npm run dist:win      # Windows installer
npm run dist:linux    # Linux AppImage/deb/rpm
```

## Architecture

Electron application that manages Docker containers for the NeuroInsight web application.

### Components
- **Main Process** (`src/main.js`): Application lifecycle, Docker management
- **Renderer**: Loads NeuroInsight web UI
- **Docker Manager**: Auto-starts and manages services
- **System Tray**: Quick access menu

### How It Works

```
User launches app
  ↓
Check Docker Desktop
  ↓
Start services (docker-compose)
  ↓
Open NeuroInsight window
  ↓
Process MRI scans
```

## System Requirements

**Minimum**: 4 cores, 16GB RAM, 30GB disk
**Recommended**: 8+ cores, 32GB RAM, 100GB SSD, NVIDIA GPU

See QUICK_START.md for detailed requirements.

## Project Structure

```
hippo_desktop/
├── src/                  # Electron source
│   ├── main.js          # Main process
│   ├── preload.js       # IPC bridge
│   ├── managers/        # Docker & services
│   └── utils/           # System checks
├── assets/               # Icons
├── build/                # Platform icons
├── config/               # Configuration
├── package.json          # Build config
└── *.md                  # Documentation
```

## Building for Production

### Requirements
- Node.js 18+
- Docker Desktop (for testing)
- Icon files (already created in `build/`)

### Build Process

1. **Check requirements**:
   ```bash
   npm run check-requirements
   ```

2. **Build**:
   ```bash
   npm run dist
   ```

3. **Test installer** on clean system

4. **Upload to GitHub Releases** (or use GitHub Actions - automatic!)

## Automatic Builds (GitHub Actions)

The repository includes GitHub Actions workflow that automatically builds installers when you create a release tag:

```bash
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

Builds complete in ~15-20 minutes, installers uploaded automatically.

## Icons

All platform icons are in `build/`:
- `icon.icns` - macOS
- `icon.ico` - Windows
- `icons/*.png` - Linux (7 sizes)

See ICON_GUIDE.md for customization.

## Testing on HPC

**Note**: This desktop app requires a GUI environment. It cannot run on headless HPC servers. Test on a desktop/laptop machine with Docker Desktop.

## Customization

### App Name/Branding
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

### System Requirements
Edit `src/utils/SystemChecker.js`:
```javascript
this.requirements = {
  minCores: 4,
  minRamGB: 16,
  minDiskGB: 30
};
```

## Support

- **User Guide**: QUICK_START.md
- **Development**: DEVELOPMENT_GUIDE.md
- **Icon Creation**: ICON_GUIDE.md
- **Issues**: https://github.com/phindagijimana/neuroinsight/issues
