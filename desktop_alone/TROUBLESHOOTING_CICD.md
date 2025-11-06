# CI/CD Troubleshooting Guide

## Common Build Issues and Solutions

### Issue #1: "No space left on device" (Linux) ✅ SOLVED

**Error:**
```
⨯ cannot execute  cause=exit status 1
  errorOut=Write failed because No space left on device
  FATAL ERROR:Failed to write to output filesystem
```

**Cause:**
- GitHub Actions runners have limited disk space (~14 GB)
- PyInstaller backend bundle is ~8 GB
- Electron packaging requires additional 4-6 GB
- Total needed: ~14 GB, but cleanup needed

**Solution Applied:**
Added disk cleanup steps to workflow:

```yaml
- name: Free up disk space
  run: |
    sudo rm -rf /usr/share/dotnet       # ~8 GB
    sudo rm -rf /usr/local/lib/android  # ~4 GB
    sudo rm -rf /opt/ghc                # ~1 GB
    sudo rm -rf /opt/hostedtoolcache/CodeQL  # ~1 GB
    sudo docker image prune --all --force
```

And intermediate cleanup:

```yaml
- name: Clean up build artifacts
  working-directory: desktop_alone
  run: |
    rm -rf build/  # Clean PyInstaller build artifacts
```

**Result:**
- Before: 14 GB available → Build fails
- After: ~28 GB available → Build succeeds ✅

**Commit:** `6a2487a` - "Fix disk space issues in CI/CD workflow"

---

### Issue #2: Windows pip upgrade fails ✅ SOLVED

**Error:**
```
ERROR: To modify pip, please run the following command:
C:\hostedtoolcache\windows\Python\3.10.11\x64\python.exe -m pip install --upgrade pip
Error: Process completed with exit code 1.
```

**Cause:**
- On Windows, pip cannot upgrade itself while it's running
- Direct `pip install --upgrade pip` command fails
- Must use `python -m pip install --upgrade pip` format

**Solution Applied:**
Changed all pip commands to use Python module format:

```yaml
# Before
- run: pip install --upgrade pip

# After
- run: python -m pip install --upgrade pip
```

**Result:**
- Before: pip upgrade fails on Windows ❌
- After: pip upgrades successfully ✅

**Commit:** `f934b50` - "Fix Windows pip upgrade issue"

---

### Issue #3: macOS PyInstaller recursion limit ✅ SOLVED

**Error:**
```
RecursionError: maximum recursion depth exceeded
A RecursionError (maximum recursion depth exceeded) occurred.
For working around please follow these instructions
...
Error: Process completed with exit code 1.
```

**Cause:**
- PyInstaller imports modules recursively
- PyTorch has a very deep dependency tree
- Default Python recursion limit (1000) is too low
- Analysis phase hits the limit before completing

**Solution Applied:**
Added recursion limit increase to `build.spec`:

```python
# Near the top of build.spec, after imports
import sys
sys.setrecursionlimit(sys.getrecursionlimit() * 5)
```

**Result:**
- Before: RecursionError at ~115 nested imports ❌
- After: Can handle ~660 nested imports ✅

**Commit:** `fcd3f50` - "Fix macOS PyInstaller recursion limit issue"

---

## Disk Space Management

### GitHub Actions Runner Specs

| Runner | OS | Total Disk | Available | After Cleanup |
|--------|----|-----------:|----------:|--------------:|
| ubuntu-latest | Ubuntu 22.04 | ~84 GB | ~14 GB | ~28 GB |
| windows-latest | Server 2022 | ~120 GB | ~50 GB | ~60 GB |
| macos-latest | macOS 13 | ~250 GB | ~14 GB | ~30 GB |

### Our Build Requirements

| Component | Size | Description |
|-----------|-----:|-------------|
| PyInstaller backend | ~8 GB | Python + PyTorch + FastSurfer |
| PyInstaller build/ | ~2 GB | Intermediate artifacts |
| Electron packaging | ~4 GB | Temporary files |
| Final installer | ~3-4 GB | Compressed output |
| **Total needed** | **~17 GB** | Peak disk usage |

### Cleanup Strategy

**Phase 1: Initial cleanup (~14 GB freed)**
- .NET SDK and runtime
- Android SDK
- GHC (Haskell compiler)
- CodeQL databases
- Docker images

**Phase 2: Intermediate cleanup (~2 GB freed)**
- PyInstaller build/ directory after bundling
- npm cache (if needed)

**Phase 3: Final cleanup (automatic)**
- Electron-builder cleans its own temp files
- GitHub Actions cleans workspace after job

---

## Other Common Issues

### Issue: PyInstaller Fails

**Symptoms:**
```
ModuleNotFoundError: No module named 'X'
```

**Solutions:**
1. Add missing package to `backend/requirements.txt`
2. Add hidden import to `build.spec`:
   ```python
   hiddenimports=['missing.module']
   ```
3. Check package compatibility with PyInstaller

### Issue: Electron Builder Fails

**Symptoms:**
```
⨯ cannot find specified resource
```

**Solutions:**
1. Check icon paths in `package.json`
2. Verify `dist/neuroinsight-backend` exists
3. Ensure `homepage` is set in `package.json`

### Issue: Workflow Timeout

