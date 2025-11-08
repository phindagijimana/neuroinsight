# NeuroInsight User Manual

**Version**: 1.1.0  
**Last Updated**: November 2025

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Uploading Scans](#uploading-scans)
4. [Understanding Results](#understanding-results)
5. [Viewer Controls](#viewer-controls)
6. [Progress Tracking](#progress-tracking)
7. [Technical Details](#technical-details)
8. [Troubleshooting](#troubleshooting)
9. [Support](#support)

---

## Getting Started

### First Launch

1. **Start NeuroInsight**:
   - Linux: `./NeuroInsight-1.0.0.AppImage`
   - Windows: Start Menu → NeuroInsight
   - macOS: Applications → NeuroInsight

2. **Splash screen** appears while loading (5-10 seconds)

3. **Main window** opens with three tabs:
   - **Jobs**: Upload and process MRI scans
   - **Stats**: View volumetric results
   - **Viewer**: Visualize segmentation overlays

---

## Interface Overview

###  Jobs Tab

The main workspace for uploading and processing scans.

**Features**:
- ✅ Upload button (supports drag & drop)
- ✅ Job list with status
- ✅ Progress tracking
- ✅ Delete completed jobs

###  Stats Tab

View hippocampal volume statistics.

**Displays**:
- Left hippocampus volume (mm³)
- Right hippocampus volume (mm³)
- Asymmetry Index (%)
- Total volume

###  Viewer Tab

Interactive visualization of segmentation results.

**Features**:
- Multi-orientation viewer (axial, coronal, sagittal)
- Slice navigation (10 slices per orientation)
- Opacity control (0-100%)
- Zoom controls
- Thumbnail previews

---

## Uploading Scans

### Supported File Formats

✅ **NIfTI**: `.nii` or `.nii.gz` (recommended)  
✅ **DICOM**: `.dcm` files

### Requirements

Your MRI scan must be:
- **T1-weighted** (not T2, FLAIR, or other modalities)
- **3D volume** (not 2D slices)
- **Standard orientation** (RAS, LAS, or LIA)

### Upload Steps

1. **Click "Upload File"** button or drag & drop

2. **Select your scan**:
   - Browse to your `.nii`, `.nii.gz`, or `.dcm` file
   - Click "Open"

3. **Optional: Enter metadata**:
   - Patient ID
   - Study date
   - Notes

4. **Click "Process"**:
   - Scan is added to job queue
   - Processing starts automatically

### Drag & Drop

You can also drag and drop files directly onto the Jobs tab:
- Drag `.nii` or `.nii.gz` file
- Drop anywhere in Jobs tab
- Processing starts immediately

---

## Understanding Results

### Hippocampal Volumes

After processing completes, view results in the **Stats** tab.

#### Normal Ranges

Typical hippocampal volumes in healthy adults:

| Measure | Normal Range |
|---------|--------------|
| Left Hippocampus | 2,500-4,500 mm³ |
| Right Hippocampus | 2,500-4,500 mm³ |
| Total | 5,000-9,000 mm³ |

**Note**: Volumes vary by age, sex, and intracranial volume.

#### Asymmetry Index (AI)

Formula: `AI = (L - R) / ((L + R) / 2) × 100`

Where:
- `L` = Left hippocampus volume
- `R` = Right hippocampus volume

**Interpretation**:
- **AI < 7%**: Normal symmetry (typical)
- **AI > 7%**: Significant asymmetry (may warrant further investigation)
- **Positive AI**: Left hippocampus is larger
- **Negative AI**: Right hippocampus is larger

**Clinical Relevance**:
- Asymmetry may indicate:
  - Unilateral hippocampal sclerosis
  - Temporal lobe epilepsy
  - Alzheimer's disease (early stage)
  - Normal anatomical variation

**Always consult with a neuroradiologist or neurologist for clinical interpretation.**

---

## Viewer Controls

### Orientation Selector

Choose viewing plane:

- **Axial**: Horizontal slices (view from below)
  - Shows left/right separation clearly
  - Standard clinical view

- **Coronal**: Frontal slices (view from front)
  - Shows anterior/posterior extent
  - Good for hippocampal body

- **Sagittal**: Side slices (view from side)
  - Shows superior/inferior extent
  - Good for hippocampal head/tail

### Slice Navigation

**10 slices per orientation**, evenly spaced across the hippocampus.

Navigation options:
- **Slider**: Drag to move through slices
- **Arrow buttons**: Click ← or → for previous/next slice
- **Thumbnails**: Click any thumbnail to jump to that slice

**Keyboard shortcuts**:
- `←` / `→`: Previous/next slice
- `Home`: First slice
- `End`: Last slice

### Opacity Control

Adjust overlay transparency with the slider (0-100%).

**Use cases**:
- **0%**: Only brain anatomy (grayscale)
  - Check scan quality
  - Verify anatomical structures

- **50%**: Balanced view (default)
  - Standard visualization
  - Good for most purposes

- **100%**: Only segmentation (colored overlay)
  - Focus on hippocampus location
  - Check segmentation quality

**Keyboard shortcuts**:
- `+` / `=`: Increase opacity
- `-`: Decrease opacity

### Zoom Controls

Scale the viewer for detailed inspection.

**Buttons**:
- **+ (Zoom In)**: Enlarge to 150%, 200%
- **- (Zoom Out)**: Shrink to 75%, 50%
- **⊙ (Reset)**: Return to 100%

**Keyboard shortcuts**:
- `Ctrl/Cmd +`: Zoom in
- `Ctrl/Cmd -`: Zoom out
- `Ctrl/Cmd 0`: Reset zoom

### Color Coding

Hippocampus structures are color-coded:
- 🔴 **RED**: Left hippocampus (label 17 in DKT atlas)
- 🔵 **BLUE**: Right hippocampus (label 53 in DKT atlas)

---

## Progress Tracking

NeuroInsight provides real-time progress updates during processing.

### Progress Stages

| Stage | % | Description | Duration |
|-------|---|-------------|----------|
| 1 | 5% | Job started - preparing file | <1 min |
| 2 | 10% | File retrieved - initializing | <1 min |
| 3 | 15% | Starting brain segmentation | <1 min |
| 4 | 17% | Preparing input file | <1 min |
| 5 | 20% | Running FastSurfer segmentation | **Longest** |
| 6 | 65% | Extracting hippocampal volumes | 1-2 min |
| 7 | 70% | Calculating asymmetry indices | <1 min |
| 8 | 75% | Generating visualizations | 2-3 min |
| 9 | 82% | Saving results | <1 min |
| 10 | 85% | Processing complete - saving metrics | <1 min |
| 11 | 95% | Finalizing results | <1 min |
| 12 | 100% | Complete | Done! |

### Processing Time

**With GPU (NVIDIA CUDA)**:
- Small scans: 5-7 minutes
- Large scans: 8-12 minutes
- **Recommended** for production use

**With CPU only**:
- Small scans: 45-60 minutes
- Large scans: 1-2 hours
- Uses multi-threading (all cores)

**FastSurfer stage** (20-65%) takes the longest:
- This is the neural network processing
- Be patient, it's working!
- Do not interrupt

### Canceling Jobs

To cancel a processing job:
1. Find the job in the Jobs tab
2. Click the **Delete** button
3. Confirm cancellation

**Note**: Cannot cancel jobs in progress. Wait for completion or force-quit the app.

---

## Technical Details

### FastSurfer Segmentation

NeuroInsight uses FastSurfer for brain segmentation:
- **Method**: Convolutional Neural Network (CNN)
- **Training**: FreeSurfer manual segmentations
- **Atlas**: Desikan-Killiany-Tourville (DKT)
- **Speed**: ~100x faster than FreeSurfer
- **Accuracy**: Comparable to FreeSurfer (Dice > 0.90)

**Reference**: Henschel et al. (2020), NeuroImage

### Volume Calculation

Hippocampal volumes are calculated by:
1. Counting voxels with label 17 (left) or 53 (right)
2. Multiplying by voxel size (from NIfTI header)
3. Converting to mm³

**No intracranial volume (ICV) correction** is applied by default.

For normalized volumes:
- Export raw volumes
- Calculate ICV separately
- Normalize: `Normalized = (Hippocampus / ICV) × 1000`

### Visualization Generation

For each orientation (axial, coronal, sagittal):
1. Find hippocampus extent in volume
2. Select 10 evenly-spaced slices
3. Generate two PNGs per slice:
   - Anatomical base (grayscale brain)
   - Overlay layer (colored hippocampus, transparent background)
4. Frontend composites layers with CSS

This allows real-time opacity control without regenerating images.

### GPU vs CPU

NeuroInsight automatically detects and uses GPU if available:

**GPU Detection**:
- Checks for NVIDIA GPU with CUDA
- Uses `torch.cuda.is_available()`
- Falls back to CPU if no GPU

**To force CPU** (if GPU issues):
- Set environment variable: `CUDA_VISIBLE_DEVICES=-1`
- Or uninstall CUDA toolkit

---

## Troubleshooting

### App Won't Start

**Check**:
- System meets requirements (8 GB RAM, 10 GB disk)
- Antivirus isn't blocking the app
- No port conflicts (port 8000 must be free)

**Try**:
- Restart computer
- Run as administrator (Windows)
- Check logs: Help → View Logs

### Processing Fails

**Common Causes**:
1. **Wrong file format**
   - Must be T1-weighted MRI
   - Check if file is actually T2, FLAIR, etc.

2. **Corrupted file**
   - Try opening file in another viewer (ITK-SNAP, 3D Slicer)
   - Re-export from DICOM if needed

3. **Out of memory**
   - Need 8+ GB RAM
   - Close other applications
   - Try smaller scan or machine with more RAM

4. **Invalid orientation**
   - Scan must be in standard orientation
   - Use `fslreorient2std` to fix (FSL tools)

**Check Logs**:
- Press `Ctrl+L` or `Cmd+L`
- Open `errors.log`
- Look for specific error messages

### Wrong Results

If volumes seem incorrect:
1. **Visual Inspection**:
   - Open Viewer tab
   - Check if segmentation looks correct
   - Red/blue should cover hippocampus

2. **Quality Control**:
   - Check all 3 orientations
   - Look for segmentation errors
   - Verify anatomical accuracy

3. **Reprocess**:
   - Delete job and reupload
   - Try with higher quality scan
   - Ensure T1-weighted (not T2)

### Slow Performance

**If processing is very slow**:
- Check if GPU is being used (should finish in 5-10 min)
- If CPU only, expect 1-2 hours
- Check Task Manager / Activity Monitor (CPU should be near 100%)
- Make sure not running on low power mode (laptops)

**If viewer is laggy**:
- Reduce zoom level
- Close other applications
- Check if RAM is full

### Crashes

If the app crashes:
1. **Check crash logs**:
   - Press `Ctrl+L` / `Cmd+L`
   - Open `crashes.log`
   - Last entry shows crash details

2. **Common crash causes**:
   - Out of memory (need 8+ GB)
   - Corrupted input file
   - Disk full during processing

3. **Report issue**:
   - Include `crashes.log`
   - Describe what you were doing
   - GitHub Issues or email

### Log Locations

Access logs anytime:
- **Keyboard**: `Ctrl+L` (Linux/Win) or `Cmd+L` (Mac)
- **Menu**: Help → View Logs
- **Manual**:
  - Linux: `~/.config/neuroinsight/logs/`
  - Windows: `C:\Users\[You]\AppData\Roaming\neuroinsight\logs\`
  - macOS: `~/Library/Application Support/neuroinsight/logs/`

**Log files**:
- `neuroinsight.log`: All events
- `errors.log`: Errors only
- `crashes.log`: Critical failures

---

## Support

### Documentation

- **Installation**: [INSTALLATION.md](INSTALLATION.md)
- **Troubleshooting**: [LOGS_AND_TROUBLESHOOTING.md](LOGS_AND_TROUBLESHOOTING.md)
- **Technical**: Repository README

### Getting Help

**Before contacting support**:
1. Check this manual
2. Check logs (`Ctrl+L` / `Cmd+L`)
3. Search GitHub Issues

**When reporting issues**:
- Your OS and version
- NeuroInsight version
- Steps to reproduce
- **Log files** (especially `errors.log` or `crashes.log`)
- Screenshots if helpful

**Contact**:
- **GitHub**: https://github.com/phindagijimana/neuroinsight/issues
- **Email**: neuroinsight@example.com
- **Response**: 1-3 business days

---

## Keyboard Shortcuts

### Global
- `Ctrl+L` / `Cmd+L`: Open log folder
- `Ctrl+Q` / `Cmd+Q`: Quit application
- `F11`: Toggle fullscreen

### Viewer Tab
- `←` / `→`: Previous/next slice
- `Home` / `End`: First/last slice
- `+` / `-`: Adjust opacity
- `Ctrl/Cmd +` / `-`: Zoom in/out
- `Ctrl/Cmd 0`: Reset zoom

---

## Tips & Best Practices

### Input Scans

✅ **DO**:
- Use T1-weighted MRI scans
- Ensure good image quality (minimal motion artifacts)
- Use standard acquisition protocols
- Check orientation is correct

❌ **DON'T**:
- Use T2-weighted, FLAIR, or other modalities
- Use 2D slices (need 3D volume)
- Use heavily motion-corrupted scans
- Use non-brain images

### Quality Control

Always visually inspect results:
1. Open Viewer tab after processing
2. Check all 3 orientations
3. Verify hippocampus is correctly segmented
4. Look for errors (missing regions, extra regions)
5. Compare left/right symmetry

### Clinical Use

⚠️ **Important**: NeuroInsight is a research tool.

For clinical use:
- Results should be reviewed by qualified clinicians
- Visual inspection is essential
- Consider as adjunct to radiological assessment
- Validate against institution-specific norms

### Batch Processing

To process multiple scans:
1. Upload first scan
2. Wait for processing to start
3. Upload next scan (queued automatically)
4. Repeat

**Note**: Only one job processes at a time. Others wait in queue.

---

## Appendix

### File Locations

**Data Directory**:
- Linux: `~/.config/neuroinsight/data/`
- Windows: `%APPDATA%\neuroinsight\data\`
- macOS: `~/Library/Application Support/neuroinsight/data/`

**Database**:
- `neuroinsight.db` (SQLite)
- Contains job history, results, metadata

**Logs**:
- See [Log Locations](#log-locations) above

### Uninstalling

See [INSTALLATION.md](INSTALLATION.md) for uninstallation instructions.

Your data is stored separately and can be deleted manually if desired.

### Privacy

NeuroInsight:
- ✅ Stores all data locally
- ✅ No internet connection required (after installation)
- ✅ No telemetry or analytics
- ✅ No external data transmission

All processing happens on your computer.

---

## Version History

### v1.1.0 (November 2025)
- Added crash logging with log viewer
- Added progress tracking (11 stages)
- Added multi-orientation viewer
- Added opacity control
- Added zoom controls
- Enhanced error handling

### v1.0.0 (November 2025)
- Initial release
- FastSurfer-based segmentation
- Hippocampal volume calculation
- Basic visualization

---

## Citation

If you use NeuroInsight in your research, please cite:

```bibtex
@software{neuroinsight2025,
  title = {NeuroInsight: Automated Hippocampal Asymmetry Analysis},
  author = {[Your Name]},
  year = {2025},
  url = {https://github.com/phindagijimana/neuroinsight}
}
```

---

## License

NeuroInsight is open-source software. See [LICENSE](../LICENSE) for details.

---

## Acknowledgments

NeuroInsight uses:
- **FastSurfer** (Henschel et al., 2020)
- **PyTorch** deep learning framework
- **Electron** desktop framework
- **FreeSurfer** tools

Developed at University of Rochester Medical Center for research use.

---

**Questions? Issues? Feedback?**

We'd love to hear from you! Open an issue on GitHub or email us.

**Thank you for using NeuroInsight!** 🧠

