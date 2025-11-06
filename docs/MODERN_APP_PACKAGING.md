# How Modern Apps Are Packaged

Real-world examples: Cursor, Facebook Messenger, Slack, and other mainstream desktop applications.

---

## The Common Pattern: Electron Framework

Most modern desktop apps use **Electron** - a framework that bundles a web app with Chromium browser and Node.js.

### Why Electron?

**One codebase, three platforms:**
- Write once in HTML/CSS/JavaScript
- Package for Windows, macOS, and Linux
- Same UI across all platforms

**Apps using Electron:**
- Cursor (code editor)
- Slack (messaging)
- Facebook Messenger (desktop)
- Discord (gaming communication)
- VS Code (code editor)
- Microsoft Teams (collaboration)
- Spotify (music, hybrid native/web)
- WhatsApp Desktop
- Signal Desktop
- Notion (productivity)
- Figma Desktop
- Obsidian (note-taking)

---

## Case Study 1: Cursor

**What is it:** AI-powered code editor (fork of VS Code)

### How Cursor Is Packaged

**Architecture:**
```
Cursor.app / Cursor.exe
├── Electron Runtime (~120MB)
│   ├── Chromium browser (for rendering UI)
│   └── Node.js (for backend logic)
├── Application Code (~50MB)
│   ├── TypeScript/JavaScript source
│   ├── Extensions API
│   └── AI integration code
├── Native Modules (~30MB)
│   ├── Git integration (native code)
│   ├── Terminal emulator
│   └── File system watcher
└── Assets (~20MB)
    ├── Icons, fonts
    └── Syntax highlighting themes
```

**Total Size:** ~200-250MB

### Cursor's Packaging Process

**1. Development (TypeScript/JavaScript)**
```javascript
// Cursor is built with Electron
// package.json
{
  "name": "cursor",
  "main": "./out/main.js",
  "dependencies": {
    "electron": "^27.0.0"
  }
}
```

**2. Build Process**
```bash
# Compile TypeScript to JavaScript
npm run compile

# Build platform-specific installers
npm run build:win   # Windows NSIS installer
npm run build:mac   # macOS DMG
npm run build:linux # AppImage/deb
```

**3. Distribution**
```
Windows: Cursor-Setup-0.17.0.exe (200MB)
- NSIS installer
- Installs to Program Files
- Creates desktop/start menu shortcuts
- Auto-updater included

macOS: Cursor-0.17.0.dmg (220MB)
- Disk image with .app bundle
- Drag to Applications
- Notarized by Apple
- Gatekeeper approved

Linux: Cursor-0.17.0.AppImage (240MB)
- Single portable file
- No installation needed
- Or .deb package for Ubuntu
```

### Cursor's Update Mechanism

**electron-updater:**
```javascript
// Built into Cursor
const { autoUpdater } = require('electron-updater');

app.on('ready', () => {
  autoUpdater.checkForUpdatesAndNotify();
});

// Checks GitHub releases or custom server
// Downloads delta updates (only changed files)
// Installs on app restart
```

**User experience:**
- Notification: "Update available"
- Downloads in background
- Installs on next launch
- No manual downloads

---

## Case Study 2: Slack

**What is it:** Business messaging platform

### How Slack Is Packaged

**Architecture:**
```
Slack.app / Slack.exe
├── Electron Runtime (~150MB)
│   ├── Chromium (custom build)
│   └── Node.js
├── Slack Application (~80MB)
│   ├── React frontend code
│   ├── WebSocket client
│   ├── Local caching layer
│   └── Notification system
├── Native Components (~40MB)
│   ├── Screen sharing (native)
│   ├── System notifications
│   ├── Spell checker
│   └── Media codecs
└── Resources (~30MB)
    ├── Emoji assets
    ├── Sound files
    └── Custom fonts
```

**Total Size:** ~300-350MB

### Slack's Special Features

**1. Multiple Workspaces**
```javascript
// Slack runs multiple instances
// Each workspace in separate window
// Shared Electron runtime

app.on('ready', () => {
  workspaces.forEach(workspace => {
    createWorkspaceWindow(workspace);
  });
});
```

