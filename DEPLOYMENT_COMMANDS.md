# 🚀 Complete Deployment Commands

## ✅ STEP 1 & 2: DONE!

Git configured and first commit created! ✓

---

## 🌐 STEP 3: Create GitHub Repository

### Option A: Via GitHub Website (Recommended)

1. **Go to GitHub**:
   ```
   https://github.com/new
   ```

2. **Fill in details**:
   ```
   Repository name: neuroinsight
   Description: Advanced Hippocampal Asymmetry Analysis Platform
   Visibility: ☑ Private (or Public if you prefer)
   
   ⚠️ DO NOT check any of these:
   ☐ Add a README file
   ☐ Add .gitignore
   ☐ Choose a license
   
   (We already have these files!)
   ```

3. **Click**: "Create repository"

4. **Copy the repository URL** shown on the next page:
   ```
   https://github.com/YOUR_USERNAME/neuroinsight.git
   ```

### Option B: Via GitHub CLI (If installed)

```bash
# If you have gh CLI installed
gh repo create neuroinsight --private --source=. --remote=origin --push
```

---

## ⬆️ STEP 4: Push to GitHub

**After creating the repository on GitHub**, run these commands:

```bash
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo

# Add GitHub as remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/neuroinsight.git

# Verify remote was added
git remote -v

# Rename branch to main (GitHub standard)
git branch -M main

# Push code to GitHub
git push -u origin main
```

**You'll be prompted for GitHub credentials:**
- Username: Your GitHub username
- Password: Your GitHub Personal Access Token (NOT your GitHub password)

### 🔑 Creating a Personal Access Token (if needed):

1. Go to: https://github.com/settings/tokens
2. Click: "Generate new token" → "Generate new token (classic)"
3. Name: "NeuroInsight Deploy"
4. Select scopes:
   - ☑ repo (Full control of private repositories)
   - ☑ workflow (Update GitHub Actions workflows)
5. Click: "Generate token"
6. **COPY THE TOKEN** (you won't see it again!)
7. Use this token as your password when pushing

---

## 🏷️ STEP 5: Create First Release

**After pushing to GitHub**, create a release:

```bash
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo

# Create version tag
git tag -a v1.0.0 -m "NeuroInsight v1.0.0 - First Stable Release

🎉 First stable release of NeuroInsight Desktop!

✨ Features:
- One-click desktop installation for Windows, macOS, and Linux
- Automatic Docker service management
- GPU acceleration support (10-20x faster processing)
- Professional desktop experience with system tray integration
- Real-time processing updates
- Interactive hippocampal visualization
- Offline processing capability

🧠 Analysis Features:
- FastSurfer whole-brain segmentation
- Hippocampal subfield analysis
- Asymmetry index calculation
- Volume measurements
- Statistical analysis

📊 System Requirements:
Minimum: 4 cores, 16GB RAM, 30GB disk
Recommended: 8+ cores, 32GB RAM, 100GB SSD, NVIDIA GPU

🚀 Desktop Platforms:
- macOS 10.15+ (Intel and Apple Silicon)
- Windows 10/11 (64-bit)
- Linux (Ubuntu 20.04+, Fedora, Debian)

📦 Installation:
Download the installer for your platform and double-click to install!

🙏 Thanks to:
- FastSurfer team for neuroimaging tools
- FreeSurfer team for analysis algorithms
- Open source community"

# Push tag to GitHub
git push origin v1.0.0
```

---

## ⏰ STEP 6: Wait for Builds (15-20 minutes)

After pushing the tag, GitHub Actions will automatically:

1. **Build macOS installer** (~5 min)
   - Creates .dmg file
   - Creates .zip file
   
2. **Build Windows installer** (~5 min)
   - Creates setup .exe
   - Creates portable .exe
   
3. **Build Linux packages** (~5 min)
   - Creates .AppImage
   - Creates .deb package
   - Creates .rpm package

**Monitor progress**:
```
https://github.com/YOUR_USERNAME/neuroinsight/actions
```

You'll see a workflow running called "Build and Release Desktop Applications"

---

## ✅ STEP 7: Verify Release

Once builds complete, check:

```
https://github.com/YOUR_USERNAME/neuroinsight/releases
```

You should see:
```
📦 NeuroInsight v1.0.0

Assets (5):
🍎 NeuroInsight-v1.0.0.dmg
🍎 NeuroInsight-v1.0.0-mac.zip
🪟 NeuroInsight-Setup-v1.0.0.exe
🪟 NeuroInsight-Portable-v1.0.0.exe
🐧 NeuroInsight-v1.0.0.AppImage
📦 neuroinsight_v1.0.0_amd64.deb
📦 neuroinsight-v1.0.0.x86_64.rpm
```

---

## 🎉 STEP 8: Share With Users!

**Your download page is now live!**

Share this link:
```
https://github.com/YOUR_USERNAME/neuroinsight/releases/latest
```

Or for a specific version:
```
https://github.com/YOUR_USERNAME/neuroinsight/releases/tag/v1.0.0
```

---

## 📝 Quick Reference

### To create future releases:

```bash
# Update version in hippo_desktop/package.json
# Then:

git add .
git commit -m "Bump version to v1.1.0"
git push

git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0

# Wait 15-20 minutes
# New release appears automatically!
```

---

## 🐛 Troubleshooting

### If GitHub Actions fails:

1. **Check workflow logs**:
   ```
   https://github.com/YOUR_USERNAME/neuroinsight/actions
   ```

2. **Common issues**:
   - Icon files missing → They're already created! ✓
   - package.json errors → Already configured! ✓
   - Permission issues → Use Personal Access Token

3. **Re-run workflow**:
   - Go to failed workflow
   - Click "Re-run all jobs"

### If push is rejected:

```bash
# Make sure you're using Personal Access Token, not password
# GitHub disabled password authentication in 2021

# Get token from: https://github.com/settings/tokens
```

### If builds succeed but no installers:

```bash
# Check the workflow file exists:
ls -la .github/workflows/release.yml

# Should show: release.yml ✓
```

---

## 🎯 Success Checklist

- [ ] Git configured
- [ ] First commit created
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Release tag created
- [ ] GitHub Actions builds completed
- [ ] Installers available on releases page
- [ ] Download link shared with users

---

## 🎊 You're Done!

Your desktop application is now professionally distributed on GitHub!

Users can:
✅ Download with one click
✅ Install with one click
✅ Launch with one click

Just like VS Code, Atom, Signal, and other professional apps!

**Congratulations!** 🎉

