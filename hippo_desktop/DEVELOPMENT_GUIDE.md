# NeuroInsight Desktop - Development Guide

## Complete Project Structure

```
hippo/
├── backend/              # FastAPI backend (existing)
├── frontend/             # React frontend (existing)
├── workers/              # Celery workers (existing)
├── pipeline/             # Processing pipeline (existing)
├── docker-compose.yml    # Service orchestration (existing)
│
└── hippo_desktop/        # ✨ NEW - Desktop application
    ├── package.json              # npm configuration & build settings
    ├── README.md                 # Desktop app documentation
    ├── QUICK_START.md            # User installation guide
    ├── DEVELOPMENT_GUIDE.md      # This file
    ├── .gitignore                # Git ignore rules
    │
    ├── src/                      # Electron application source
    │   ├── main.js               # Main process (app lifecycle)
    │   ├── preload.js            # IPC bridge (security)
    │   ├── setup.html            # First-run setup wizard
    │   │
    │   ├── managers/             # Service management
    │   │   ├── DockerManager.js  # Docker Desktop integration
    │   │   └── ServiceManager.js # Container orchestration
    │   │
    │   └── utils/                # Utilities
    │       ├── SystemChecker.js  # Requirements verification
    │       └── logger.js         # Winston logging
    │
    ├── assets/                   # Application assets
    │   ├── icon.png              # App icon (1024x1024)
    │   ├── tray-icon.png         # System tray icon
    │   └── dmg-background.png    # macOS DMG background
    │
    ├── build/                    # Build resources
    │   ├── icon.icns             # macOS icon
    │   ├── icon.ico              # Windows icon
    │   ├── icons/                # Linux icons (16-512px)
    │   ├── license.txt           # License for installer
    │   └── entitlements.mac.plist # macOS signing
    │
    ├── config/                   # Configuration
    │   └── env.template          # Environment template
    │
    ├── scripts/                  # Build/setup scripts
    │   ├── check-requirements.js # Pre-build checker
    │   └── setup.js              # Post-install setup
    │
    └── installers/               # Platform-specific configs
        ├── windows/
        │   └── installer.nsh     # NSIS installer script
        └── macos/
            └── dmg-spec.json     # DMG configuration
```

## Development Workflow

### 1. Initial Setup

```bash
# Navigate to hippo_desktop
cd hippo_desktop

# Install dependencies
npm install

# This will install:
# - Electron (desktop framework)
# - electron-builder (packaging)
# - dockerode (Docker API)
# - docker-compose (service orchestration)
# - systeminformation (system info)
# - winston (logging)
# - electron-store (settings persistence)
```

### 2. Development Mode

```bash
# Start in development mode
npm run dev

# This will:
# 1. Start Electron with DevTools open
# 2. Enable hot-reload
# 3. Point to localhost:5173 (existing Vite dev server)
# 4. Show verbose logging
```

### 3. Testing

```bash
# Test without creating installer
npm run pack

# This creates an unpacked version in dist/ folder
# Test the actual packaged app without going through full build

# macOS: dist/mac/NeuroInsight.app
# Windows: dist/win-unpacked/NeuroInsight.exe
# Linux: dist/linux-unpacked/neuroinsight
```

### 4. Building Installers

```bash
# Check build requirements first
npm run check-requirements

# Build for current platform
npm run dist

# Build for specific platforms
npm run dist:mac      # macOS DMG + ZIP
npm run dist:win      # Windows NSIS + Portable
npm run dist:linux    # AppImage + deb + rpm
```

## Key Concepts

### Electron Architecture

```
┌─────────────────────────────────────────┐
│         Main Process (Node.js)          │
│  - src/main.js                          │
│  - Full Node.js API access              │
│  - Window management                    │
│  - System integration                   │
│  - Docker management                    │
└────────────┬────────────────────────────┘
             │
             │ IPC (Inter-Process Communication)
             │
┌────────────▼────────────────────────────┐
│      Renderer Process (Chromium)        │
│  - Web content                          │
│  - Limited API access (security)        │
│  - React frontend                       │
│  - User interface                       │
└─────────────────────────────────────────┘
             ▲
             │ preload.js (Bridge)
             │ - Exposes safe APIs
             │ - window.electronAPI
```

### Service Management Flow