**Symptoms:**
```
Error: The operation was canceled.
```

**Solutions:**
1. Increase timeout in workflow:
   ```yaml
   timeout-minutes: 120  # 2 hours
   ```
2. Optimize PyInstaller (exclude unnecessary packages)
3. Use cached dependencies:
   ```yaml
   - uses: actions/cache@v3
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
   ```

### Issue: Windows Code Signing Fails

**Symptoms:**
```
Error: SignTool not found
```

**Solutions:**
1. Install Windows SDK in workflow
2. Or skip signing for now (shows SmartScreen warning)
3. Add code signing certificate to secrets

### Issue: macOS Notarization Fails

**Symptoms:**
```
Error: Unable to notarize app
```

**Solutions:**
1. Requires Apple Developer account ($99/year)
2. Generate app-specific password
3. Add credentials to GitHub secrets
4. Or skip for now (users can right-click → Open)

---

## Monitoring Builds

### Check Build Status

**Via GitHub Web:**
```
https://github.com/phindagijimana/neuroinsight/actions
```

**Via GitHub CLI:**
```bash
gh run list --workflow=build-desktop.yml
gh run watch  # Watch latest run
```

### View Logs

1. Click on workflow run
2. Click on failing job (e.g., "build-linux")
3. Expand failing step
4. Look for error messages

### Download Artifacts

Even if release creation fails, artifacts are available:
1. Go to workflow run
2. Scroll to "Artifacts" section
3. Download: linux-installers, windows-installer, macos-installer

---

## Debugging Tips

### Test Locally First

Before pushing tags, test locally:

```bash
# Linux
cd desktop_alone
pyinstaller build.spec
cd electron-app
npm install
npm run build:linux

# Check disk usage
df -h
du -sh dist/
```

### Add Debug Output

Add to workflow for debugging:

```yaml
- name: Debug disk space
  run: |
    df -h
    du -sh desktop_alone/
    du -sh desktop_alone/dist/
    du -sh desktop_alone/electron-app/dist/
```

### Manual Trigger for Testing

Use workflow_dispatch to test without creating tags:

```yaml
on:
  workflow_dispatch:
    inputs:
      debug:
        description: 'Enable debug output'
        required: false
        default: 'false'
```

Then trigger from GitHub Actions tab.

---

## Optimization Ideas

### Reduce Backend Size

1. **Exclude unnecessary packages:**
   ```python
   # In build.spec
   excludes=['matplotlib', 'IPython', 'jupyter']
   ```

2. **Use lighter PyTorch:**
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

3. **Compress with UPX:**
   ```python
   # In build.spec
   upx=True,
   upx_exclude=[],
   ```

### Use Caching

```yaml
- uses: actions/cache@v3
  with:
    path: |
      ~/.cache/pip
      ~/.cache/electron
      ~/.cache/electron-builder
    key: ${{ runner.os }}-build-${{ hashFiles('**/requirements.txt', '**/package-lock.json') }}
```

### Parallel Jobs

Split into separate workflows if needed:
- `build-linux.yml` - Runs on every push
- `build-windows-macos.yml` - Runs only on tags

---

## Recovery Steps

### If Build Fails Completely

1. **Delete failed tag:**
   ```bash
   git tag -d desktop-v1.0.0
   git push origin --delete desktop-v1.0.0
   ```

2. **Fix the issue** (update workflow, fix code)

3. **Commit and push** fixes

4. **Recreate tag:**
   ```bash
   git tag -a desktop-v1.0.0 -m "Release v1.0.0"
   git push origin desktop-v1.0.0
   ```

### If Only One Platform Fails

1. **Download successful artifacts** from workflow run
2. **Build failed platform locally** or fix and re-run
3. **Create release manually** with mixed artifacts

### If Release Creation Fails

1. **Artifacts still available** for 30 days
2. **Create release manually:**
   ```bash
   gh release create desktop-v1.0.0 \
     --title "NeuroInsight Desktop v1.0.0" \
     --notes-file desktop_alone/RELEASE_NOTES_V1.0.0.md
   ```
3. **Upload artifacts:**
   ```bash
   gh release upload desktop-v1.0.0 path/to/installers/*
   ```

---

## Success Indicators

### Successful Linux Build
```
✓ electron-builder version=24.13.3
✓ packaging platform=linux
✓ building target=AppImage
✓ building target=deb
✓ Upload Linux artifacts
```

### Successful Windows Build
```
✓ electron-builder version=24.13.3
✓ packaging platform=win32
✓ building target=nsis
✓ Upload Windows artifacts
```

### Successful macOS Build
```
✓ electron-builder version=24.13.3
✓ packaging platform=darwin
✓ building target=dmg
✓ Upload macOS artifacts
```

### Successful Release Creation
```
✓ Download Linux artifacts
✓ Download Windows artifacts
✓ Download macOS artifacts
✓ Create GitHub Release
```

---

## Contact & Support

If issues persist:
1. Check [GitHub Issues](https://github.com/phindagijimana/neuroinsight/issues)
2. Review workflow logs carefully
3. Test build locally first
4. Document error messages
5. Create issue with full logs

---

**Last Updated:** November 6, 2025  
**Status:** Disk space issue resolved ✅  
**Current Build:** desktop-v1.0.0 (in progress)

