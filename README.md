# NeuroInsight

**Automated hippocampal asymmetry analysis from T1-weighted MRI scans**

Fast, accurate brain segmentation with GPU acceleration using FastSurfer. Runs locally on your computer with 100% privacy.

---

## 🚀 Quick Start

### Prerequisites

1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
   - macOS 10.15+
   - Windows 10/11
   - Ubuntu 20.04+

2. **System Requirements:**
   - **Minimum**: 4 CPU cores, 16GB RAM, 30GB free storage
   - **Recommended**: 8+ CPU cores, 32GB RAM, 100GB SSD
   - **Optional**: NVIDIA GPU (10-20x faster processing)

---

### Installation

#### Step 1: Install Docker Desktop

**macOS:**
```bash
# Download from https://www.docker.com/products/docker-desktop
# Install and start Docker Desktop
# Wait for the whale icon in menu bar to appear
```

**Windows:**
```bash
# Download from https://www.docker.com/products/docker-desktop
# Install and restart computer
# Start Docker Desktop
# Wait for "Docker Desktop is running" notification
```

**Linux:**
```bash
# Install Docker Engine and Docker Compose
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl start docker
```

---

#### Step 2: Download NeuroInsight

**Option A: Download ZIP (Easiest)**
1. Go to: https://github.com/phindagijimana/neuroinsight
2. Click green "Code" button
3. Click "Download ZIP"
4. Extract ZIP file
5. Open Terminal/Command Prompt and navigate to extracted folder

**Option B: Clone with Git**
```bash
git clone https://github.com/phindagijimana/neuroinsight.git
cd neuroinsight
```

---

#### Step 3: Start NeuroInsight

**macOS / Linux:**
```bash
# Navigate to the neuroinsight folder
cd neuroinsight

# Create environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Wait about 30 seconds for services to start

# Open in browser
open http://localhost:3000
```

**Windows (Command Prompt):**
```cmd
# Navigate to the neuroinsight folder
cd neuroinsight

# Create environment file
copy .env.example .env

# Start all services
docker-compose up -d

# Wait about 30 seconds for services to start

# Open browser and go to:
# http://localhost:3000
```

**Windows (PowerShell):**
```powershell
cd neuroinsight
Copy-Item .env.example .env
docker-compose up -d
Start-Process "http://localhost:3000"
```

---

### First Time Setup

When you first open http://localhost:3000, you'll see the NeuroInsight interface.

**That's it! You're ready to process MRI scans.**

---

## 📖 How to Use

### 1. Upload an MRI Scan
- Click "Upload" or drag & drop
- Supported formats: `.nii`, `.nii.gz`, `.dcm`
- File should be a T1-weighted structural MRI

### 2. Start Processing
- Click "Process" button
- Processing time:
  - With GPU: 1-3 minutes
  - Without GPU (CPU): 5-15 minutes

### 3. View Results
- Left hippocampal volume (mm³)
- Right hippocampal volume (mm³)
- Asymmetry Index: (L - R) / (L + R)
- 3D visualization with overlays
- Interactive brain viewer

### 4. Export Results
- Download as JSON
- Download as CSV
- Save 3D visualizations
- Export reports

---

## 🛑 Stopping NeuroInsight

When you're done, stop the services:

```bash
docker-compose down
```

To remove all data and start fresh next time:
```bash
docker-compose down -v
```

---

## 🔄 Updating NeuroInsight

To get the latest version:

```bash
# Navigate to neuroinsight folder
cd neuroinsight

# Stop services
docker-compose down

# Update code
git pull origin main
# OR download new ZIP and extract

# Update Docker images
docker-compose pull

# Restart
docker-compose up -d
```

---

## ❓ Troubleshooting

### "Cannot connect to Docker daemon"
**Solution:** Make sure Docker Desktop is running
- macOS: Look for whale icon in menu bar
- Windows: Look for whale icon in system tray
- Linux: `sudo systemctl status docker`

### "Port already in use"
**Solution:** Stop existing services
```bash
docker-compose down
docker-compose up -d
```

### "localhost:3000 not loading"
**Solution:** Check if services started correctly
```bash
# Check status
docker-compose ps

# View logs
docker-compose logs frontend
docker-compose logs backend
```

### Database errors
**Solution:** Fresh start
```bash
docker-compose down -v  # Removes all data
docker-compose up -d    # Fresh start
```

