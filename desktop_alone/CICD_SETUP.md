# CI/CD Setup for Multi-Platform Builds

**Purpose:** Automate Windows and macOS installer builds without requiring physical access to those platforms.

## Why CI/CD?

### Problems Without CI/CD
- Need Windows machine for `.exe` builds
- Need macOS machine for `.dmg` builds  
- Manual builds are time-consuming
- Inconsistent build environments

### Benefits With CI/CD
- ✓ Build all platforms from Linux
- ✓ Automated on every release
- ✓ Consistent, reproducible builds
- ✓ Free GitHub Actions minutes

## Recommended: GitHub Actions

GitHub provides free Windows and macOS runners for open-source projects.

### Create `.github/workflows/build-desktop.yml`

```yaml
name: Build Desktop Installers

on:
  push:
    tags:
      - 'desktop-v*'
  workflow_dispatch:

jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        working-directory: desktop_alone
        run: |
          pip install -r backend/requirements.txt
          pip install pyinstaller
          cd electron-app && npm install
      
      - name: Build backend
        working-directory: desktop_alone
        run: |
          pyinstaller build.spec
      
      - name: Build Linux installers
        working-directory: desktop_alone/electron-app
        run: npm run build:linux
      
      - name: Generate checksums
        working-directory: desktop_alone/electron-app/dist
        run: |
          sha256sum *.AppImage *.deb > checksums-linux.txt
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: linux-installers
          path: |
            desktop_alone/electron-app/dist/*.AppImage
            desktop_alone/electron-app/dist/*.deb
            desktop_alone/electron-app/dist/checksums-linux.txt

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        working-directory: desktop_alone
        run: |
          pip install -r backend/requirements.txt
          pip install pyinstaller
          cd electron-app
          npm install
      
      - name: Build backend
        working-directory: desktop_alone
        run: |
          pyinstaller build.spec
      
      - name: Build Windows installer
        working-directory: desktop_alone/electron-app
        run: npm run build:win
      
      - name: Generate checksum
        working-directory: desktop_alone/electron-app/dist
        run: |
          Get-FileHash *.exe -Algorithm SHA256 | Format-List > checksums-windows.txt
        shell: pwsh
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: windows-installer
          path: |
            desktop_alone/electron-app/dist/*.exe
            desktop_alone/electron-app/dist/checksums-windows.txt

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        working-directory: desktop_alone
        run: |
          pip install -r backend/requirements.txt
          pip install pyinstaller
          cd electron-app && npm install
      
      - name: Build backend
        working-directory: desktop_alone
        run: |
          pyinstaller build.spec
      
      - name: Build macOS installer
        working-directory: desktop_alone/electron-app
        run: npm run build:mac
      
      - name: Generate checksums
        working-directory: desktop_alone/electron-app/dist
        run: |
          shasum -a 256 *.dmg > checksums-macos.txt
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: macos-installer
          path: |
            desktop_alone/electron-app/dist/*.dmg
            desktop_alone/electron-app/dist/checksums-macos.txt

  create-release:
    needs: [build-linux, build-windows, build-macos]
    runs-on: ubuntu-latest
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v4
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            linux-installers/*
            windows-installer/*
            macos-installer/*
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Alternative: CircleCI

```yaml
version: 2.1

jobs:
  build-linux:
    docker:
      - image: cimg/node:18.20
    steps:
      - checkout
      - run: cd desktop_alone && ./scripts/build_backend.sh
      - run: cd desktop_alone/electron-app && npm install && npm run build:linux
      - store_artifacts:
          path: desktop_alone/electron-app/dist

  build-windows:
    machine:
      image: windows-server-2019
    steps:
      - checkout
      - run: cd desktop_alone && pyinstaller build.spec
      - run: cd desktop_alone/electron-app && npm install && npm run build:win
      - store_artifacts:
          path: desktop_alone/electron-app/dist

  build-macos:
    macos:
      xcode: "14.0"
    steps:
      - checkout
      - run: cd desktop_alone && pyinstaller build.spec
      - run: cd desktop_alone/electron-app && npm install && npm run build:mac
      - store_artifacts:
          path: desktop_alone/electron-app/dist

workflows:
  build-all:
    jobs:
      - build-linux
      - build-windows
      - build-macos
