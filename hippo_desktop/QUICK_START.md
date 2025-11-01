# NeuroInsight Desktop - Quick Start Guide

## 🚀 Installation

### Windows

1. **Download** `NeuroInsight-Setup-1.0.0.exe`
2. **Double-click** the installer
3. **Follow** the setup wizard
4. **Wait** for Docker images to download (~15GB, one-time)
5. **Launch** NeuroInsight from desktop shortcut

**First time?** The installer will:
- Check system requirements
- Install/start Docker Desktop (if needed)
- Download processing containers
- Configure data directories
- Create desktop shortcut

### macOS

1. **Download** `NeuroInsight-1.0.0.dmg`
2. **Open** the DMG file
3. **Drag** NeuroInsight to Applications folder
4. **Launch** from Applications
5. **Allow** security permissions if prompted

**Apple Silicon (M1/M2)?** The app works but GPU acceleration is not available (NVIDIA only).

### Linux

**AppImage** (Universal):
```bash
# Download
wget https://neuroinsight.app/download/NeuroInsight-1.0.0.AppImage

# Make executable
chmod +x NeuroInsight-1.0.0.AppImage

# Run
./NeuroInsight-1.0.0.AppImage
```

**Ubuntu/Debian**:
```bash
# Download
wget https://neuroinsight.app/download/neuroinsight_1.0.0_amd64.deb

# Install
sudo dpkg -i neuroinsight_1.0.0_amd64.deb

# Fix dependencies if needed
sudo apt-get install -f

# Launch
neuroinsight
```

**Fedora/RHEL**:
```bash
# Download
wget https://neuroinsight.app/download/neuroinsight-1.0.0.x86_64.rpm

# Install
sudo rpm -i neuroinsight-1.0.0.x86_64.rpm

# Launch
neuroinsight
```

## 📋 System Requirements

### Minimum (CPU Processing)
- **CPU**: 4 cores (Intel i5, AMD Ryzen 5)
- **RAM**: 16GB
- **Storage**: 30GB free
- **OS**: Windows 10, macOS 10.15+, Ubuntu 20.04+

**Processing time**: ~40-60 minutes per scan

### Recommended (GPU Processing)
- **CPU**: 8+ cores
- **RAM**: 32GB
- **Storage**: 100GB SSD
- **GPU**: NVIDIA GPU with 8GB+ VRAM
- **OS**: Same as minimum

**Processing time**: ~2-5 minutes per scan ⚡

## 🎯 First Run

### 1. Setup Wizard

On first launch, you'll see:

```
┌─────────────────────────────────┐
│   NeuroInsight Setup Wizard     │
├─────────────────────────────────┤
│                                 │
│ 1. System Requirements Check    │
│    ✓ CPU: 8 cores               │
│    ✓ RAM: 32GB                  │
│    ⚠ GPU: None (CPU mode)      │
│                                 │
│ 2. Docker Desktop               │
│    ⚠ Not installed              │
│    [Download Docker Desktop]    │
│                                 │
│ 3. Data Directory               │
│    📁 ~/NeuroInsight/data      │
│    [Change Location...]         │
│                                 │
│         [Continue Setup]        │
└─────────────────────────────────┘
```

### 2. Docker Desktop

If Docker isn't installed:
1. Click "Download Docker Desktop"
2. Install Docker Desktop
3. Start Docker Desktop
4. Return to NeuroInsight and click "I've Installed Docker"

### 3. Initial Download

First run downloads containers (~15GB):
- FastSurfer (neuroimaging): ~15GB
- PostgreSQL: ~350MB
- Redis: ~50MB
- MinIO: ~100MB

**Time**: 10-30 minutes depending on internet speed

## 💻 Using NeuroInsight

### Upload a Scan

1. **Click** "Upload" in navigation
2. **Select** your MRI file:
   - Formats: `.nii`, `.nii.gz`, `.dcm`
   - Max size: 500MB
3. **Click** "Upload and Process"

### Monitor Processing

```
Processing: sub-01_T1w.nii.gz
Status: Running
Progress: [████████░░] 80%

Steps:
✓ Upload complete
✓ Input validation
✓ FastSurfer segmentation
⏳ Hippocampal analysis
○ Asymmetry calculation
```

### View Results

Once complete:
- **Metrics Table**: Volume measurements
- **Asymmetry Chart**: Left vs Right comparison
- **Viewer**: Interactive 3D visualization
- **Export**: Download CSV/JSON results

## 🎛️ System Tray Controls

Right-click the NeuroInsight icon in system tray:

