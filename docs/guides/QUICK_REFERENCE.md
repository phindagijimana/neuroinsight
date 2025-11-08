# NeuroInsight - Quick Reference Card

**Print this page for easy reference**

---

## 🚀 First Time Setup

1. **Install Docker Desktop**: https://www.docker.com/products/docker-desktop
2. **Download NeuroInsight**: https://github.com/phindagijimana/neuroinsight
3. **Extract ZIP** to your preferred location

---

## ▶️ Starting NeuroInsight

```bash
cd /path/to/neuroinsight
docker-compose up -d
```

Wait 30 seconds, then open: **http://localhost:3000**

---

## ⏸️ Stopping NeuroInsight

```bash
docker-compose down
```

---

## 🔄 Restarting (Next Time You Use It)

```bash
cd /path/to/neuroinsight
docker-compose up -d
```

Open: **http://localhost:3000**

---

## 📊 Common Commands

| Task | Command |
|------|---------|
| **Start** | `docker-compose up -d` |
| **Stop** | `docker-compose down` |
| **Restart** | `docker-compose restart` |
| **Check status** | `docker-compose ps` |
| **View logs** | `docker-compose logs -f` |
| **Fresh start** | `docker-compose down -v && docker-compose up -d` |

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| **Main Interface** | http://localhost:3000 |
| **API Documentation** | http://localhost:8000/docs |
| **Backend API** | http://localhost:8000 |

---

## 📁 Supported File Formats

- `.nii` - NIfTI
- `.nii.gz` - Compressed NIfTI
- `.dcm` - DICOM

**Required:** T1-weighted structural MRI

---

## ⏱️ Processing Times

| Setup | Time per Scan |
|-------|---------------|
| **CPU only** | 5-15 minutes |
| **With NVIDIA GPU** | 1-3 minutes |

---

## ❓ Troubleshooting

### Docker not running?
```bash
# macOS: Check menu bar for whale icon
# Windows: Check system tray for whale icon
# Linux: sudo systemctl status docker
```

### Can't access localhost:3000?
```bash
docker-compose ps  # Check if running
docker-compose logs frontend  # Check errors
```

### Services won't start?
```bash
docker-compose down -v  # Remove all data
docker-compose up -d    # Fresh start
```

### Need to see what's happening?
```bash
docker-compose logs -f  # Live logs
docker-compose logs -f worker  # Worker logs only
```

---

## 💻 System Requirements

**Minimum:**
- 4 CPU cores
- 16GB RAM
- 30GB storage

**Recommended:**
- 8+ cores
- 32GB RAM
- 100GB SSD
- NVIDIA GPU

---

## 📞 Getting Help

- **Full documentation**: See `README.md`
- **Installation guide**: See `INSTALL.md`
- **Issues**: https://github.com/phindagijimana/neuroinsight/issues

---

## 🔒 Privacy

**All processing happens on YOUR computer:**
- No data uploaded to servers
- No internet required (after installation)
- 100% private and HIPAA-compliant

---

## 📈 Typical Workflow

1. **Start NeuroInsight** → `docker-compose up -d`
2. **Open browser** → http://localhost:3000
3. **Upload MRI scan** → Drag & drop `.nii` or `.nii.gz`
4. **Click "Process"** → Wait 1-15 minutes
5. **View results** → Volumes, asymmetry index, 3D visualization
6. **Export** → Download JSON/CSV reports
7. **Stop when done** → `docker-compose down`

---

**Keep this reference handy for quick access to commands!**

*Last updated: November 2025*