### Processing stuck or failed
**Solution:** Check worker logs
```bash
docker-compose logs worker
```

---

## 🔍 Advanced Usage

### View Live Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f worker
```

### Restart Services
```bash
docker-compose restart
```

### Access Backend API Directly
```
http://localhost:8000/docs
```
Interactive API documentation (Swagger UI)

### GPU Configuration

If you have an NVIDIA GPU:

1. **Install NVIDIA Docker Runtime**
   ```bash
   # Linux
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update && sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

2. **GPU will be automatically detected and used**

---

## 📊 Features

- **Automated Processing**: Upload scan → get results in minutes
- **FastSurfer Segmentation**: State-of-the-art deep learning brain segmentation
- **Asymmetry Analysis**: Quantify left-right hippocampal differences
- **GPU Acceleration**: 10-20x faster with NVIDIA GPU (optional)
- **Interactive 3D Viewer**: Real-time brain visualization
- **100% Local**: All processing on your computer (HIPAA-compliant)
- **No Internet Required**: Works completely offline
- **Export Reports**: JSON, CSV, images

---

## 🔒 Privacy & Security

**Your data never leaves your computer:**
- All processing happens locally
- No data uploaded to servers
- No internet connection required
- HIPAA-compliant by design
- Perfect for sensitive medical data

---

## 💻 System Information

### What Gets Installed?

NeuroInsight runs in Docker containers. When you run `docker-compose up -d`, it downloads and starts:

1. **PostgreSQL** (database) - ~250MB
2. **Redis** (cache) - ~30MB
3. **MinIO** (file storage) - ~100MB
4. **Backend API** (FastAPI) - ~500MB
5. **Worker** (FastSurfer processing) - ~3GB
6. **Frontend** (React web UI) - ~200MB

**Total download:** ~4GB (first time only)

### Ports Used

- `3000` - Frontend (web interface)
- `8000` - Backend API
- `5432` - PostgreSQL database
- `6379` - Redis cache
- `9000` - MinIO storage

If any port is already in use, edit `docker-compose.yml` to change ports.

---

## 🏥 Clinical Use

NeuroInsight is designed for research and clinical assessment of hippocampal asymmetry, which may be relevant in:

- Temporal lobe epilepsy
- Alzheimer's disease
- Hippocampal sclerosis
- Memory disorders
- Neurodevelopmental conditions

**Note:** This software is for research purposes. Clinical decisions should be made by qualified healthcare professionals.

---

## 📚 Documentation

- **Installation Guide**: This README
- **User Guide**: See `docs/USER_GUIDE.md`
- **API Documentation**: http://localhost:8000/docs (when running)
- **Technical Details**: See `docs/TECHNICAL.md`

---

## 🤝 Support

### Common Questions

**Q: Do I need an internet connection?**
A: Only for initial download. After that, works completely offline.

**Q: Can I process multiple scans at once?**
A: Yes! Upload multiple scans and queue them.

**Q: What MRI sequences are supported?**
A: T1-weighted structural MRI (MPRAGE, SPGR, etc.)

**Q: Does it work with clinical DICOM files?**
A: Yes! Supports DICOM (.dcm) format.

**Q: How accurate is the segmentation?**
A: FastSurfer achieves comparable accuracy to FreeSurfer (gold standard) in ~5 minutes vs 8 hours.

### Getting Help

1. **Check logs**: `docker-compose logs -f`
2. **Read troubleshooting section** above
3. **Open GitHub issue**: https://github.com/phindagijimana/neuroinsight/issues

---

## 🚀 For Developers

Want to contribute or customize NeuroInsight?

See:
- `CONTRIBUTING.md` - Development guide
- `docs/ARCHITECTURE.md` - System architecture
- `docs/API.md` - API documentation

---

## 📄 License

MIT License - See `LICENSE` file for details.

---

## 🙏 Acknowledgments

- **FastSurfer**: Deep learning-based brain segmentation
- **FreeSurfer**: Gold standard brain MRI analysis
- **Docker**: Containerization platform
- Research funded by: [Your institution/grants]

---

## 📞 Contact

- **Issues**: https://github.com/phindagijimana/neuroinsight/issues
- **Email**: support@neuroinsight.app
- **Website**: https://neuroinsight.app

---

**Ready to analyze hippocampal asymmetry? Start with Step 1 above!** 🧠