```
┌─────────────────────────┐
│ NeuroInsight            │
│ Status: Running         │
├─────────────────────────┤
│ Open NeuroInsight       │
│ View Logs               │
├─────────────────────────┤
│ Restart Services        │
│ Stop Services           │
├─────────────────────────┤
│ Preferences             │
│ Quit                    │
└─────────────────────────┘
```

## ⚙️ Settings

### Data Location

Default: `~/NeuroInsight/data` (or `C:\Users\You\NeuroInsight\data` on Windows)

Change in **Preferences → Data Directory**

### Processing Mode

- **Auto**: Use GPU if available, else CPU
- **CPU Only**: Force CPU processing
- **GPU Only**: Require GPU (fail if unavailable)

### Auto-Cleanup

Configure automatic cleanup:
- **Keep completed scans**: 90 days
- **Keep failed scans**: 30 days
- **Max scans retained**: 100

## 🔧 Troubleshooting

### Problem: "Docker Desktop is not running"

**Solution**:
```bash
# Windows
Start Docker Desktop from Start Menu

# macOS
Open Docker from Applications

# Linux
sudo systemctl start docker
```

### Problem: "Not enough memory"

**Symptoms**: Processing fails, app crashes

**Solution**:
1. Close other applications
2. Increase Docker memory limit:
   - Docker Desktop → Settings → Resources
   - Set to at least 16GB
3. Restart NeuroInsight

### Problem: "Processing is very slow"

**Check**:
```
System Tray → View Logs → worker.log

Look for:
[INFO] using_cpu_for_processing    ← CPU mode (slow)
[INFO] using_gpu_for_processing    ← GPU mode (fast)
```

**Speed up**:
- Add NVIDIA GPU (~$300-1500)
- Or use cloud processing option

### Problem: Can't access application

**Steps**:
1. Check if services are running:
   - System Tray → should say "Running"
2. Restart services:
   - System Tray → Restart Services
3. Check logs:
   - System Tray → View Logs
4. Reinstall if needed

### Get Help

- **Docs**: https://neuroinsight.app/docs
- **Forum**: https://community.neuroinsight.app
- **Email**: support@neuroinsight.app
- **Issues**: https://github.com/neuroinsight/desktop/issues

## 📦 Advanced

### Command Line

```bash
# Start app
neuroinsight

# Development mode
neuroinsight --dev

# Custom data directory
neuroinsight --data-dir /path/to/data

# Check version
neuroinsight --version

# Run system check
neuroinsight --check-system
```

### Environment Variables

```bash
# Set log level
export NEUROINSIGHT_LOG_LEVEL=DEBUG

# Custom Docker socket
export DOCKER_HOST=unix:///var/run/docker.sock

# Disable GPU
export NEUROINSIGHT_DISABLE_GPU=1
```

### Data Backup

**Important directories**:
```
~/NeuroInsight/data/
├── uploads/          # Original scans
├── outputs/          # Processing results
└── database/         # Job metadata
```

**Backup command**:
```bash
# Full backup
tar -czf neuroinsight-backup-$(date +%Y%m%d).tar.gz \
  ~/NeuroInsight/data

# Results only (smaller)
tar -czf neuroinsight-outputs-$(date +%Y%m%d).tar.gz \
  ~/NeuroInsight/data/outputs
```

## 🚀 Performance Tips

### Faster Processing

1. **Use GPU**: 10-20x faster than CPU
   - Requires NVIDIA GPU
   - Install NVIDIA drivers
   - Install NVIDIA Container Toolkit

2. **SSD Storage**: 2-3x faster file I/O
   - Move data directory to SSD
   - Preferences → Data Directory

3. **More RAM**: Reduces swapping
   - 32GB recommended for parallel processing
   - Can process 2-3 scans simultaneously

4. **Close Apps**: Free up resources
   - Close Chrome, video editing software
   - Monitor with Task Manager/Activity Monitor

### Batch Processing

Process multiple scans:
1. Upload all scans
2. They queue automatically
3. Process in parallel (if enough RAM)
4. Review results when complete

## 📊 Benchmarks

**Test scan**: 512×171×512 T1-weighted MRI

| Configuration | Processing Time |
|---------------|----------------|
| 4 cores, 16GB RAM, CPU | ~50 minutes |
| 8 cores, 32GB RAM, CPU | ~25 minutes |
| RTX 3060, 12GB VRAM | ~4 minutes ⚡ |
| RTX 3080, 10GB VRAM | ~2.5 minutes ⚡⚡ |
| RTX 4090, 24GB VRAM | ~1.5 minutes ⚡⚡⚡ |

## 🎓 Next Steps

1. ✅ Install NeuroInsight
2. ✅ Run your first scan
3. 📖 Read the full documentation
4. 🎥 Watch video tutorials
5. 💬 Join the community

**Ready to analyze?** Upload your first scan and see the magic happen! 🧠


