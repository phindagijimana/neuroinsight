# NeuroInsight

**Advanced Hippocampal Asymmetry Analysis Platform**

NeuroInsight processes T1-weighted MRI scans to compute hippocampal asymmetry indices using FastSurfer segmentation. Available as both a web application and desktop software.

## Quick Start

### Web Application (HPC/Server)

```bash
./RUN_ALL.sh
# Access at: http://localhost:56052/hippo_new_version.html
```

### Desktop Application (End Users)

Download from: https://github.com/phindagijimana/neuroinsight/releases

- **macOS**: Download `.dmg` file
- **Windows**: Download `.exe` installer
- **Linux**: Download `.AppImage` file

See `hippo_desktop/QUICK_START.md` for detailed installation instructions.

## Features

- **MRI Processing**: FastSurfer-based whole-brain segmentation
- **Hippocampal Analysis**: Automated subfield extraction and volumetric measurements
- **Asymmetry Calculation**: Left-right asymmetry index with laterality classification
- **Interactive Visualization**: Real-time 3D viewer and statistical charts
- **GPU Acceleration**: 10-20x faster processing with NVIDIA GPUs
- **Desktop Application**: One-click installation for Windows, macOS, and Linux

## Architecture

### Technology Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18 + Vite
- **Processing**: Celery + FastSurfer (Singularity/Docker)
- **Database**: PostgreSQL 15
- **Queue**: Redis 7
- **Storage**: MinIO (S3-compatible)
- **Desktop**: Electron 28

### Components

```
┌────────────────────┐
│  React Frontend    │
└─────────┬──────────┘
          │
┌─────────▼──────────┐
│  FastAPI Backend   │
└────┬─────────┬─────┘
     │         │
┌────▼────┐ ┌─▼──────────┐
│PostgreSQL│ │Celery Worker│
└─────────┘ └──────┬──────┘
                   │
            ┌──────▼────────┐
            │   FastSurfer  │
            │  (Container)  │
            └───────────────┘
```

## System Requirements

### Minimum (CPU Processing)
- **CPU**: 4 cores
- **RAM**: 16GB
- **Storage**: 30GB free
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **Processing time**: ~40-60 minutes per scan

### Recommended (GPU Processing)
- **CPU**: 8+ cores
- **RAM**: 32GB
- **Storage**: 100GB SSD
- **GPU**: NVIDIA GPU with 8GB+ VRAM
- **Processing time**: ~2-5 minutes per scan

## Installation

### Web Version (Development)

```bash
# Install dependencies
cd backend && pip install -r requirements.txt
cd frontend && npm install

# Start services
./RUN_ALL.sh
```

### Desktop Version (End Users)

1. Download installer from [Releases](https://github.com/phindagijimana/neuroinsight/releases)
2. Double-click to install
3. Launch NeuroInsight
4. Follow setup wizard

## Usage

### Upload MRI Scan
1. Navigate to Upload page
2. Select T1-weighted MRI file (`.nii`, `.nii.gz`, or `.dcm`)
3. Click "Upload and Process"

### Monitor Processing
- Job status updates automatically
- View progress in Jobs page
- Typical processing: 2-60 minutes depending on hardware

### View Results
- Hippocampal volume measurements
- Asymmetry index calculations
- Interactive 3D visualization
- Export data as JSON/CSV

## Asymmetry Index Formula

```
AI = (Left - Right) / (Left + Right)
```

Where:
- **AI > 0**: Left hemisphere larger
- **AI < 0**: Right hemisphere larger
- **AI ≈ 0**: Symmetric

## Documentation

- **Desktop App**: `hippo_desktop/README.md` - Desktop application guide
- **Quick Start**: `hippo_desktop/QUICK_START.md` - Installation for end users
- **Architecture**: `docs/ARCHITECTURE.md` - Technical architecture
- **Storage**: `docs/STORAGE_MANAGEMENT.md` - Data management
- **Contributing**: `CONTRIBUTING.md` - Development guide

## Project Structure

```
neuroinsight/
├── backend/              # FastAPI application
│   ├── api/             # REST endpoints
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   └── schemas/         # Pydantic schemas
├── frontend/            # React UI
├── workers/             # Celery task workers
├── pipeline/            # MRI processing
│   ├── processors/     # Main processing logic
│   └── utils/          # Processing utilities
├── hippo_desktop/       # Desktop application (Electron)
├── docker/              # Docker configurations
├── docs/                # Technical documentation
└── tests/               # Test suite
```

## Support

- **Issues**: https://github.com/phindagijimana/neuroinsight/issues
- **Releases**: https://github.com/phindagijimana/neuroinsight/releases
- **Documentation**: See `docs/` folder

## License

See LICENSE file for details.

## Acknowledgments

- FastSurfer team for neuroimaging segmentation tools
- FreeSurfer team for hippocampal analysis algorithms
- Open source community
