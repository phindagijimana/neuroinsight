# NeuroInsight Web App - User Guide

## 🌐 Accessing the Application

### Current Setup (HPC/Server)

Your NeuroInsight instance is running at:
```
http://localhost:8000
```

**From your local machine** (if accessing remotely):
```bash
# SSH tunnel from your computer
ssh -L 8000:localhost:8000 your_username@hpc_server

# Then open in browser:
http://localhost:8000
```

The application will open in your web browser showing the NeuroInsight interface.

---

## 📋 Interface Overview

### Navigation Bar

```
┌─────────────────────────────────────────────────────────────┐
│  🧠 NeuroInsight    [Home] [Jobs] [Metrics] [Viewer]       │
└─────────────────────────────────────────────────────────────┘
```

- **Home**: Upload new scans and view system status
- **Jobs**: Monitor all processing jobs (pending, running, completed)
- **Metrics**: View statistical analysis and results
- **Viewer**: Interactive 3D brain visualization

---

## 🔄 Complete Workflow

### Step 1: Upload an MRI Scan

1. **Click "Home"** in the navigation bar
2. **Click "Upload MRI Scan"** button or drag & drop
3. **Select your file**:
   - **Supported formats**: `.nii`, `.nii.gz`, `.dcm`
   - **Requirements**: T1-weighted structural MRI
   - **Max size**: 500MB

4. **Wait for upload**:
   ```
   Uploading: sub-01_T1w.nii.gz
   [████████████░░] 85% - 2.3 MB/s
   ```

5. **Processing starts automatically** after upload completes

**Supported File Types:**
- **NIfTI**: `.nii` or `.nii.gz` (most common)
- **DICOM**: `.dcm` (single file or folder)

---

### Step 2: Monitor Processing

#### View in Jobs Page

Click **"Jobs"** in navigation to see all your scans:

```
┌─────────────────────────────────────────────────────────────┐
│ Job ID              │ Filename         │ Status    │ Created│
├─────────────────────────────────────────────────────────────┤
│ 54dc2ecf-7c93...   │ sub-01.nii.gz   │ Running   │ 2 min  │
│ a8f3d2e1-4b5c...   │ sub-02.nii.gz   │ Completed │ 1 hour │
│ 9c7e1f3a-2d4b...   │ sub-03.nii.gz   │ Pending   │ 5 min  │
└─────────────────────────────────────────────────────────────┘
```

**Status Indicators:**
- 🟡 **Pending**: Waiting in queue
- 🔵 **Running**: Currently processing
- 🟢 **Completed**: Finished successfully
- 🔴 **Failed**: Error occurred
- ⚫ **Cancelled**: Stopped by user

#### Click on a Job to See Details

```
┌─────────────────────────────────────────────────────────────┐
│  Job: sub-01_T1w.nii.gz                           [Cancel]  │
├─────────────────────────────────────────────────────────────┤
│  Status: Running                                             │
│  Progress: FastSurfer segmentation in progress...            │
│  Started: 2025-11-05 14:23:15                               │
│  Duration: 8 minutes 32 seconds                              │
│                                                              │
│  Processing Steps:                                           │
│  ✓ Upload received                                           │
│  ✓ File validation                                           │
│  ✓ Format conversion                                         │
│  ⏳ FastSurfer whole-brain segmentation (current)           │
│  ○ Hippocampal subfield analysis                            │
│  ○ Volume calculation                                        │
│  ○ Asymmetry computation                                     │
└─────────────────────────────────────────────────────────────┘
```

**Processing Time:**
- **With GPU**: 2-5 minutes ⚡
- **CPU only**: 40-60 minutes (current setup: 2 CPU threads)

#### Real-Time Updates

The interface automatically refreshes every 5 seconds to show:
- Current processing step
- Time elapsed
- Any errors or warnings

---

### Step 3: View Results

Once status shows **"Completed"**, you can view results in multiple ways:

#### Option A: Metrics Page

Click **"Metrics"** to see all results in a table:

```
┌──────────────────────────────────────────────────────────────────┐
│ Scan            │ Left (mm³) │ Right (mm³) │ Asymmetry │ Date   │
├──────────────────────────────────────────────────────────────────┤
│ sub-01.nii.gz  │ 3,845      │ 3,672       │ +2.3%     │ Today  │
│ sub-02.nii.gz  │ 4,021      │ 3,988       │ +0.4%     │ 1h ago │
│ sub-03.nii.gz  │ 3,567      │ 3,812       │ -3.3%     │ 2h ago │
└──────────────────────────────────────────────────────────────────┘
```

**Metrics Explained:**
- **Left Hippocampal Volume**: Total volume in mm³
- **Right Hippocampal Volume**: Total volume in mm³
- **Asymmetry Index**: `(Left - Right) / (Left + Right) × 100`
  - **Positive**: Left larger than right
  - **Negative**: Right larger than left
  - **Normal range**: ±5% is typical