**2. Deep OS Integration**
```javascript
// macOS notifications
const { Notification } = require('electron');

new Notification({
  title: 'Slack',
  body: 'New message from @user',
  sound: 'Ping',
  icon: 'assets/icon.png'
}).show();

// Badge count on dock/taskbar
app.setBadgeCount(5);  // macOS
app.setOverlayIcon(icon, '5');  // Windows
```

**3. Rich Media Handling**
```javascript
// Native screen sharing
const { desktopCapturer } = require('electron');

// Video/audio processing
// Uses native codecs for performance
```

### Slack's Build & Distribution

**Build Process:**
```bash
# Internal build system
slack-build compile --platform all
slack-build package --platform all
slack-build sign --platform all
slack-build upload --channel stable
```

**Distribution Channels:**
```
Website: slack.com/downloads
- Direct download links
- Auto-detects OS
- Signed installers

Microsoft Store (Windows)
- Auto-updates through store
- Sandboxed environment

Mac App Store (macOS)
- Sandboxed version
- Separate from direct download

Snap Store (Linux)
- Auto-updates
- Sandboxed
```

**Update Strategy:**
```javascript
// Checks for updates every 4 hours
// Downloads in background
// Shows notification when ready
// Installs on app restart or manually

"Update available - Restart Slack to update"
```

---

## Case Study 3: Facebook Messenger Desktop

**What is it:** Facebook messaging app

### How Facebook Messenger Is Packaged

**Architecture:**
```
Messenger.app / Messenger.exe
├── Electron Runtime (~140MB)
├── React Native Web (~60MB)
│   ├── Facebook's React components
│   ├── GraphQL client
│   └── State management
├── Native Modules (~50MB)
│   ├── Video calling (WebRTC)
│   ├── Voice calls
│   ├── Camera access
│   └── Microphone access
└── Resources (~20MB)
    ├── Stickers
    ├── Emoji
    └── Themes
```

**Total Size:** ~270-300MB

### Facebook's Special Approach

**1. Code Splitting**
```javascript
// Loads features on demand
// Reduces initial load time

async function openVideoCall() {
  const videoModule = await import('./video-call');
  videoModule.startCall();
}
```

**2. Auto-Update (Silent)**
```javascript
// Updates automatically in background
// No user notification unless critical
// Seamless experience

autoUpdater.on('update-downloaded', () => {
  // Restart on next launch
  // User doesn't notice
});
```

**3. Performance Optimization**
```javascript
// Preloads common operations
// Caches messages locally
// Background sync

app.on('ready', () => {
  preloadMessagesCache();
  startBackgroundSync();
});
```

---

## Common Packaging Pattern

All these apps follow the same pattern:

### Step 1: Build the Web App

```javascript
// Modern JavaScript framework
import React from 'react';
import ReactDOM from 'react-dom';

// Your app code
function App() {
  return <div>Your Application</div>;
}

// Bundle with webpack/vite
npm run build
// Output: HTML, CSS, JavaScript files
```

### Step 2: Wrap in Electron

```javascript
// main.js - Electron entry point
const { app, BrowserWindow } = require('electron');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load your web app
  win.loadFile('index.html');
  // Or remote: win.loadURL('https://yourapp.com');
}

app.whenReady().then(createWindow);
```

### Step 3: Configure Package

```json
// package.json
{
  "name": "your-app",
  "version": "1.0.0",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build": "electron-builder"
  },
  "build": {
    "appId": "com.yourcompany.yourapp",
    "productName": "Your App",
    "directories": {
      "output": "dist"
    },
    "files": [
      "**/*",
      "!**/*.ts",
      "!*.map"
    ],
    "win": {
      "target": ["nsis"],
      "icon": "build/icon.ico"
    },
    "mac": {
      "target": ["dmg"],
      "icon": "build/icon.icns",
      "category": "public.app-category.productivity"
    },
    "linux": {
      "target": ["AppImage", "deb"],
      "icon": "build/icons"
    }
  }
}
```

### Step 4: Build Installers

```bash
# Build for current platform
npm run build

# Or build for all platforms (requires platform-specific machines)
npm run build:all

# Output:
dist/
├── Your-App-Setup-1.0.0.exe     # Windows
├── Your-App-1.0.0.dmg           # macOS
└── Your-App-1.0.0.AppImage      # Linux
```

