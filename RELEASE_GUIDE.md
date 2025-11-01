# 🚀 Release Guide - Creating New NeuroInsight Releases

## How to Create a New Release

### Method 1: Automatic (Recommended) 🤖

GitHub Actions will automatically build installers when you create a version tag!

**Steps:**

1. **Update version in code:**
   ```bash
   # Update version in hippo_desktop/package.json
   # Change "version": "1.0.0" to "version": "1.1.0"
   ```

2. **Commit changes:**
   ```bash
   git add hippo_desktop/package.json
   git commit -m "Bump version to 1.1.0"
   git push
   ```

3. **Create and push a version tag:**
   ```bash
   # Create tag
   git tag -a v1.1.0 -m "Release version 1.1.0

   Changes:
   - Added new feature X
   - Fixed bug Y
   - Improved performance Z"
   
   # Push tag to GitHub
   git push origin v1.1.0
   ```

4. **Wait for builds (15-20 minutes):**
   - GitHub Actions automatically:
     ✅ Builds macOS DMG
     ✅ Builds Windows installer
     ✅ Builds Linux packages
     ✅ Creates GitHub Release
     ✅ Uploads all installers

5. **Check release:**
   - Go to: `https://github.com/YOUR_USERNAME/neuroinsight/releases`
   - Your new release is live!
   - Users can download immediately!

**That's it!** 🎉

---

### Method 2: Manual (Backup option)

If GitHub Actions fails or you want manual control:

1. **Build installers locally:**
   ```bash
   # On your desktop machine
   cd hippo_desktop
   
   # macOS
   npm run dist:mac
   
   # Windows  
   npm run dist:win
   
   # Linux
   npm run dist:linux
   ```

2. **Create tag:**
   ```bash
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   ```

3. **Create release on GitHub:**
   - Go to: `https://github.com/YOUR_USERNAME/neuroinsight/releases/new`
   - Choose tag: `v1.1.0`
   - Add release notes
   - Upload installers from `dist/` folder
   - Click "Publish release"

---

## 📋 Release Checklist

Before creating a release:

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version number bumped in `package.json`
- [ ] Icons look correct
- [ ] Test installers on all platforms
- [ ] No sensitive data in code
- [ ] License file present

---

## 🎯 Version Numbering

Use Semantic Versioning (semver): `MAJOR.MINOR.PATCH`

**Examples:**
- `v1.0.0` - First stable release
- `v1.1.0` - New features added
- `v1.1.1` - Bug fixes
- `v2.0.0` - Breaking changes

**What to bump:**
- **MAJOR**: Breaking changes (v1.0.0 → v2.0.0)
- **MINOR**: New features (v1.0.0 → v1.1.0)
- **PATCH**: Bug fixes (v1.0.0 → v1.0.1)

---

## 📝 Release Notes Template

```markdown
## ✨ What's New

- Added feature X
- Improved Y performance by 50%
- New Z visualization

## 🐛 Bug Fixes

- Fixed crash when uploading large files
- Resolved GPU detection issue on Windows
- Corrected asymmetry calculation

## 📈 Improvements

- Faster startup time
- Better error messages
- Updated dependencies

## 🔧 Technical

- Upgraded Electron to v28
- Updated FastSurfer integration
- Improved Docker management

## 📥 Installation

Download the installer for your platform below.

## 📋 System Requirements

**Minimum**: 4 cores, 16GB RAM, 30GB disk
**Recommended**: 8+ cores, 32GB RAM, 100GB SSD, NVIDIA GPU
```

---

## 🌟 Example: Full Release Workflow

**Scenario**: You've added a new feature and want to release v1.1.0