#### Option B: Job Details

Click on a completed job to see detailed metrics:

```
┌─────────────────────────────────────────────────────────────┐
│  Results: sub-01_T1w.nii.gz                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📊 Hippocampal Volumes                                     │
│                                                              │
│  Left Hemisphere                                             │
│  ████████████████████ 3,845 mm³                             │
│                                                              │
│  Right Hemisphere                                            │
│  ██████████████████   3,672 mm³                             │
│                                                              │
│  Asymmetry Index: +2.3%                                      │
│  (Left is 2.3% larger than Right)                           │
│                                                              │
│  Subfield Breakdown:                                         │
│  • CA1: 1,234 mm³                                           │
│  • CA2/3: 856 mm³                                           │
│  • CA4/DG: 892 mm³                                          │
│  • Subiculum: 563 mm³                                       │
│                                                              │
│  [Download JSON] [Download CSV] [View 3D]                   │
└─────────────────────────────────────────────────────────────┘
```

#### Option C: 3D Viewer

Click **"Viewer"** or **"View 3D"** button:

```
┌─────────────────────────────────────────────────────────────┐
│  3D Brain Viewer                           [← → ↑ ↓ Rotate] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│              [Interactive 3D Brain Model]                    │
│                                                              │
│          🧠 Rotate with mouse                               │
│          🔍 Scroll to zoom                                  │
│          👆 Click to select regions                         │
│                                                              │
│  Overlays:                                                   │
│  ☑ Show hippocampus                                         │
│  ☑ Show segmentation                                        │
│  ☐ Show subfields                                           │
│                                                              │
│  Selected Region: Left Hippocampus                           │
│  Volume: 3,845 mm³                                          │
└─────────────────────────────────────────────────────────────┘
```

**Viewer Controls:**
- **Rotate**: Click and drag
- **Zoom**: Scroll wheel
- **Pan**: Right-click and drag
- **Reset View**: Double-click
- **Toggle layers**: Checkboxes on left

---

## 📥 Exporting Results

### Export Single Job

From job details page:

1. **JSON Format** (for developers/scripts):
   ```json
   {
     "job_id": "54dc2ecf-7c93-445d-8e46-6beb89e3eaca",
     "filename": "sub-01_T1w.nii.gz",
     "metrics": {
       "left_hippocampus_volume_mm3": 3845.2,
       "right_hippocampus_volume_mm3": 3672.1,
       "asymmetry_index": 2.3
     },
     "subfields": {...}
   }
   ```

2. **CSV Format** (for Excel/SPSS):
   ```csv
   job_id,filename,left_volume,right_volume,asymmetry
   54dc2ecf...,sub-01.nii.gz,3845.2,3672.1,2.3
   ```

### Export All Results

From **Metrics** page:

1. Click **"Export All"** button
2. Choose format: CSV or JSON
3. Downloads file: `neuroinsight-results-2025-11-05.csv`

**Batch Export Example (CSV):**
```csv
filename,left_volume_mm3,right_volume_mm3,asymmetry_index,date
sub-01.nii.gz,3845.2,3672.1,2.3,2025-11-05
sub-02.nii.gz,4021.3,3988.4,0.4,2025-11-05
sub-03.nii.gz,3567.8,3812.2,-3.3,2025-11-05
```

---

## 🗑️ Managing Jobs

### Delete a Job

1. Go to **Jobs** page
2. Find the job you want to delete
3. Click **"Delete"** button or trash icon
4. Confirm deletion

**What gets deleted:**
- ✓ Job record from database
- ✓ Uploaded MRI file
- ✓ Processing outputs
- ✓ Generated visualizations
- ✓ All associated files

**For running jobs:**
- Task is cancelled first
- FastSurfer process is terminated
- Then files are cleaned up

### Bulk Delete

**Delete old completed jobs:**
```bash
# Via command line (on server)
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
python bin/cleanup_storage.py --old-completed --days 30
```

**Delete failed jobs:**
```bash
python bin/cleanup_storage.py --old-failed --days 7
```

---

## 🔍 Troubleshooting

### Problem: Upload Fails

**Symptoms:**
- "Upload failed" message
- File doesn't appear in Jobs list

**Solutions:**
1. **Check file format**: Must be `.nii`, `.nii.gz`, or `.dcm`
2. **Check file size**: Maximum 500MB
3. **Check disk space**: Server may be full
4. **Check browser console**: Press F12 → Console tab for errors

### Problem: Processing Stuck at "Pending"

**Causes:**
- Worker not running
- Another job is processing (only 1 concurrent job with 2 CPU threads)

**Solutions:**
1. **Check worker status**:
   ```bash
   # On server
   ps aux | grep celery
   ```

2. **Check if another job is running**:
   - Go to Jobs page
   - Look for jobs with "Running" status