---

## Real Package Sizes

| App | Windows | macOS | Linux | Components |
|-----|---------|-------|-------|------------|
| **Cursor** | 200MB | 220MB | 240MB | Electron + Code editor |
| **Slack** | 300MB | 350MB | 320MB | Electron + React + WebRTC |
| **Discord** | 140MB | 150MB | 160MB | Electron + React |
| **VS Code** | 95MB | 105MB | 110MB | Electron + Monaco editor |
| **WhatsApp** | 120MB | 135MB | 125MB | Electron + React Native |
| **Signal** | 100MB | 110MB | 115MB | Electron + WebRTC |
| **Notion** | 80MB | 90MB | 95MB | Electron + Custom editor |

---

## Installation User Experience

### Cursor Installation Example

**Windows:**
```
1. Download: Cursor-Setup-0.17.0.exe
2. Double-click installer
3. User Account Control prompt (if needed)
4. Shows installation progress bar
5. Creates shortcuts:
   - Desktop
   - Start Menu
   - Adds to PATH (for terminal use)
6. "Launch Cursor" checkbox
7. Done - app opens

Time: 30-60 seconds
```

**macOS:**
```
1. Download: Cursor-0.17.0.dmg
2. Double-click to mount
3. Window opens with Cursor icon
4. Drag Cursor to Applications folder
5. Eject DMG
6. Open Cursor from Applications
7. First run: "Cursor is an app downloaded from internet"
8. Click "Open"

Time: 15-30 seconds
```

**Linux:**
```
1. Download: Cursor-0.17.0.AppImage
2. Make executable: chmod +x Cursor-0.17.0.AppImage
3. Double-click to run (portable)

OR for system installation:
1. Download: cursor_0.17.0_amd64.deb
2. Double-click or: sudo dpkg -i cursor_0.17.0_amd64.deb
3. Launch from applications menu

Time: 15-30 seconds
```

---

## Auto-Update Flow

How Slack handles updates (typical pattern):

**1. Background Check**
```javascript
// Every 4 hours
setInterval(() => {
  autoUpdater.checkForUpdates();
}, 4 * 60 * 60 * 1000);
```

**2. Download**
```javascript
autoUpdater.on('update-available', (info) => {
  // Download silently in background
  console.log('Update available:', info.version);
});

autoUpdater.on('download-progress', (progress) => {
  // Show in menu bar or status
  console.log(`Downloaded ${progress.percent}%`);
});
```

**3. Install**
```javascript
autoUpdater.on('update-downloaded', () => {
  // Notify user
  showNotification({
    title: 'Update Ready',
    body: 'Restart Slack to update',
    actions: [
      { text: 'Restart Now', action: () => {
        autoUpdater.quitAndInstall();
      }},
      { text: 'Later' }
    ]
  });
});
```

**User sees:**
- Small notification: "Update available"
- Downloads in background (no interruption)
- "Restart to update" notification
- Clicks restart → app closes → installs → reopens
- Total time: 5-10 seconds

---

## Code Signing & Security

### How Apps Are Signed

**Windows (Cursor, Slack, etc.):**
```bash
# Developer purchases certificate (~$300-500/year)
# Signs the executable

signtool sign /f certificate.pfx \
  /p password \
  /fd sha256 \
  /tr http://timestamp.digicert.com \
  /td sha256 \
  Cursor-Setup.exe

# Result: No SmartScreen warning
# "Verified publisher: Cursor Inc."
```

**macOS (Cursor, Slack, etc.):**
```bash
# Developer ID certificate from Apple ($99/year)

# 1. Sign the app
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Company Name" \
  --options runtime \
  Cursor.app

# 2. Notarize with Apple
xcrun altool --notarize-app \
  --primary-bundle-id com.cursor.app \
  --username developer@email.com \
  --password @keychain:AC_PASSWORD \
  --file Cursor.dmg

# 3. Staple notarization
xcrun stapler staple Cursor.dmg

# Result: No Gatekeeper warning
# "Cursor.app verified by Apple"
```

---

## Distribution Infrastructure

### How Companies Distribute Apps

