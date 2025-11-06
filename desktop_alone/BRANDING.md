# NeuroInsight Branding & Icons

## Icons Reused from hippo_desktop

**All icons and branding assets copied from `hippo_desktop/` to `desktop_alone/electron-app/`**

---

## Available Icons

### Platform Icons

**macOS:**
```
electron-app/build/icon.icns
- Size: 54 KB
- Format: Apple ICNS (contains multiple resolutions)
- Used for: App bundle, Dock icon, Finder
```

**Windows:**
```
electron-app/build/icon.ico
- Size: 23 KB
- Format: Windows ICO (contains multiple resolutions)
- Used for: Executable icon, taskbar, Start Menu
```

**Linux:**
```
electron-app/build/icons/
├── 16x16.png    (497 bytes)
├── 32x32.png    (1 KB)
├── 48x48.png    (1.7 KB)
├── 64x64.png    (2.4 KB)
├── 128x128.png  (5.1 KB)
├── 256x256.png  (11 KB)
└── 512x512.png  (22 KB)

Used for: Desktop entries, application menu, various sizes
```

---

### Application Assets

**App Icon:**
```
electron-app/assets/icon.png
- Size: 21 KB
- Resolution: High resolution app icon
- Used for: About dialog, in-app branding
```

**Tray Icons:**
```
electron-app/assets/tray-icon.png
electron-app/assets/tray-icon-Template.png
- System tray icons (if we add tray feature)
- macOS template icon (follows dark/light mode)
```

---

## Where Icons Are Used

### During Installation

**Windows (NSIS Installer):**
```
Installer wizard shows:
- icon.ico on installer window
- icon.ico in Add/Remove Programs
- icon.ico for desktop shortcut
- icon.ico for Start Menu shortcut
```

**macOS (DMG):**
```
DMG window shows:
- icon.icns for the app
- icon.icns in Applications folder
- icon.icns in Dock when running
```

**Linux (AppImage/DEB):**
```
Application menu shows:
- Appropriate size icon (32x32, 48x48, etc.)
- Desktop file references icons/
```

---

### When App is Running

**Application Window:**
```
- Window titlebar icon
- Dock/Taskbar icon
- Alt+Tab icon
- About dialog icon
```

**In-App:**
```
- Loading screens
- About dialog
- Error dialogs
```

---

## Icon Configuration

### Electron Builder Configuration

Already configured in `electron-app/package.json`:

```json
{
  "build": {
    "win": {
      "icon": "build/icon.ico"
    },
    "mac": {
      "icon": "build/icon.icns"
    },
    "linux": {
      "icon": "build/icons"
    }
  }
}
```

**electron-builder automatically:**
- Uses correct icon for each platform
- Embeds in installers
- Sets up desktop integration
- No additional configuration needed

---

## Branding Consistency

**Same branding across:**
- ✓ hippo_desktop (current Docker manager)
- ✓ desktop_alone (new standalone)
- ✓ Web version (favicon could match)

**Benefits:**
- Consistent user recognition
- Professional appearance
- Brand identity maintained

---

## Icon Source

**Original icons created for hippo_desktop**

If you want to update icons:
1. Edit source files in `hippo_desktop/`
2. Regenerate using `hippo_desktop/CREATE_MACOS_ICON.sh`
3. Copy to `desktop_alone/electron-app/build/`

**For now:** Using existing professional icons ✓

---

## Technical Details

### Icon Formats

**ICNS (macOS):**
- Multi-resolution format
- Contains: 16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024
- Required for macOS app bundles

**ICO (Windows):**
- Multi-resolution format
- Contains: 16x16, 32x32, 48x48, 256x256
- Required for Windows executables

**PNG (Linux):**
- Individual files for each size
- Follows FreeDesktop.org standards
- Multiple sizes for different contexts

---

## Summary

**Icons Status:** ✓ Complete

**All platform icons copied and configured:**
- macOS: icon.icns ✓
- Windows: icon.ico ✓
- Linux: 7 PNG sizes ✓
- Assets: App icons ✓

**Configuration:** ✓ Already set in package.json

**Consistency:** ✓ Same branding as hippo_desktop

**No additional work needed for icons!**

---

When you build the installers, icons will automatically be:
- Embedded in executables
- Used for shortcuts
- Displayed in system UI
- Shown in application window

All branding is ready to go!