3. **Restart worker** (if needed):
   ```bash
   cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
   bash RUN_ALL.sh --restart
   ```

### Problem: Processing Failed

**Symptoms:**
- Status changes to "Failed"
- Red error icon

**Check error message:**
1. Click on failed job
2. Scroll down to "Error Details"
3. Common errors:
   - **"Invalid NIfTI file"**: File is corrupted
   - **"Out of memory"**: Not enough RAM (need 16GB+)
   - **"FastSurfer error"**: Processing failed (check file quality)

**Solutions:**
- **Bad file**: Try different scan or re-export from imaging software
- **Memory**: Process one job at a time
- **Other errors**: Check logs (contact support)

### Problem: Can't See Results

**Symptoms:**
- Job shows "Completed" but no metrics
- Viewer shows empty/black screen

**Solutions:**
1. **Refresh page**: Press F5 or Ctrl+R
2. **Wait a moment**: Metrics may still be generating
3. **Check browser console**: F12 → Console for errors
4. **Check outputs directory**:
   ```bash
   # On server
   ls -lh data/outputs/<job-id>/
   ```

### Problem: Very Slow Processing

**Current setup: 2 CPU threads → ~40-60 minutes per scan**

**Why it's slow:**
- No GPU available
- Only 2 threads allocated (4 total cores - 2 for system)
- FastSurfer is computationally intensive

**To speed up:**
1. **Add GPU**: RTX 3060+ → 2-5 minutes per scan ⚡
2. **More CPU cores**: Scale up HPC node
3. **Process overnight**: Queue multiple scans

### Problem: Can't Access from Browser

**Symptoms:**
- "Connection refused" or "Can't reach server"

**Solutions:**
1. **Check SSH tunnel** (if remote):
   ```bash
   ssh -L 8000:localhost:8000 user@server
   ```

2. **Check backend is running**:
   ```bash
   ps aux | grep uvicorn
   ```

3. **Check port**:
   ```bash
   netstat -tuln | grep 8000
   ```

4. **Restart services**:
   ```bash
   cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
   bash RUN_ALL.sh --restart
   ```

---

## 💡 Tips & Best Practices

### For Best Results

1. **Use high-quality scans**:
   - T1-weighted structural MRI
   - 1mm³ isotropic resolution preferred
   - Minimal motion artifacts

2. **File naming**:
   - Use descriptive names: `patient-001_T1w.nii.gz`
   - Avoid spaces: Use underscores or hyphens
   - Include date if processing multiple timepoints

3. **Processing queue**:
   - With 2 CPU threads: Process one at a time
   - Queue fills up automatically
   - Don't upload more than 5-10 at once

4. **Keep organized**:
   - Delete old test jobs
   - Export results regularly
   - Download important scans before deleting

### Batch Processing Multiple Scans

**Strategy:**
1. Upload all scans (they queue automatically)
2. Let them process overnight/weekend
3. Check results in the morning
4. Export all results at once

**Expected timeline** (with 2 CPU threads):
- 5 scans: ~4-5 hours
- 10 scans: ~8-10 hours
- 20 scans: ~16-20 hours

---

## 📊 Understanding the Results

### Hippocampal Volume

**Normal adult ranges** (approximate):
- **Total hippocampus**: 3,000-4,500 mm³ per side
- **Varies by**: Age, sex, head size

**Clinical significance:**
- **Reduced volume**: May indicate atrophy (Alzheimer's, depression, etc.)
- **Asymmetry**: Normal to have slight differences (<5%)
- **Large asymmetry** (>10%): May warrant further investigation

### Asymmetry Index

**Formula**: `(Left - Right) / (Left + Right) × 100`

**Interpretation:**
- **+5%**: Left is 5% larger (typical)
- **-5%**: Right is 5% larger (typical)
- **0%**: Perfect symmetry (rare)
- **>10%**: Significant asymmetry

**Note**: This tool is for research purposes. Clinical decisions should involve medical professionals.

---

## 🆘 Getting Help

### Check Logs

**Backend logs:**
```bash
tail -f /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo/logs/backend.out
```

**Worker logs:**
```bash
tail -f /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo/logs/worker.out
```

**Job-specific logs:**
```bash
# Replace <job-id> with actual job ID
cat data/outputs/<job-id>/fastsurfer/*/scripts/deep-seg.log
```

### Common Commands

**Check system status:**
```bash
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
bash RUN_ALL.sh --status
```

**Restart everything:**
```bash
bash RUN_ALL.sh --restart
```

**View all jobs:**
```bash
curl http://localhost:8000/api/jobs | python -m json.tool
```

---

## 📚 Next Steps

1. ✅ Upload your first scan
2. ✅ Monitor processing
3. ✅ View results
4. 📥 Export data
5. 📊 Analyze in your preferred tool (Excel, SPSS, Python, R)

**Ready to start?** Open [http://localhost:8000](http://localhost:8000) and upload your first MRI scan! 🧠