```
User launches app
    │
    ├─> Check system requirements
    │   ├─> CPU, RAM, Disk
    │   ├─> Docker Desktop installed?
    │   └─> GPU available?
    │
    ├─> Initialize Docker connection
    │   ├─> Docker running? Yes → Connect
    │   └─> No → Start Docker Desktop → Wait → Connect
    │
    ├─> Start NeuroInsight services
    │   ├─> docker-compose up -d
    │   ├─> Wait for health checks
    │   └─> Services ready!
    │
    └─> Open main window
        └─> Load http://localhost:56052
```

### Docker Integration

The app uses `dockerode` and `docker-compose` packages:

```javascript
// DockerManager.js handles:
- Checking if Docker is installed
- Starting Docker Desktop
- Pulling images
- Container health checks
- Getting system info

// ServiceManager.js handles:
- docker-compose up/down
- Service status monitoring
- Health checking
- Log retrieval
```

## Customization

### Changing App Name/ID

Edit `package.json`:

```json
{
  "name": "your-app-name",
  "productName": "Your App Name",
  "build": {
    "appId": "com.yourcompany.yourapp"
  }
}
```

### Adding Menu Bar

Create `src/menu.js`:

```javascript
const { Menu } = require('electron');

const template = [
  {
    label: 'File',
    submenu: [
      { label: 'Open Scan...', click: () => {} },
      { type: 'separator' },
      { label: 'Exit', role: 'quit' }
    ]
  },
  {
    label: 'View',
    submenu: [
      { role: 'reload' },
      { role: 'toggleDevTools' }
    ]
  }
];

const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);
```

### Custom System Tray Menu

Edit `src/main.js`:

```javascript
const contextMenu = Menu.buildFromTemplate([
  { label: 'Your Custom Item', click: () => {} },
  // ... existing items
]);
```

### Environment Variables

The app sets these automatically:

```javascript
process.env.NEUROINSIGHT_DATA_DIR  // User data directory
process.env.UPLOADS_DIR             // Upload folder
process.env.OUTPUTS_DIR             // Results folder
process.env.DB_PATH                 // Database folder
process.env.POSTGRES_HOST           // Always localhost
process.env.REDIS_HOST              // Always localhost
```

## Platform-Specific Notes

### macOS

**Code Signing** (required for distribution):
1. Join Apple Developer Program ($99/year)
2. Create Developer ID Application certificate
3. Export as .p12 file
4. Set environment variables:

```bash
export CSC_LINK=/path/to/cert.p12
export CSC_KEY_PASSWORD=your_password
```

**Notarization** (required for macOS 10.15+):

```bash
export APPLE_ID=your@email.com
export APPLE_ID_PASSWORD=app-specific-password
export APPLE_TEAM_ID=TEAM_ID
```

**DMG Customization**:
- Background: `assets/dmg-background.png` (540x380)
- Icon: `build/icon.icns` (512x512@2x)

### Windows

**Code Signing**:
1. Purchase code signing certificate
2. Export as .pfx file
3. Set environment variables:

```bash
export CSC_LINK=/path/to/cert.pfx
export CSC_KEY_PASSWORD=your_password
```

**NSIS Customization**:
Edit `installers/windows/installer.nsh`:

```nsis
!macro customHeader
  !system "echo 'Custom installer step'"
!macroend

!macro customInstall
  # Custom install logic
!macroend
```

### Linux

**Dependencies** for building:

```bash
# Ubuntu/Debian
sudo apt-get install -y rpm fakeroot dpkg

# Fedora/RHEL
sudo dnf install -y rpm-build
```

**AppImage** (universal):
- Works on all distros
- No installation required
- Self-contained

**Desktop Entry**:
Auto-created at: `~/.local/share/applications/neuroinsight.desktop`

## Debugging

### Enable Verbose Logging

```bash
# Set log level
export LOG_LEVEL=debug

# Run app
npm run dev
```

### Access Logs

```javascript
// In renderer process
window.electronAPI.getLogs('worker').then(console.log);
window.electronAPI.getLogs('backend').then(console.log);
```

### Inspect Main Process

```bash
# Add to main.js
require('electron').app.on('ready', () => {
  require('inspector').open(9229, '127.0.0.1', true);
  debugger; // Pause here
});

# Then connect Chrome DevTools to: chrome://inspect
```

