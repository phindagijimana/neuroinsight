# NeuroInsight

**Automated hippocampal asymmetry analysis from T1-weighted MRI scans**

Fast, accurate brain segmentation with GPU acceleration using FastSurfer.

## Quick Start

### Desktop App (Recommended)

**Download**: [Latest Release](https://github.com/phindagijimana/neuroinsight/releases)

- **macOS**: Download `.zip`, extract, drag to Applications, right-click → Open
- **Windows**: Download `.exe`, run installer
- **Linux**: Download `.AppImage`, make executable, run

**Requirements**: 4+ cores, 16GB RAM, 30GB storage, Docker Desktop

### Web Application (For Servers/HPC)

```bash
git clone https://github.com/phindagijimana/neuroinsight.git
cd neuroinsight
docker-compose up -d
```

Open http://localhost:3000

## Features

- **Automated Processing**: Upload MRI scan → get results in minutes
- **FastSurfer Segmentation**: Whole-brain segmentation with hippocampal subfields
- **Asymmetry Analysis**: AI = (Left - Right) / (Left + Right)
- **GPU Acceleration**: 10-20x faster with NVIDIA GPU (optional)
- **Interactive Viewer**: Real-time 3D visualization
- **Offline**: 100% local processing (HIPAA-compatible)

## How It Works

1. Upload T1-weighted MRI (`.nii`, `.nii.gz`, or `.dcm`)
2. FastSurfer performs brain segmentation
3. Extract hippocampal volumes (left/right)
4. Calculate asymmetry index
5. View 3D overlays and charts
6. Export results (JSON/CSV)

## System Requirements

**Minimum** (CPU mode):
- 4 cores, 16GB RAM, 30GB storage
- Processing: ~40-60 min/scan

**Recommended** (GPU mode):
- 8+ cores, 32GB RAM, 100GB SSD
- NVIDIA GPU (8GB+ VRAM)
- Processing: ~2-5 min/scan

## Technology

- **Backend**: FastAPI, PostgreSQL, Redis, Celery, MinIO
- **Frontend**: React, Vite, Tailwind CSS, Plotly, NiiVue
- **Processing**: FastSurfer, Singularity/Docker
- **Desktop**: Electron, Docker Compose

## Documentation

- [Desktop Quick Start](hippo_desktop/QUICK_START.md)
- [Development Guide](hippo_desktop/README.md)
- [Contributing](CONTRIBUTING.md)

## Architecture

```
┌─────────────┐
│   Upload    │ → NIfTI/DICOM scan
└──────┬──────┘
       ↓
┌─────────────┐
│  FastSurfer │ → Whole-brain segmentation (GPU/CPU)
└──────┬──────┘
       ↓
┌─────────────┐
│  Analysis   │ → Volume measurements + asymmetry
└──────┬──────┘
       ↓
┌─────────────┐
│   Results   │ → 3D viewer, charts, exports
└─────────────┘
```

## Clinical Interpretation

**Asymmetry Index (AI)**:
- **AI > 0.047**: Left-dominant (possible right hippocampal sclerosis)
- **AI < -0.068**: Right-dominant (possible left hippocampal sclerosis)
- **-0.068 to 0.047**: Balanced (normal range)

## Support

- **Issues**: https://github.com/phindagijimana/neuroinsight/issues
- **Discussions**: https://github.com/phindagijimana/neuroinsight/discussions

## License

MIT License - See [LICENSE](LICENSE) for details

## Acknowledgments

Built with [FastSurfer](https://github.com/Deep-MI/FastSurfer) for deep learning-based brain MRI segmentation.

---

**Ready to start?** [Download the latest release](https://github.com/phindagijimana/neuroinsight/releases) or [try the web version](#web-application-for-servershpc)!
