# NeuroInsight - Quick User Guide

## 🚀 5-Minute Quick Start

### 1. Access the App
```
http://localhost:8000
```
(Or use SSH tunnel if remote)

### 2. Upload MRI Scan
- Click **"Upload MRI Scan"**
- Select `.nii`, `.nii.gz`, or `.dcm` file
- Wait for upload to complete

### 3. Monitor Processing
- Go to **"Jobs"** tab
- Watch status change: Pending → Running → Completed
- **Processing time**: 40-60 minutes (with 2 CPU threads)

### 4. View Results
- Click on completed job
- See hippocampal volumes and asymmetry
- Click **"View 3D"** for brain visualization

### 5. Export Data
- Click **"Download CSV"** or **"Download JSON"**
- Results saved to your computer

---

## 📊 What You'll See

### Hippocampal Volumes
```
Left Hippocampus:  3,845 mm³
Right Hippocampus: 3,672 mm³
Asymmetry Index:   +2.3% (Left larger)
```

### Job Status
- 🟡 **Pending**: Waiting in queue
- 🔵 **Running**: Currently processing
- 🟢 **Completed**: Finished successfully
- 🔴 **Failed**: Error occurred

---

## 🎯 Main Pages

### Home
- Upload new scans
- System status

### Jobs
- All processing jobs
- Status monitoring
- Delete jobs

### Metrics
- All results in table
- Export all data

### Viewer
- Interactive 3D brain visualization
- Rotate, zoom, explore

---

## ⚡ Quick Tips

1. **Supported formats**: `.nii`, `.nii.gz`, `.dcm`
2. **Processing time**: ~45 minutes per scan (CPU only)
3. **Queue system**: Scans process one at a time
4. **Auto-refresh**: Page updates every 5 seconds
5. **Delete jobs**: Removes files and frees disk space

---

## 🔧 Common Issues

### Upload fails
- Check file format (must be NIfTI or DICOM)
- Check file size (max 500MB)

### Processing stuck
- Check if another job is running
- Wait for current job to finish

### Can't access app
```bash
# Restart services
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
bash RUN_ALL.sh --restart
```

---

## 📖 Full Documentation

For detailed information, see:
- **`docs/USER_GUIDE.md`** - Complete user manual
- **`docs/ARCHITECTURE.md`** - Technical details
- **`README.md`** - Installation and setup

---

## 🆘 Need Help?

**Check logs:**
```bash
# Backend
tail -f logs/backend.out

# Worker
tail -f logs/worker.out
```

**Restart everything:**
```bash
bash RUN_ALL.sh --restart
```

**Contact**: Open an issue on GitHub or contact support

---

**Happy analyzing! 🧠**

