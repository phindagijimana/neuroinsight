# 🚀 Deploy v1.3.5 NOW - Quick Guide

## What Was Fixed

### Critical Bug #1: Metrics Not Saving ✅
- **Problem**: Jobs completed but metrics never appeared in UI
- **Cause**: UUID objects couldn't bind to SQLite database
- **Fix**: Convert UUID to string in `metric_service.py`
- **Result**: Metrics now save and display correctly

### Critical Bug #2: Docker Mount Failures ✅
- **Problem**: FastSurfer couldn't access files on macOS
- **Cause**: Using container paths instead of host paths
- **Fix**: Detect desktop mode and use actual file paths
- **Result**: FastSurfer can now mount volumes properly on macOS

---

## Deploy Steps (5 minutes)

```bash
# 1. Navigate to project
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo

# 2. Stage all changes
git add desktop_alone/backend/services/metric_service.py \
        desktop_alone/pipeline/processors/mri_processor.py \
        desktop_alone/electron-app/package.json \
        desktop_alone/V1.3.5_FIX_SUMMARY.md \
        desktop_alone/DEPLOY_v1.3.5_NOW.md

# 3. Commit with descriptive message
git commit -m "fix(desktop): v1.3.5 critical bugfixes

- Fix SQLite UUID binding error preventing metrics from saving
- Fix Docker volume mount paths for desktop mode
- Metrics now save successfully and display in UI
- FastSurfer can run on macOS with proper volume mounts

Closes: #metrics-not-saving #docker-mount-failure
Version: v1.3.5"

# 4. Create and push tag
git tag -a desktop-v1.3.5 -m "NeuroInsight Desktop v1.3.5 - Critical Bugfixes

Fixes:
- SQLite UUID binding error (metrics not saving)
- Docker volume mount issues (FastSurfer file access)

This is a hotfix release for v1.3.4."

git push origin main
git push origin desktop-v1.3.5

# 5. Done! Monitor GitHub Actions for builds
```

---

## After Deployment

### 1. Monitor GitHub Actions (~20 minutes)
Watch: https://github.com/YOUR_ORG/hippo/actions

Expected artifacts:
- ✅ `NeuroInsight-1.3.5.AppImage` (Linux x64)
- ✅ `NeuroInsight-Setup-1.3.5.exe` (Windows x64)
- ✅ `NeuroInsight-1.3.5.dmg` (macOS Universal)

### 2. Download and Test
```bash
# Download from GitHub Releases
cd ~/Downloads
curl -LO https://github.com/YOUR_ORG/hippo/releases/download/desktop-v1.3.5/NeuroInsight-1.3.5.dmg

# Install
open NeuroInsight-1.3.5.dmg
# Drag to Applications

# Test with real data
open -a NeuroInsight
# Upload MRI scan
# Verify metrics appear in UI
```

### 3. Verify Fixes

#### Check 1: Metrics Save Successfully
```bash
# Check logs after job completes
tail -f ~/Library/Logs/NeuroInsight/main.log | grep metrics_created_bulk

# Expected: "metrics_created_bulk" log entry with count=1
# Should NOT see: "InterfaceError" or "Error binding parameter"
```

#### Check 2: Docker Mounts Work
```bash
# Check logs during FastSurfer execution
tail -f ~/Library/Logs/NeuroInsight/main.log | grep desktop_mode_paths

# Expected: "desktop_mode_paths" with actual host paths
# Should NOT see: "mounts denied" or "/data/uploads"
```

#### Check 3: UI Shows Metrics
- Open NeuroInsight app
- Upload T1w MRI scan
- Wait for processing to complete
- **Verify**: Hippocampal volumes appear in UI
- **Verify**: Asymmetry index is displayed
- **Verify**: Job status shows 100% complete

---

## If Something Goes Wrong

### Rollback (1 minute)
```bash
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo

# Delete the tag
git tag -d desktop-v1.3.5
git push origin :refs/tags/desktop-v1.3.5

# Revert commits
git revert HEAD~3..HEAD
git push origin main

# Users can download v1.3.3 or v1.3.2
```

### Get Help
- Check logs: `~/Library/Logs/NeuroInsight/main.log`
- Review fix summary: `desktop_alone/V1.3.5_FIX_SUMMARY.md`
- Test with mock data first (no Docker required)

---

## Success Criteria

✅ **Immediate** (within 1 hour):
- GitHub Actions builds complete successfully
- Local test shows metrics in UI
- No SQLite binding errors in logs

✅ **Short-term** (within 24 hours):
- At least 3 successful real processing runs
- No Docker mount errors reported
- Metrics persist after app restart

✅ **Long-term** (within 1 week):
- No rollback required
- Positive user feedback
- Consider v1.3.5 the new stable release

---

## What's Next?

After v1.3.5 is stable and deployed:

1. **Monitor** for 24-48 hours
2. **Collect** user feedback
3. **Plan** v1.4.0 with new features:
   - Native ARM64 FastSurfer support
   - Progress streaming
   - Enhanced error messages
   - Job cancellation

---

## Quick Reference

| Item | Value |
|------|-------|
| Version | v1.3.5 |
| Type | Hotfix |
| Priority | **CRITICAL** |
| Fixes | UUID binding + Docker mounts |
| Upgrade | Recommended for all users |
| Downtime | None (new installers only) |

---

## Questions?

- Detailed fix info: `V1.3.5_FIX_SUMMARY.md`
- Deployment steps: This file
- Logs location: `~/Library/Logs/NeuroInsight/main.log` (macOS)