**Cursor:**
```
Primary: cursor.sh/download
- Auto-detects OS
- Direct downloads from CDN
- GitHub releases as backup

Update Server:
- Custom server for electron-updater
- Differential updates
- Staged rollouts (5% → 25% → 100%)
```

**Slack:**
```
Primary: slack.com/downloads
- Multiple download options
- Enterprise MSI installer (Windows)
- Bulk deployment tools

Update Servers:
- Global CDN (CloudFront/similar)
- Geographic load balancing
- Staged rollouts

Additional Channels:
- Microsoft Store
- Mac App Store
- Snap Store
- Homebrew Cask (macOS)
- Chocolatey (Windows)
```

**Facebook Messenger:**
```
Primary: messenger.com/desktop
- Auto-detects platform
- CDN distribution

Updates:
- Silent automatic updates
- No user intervention
- Can't disable (policy)
```

---

## Cost Breakdown

What it costs to distribute like Cursor/Slack:

**Code Signing:**
- Windows certificate: $300-500/year
- macOS Developer: $99/year
- Total: ~$400-600/year

**Build Infrastructure:**
- GitHub Actions: Free (or $4/month for private)
- Or self-hosted: ~$100/month for build servers

**Distribution:**
- CDN (CloudFlare/AWS): $20-100/month depending on downloads
- Or GitHub Releases: Free

**Total Annual Cost:** $500-2000/year for professional distribution

---

## How NeuroInsight Would Compare

Using the same approach as Cursor/Slack:

**Package Structure:**
```
NeuroInsight.exe / NeuroInsight.app
├── Electron Runtime (~120MB) ← Same as Cursor
├── NeuroInsight Frontend (~50MB) ← Same as Cursor
├── Python Backend (~500MB) ← Different (bundled Python)
├── FastSurfer Models (~400MB) ← Different (AI models)
└── Native Modules (~30MB) ← Similar to Cursor

Total: ~1.5GB (larger due to ML models)
```

**Same packaging tools:**
- electron-builder (like Cursor/Slack)
- NSIS/DMG/AppImage (like Cursor/Slack)
- Auto-updates (like Cursor/Slack)
- Code signing (like Cursor/Slack)

**Same user experience:**
1. Download installer
2. Double-click
3. Install
4. Launch
5. Use immediately

**Only difference:** Larger due to ML models (1.5GB vs 200-300MB)

---

## Key Takeaways

### 1. Standard Pattern
All modern apps use Electron or similar:
- Cursor, Slack, Discord, VS Code, WhatsApp
- Same packaging approach
- Same tools (electron-builder)
- Same distribution method

### 2. One-Click Installation
All install the same way:
- Windows: .exe installer
- macOS: .dmg with drag-to-Applications
- Linux: AppImage or .deb

### 3. Auto-Updates
All update automatically:
- Background checks
- Silent downloads
- Notification to restart
- Seamless experience

### 4. Code Signing
All professionally signed:
- No security warnings
- Verified publishers
- User trust

### 5. NeuroInsight Can Do Exactly The Same
The only difference:
- Larger download (ML models)
- Bundle Python instead of just JavaScript
- Everything else identical

---

## Summary Table

| Aspect | Cursor | Slack | NeuroInsight (Plan) |
|--------|--------|-------|---------------------|
| **Framework** | Electron | Electron | Electron |
| **Size** | 200MB | 300MB | 1.5GB |
| **Installer** | NSIS/DMG | NSIS/DMG | NSIS/DMG |
| **Auto-Update** | Yes | Yes | Yes |
| **Code Signed** | Yes | Yes | Yes (planned) |
| **Prerequisites** | None | None | None |
| **Install Time** | 30-60s | 30-60s | 1-2min (larger) |
| **Updates** | Background | Background | Background |

**Conclusion:** NeuroInsight will work exactly like Cursor and Slack, just with larger initial download due to ML models.

---

**Next Steps:** 
- See [ONE_CLICK_PACKAGING_GUIDE.md](ONE_CLICK_PACKAGING_GUIDE.md) for implementation
- See [DESKTOP_APP_WITHOUT_DOCKER.md](DESKTOP_APP_WITHOUT_DOCKER.md) for architecture