```bash
# 1. Update version
cd hippo_desktop
# Edit package.json: "version": "1.1.0"

# 2. Update changelog
# Edit CHANGELOG.md or create release notes

# 3. Commit
git add .
git commit -m "Release v1.1.0: Added feature X"
git push

# 4. Create tag
git tag -a v1.1.0 -m "Release v1.1.0

New Features:
- Feature X: Allows users to do Y
- Feature Z: Improves performance

Bug Fixes:
- Fixed issue #123
- Resolved GPU detection

Breaking Changes:
- None

Migration Guide:
- No changes needed"

# 5. Push tag
git push origin v1.1.0

# 6. GitHub Actions automatically:
#    - Builds for macOS, Windows, Linux
#    - Creates release
#    - Uploads installers
#
# 7. Wait 15-20 minutes
# 8. Check: https://github.com/YOUR_USERNAME/neuroinsight/releases
# 9. Done! Users can download!
```

---

## 📊 Release Statistics

After release, you can track:

- **Downloads per platform**: See which OS is most popular
- **Total downloads**: Track adoption
- **Issues**: Monitor bug reports
- **Stars**: See community interest

**View at**: `https://github.com/YOUR_USERNAME/neuroinsight/releases`

---

## 🎁 Pre-releases (Beta versions)

For testing before stable release:

```bash
# Create pre-release tag
git tag -a v1.1.0-beta.1 -m "Beta release"
git push origin v1.1.0-beta.1

# On GitHub, mark as "Pre-release"
```

Users see:
```
v1.1.0-beta.1 (Pre-release)
⚠️ This is a beta version for testing
```

---

## 🔄 Updating a Release

If you need to fix something after release:

**Option 1: Patch release**
```bash
# Preferred: Create new version
git tag v1.1.1
git push origin v1.1.1
```

**Option 2: Update existing**
```bash
# Delete tag locally and remotely
git tag -d v1.1.0
git push origin :refs/tags/v1.1.0

# Create new tag
git tag -a v1.1.0 -m "Updated release"
git push origin v1.1.0
```

---

## 🎯 Auto-Update Configuration

Your app can check for new releases automatically!

Already configured in `hippo_desktop/package.json`:

```json
"publish": {
  "provider": "github",
  "owner": "YOUR_USERNAME",
  "repo": "neuroinsight"
}
```

Users will see:
```
┌────────────────────────────────┐
│  Update Available!             │
│  NeuroInsight v1.1.0          │
│                                │
│  • Added feature X             │
│  • Fixed bug Y                 │
│                                │
│  [Download] [Install Later]    │
└────────────────────────────────┘
```

---

## 📦 What Users See

**GitHub Releases Page:**

```
📦 NeuroInsight Releases

┌─────────────────────────────────────────┐
│ v1.1.0 - Latest                         │
│ Released 2 hours ago                    │
│                                         │
│ ✨ What's New                           │
│ - Feature X                             │
│ - Bug fixes                             │
│                                         │
│ 📥 Assets (5)                           │
│                                         │
│ NeuroInsight-v1.1.0.dmg         54MB   │ ← 1-click download
│ NeuroInsight-Setup-v1.1.0.exe   45MB   │ ← 1-click download
│ NeuroInsight-v1.1.0.AppImage    60MB   │ ← 1-click download
│ neuroinsight_v1.1.0_amd64.deb   40MB   │ ← 1-click download
│ neuroinsight-v1.1.0.x86_64.rpm  42MB   │ ← 1-click download
│                                         │
│ 📊 Downloads: 1,234                     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ v1.0.0                                  │
│ Released 1 month ago                    │
│ 📊 Downloads: 5,678                     │
└─────────────────────────────────────────┘
```

---

## 🎓 Tips

**Best Practices:**
1. ✅ Test on all platforms before release
2. ✅ Write clear release notes
3. ✅ Include screenshots/GIFs
4. ✅ Link to documentation
5. ✅ Mention breaking changes
6. ✅ Thank contributors

**Avoid:**
1. ❌ Deleting releases (users may be downloading)
2. ❌ Skipping version numbers
3. ❌ Releasing without testing
4. ❌ Missing release notes
5. ❌ Forgetting to update version number

---

## 🚀 You're Ready!

Your release workflow is set up!

**To create first release:**
```bash
git tag -a v1.0.0 -m "First stable release!"
git push origin v1.0.0
```

**Watch the magic happen:**
- GitHub Actions builds installers
- Release page appears
- Users can download!

🎉 **Congratulations - You're distributing professional software!**

