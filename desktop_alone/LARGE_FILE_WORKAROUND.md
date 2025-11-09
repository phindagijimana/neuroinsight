# Large File Workaround - GitHub Release Limits

**Issue**: Desktop app installers exceed GitHub's 2GB file size limit  
**Status**: **Workaround Implemented** ✅

---

## 📊 File Sizes

| Platform | File | Size | GitHub Limit | Status |
|----------|------|------|--------------|--------|
| Linux | NeuroInsight-1.0.0.AppImage | 2.8 GB | 2 GB | ❌ Too Large |
| Windows | NeuroInsight-Setup-1.0.0.exe | ~2.5 GB | 2 GB | ❌ Too Large |
| macOS (x64) | NeuroInsight-1.0.0.dmg | 232 MB | 2 GB | ✅ OK |
| macOS (arm64) | NeuroInsight-1.0.0-arm64.dmg | 228 MB | 2 GB | ✅ OK |

---

## 🚫 The Problem

GitHub Releases have a **2GB per file limit**. Our installers exceed this because they bundle:
- Python backend (~500 MB)
- PyTorch (~1.5 GB)
- FastSurfer models (~500 MB)
- Electron + Chromium (~200 MB)
- Frontend assets (~5 MB)

---

## ✅ Current Workaround (v1.1.2+)

### What We Do:

1. **Build all installers successfully** in GitHub Actions
2. **Upload as artifacts** (available for 30 days)
3. **Create release with:**
   - Checksums only
   - Download instructions
   - Links to artifacts

### How Users Download:

**Step 1:** Go to Actions tab
```
https://github.com/phindagijimana/neuroinsight/actions
```

**Step 2:** Click on latest successful workflow  
Look for: "Desktop Build v15 - Fixed (Frontend Bundled)"

**Step 3:** Scroll to "Artifacts" section

**Step 4:** Download the zip for your platform:
- `neuroinsight-linux.zip` (2.8 GB)
- `neuroinsight-windows.zip` (~2.5 GB)
- `neuroinsight-mac.zip` (460 MB)

**Step 5:** Unzip and install!

---

## 🎯 Long-Term Solutions

### Option 1: External Hosting ⭐ **RECOMMENDED**

Host large files on cloud storage:

**AWS S3:**
```yaml
# Add to workflow after build
- name: Upload to S3
  run: |
    aws s3 cp dist/*.AppImage s3://neuroinsight-releases/
    aws s3 cp dist/*.exe s3://neuroinsight-releases/
```

**Pros:**
- No size limits
- Fast downloads
- Permanent storage
- CDN available

**Cons:**
- Costs money (~$0.023/GB/month storage + bandwidth)
- Requires AWS account

**Cost estimate:**
- Storage: 6 GB × $0.023 = $0.14/month
- Bandwidth: 100 downloads × 6 GB × $0.09 = $54/month
- **Total**: ~$50-100/month depending on usage

---

### Option 2: Reduce File Sizes

Compress/optimize the installers:

**A. Remove unnecessary dependencies:**
```python
# Only include required PyTorch components
pip install torch --index-url https://download.pytorch.org/whl/cpu
# Use CPU-only (saves ~800 MB)
```

**B. Compress AppImage:**
```bash
# Use higher compression
mksquashfs ... -comp xz -Xdict-size 100%
```

**C. Split models from installer:**
- Ship app without models (~1.5 GB)
- Download models on first run

**Pros:**
- Stay within GitHub limits
- Faster downloads

**Cons:**
- May affect functionality
- Requires code changes

---

### Option 3: Git LFS (Large File Storage)

Use Git LFS for release assets:

```bash
git lfs install
git lfs track "*.AppImage"
git lfs track "*.exe"
```

**Pros:**
- Integrated with GitHub
- Versioned files

**Cons:**
- GitHub LFS pricing: $5/month for 50GB storage + bandwidth
- Still has limits (5 GB per file with Pro)

---

### Option 4: Split Archives

Split large files into 2GB chunks:

```bash
# Split
split -b 2000M NeuroInsight-1.0.0.AppImage neuroinsight-part-

# Upload parts to release
# Users rejoin:
cat neuroinsight-part-* > NeuroInsight-1.0.0.AppImage
```

**Pros:**
- Works with GitHub Releases
- No external hosting

**Cons:**
- Complex for users
- Manual reassembly required

---

## 📝 Recommendation

**For Research/Academic Use:**
Use **GitHub Actions Artifacts** (current solution) with 30-day retention.

**For Production/Public Distribution:**
Use **AWS S3 or DigitalOcean Spaces** with CDN.

**For Private/Internal Use:**
Use **institutional storage** or shared network drive.

---

## 🔧 Implementation Guide

### If You Choose External Hosting (S3):

**1. Create S3 bucket:**
```bash
aws s3 mb s3://neuroinsight-releases
aws s3 website s3://neuroinsight-releases --index-document index.html
```

**2. Update workflow:**
```yaml
- name: Upload to S3
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  run: |
    aws s3 sync dist/ s3://neuroinsight-releases/v${{ github.ref_name }}/ \
      --exclude "*" --include "*.AppImage" --include "*.exe" --include "*.dmg"
```

**3. Update release notes:**
```markdown
Download from:
- Linux: https://neuroinsight-releases.s3.amazonaws.com/v1.1.2/NeuroInsight-1.0.0.AppImage
- Windows: https://neuroinsight-releases.s3.amazonaws.com/v1.1.2/NeuroInsight-Setup-1.0.0.exe
```

---

## 🎯 Current Status

**v1.1.2+**: Using GitHub Actions Artifacts workaround  
**Works for**: Small-scale distribution (< 100 downloads/month)  
**Recommended upgrade**: External hosting when usage grows

---

## 📞 Questions?

- **Artifacts expired?** Re-run the workflow or create new tag
- **Need permanent hosting?** Set up S3 or contact IT
- **Want to reduce size?** See "Option 2: Reduce File Sizes" above

---

**Last Updated**: November 9, 2025  
**Workflow Version**: v15  
**Workaround Status**: ✅ Active and Working

