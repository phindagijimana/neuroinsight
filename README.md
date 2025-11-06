# NeuroInsight

Automated hippocampal asymmetry analysis from T1-weighted MRI scans using FastSurfer deep learning segmentation.

---

## Deployment Options

### 1. HPC Access (URMC Lab Members)

Access the shared HPC installation via SSH tunnel - no local installation required.

```bash
ssh -L 56052:localhost:56052 username@urmc-sh.rochester.edu
```

Open browser to: `http://localhost:56052`

**Documentation:** [docs/LAB_ACCESS_GUIDE.md](docs/LAB_ACCESS_GUIDE.md)

---

### 2. Server Deployment (Docker Compose)

Deploy on Linux servers, HPC systems, or for local development.

```bash
git clone https://github.com/phindagijimana/neuroinsight-web-app
cd neuroinsight-web-app
docker-compose up -d
```

Open browser to: `http://localhost:56052`

**Supported Platforms:**
- Linux x86_64 (Recommended)
- macOS ARM64 (Limited - requires 20GB+ RAM, emulation)
- Windows x86_64 (Untested)

**Documentation:** See [Installation](#installation) below

---

### 3. Desktop Application

**Current Status:** Docker manager with Electron UI (requires Docker Desktop)

**Future Development:** Standalone executable with embedded backend (1-2 months)

**Documentation:** [docs/STANDALONE_DESKTOP_APP.md](docs/STANDALONE_DESKTOP_APP.md)

---

## Installation

### Prerequisites

**Required:**
- Docker Desktop ([download](https://www.docker.com/products/docker-desktop))
- 16GB RAM minimum, 32GB recommended
- 30GB free disk space

**Optional:**
- NVIDIA GPU with CUDA support (10-20x faster processing)

### Quick Start

1. **Clone repository:**
   ```bash
   git clone https://github.com/phindagijimana/neuroinsight-web-app
   cd neuroinsight-web-app
   ```

2. **Start services:**
   ```bash
   docker-compose up -d
   ```

3. **Access application:**
   ```
   http://localhost:56052
   ```

### Platform-Specific Notes

**Linux (x86_64):**
- Full support with Docker or Singularity
- Recommended for production deployments

**macOS (Apple Silicon):**
- Increase Docker Desktop memory to 20GB+
- Expect slower performance due to x86_64 emulation
- Consider using SSH tunnel to HPC instead

**Windows:**
- Should work similar to Linux (untested)
- Increase Docker Desktop memory allocation

---

## Usage

### Processing Workflow

1. **Upload** - T1-weighted MRI scan (.nii, .nii.gz, .dcm)
2. **Process** - Automated FastSurfer segmentation
3. **Analyze** - View hippocampal volumes and asymmetry metrics
4. **Export** - Download results in JSON, CSV, or image format

### Processing Time

- **GPU:** 1-3 minutes per scan
- **CPU:** 40-60 minutes per scan

### Results

- Left and right hippocampal volumes (mm³)
- Asymmetry Index: (L - R) / (L + R)
- 3D visualization and overlays
- Interactive brain viewer

---

## Management

### View Logs

```bash
docker-compose logs -f worker    # Processing logs
docker-compose logs -f backend   # API logs
```

### Stop Services

```bash
docker-compose down
```

### Update Installation

```bash
docker-compose down
git pull origin web-app
docker-compose pull
docker-compose up -d
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Lab Access Guide](docs/LAB_ACCESS_GUIDE.md) | SSH tunnel access for institutional users |
| [User Guide](docs/USER_GUIDE.md) | Detailed usage instructions |
| [API Documentation](http://localhost:8000/docs) | Interactive API reference (when running) |
| [Desktop App Plan](docs/STANDALONE_DESKTOP_APP.md) | Standalone application development |
| [Publication Checklist](PUBLICATION_READINESS_CHECKLIST.md) | Preparation for scientific publication |
| [Platform Testing](TEST_BOTH_VERSIONS.md) | Compatibility test results |

---

## Technical Details

### System Architecture

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Vite + Vanilla JS | Web interface |
| Backend | FastAPI | REST API server |
| Worker | Celery | Async task processing |
| Database | PostgreSQL | Data persistence |
| Cache | Redis | Task queue |
| Storage | MinIO | File management |
| Processing | FastSurfer + PyTorch | Brain segmentation |

### Network Ports

- `56052` - Web interface
- `8000` - API server
- `15432` - PostgreSQL
- `6379` - Redis
- `9000` - MinIO

### Storage Requirements

- **Docker images:** ~2.5GB (one-time download)
- **Per scan:** ~500MB (input + processed output)
- **Database:** Minimal (<100MB for metadata)

---

## Clinical Applications

Hippocampal asymmetry analysis is relevant to:

- Temporal lobe epilepsy
- Alzheimer's disease and dementia
- Hippocampal sclerosis
- Memory disorders
- Neurodevelopmental conditions

**Note:** This software is intended for research purposes. Clinical decisions should be made by qualified healthcare professionals based on comprehensive patient evaluation.

---

## Privacy & Compliance

- All processing occurs locally on your infrastructure
- No data transmitted to external servers
- No internet connection required after initial installation
- Suitable for HIPAA-compliant workflows
- Appropriate for sensitive medical data

---

## Performance

### GPU Acceleration (Linux only)

Install NVIDIA Docker Runtime:

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

GPU will be automatically detected and utilized.

---

## Troubleshooting

### Docker daemon not running

**Solution:** Start Docker Desktop and wait for initialization.

### Port conflicts

**Solution:** Stop existing services before starting:
```bash
docker-compose down
docker-compose up -d
```

### Out of memory errors

**Solution:** Increase Docker Desktop memory allocation to 20GB+ (Preferences → Resources → Memory)

### Processing failures

**Solution:** Check worker logs:
```bash
docker-compose logs worker
```

**Additional help:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## Development

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

### API Reference

Interactive documentation available at `http://localhost:8000/docs` when services are running.

### Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design details.

---

## License

MIT License - See [LICENSE](LICENSE) file for full text.

---

## Acknowledgments

This project builds upon:

- **FastSurfer** - Deep learning-based neuroimaging segmentation
- **FreeSurfer** - Gold standard brain MRI analysis suite
- **Docker** - Container platform for reproducible deployments

---

## Support

**Issues and bug reports:** [GitHub Issues](https://github.com/phindagijimana/neuroinsight-web-app/issues)

**Email:** support@neuroinsight.app

**Institution:** University of Rochester Medical Center, Neurology Department

---

## Citation

If you use NeuroInsight in your research, please cite:

```
[Citation information pending publication]
```

---

**Version:** 1.0.0  
**Last Updated:** November 2025
