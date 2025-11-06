# NeuroInsight

Automated brain MRI analysis for hippocampal volume and asymmetry measurement using deep learning.

---

## Getting Started

### Choose Your Setup

**For Clinical/Research Users**
- [Lab Access (No Installation)](#lab-access) - Simplest option for institutional users

**For Local Installation**
- [Docker Installation](#docker-installation) - Run on your own computer

**For Developers**
- [Development Setup](#development) - Full development environment

---

## Lab Access

Access the shared installation via secure tunnel. No software installation required.

### Requirements
- Institutional HPC account
- Terminal or SSH client

### Steps

1. Open terminal (Command Prompt on Windows)
2. Connect to server:
   ```bash
   ssh -L 56052:localhost:56052 username@urmc-sh.rochester.edu
   ```
3. Open browser: `http://localhost:56052`

**Disconnect:** Close terminal or type `exit`

---

## Docker Installation

Install and run NeuroInsight on your local computer.

### Requirements

- Docker Desktop ([download](https://www.docker.com/products/docker-desktop))
- 16GB RAM minimum (32GB recommended)
- 30GB free disk space
- Windows 10+, macOS 10.15+, or Linux

### Installation

1. **Install Docker Desktop**
   - Download and install from link above
   - Start Docker and wait for it to initialize
   - Increase memory to 20GB (Settings → Resources → Memory)

2. **Download NeuroInsight**
   ```bash
   git clone https://github.com/phindagijimana/neuroinsight-web-app
   cd neuroinsight-web-app
   ```

3. **Start Application**
   ```bash
   docker-compose up -d
   ```
   
4. **Access Application**
   
   Open browser: `http://localhost:56052`

### Stopping

```bash
docker-compose down
```

---

## Using NeuroInsight

### 1. Upload Scan

- Supported formats: `.nii`, `.nii.gz`, `.dcm` (DICOM)
- File type: T1-weighted structural MRI

### 2. Process

- Click "Process" button
- Wait for completion (1-60 minutes depending on system)

### 3. View Results

- Hippocampal volumes (left and right)
- Asymmetry index
- 3D visualization
- Statistical analysis

### 4. Export

- Download results as JSON or CSV
- Save visualizations as images
- Generate reports

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 16 GB | 32 GB |
| Storage | 30 GB | 100 GB |
| GPU | Not required | NVIDIA GPU (faster) |

**Processing Time:**
- With GPU: 1-3 minutes per scan
- CPU only: 40-60 minutes per scan

---

## Platform Support

| Platform | Docker Method | Lab Access |
|----------|--------------|------------|
| Linux | Recommended | Yes |
| macOS Intel | Supported | Yes |
| macOS Apple Silicon | Limited* | Yes |
| Windows | Expected** | Yes |

*Requires 20GB+ RAM allocation, slower performance  
**Untested but should work

---

## Clinical Applications

NeuroInsight analyzes hippocampal asymmetry, relevant for:

- Temporal lobe epilepsy
- Alzheimer's disease
- Memory disorders
- Hippocampal sclerosis
- Neurodevelopmental conditions

**Note:** For research use. Clinical decisions require professional medical evaluation.

---

## Privacy

- All data processed locally on your system
- No internet connection required after installation
- No data transmitted to external servers
- Suitable for protected health information

---

## Troubleshooting

**"Cannot connect to Docker"**
- Ensure Docker Desktop is running
- Look for Docker icon in system tray/menu bar

**"Out of memory"**
- Increase Docker memory allocation to 20GB+
- Close other applications

**"Port already in use"**
- Stop and restart services:
  ```bash
  docker-compose down
  docker-compose up -d
  ```

**Processing fails or takes too long**
- Check system meets minimum requirements
- View logs: `docker-compose logs worker`

---

## Documentation

- **Quick Start:** [QUICK_START.md](QUICK_START.md)
- **Lab Access Guide:** [docs/LAB_ACCESS_GUIDE.md](docs/LAB_ACCESS_GUIDE.md)
- **Platform Testing:** [TEST_BOTH_VERSIONS.md](TEST_BOTH_VERSIONS.md)
- **API Reference:** `http://localhost:8000/docs` (when running)

---

## Development

### Setup

```bash
git clone https://github.com/phindagijimana/neuroinsight-web-app
cd neuroinsight-web-app
docker-compose up -d
```

### Architecture

- **Frontend:** Vite + JavaScript (Port 56052)
- **Backend:** FastAPI (Port 8000)
- **Worker:** Celery + FastSurfer
- **Database:** PostgreSQL
- **Queue:** Redis

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

---

## Support

**Common Issues:** See [Troubleshooting](#troubleshooting) section above

**GitHub Issues:** [Report bugs or request features](https://github.com/phindagijimana/neuroinsight-web-app/issues)

**Email:** support@neuroinsight.app

---

## Citation

If using NeuroInsight in research, please cite:

```
[Citation information to be added upon publication]
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

Built using FastSurfer deep learning neuroimaging segmentation, comparable to FreeSurfer accuracy in significantly less processing time.

---

**Version:** 1.0.0  
**Institution:** University of Rochester Medical Center
