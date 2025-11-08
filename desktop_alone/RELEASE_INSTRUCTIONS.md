# How to Create GitHub Release

## ✅ Automated Release (Recommended)

**Status:** Tag `desktop-v1.0.0` has been pushed! 🎉

The GitHub Actions workflow is now building installers for all platforms automatically.

### Monitor the Build

1. **Go to GitHub Actions:**
   ```
   https://github.com/phindagijimana/neuroinsight/actions
   ```

2. **Find the workflow run:**
   - Look for "Build Desktop Installers"
   - Should show "desktop-v1.0.0" tag
   - Status: Running (yellow) → Success (green)

3. **Wait for completion:**
   - Linux build: ~30 minutes
   - Windows build: ~40 minutes  
   - macOS build: ~50 minutes
   - **Total: ~1-1.5 hours**

### What Happens Automatically

The workflow will:
1. ✅ Build Linux AppImage + DEB
2. ✅ Build Windows .exe installer
3. ✅ Build macOS .dmg installer
4. ✅ Generate SHA256 checksums for all
5. ✅ Create GitHub Release automatically
6. ✅ Upload all installers to the release

### After Build Completes

1. **Check the Release:**
   ```
   https://github.com/phindagijimana/neuroinsight/releases/tag/desktop-v1.0.0
   ```

2. **Verify all files are present:**
   - NeuroInsight-1.0.0.AppImage
   - neuroinsight-standalone_1.0.0_amd64.deb
   - checksums-linux.txt
   - NeuroInsight-Setup-1.0.0.exe
   - checksums-windows.txt
   - NeuroInsight-1.0.0.dmg
   - checksums-macos.txt

3. **Download and test** each installer

## 🔧 Manual Release (If Automated Fails)

If the automated workflow fails or you want to create a Linux-only release immediately:

### Option A: Via GitHub Web Interface

1. **Go to Releases:**
   ```
   https://github.com/phindagijimana/neuroinsight/releases/new
   ```

2. **Fill in details:**
   - **Tag:** Select `desktop-v1.0.0` (existing tag)
   - **Release title:** `NeuroInsight Desktop v1.0.0`
   - **Description:** Copy from `desktop_alone/RELEASE_NOTES_V1.0.0.md`

3. **Upload Linux installers:**
   ```
   desktop_alone/electron-app/dist/NeuroInsight-1.0.0.AppImage
   desktop_alone/electron-app/dist/neuroinsight-standalone_1.0.0_amd64.deb
   desktop_alone/electron-app/dist/checksums-linux.txt
   ```

4. **Click "Publish release"**

### Option B: Using GitHub CLI (if installed)

```bash
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo

# Create release
gh release create desktop-v1.0.0 \
  --title "NeuroInsight Desktop v1.0.0" \
  --notes-file desktop_alone/RELEASE_NOTES_V1.0.0.md \
  desktop_alone/electron-app/dist/NeuroInsight-1.0.0.AppImage \
  desktop_alone/electron-app/dist/neuroinsight-standalone_1.0.0_amd64.deb \
  desktop_alone/electron-app/dist/checksums-linux.txt
```

### Option C: Using curl/API

```bash
# Get your GitHub token from https://github.com/settings/tokens
export GITHUB_TOKEN="your_token_here"

# Create release
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/phindagijimana/neuroinsight/releases \
  -d '{
    "tag_name": "desktop-v1.0.0",
    "name": "NeuroInsight Desktop v1.0.0",
    "body": "See RELEASE_NOTES_V1.0.0.md for details",
    "draft": false,
    "prerelease": false
  }'

# Upload assets (get upload_url from previous response)
# Then upload each file...
```

## 📊 Build Status Checks

### Check Workflow Status
```bash
# If gh CLI is installed
gh run list --workflow=build-desktop.yml

# Or visit:
https://github.com/phindagijimana/neuroinsight/actions/workflows/build-desktop.yml
```

### View Build Logs
1. Click on the workflow run
2. Click on each job (build-linux, build-windows, build-macos)
3. View logs for debugging

### Download Artifacts Early
If you want to test before the release is created:
1. Go to the workflow run
2. Scroll to "Artifacts" section
3. Download:
   - linux-installers
   - windows-installer
   - macos-installer

## 🔍 Troubleshooting

### Build Fails on Windows/macOS

**Common Issues:**
1. **PyInstaller fails:** May need Windows/macOS specific fixes
2. **electron-builder fails:** Check icon paths are correct
3. **Timeout:** Builds can take 1+ hours

**Solutions:**
- Check workflow logs for specific errors
- May need to adjust `build.spec` for Windows/macOS
- Increase timeout in workflow if needed

### Build Succeeds but No Release Created

**Check:**
1. Tag format: Must be `desktop-v*` pattern
2. Workflow permissions: Needs `GITHUB_TOKEN` write access
3. Branch protection: May block automated releases

**Fix:**
- Create release manually using Option A above
- Check repository settings → Actions → Workflow permissions

### Installers Too Large for GitHub

GitHub has 2 GB file size limit for releases.

**Solutions:**
1. **Use Git LFS:** For files >100 MB
2. **External hosting:** Upload to AWS S3, DigitalOcean Spaces
3. **Split archives:** Create multi-part archives

## 📝 Post-Release Checklist

After release is created:

- [ ] Test AppImage on Ubuntu 22.04/24.04
- [ ] Test DEB on Debian 12
- [ ] Test Windows .exe on Windows 10/11
- [ ] Test macOS .dmg on Intel and Apple Silicon
- [ ] Verify all checksums
- [ ] Update main README with download links
- [ ] Announce on social media/mailing lists
- [ ] Monitor GitHub Issues for user feedback

## 🔄 Future Releases

### Patch Release (v1.0.1)
```bash
git tag -a desktop-v1.0.1 -m "Bug fixes"
git push origin desktop-v1.0.1
```

### Minor Release (v1.1.0)
```bash
git tag -a desktop-v1.1.0 -m "New features"
git push origin desktop-v1.1.0
```

### Major Release (v2.0.0)
```bash
git tag -a desktop-v2.0.0 -m "Breaking changes"
git push origin desktop-v2.0.0
```

All will trigger the same automated workflow!

## 🎯 Quick Commands

### Check if tag exists
```bash
git tag -l "desktop-v*"
```

### Delete tag (if need to recreate)
```bash
git tag -d desktop-v1.0.0              # Delete locally
git push origin --delete desktop-v1.0.0 # Delete remote
```

### View tag details
```bash
git show desktop-v1.0.0
```

### List all releases
```bash
gh release list  # or visit /releases on GitHub
```

## 📍 Current Status

**Tag Pushed:** ✅ `desktop-v1.0.0`  
**Workflow Triggered:** ✅ Check Actions tab  
**Estimated Completion:** ~1-1.5 hours from tag push  
**Expected Outcome:** Automatic release with all installers

---

**Next:** Monitor https://github.com/phindagijimana/neuroinsight/actions for build progress!