```

## Code Signing in CI/CD

### Windows Code Signing

```yaml
# Add to build-windows job
- name: Sign Windows installer
  env:
    CERTIFICATE: ${{ secrets.WINDOWS_CERTIFICATE }}
    CERTIFICATE_PASSWORD: ${{ secrets.CERTIFICATE_PASSWORD }}
  run: |
    # Import certificate
    $cert = [Convert]::FromBase64String($env:CERTIFICATE)
    [IO.File]::WriteAllBytes("cert.pfx", $cert)
    
    # Sign executable
    signtool sign /f cert.pfx /p $env:CERTIFICATE_PASSWORD /tr http://timestamp.digicert.com /td sha256 /fd sha256 dist/*.exe
  shell: pwsh
```

**Setup:**
1. Purchase code signing certificate
2. Export as `.pfx` with password
3. Base64 encode: `base64 cert.pfx > cert.txt`
4. Add to GitHub Secrets:
   - `WINDOWS_CERTIFICATE`: Base64 certificate
   - `CERTIFICATE_PASSWORD`: Certificate password

### macOS Code Signing

```yaml
# Add to build-macos job
- name: Import signing certificate
  env:
    MACOS_CERTIFICATE: ${{ secrets.MACOS_CERTIFICATE }}
    MACOS_CERTIFICATE_PASSWORD: ${{ secrets.MACOS_CERTIFICATE_PASSWORD }}
  run: |
    echo $MACOS_CERTIFICATE | base64 --decode > certificate.p12
    security create-keychain -p actions build.keychain
    security default-keychain -s build.keychain
    security unlock-keychain -p actions build.keychain
    security import certificate.p12 -k build.keychain -P $MACOS_CERTIFICATE_PASSWORD -T /usr/bin/codesign
    security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k actions build.keychain

- name: Sign and notarize
  env:
    APPLE_ID: ${{ secrets.APPLE_ID }}
    APPLE_PASSWORD: ${{ secrets.APPLE_APP_PASSWORD }}
    APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
  run: |
    npx electron-notarize --bundle-id com.neuroinsight.app --apple-id $APPLE_ID --password $APPLE_PASSWORD --team-id $APPLE_TEAM_ID
```

**Setup:**
1. Enroll in Apple Developer Program ($99/year)
2. Create Developer ID certificate
3. Export certificate as `.p12`
4. Generate app-specific password
5. Add to GitHub Secrets:
   - `MACOS_CERTIFICATE`: Base64 encoded `.p12`
   - `MACOS_CERTIFICATE_PASSWORD`: Certificate password
   - `APPLE_ID`: Apple ID email
   - `APPLE_APP_PASSWORD`: App-specific password
   - `APPLE_TEAM_ID`: 10-character team ID

## Triggering Builds

### Automatic (On Tag Push)
```bash
git tag desktop-v1.0.0
git push origin desktop-v1.0.0
```

### Manual (Workflow Dispatch)
1. Go to GitHub Actions tab
2. Select "Build Desktop Installers"
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow"

## Cost Analysis

### Free Tier (Public Repos)
- **Linux:** 2,000 minutes/month
- **Windows:** 2,000 minutes/month (2x multiplier = 1,000 effective)
- **macOS:** 2,000 minutes/month (10x multiplier = 200 effective)

### Estimated Build Times
- Linux: ~30 minutes (PyInstaller + Electron)
- Windows: ~40 minutes (PyInstaller + Electron)
- macOS: ~50 minutes (PyInstaller + Electron + signing)

### Builds Per Month (Free)
- **Total time:** ~2 hours per full build (all platforms)
- **Monthly builds:** ~100 Linux-only, ~25 Windows, ~4 macOS
- **Realistic:** 4 full releases/month within free tier

### Paid Tier (If Needed)
- $0.008/minute (Linux)
- $0.016/minute (Windows)
- $0.08/minute (macOS)
- **Cost per full build:** ~$5

## Troubleshooting

### Large File Warnings
GitHub has 100 MB file limit for releases. If installers exceed:
- Use [git-lfs](https://git-lfs.github.com/) for large files
- Or upload to external storage (AWS S3, DigitalOcean Spaces)

### macOS Notarization Timeout
If notarization takes >2 hours:
```yaml
timeout-minutes: 180  # 3 hours
```

### Windows Signing Errors
Ensure certificate is EV (Extended Validation) for no SmartScreen warnings.

## Next Steps

1. **Create `.github/workflows/build-desktop.yml`**
2. **Test manual trigger** first
3. **Set up code signing** (optional)
4. **Tag and push** for automatic builds
5. **Download artifacts** from GitHub Actions
6. **Create GitHub Release** with installers

## Resources

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [electron-builder CI Guide](https://www.electron.build/multi-platform-build)
- [Code Signing Guide](https://www.electron.build/code-signing)
- [Apple Notarization](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