### Common Issues

**Problem**: "Cannot find module 'electron'"
```bash
rm -rf node_modules package-lock.json
npm install
```

**Problem**: Docker containers not starting
```bash
# Check Docker manually
docker ps

# Check logs
docker-compose logs

# Reset Docker
docker-compose down -v
docker-compose up -d
```

**Problem**: Build fails with "No code sign identity"
```bash
# macOS - disable signing for testing
export CSC_IDENTITY_AUTO_DISCOVERY=false

# Windows - same
export CSC_IDENTITY_AUTO_DISCOVERY=false
```

## Publishing

### Auto-Updater Setup

Install `electron-updater`:

```bash
npm install electron-updater
```

Add to `src/main.js`:

```javascript
const { autoUpdater } = require('electron-updater');

app.on('ready', () => {
  // Check for updates on startup
  autoUpdater.checkForUpdatesAndNotify();
  
  // Check every hour
  setInterval(() => {
    autoUpdater.checkForUpdatesAndNotify();
  }, 60 * 60 * 1000);
});

autoUpdater.on('update-available', () => {
  dialog.showMessageBox({
    type: 'info',
    title: 'Update Available',
    message: 'A new version is available. Downloading now...'
  });
});

autoUpdater.on('update-downloaded', () => {
  dialog.showMessageBox({
    type: 'info',
    title: 'Update Ready',
    message: 'Update downloaded. Restart to install?',
    buttons: ['Restart', 'Later']
  }).then(result => {
    if (result.response === 0) {
      autoUpdater.quitAndInstall();
    }
  });
});
```

### Release Process

1. **Update version** in `package.json`
2. **Create changelog** entry
3. **Build for all platforms**:
   ```bash
   npm run dist:mac
   npm run dist:win
   npm run dist:linux
   ```
4. **Test installers** on clean systems
5. **Upload to GitHub Releases** or your server
6. **Update auto-updater** configuration

### Distribution Channels

**Direct Download**:
- Host on your website
- Users download installers directly

**GitHub Releases**:
- Free hosting
- Auto-updater compatible
- Version tracking

**App Stores**:
- macOS App Store (requires $99/year)
- Microsoft Store (requires $19 one-time)
- Snap Store (free, Linux)

## Performance

### Reducing App Size

```javascript
// In package.json build config
{
  "build": {
    "compression": "maximum",
    "asar": true,
    "fileAssociations": [],
    "files": [
      "!**/node_modules/*/{CHANGELOG.md,README.md}",
      "!**/node_modules/**/*.map",
      "!**/.*"
    ]
  }
}
```

### Startup Time Optimization

```javascript
// Lazy load heavy modules
let heavyModule;
function getHeavyModule() {
  if (!heavyModule) {
    heavyModule = require('./heavy-module');
  }
  return heavyModule;
}

// Use when needed
const module = getHeavyModule();
```

## Security

### Best Practices

1. **Context Isolation**: Already enabled
2. **Node Integration**: Disabled in renderer
3. **Preload Scripts**: Use for secure IPC
4. **CSP**: Add Content Security Policy
5. **HTTPS**: Use for all external requests

### Secure IPC

```javascript
// ✗ BAD - Exposing entire ipcRenderer
contextBridge.exposeInMainWorld('electron', {
  ipcRenderer: ipcRenderer
});

// ✓ GOOD - Exposing specific methods
contextBridge.exposeInMainWorld('electronAPI', {
  specificMethod: () => ipcRenderer.invoke('specific-channel')
});
```

## Next Steps

1. **Test the app**: `npm run dev`
2. **Create icons**: 1024x1024 PNG
3. **Customize branding**: Edit assets/
4. **Build installers**: `npm run dist`
5. **Test on target platforms**
6. **Set up code signing**
7. **Configure auto-updates**
8. **Publish release**

## Resources

- [Electron Docs](https://www.electronjs.org/docs)
- [electron-builder](https://www.electron.build/)
- [Dockerode API](https://github.com/apocas/dockerode)
- [Winston Logging](https://github.com/winstonjs/winston)

## Support

Questions? Check:
- README.md (user guide)
- QUICK_START.md (installation)
- GitHub Issues
- Community forum


