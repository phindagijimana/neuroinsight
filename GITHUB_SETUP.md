# GitHub Setup Guide for NeuroInsight

## 🎯 Quick Setup

### Step 1: Initialize Git (if not already done)

```bash
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo

# Initialize Git repository
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: NeuroInsight with Desktop Application"
```

### Step 2: Create GitHub Repository

**Option A: Via GitHub Website (Easiest)**

1. Go to: https://github.com/new
2. Repository name: `neuroinsight` (or `hippo`)
3. Description: "Advanced Hippocampal Asymmetry Analysis Platform"
4. Choose: **Private** (recommended initially) or Public
5. **DO NOT** initialize with README (you already have one)
6. Click "Create repository"

**Option B: Via GitHub CLI**

```bash
# Install GitHub CLI if not available
# Then:
gh repo create neuroinsight --private --source=. --remote=origin
```

### Step 3: Connect Local Repository to GitHub

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/neuroinsight.git

# Or if using SSH:
git remote add origin git@github.com:YOUR_USERNAME/neuroinsight.git

# Verify remote
git remote -v
```

### Step 4: Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

---

## 📁 What Will Be Uploaded

### ✅ Included in Git

```
neuroinsight/
├── backend/              ✅ FastAPI application
├── frontend/             ✅ React UI (build files excluded)
├── workers/              ✅ Celery workers
├── pipeline/             ✅ Processing pipeline
├── hippo_desktop/        ✅ Desktop application
│   ├── src/             ✅ Source code
│   ├── assets/          ✅ Icons
│   ├── build/           ✅ Icon files only
│   ├── config/          ✅ Templates
│   ├── scripts/         ✅ Build scripts
│   ├── *.md             ✅ Documentation
│   └── package.json     ✅ Configuration
├── docker-compose.yml    ✅ Service orchestration
├── README*.md            ✅ All documentation
└── .gitignore            ✅ Git configuration
```

### ❌ Excluded from Git (via .gitignore)

```
❌ node_modules/          (Too large, can reinstall)
❌ venv/                  (Virtual environment)
❌ data/uploads/*         (User data)
❌ data/outputs/*         (Processing results)
❌ logs/*.log             (Runtime logs)
❌ *.sif                  (Large container images)
❌ instance-data/         (Runtime database/minio data)
❌ _trash/                (Archived files)
❌ .env                   (Secrets)
❌ license.txt            (FreeSurfer license - sensitive)
```

---

## 🔒 Security Best Practices

### Before Pushing to GitHub

**1. Remove Sensitive Data**

Check for passwords, API keys, tokens:

```bash
# Search for common secrets
grep -r "password" --include="*.py" --include="*.js" .
grep -r "api_key" --include="*.py" --include="*.js" .
grep -r "secret" --include="*.py" --include="*.js" .
```

**2. Use Environment Variables**

Instead of hardcoded secrets, use `.env` files (which are gitignored):

```python
# ✗ BAD
DATABASE_PASSWORD = "mypassword123"

# ✓ GOOD
import os
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
```

**3. Create .env.example**

```bash
# .env.example (safe to commit)
DATABASE_PASSWORD=your_password_here
API_KEY=your_api_key_here
```

---

## 📦 Repository Size Optimization

### Current Size Estimate

```
Source code:           ~5MB
Documentation:         ~500KB
Icons/assets:          ~200KB
Dependencies:          Not included (gitignored)

Total Git repo size:   ~6MB ✅ (Very reasonable!)
```

### If Repo Gets Too Large

**Use Git LFS for Large Files:**

```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.sif"
git lfs track "*.nii.gz"
git lfs track "*.dmg"
git lfs track "*.exe"

# Add .gitattributes
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

---

## 🚀 Recommended Repository Structure

### Public vs Private

**Start Private, Go Public Later:**

```
Phase 1: Private Repository
  - Develop and test
  - Remove any sensitive data
  - Polish documentation
  - Add license

Phase 2: Public Repository
  - Make repository public
  - Add contributing guidelines
  - Add code of conduct
  - Enable GitHub Pages for docs
```

### Repository Settings

**Recommended Settings on GitHub:**

1. **About Section**:
   - Description: "Advanced Hippocampal Asymmetry Analysis Platform with Desktop Application"
   - Website: Your project URL
   - Topics: `neuroscience`, `mri`, `medical-imaging`, `electron`, `fastapi`, `brain-analysis`

2. **Features**:
   - ✅ Issues (for bug tracking)
   - ✅ Discussions (for community)
   - ✅ Wiki (for detailed docs)
   - ✅ Projects (for roadmap)

3. **Actions** (CI/CD):
   - Enable GitHub Actions
   - Auto-build desktop installers

---

## 🔄 CI/CD with GitHub Actions

### Automatic Desktop Builds

Create `.github/workflows/build-desktop.yml`:

```yaml
name: Build Desktop Applications

on:
  push:
    tags:
      - 'v*'  # Trigger on version tags
  workflow_dispatch:  # Manual trigger

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install dependencies
        run: |
          cd hippo_desktop
          npm install
      
      - name: Build macOS
        run: |
          cd hippo_desktop
          npm run dist:mac
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: macos-installer
          path: hippo_desktop/dist/*.dmg

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install dependencies
        run: |
          cd hippo_desktop
          npm install
      
      - name: Build Windows
        run: |
          cd hippo_desktop
          npm run dist:win
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: windows-installer
          path: hippo_desktop/dist/*.exe

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install dependencies
        run: |
          cd hippo_desktop
          npm install
      
      - name: Build Linux
        run: |
          cd hippo_desktop
          npm run dist:linux
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: linux-packages
          path: |
            hippo_desktop/dist/*.AppImage
            hippo_desktop/dist/*.deb
            hippo_desktop/dist/*.rpm

  create-release:
    needs: [build-macos, build-windows, build-linux]
    runs-on: ubuntu-latest
    steps:
      - name: Download all artifacts
        uses: actions/download-artifact@v3
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: |
            macos-installer/*
            windows-installer/*
            linux-packages/*
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Result**: Automatic installers built on every release! 🎉

---

## 📝 Add LICENSE File

### Recommended: MIT License

Create `LICENSE` file:

```text
MIT License

Copyright (c) 2025 NeuroInsight Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🎯 Quick Commands Reference

```bash
# Initial setup
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/neuroinsight.git
git push -u origin main

# Regular workflow
git add .
git commit -m "Description of changes"
git push

# Create a release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Check status
git status
git log --oneline

# View what will be committed
git diff
git diff --staged
```

---

## 🌟 Benefits of GitHub

### For You

✅ **Backup** - Never lose your work
✅ **Version Control** - Track all changes
✅ **Collaboration** - Work with others
✅ **CI/CD** - Automatic builds
✅ **Issue Tracking** - Manage bugs/features
✅ **Documentation** - GitHub Pages, Wiki

### For Users

✅ **Easy Download** - GitHub Releases
✅ **Bug Reports** - GitHub Issues
✅ **Feature Requests** - GitHub Discussions
✅ **Community** - Contributions welcome
✅ **Trust** - Open source transparency

---

## 📊 Example: Public Repository Features

**Once public, you can enable:**

1. **GitHub Pages** (free hosting):
   - Website: `https://your-username.github.io/neuroinsight/`
   - Documentation
   - Download page

2. **Releases**:
   - Users download from: `https://github.com/YOUR_USERNAME/neuroinsight/releases`
   - Automatic changelog
   - Asset uploads (installers)

3. **Community**:
   - Issue templates
   - Pull request templates
   - Contributing guidelines
   - Code of conduct

4. **Badges** (for README):
   ```markdown
   ![Build Status](https://github.com/YOUR_USERNAME/neuroinsight/actions/workflows/build.yml/badge.svg)
   ![License](https://img.shields.io/github/license/YOUR_USERNAME/neuroinsight)
   ![Downloads](https://img.shields.io/github/downloads/YOUR_USERNAME/neuroinsight/total)
   ```

---

## ✅ Checklist Before First Push

- [ ] Created .gitignore file
- [ ] Removed sensitive data (.env, passwords, keys)
- [ ] Added LICENSE file
- [ ] Updated README.md with project description
- [ ] Created .env.example (without secrets)
- [ ] Tested that large files are excluded
- [ ] Created GitHub repository
- [ ] Connected local repo to GitHub remote
- [ ] Made first commit
- [ ] Pushed to GitHub

---

## 🎉 You're Ready!

Your NeuroInsight project is now ready to be connected to GitHub!

**Next steps:**
1. Review the .gitignore file
2. Create GitHub repository
3. Push your code
4. Set up CI/CD (optional)
5. Share with the world! 🚀

