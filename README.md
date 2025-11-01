# NeuroInsight

**Advanced Hippocampal Asymmetry Analysis Platform**

NeuroInsight is a neuroimaging application that processes T1-weighted MRI scans to compute hippocampal asymmetry indices using FastSurfer segmentation. Available as both a web application (for HPC/servers) and desktop software (for clinical/research use).

## Download

**Desktop Application**: https://github.com/phindagijimana/neuroinsight/releases

- **macOS 10.15+**: Download `.dmg` file
- **Windows 10/11**: Download `.exe` installer
- **Linux (Ubuntu 20.04+)**: Download `.AppImage` file

## Features

### Core Capabilities
- **Automated MRI Processing**: Upload T1-weighted scans (NIfTI or DICOM format)
- **FastSurfer Segmentation**: Whole-brain segmentation with hippocampal subfield extraction
- **Volume Measurements**: Bilateral hippocampal volume quantification
- **Asymmetry Analysis**: Left-right asymmetry index calculation with laterality classification
- **Interactive Visualization**: Real-time 3D viewer with overlay rendering
- **Statistical Charts**: Plotly-based interactive graphs
- **GPU Acceleration**: 10-20x faster processing with NVIDIA GPUs (optional)
- **Offline Processing**: All computation happens locally (HIPAA-compatible)

### Desktop Application Features
- **One-Click Installation**: Professional installer for all platforms
- **Auto-Service Management**: Docker containers managed automatically
- **System Tray Integration**: Quick access from taskbar/menu bar
- **First-Run Wizard**: Guided setup with system requirements check
- **Auto-Updates**: Built-in update mechanism (configurable)

## How It Works

### Processing Pipeline

1. **Upload**: Select T1-weighted MRI scan (NIfTI `.nii/.nii.gz` or DICOM `.dcm`)
2. **Validation**: Automatic format and quality checks
3. **Segmentation**: FastSurfer performs whole-brain segmentation
4. **Extraction**: Hippocampal subfields extracted from segmentation
5. **Analysis**: Volume measurements and asymmetry index calculation
6. **Visualization**: Interactive 3D overlays and statistical charts
7. **Export**: Results available as JSON and CSV

### Asymmetry Index Formula

```
AI = (Left - Right) / (Left + Right)
```

**Interpretation**:
- **AI > 0**: Left hemisphere larger than right
- **AI < 0**: Right hemisphere smaller than left  
- **AI ≈ 0**: Symmetric (balanced)

**Typical ranges**:
- Normal asymmetry: -0.10 to +0.10
- Significant asymmetry: |AI| > 0.10

### Laterality Classification

Based on clinical thresholds:
- **Left-dominant** (Right Hippocampal Sclerosis): AI > 0.047
- **Right-dominant** (Left Hippocampal Sclerosis): AI < -0.068
- **Balanced** (No Sclerosis): -0.068 ≤ AI ≤ 0.047

## Technology Stack

### Backend
- **API**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15 (job metadata, metrics storage)
- **Queue**: Redis 7 (Celery broker and result backend)
- **Storage**: MinIO (S3-compatible object storage)
- **Processing**: Celery workers with FastSurfer integration

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Visualization**: Plotly.js (charts), NiiVue (3D viewer)
- **State Management**: React hooks

### Processing Engine
- **Segmentation**: FastSurfer (deep learning-based brain segmentation)
- **Container**: Singularity/Apptainer or Docker
- **GPU Support**: NVIDIA CUDA (optional, auto-detected)
- **Image Processing**: nibabel, nilearn, matplotlib

### Desktop Application
- **Framework**: Electron 28
- **Docker Integration**: dockerode + docker-compose
- **Service Management**: Automatic container orchestration
- **System Integration**: Native menus, system tray, auto-start

## System Requirements

### Minimum Requirements (CPU Processing)
- **CPU**: 4 cores (Intel i5-11400, AMD Ryzen 5 5600 or equivalent)
- **RAM**: 16GB DDR4
- **Storage**: 30GB free space (SSD recommended)
- **OS**: Windows 10 64-bit, macOS 10.15+, Ubuntu 20.04+, or equivalent Linux
- **Docker**: Docker Desktop 4.0+ (auto-managed in desktop app)
- **Processing Time**: ~40-60 minutes per scan

### Recommended Requirements (GPU Processing)
- **CPU**: 8+ cores (Intel i7/i9, AMD Ryzen 7/9)
- **RAM**: 32GB DDR5
- **Storage**: 100GB NVMe SSD
- **GPU**: NVIDIA GPU with 8GB+ VRAM (RTX 3060, RTX 4060 Ti, or better)
- **CUDA**: Version 11.0+
- **Processing Time**: ~2-5 minutes per scan (10-20x faster)

### GPU Performance Benchmarks

| GPU Model | VRAM | Processing Time | Use Case |
|-----------|------|-----------------|----------|
| CPU Only | - | 40-60 min | Development, low-volume |
| RTX 3060 | 12GB | 3-5 min | Entry-level clinical |
| RTX 3080 | 10GB | 2-3 min | High-performance |
| RTX 4090 | 24GB | 1-2 min | Professional workstation |

## Installation

### Desktop Application (Recommended for End Users)

**Download**: https://github.com/phindagijimana/neuroinsight/releases

**macOS**:
1. Download `NeuroInsight-v1.0.0.dmg`
2. Open DMG and drag app to Applications
3. Launch from Applications folder
4. Follow first-run setup wizard

**Windows**:
1. Download `NeuroInsight-Setup-v1.0.0.exe`
2. Run installer (administrator rights required)
3. Follow installation wizard
4. Launch from Start Menu or desktop shortcut

**Linux**:
1. Download `NeuroInsight-v1.0.0.AppImage`
2. Make executable: `chmod +x NeuroInsight-v1.0.0.AppImage`
3. Double-click to run (no installation needed)

Or install via package manager:
```bash
# Ubuntu/Debian
sudo dpkg -i neuroinsight_1.0.0_amd64.deb

# Fedora/RHEL
sudo rpm -i neuroinsight-1.0.0.x86_64.rpm
```

### Web Application (Development/HPC)

**Prerequisites**:
- Python 3.11+
- Node.js 18+
- Docker or Singularity/Apptainer
- PostgreSQL 15, Redis 7, MinIO

**Quick Setup**:
```bash
# Clone repository
git clone https://github.com/phindagijimana/neuroinsight.git
cd neuroinsight

# Start all services
./RUN_ALL.sh

# Access application
# Frontend: http://localhost:56052/hippo_new_version.html
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Manual Setup**:
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Worker
celery -A workers.celery_app worker -l info

# Frontend
cd frontend
npm install
npm run dev  # Starts on port 56052
```

## Usage

### 1. Upload MRI Scan

**Supported Formats**:
- NIfTI: `.nii`, `.nii.gz` (preferred)
- DICOM: `.dcm` (single file or series)

**Requirements**:
- T1-weighted sequence (MPRAGE, SPGR, TFE, or TFL)
- 3D volume (512×512×170 typical)
- Voxel size: 0.5-2.0mm isotropic recommended
- File size: < 500MB

**Steps**:
1. Click "Upload" in navigation
2. Select or drag-and-drop MRI file
3. Click "Upload and Process"
4. Redirected to job detail page

### 2. Monitor Processing

**Job Stati**:
- **Pending**: Queued, waiting to start
- **Running**: Currently processing
- **Completed**: Results available
- **Failed**: Error occurred (see error message)

**Progress Updates**:
- Status updates automatically (5-second polling)
- Processing time displayed
- Real-time log streaming (web version)

### 3. View Results

Once processing completes:

**Metrics Table**:
- Region names (Hippocampus, CA1, CA3, CA4, DG, Subiculum, etc.)
- Left hemisphere volume (mm³)
- Right hemisphere volume (mm³)
- Asymmetry index
- Laterality classification

**Visualizations**:
- 3D MRI viewer with hippocampal overlays
- Coronal slice navigation (10 slices)
- Asymmetry index bar chart
- Volume comparison chart (left vs right)
- Interactive Plotly charts (zoom, pan, export)

**Data Export**:
- JSON format: `data/outputs/{job_id}/results.json`
- CSV format: `data/outputs/{job_id}/metrics.csv`
- Visualization PNGs: `data/outputs/{job_id}/visualizations/`

## Architecture Details

### Backend (FastAPI)

**Key Components**:
- `backend/main.py`: Application entry point with CORS and routing
- `backend/api/`: REST endpoints (upload, jobs, metrics, visualizations)
- `backend/services/`: Business logic (job management, storage, cleanup)
- `backend/models/`: SQLAlchemy ORM models
- `backend/schemas/`: Pydantic validation schemas

**Endpoints**:
- `POST /upload/`: Upload MRI file and start processing
- `GET /jobs/`: List all jobs (with pagination and filtering)
- `GET /jobs/{id}`: Get job details with metrics
- `GET /metrics/?job_id={id}`: Get metrics for job
- `GET /visualizations/{job_id}/overlay/{slice}`: Serve overlay images
- `GET /health`: Health check endpoint

### Processing Pipeline

**MRI Processor** (`pipeline/processors/mri_processor.py`):

1. **Input Preparation**:
   - Validate NIfTI format or convert DICOM to NIfTI
   - Check image dimensions and voxel spacing
   - Verify T1-weighted characteristics

2. **FastSurfer Segmentation**:
   - Run FastSurfer in Singularity/Docker container
   - Auto-detect GPU (CUDA) or use CPU
   - Whole-brain segmentation with hippocampal subfields
   - Thread optimization (uses n-2 cores for CPU processing)

3. **Hippocampal Extraction**:
   - Parse FastSurfer statistics files
   - Extract bilateral volumes for each subfield
   - Validate data completeness

4. **Asymmetry Calculation** (`pipeline/utils/asymmetry.py`):
   - Compute AI = (L - R) / (L + R) for each region
   - Classify laterality based on clinical thresholds
   - Generate summary statistics

5. **Visualization** (`pipeline/utils/visualization.py`):
   - Generate hippocampal overlay images
   - Create coronal slices with proper orientation
   - Apply color mapping for different structures

6. **Storage**:
   - Save results to MinIO (S3-compatible storage)
   - Store metrics in PostgreSQL database
   - Generate JSON and CSV exports

### Frontend (React)

**Single-Page Application** (`frontend/public/hippo_new_version.html`):
- Home page with system status
- Upload interface with drag-and-drop
- Jobs list with real-time updates
- Job detail page with metrics and visualizations
- Interactive 3D viewer (NiiVue-based)
- Statistical charts (Plotly.js)

**API Integration**:
- Axios-based HTTP client
- Automatic polling for job status
- Cache-busting for visualization images
- Error handling and user feedback

### Worker (Celery)

**Task Queue** (`workers/tasks/processing.py`):
- Asynchronous MRI processing
- Job state management (pending → running → completed/failed)
- Error handling and logging
- Resource cleanup on failure

**Configuration** (`workers/celery_app.py`):
- Redis broker for message queue
- PostgreSQL result backend
- Task routing and priority
- Retry logic for failed tasks

### Desktop Application (Electron)

**Components**:
- `src/main.js`: Main process with window and tray management
- `src/managers/DockerManager.js`: Docker Desktop integration
- `src/managers/ServiceManager.js`: docker-compose orchestration
- `src/utils/SystemChecker.js`: Requirements validation
- `src/setup.html`: First-run setup wizard

**Features**:
- Automatic Docker service startup
- Health monitoring for all services
- System tray menu (start/stop/restart)
- Cross-platform support (Windows/macOS/Linux)
- Auto-update capability

## Data Storage

### Directory Structure
```
data/
├── uploads/          # Original MRI files
├── outputs/          # Processing results
│   └── {job_id}/
│       ├── fastsurfer/              # FastSurfer outputs
│       ├── visualizations/
│       │   └── overlays/            # PNG overlay images
│       ├── results.json             # Metrics (JSON)
│       └── metrics.csv              # Metrics (CSV)
└── logs/             # Application logs
```

### Storage Management

**Cleanup Utility** (`bin/cleanup_storage.py`):
```bash
# Dry run (see what would be deleted)
python bin/cleanup_storage.py --dry-run

# Clean orphaned files
python bin/cleanup_storage.py --orphaned-only

# Clean old completed jobs (default: 90 days)
python bin/cleanup_storage.py --old-completed --completed-days 60

# Clean old failed jobs (default: 30 days)  
python bin/cleanup_storage.py --old-failed --failed-days 14
```

**Retention Policy**:
- Completed jobs: 90 days (configurable)
- Failed jobs: 30 days (configurable)
- Orphaned files: Cleaned on demand

## Configuration

### Environment Variables

**Database**:
- `POSTGRES_HOST`: PostgreSQL host (default: localhost)
- `POSTGRES_PORT`: PostgreSQL port (default: 5432)
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

**Redis**:
- `REDIS_HOST`: Redis host (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)

**MinIO (S3 Storage)**:
- `MINIO_ENDPOINT`: MinIO endpoint (default: localhost:9000)
- `MINIO_ACCESS_KEY`: Access key (default: minioadmin)
- `MINIO_SECRET_KEY`: Secret key
- `MINIO_BUCKET`: Bucket name (default: neuroinsight-data)

**Application**:
- `ENVIRONMENT`: development/production
- `LOG_LEVEL`: DEBUG/INFO/WARNING/ERROR
- `UPLOAD_DIR`: Upload directory path
- `OUTPUT_DIR`: Output directory path

**Processing**:
- `MAX_CONCURRENT_JOBS`: Maximum parallel jobs (default: 2)
- `PROCESSING_TIMEOUT`: Job timeout in seconds (default: 3600)
- `RETENTION_COMPLETED_DAYS`: Days to keep completed jobs (default: 90)
- `RETENTION_FAILED_DAYS`: Days to keep failed jobs (default: 30)

## API Documentation

### Upload Endpoint

```http
POST /upload/
Content-Type: multipart/form-data

Request:
  file: <MRI file>

Response: 201 Created
{
  "id": "uuid",
  "filename": "scan.nii.gz",
  "status": "pending",
  "created_at": "2025-11-01T12:00:00Z"
}
```

### Get Job

```http
GET /jobs/{job_id}

Response: 200 OK
{
  "id": "uuid",
  "filename": "scan.nii.gz",
  "status": "completed",
  "started_at": "2025-11-01T12:01:00Z",
  "completed_at": "2025-11-01T12:45:00Z",
  "result_path": "data/outputs/uuid/",
  "metrics": [
    {
      "region": "Hippocampus",
      "left_volume": 4250.5,
      "right_volume": 4100.2,
      "asymmetry_index": 0.0179
    }
  ]
}
```

### List Jobs

```http
GET /jobs/?skip=0&limit=100&status=completed

Response: 200 OK
[
  { "id": "...", "filename": "...", "status": "completed", ... }
]
```

### Visualization Endpoint

```http
GET /visualizations/{job_id}/overlay/slice_00

Response: 200 OK
Content-Type: image/png
[PNG image data]
```

**Interactive API Documentation**: http://localhost:8000/docs

## Project Structure

```
neuroinsight/
├── backend/                  # FastAPI backend
│   ├── api/                 # REST endpoint handlers
│   │   ├── upload.py       # File upload with validation
│   │   ├── jobs.py         # Job CRUD operations
│   │   ├── metrics.py      # Metrics retrieval
│   │   ├── visualizations.py # Image serving
│   │   └── cleanup.py      # Storage cleanup endpoint
│   ├── core/
│   │   ├── config.py       # Settings management
│   │   ├── database.py     # Database connection
│   │   └── logging.py      # Structured logging
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── job.py          # Job model
│   │   └── metric.py       # Metric model
│   ├── schemas/             # Pydantic validation
│   │   ├── job.py          # Job schemas
│   │   └── metric.py       # Metric schemas
│   ├── services/            # Business logic
│   │   ├── job_service.py  # Job operations
│   │   ├── metric_service.py # Metric operations
│   │   ├── storage_service.py # File storage (MinIO)
│   │   └── cleanup_service.py # Cleanup operations
│   ├── main.py              # Application entry point
│   └── requirements.txt     # Python dependencies
│
├── frontend/                 # React frontend
│   ├── public/
│   │   └── hippo_new_version.html # Single-file React app
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration with proxy
│
├── workers/                  # Celery workers
│   ├── celery_app.py        # Celery configuration
│   └── tasks/
│       ├── processing.py    # MRI processing task
│       └── cleanup.py       # Cleanup task
│
├── pipeline/                 # MRI processing pipeline
│   ├── processors/
│   │   └── mri_processor.py # Main processor orchestration
│   └── utils/
│       ├── asymmetry.py     # Asymmetry calculations
│       ├── file_utils.py    # File operations
│       ├── segmentation.py  # FastSurfer parsing
│       └── visualization.py # Overlay generation
│
├── hippo_desktop/            # Desktop application (Electron)
│   ├── src/
│   │   ├── main.js          # Main process
│   │   ├── preload.js       # IPC bridge
│   │   ├── managers/        # Docker & service management
│   │   └── utils/           # System checks, logging
│   ├── assets/              # Icons
│   ├── build/               # Platform-specific icons
│   ├── package.json         # Build configuration
│   └── README.md            # Desktop app documentation
│
├── docker/                   # Docker configurations
│   ├── Dockerfile.backend
│   ├── Dockerfile.worker
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── docs/                     # Technical documentation
├── tests/                    # Test suite
├── bin/                      # Utility scripts
├── docker-compose.yml        # Service orchestration
└── RUN_ALL.sh               # Quick start script
```

## Development

### Running Locally

```bash
# Start all services
./RUN_ALL.sh

# Or start individually:
# 1. Database and Redis (via Singularity or Docker)
# 2. Backend
cd backend
uvicorn backend.main:app --reload --port 8000

# 3. Worker
celery -A workers.celery_app worker -l info

# 4. Frontend
cd frontend
npm run dev
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test
pytest tests/unit/test_asymmetry.py
```

### Database Migrations

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Troubleshooting

### Web Application

**Backend not accessible**:
```bash
# Check health
curl http://localhost:8000/health

# Check logs
tail -f logs/backend.out
```

**Worker not processing**:
```bash
# Check worker logs
tail -f logs/worker.out

# Verify Redis
redis-cli ping
```

**Uploads failing**:
- Ensure file is T1-weighted MRI
- Check file size < 500MB
- Verify format (NIfTI or DICOM)
- Check logs for validation errors

### Desktop Application

**Docker not starting**:
- Ensure Docker Desktop is installed and running
- Check Docker Desktop settings
- Restart Docker Desktop

**Services not healthy**:
- System Tray → View Logs
- System Tray → Restart Services
- Check system resources (RAM, disk space)

**Processing slow**:
- Check if GPU is detected (System Info)
- Increase Docker memory limit (Docker Desktop → Settings → Resources)
- Close other applications

## Performance Optimization

### GPU Acceleration

**Setup** (Linux):
```bash
# Install NVIDIA drivers
sudo ubuntu-drivers autoinstall

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

**Verify GPU Detection**:
```bash
nvidia-smi  # Should show GPU info
```

### Parallel Processing

Edit `.env` or configuration:
```bash
MAX_CONCURRENT_JOBS=4  # Process multiple scans simultaneously
# Note: Requires 16GB RAM per job
```

## Security & Privacy

### Data Privacy
- **Local Processing**: All computation happens on your infrastructure
- **No Cloud**: Data never leaves your server/desktop
- **HIPAA Compatible**: Suitable for protected health information
- **Offline Capable**: No internet required after installation

### Security Best Practices
- Change default passwords in production
- Use environment variables for secrets (never commit `.env` files)
- Enable HTTPS/TLS for production deployments
- Implement authentication for multi-user setups
- Regular security updates

## Deployment

### Production Web Deployment

**Docker Compose** (recommended):
```bash
docker-compose up -d
```

**Services**:
- Frontend: nginx on port 80/443
- Backend: uvicorn behind nginx
- Worker: celery worker(s)
- Database: PostgreSQL with persistent volumes
- Redis: message broker
- MinIO: object storage

### Desktop Distribution

**Create Release**:
```bash
# Update version in hippo_desktop/package.json
# Then create git tag:
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

GitHub Actions automatically:
- Builds installers for all platforms
- Creates GitHub Release
- Uploads installers

## Utility Scripts

**Located in `bin/` folder**:

- `cleanup_storage.py`: Clean old jobs and orphaned files
- `regenerate_metrics.py`: Recompute metrics for existing job
- `regenerate_visualizations.py`: Regenerate overlay images
- `restore_orphaned_jobs.py`: Restore jobs from output directories
- `migrate_add_cancelled_status.py`: Database migration helper
- `test_complete_pipeline.sh`: Integration test suite
- `test_viewer_with_real_job.sh`: Viewer integration test

## Contributing

See `CONTRIBUTING.md` for:
- Development setup
- Code style guidelines
- How to create releases
- Commit message conventions

## Support & Resources

- **GitHub Repository**: https://github.com/phindagijimana/neuroinsight
- **Issues**: https://github.com/phindagijimana/neuroinsight/issues
- **Releases/Downloads**: https://github.com/phindagijimana/neuroinsight/releases
- **API Documentation**: http://localhost:8000/docs (when running)

## License

This project is provided for research and educational purposes. Please ensure compliance with:
- FastSurfer licensing terms
- FreeSurfer licensing terms (license.txt required)
- Medical imaging data regulations (HIPAA, GDPR as applicable)

## Acknowledgments

- **FastSurfer Team**: Deep learning-based brain segmentation
- **FreeSurfer Team**: Hippocampal subfield analysis algorithms
- **Open Source Community**: Excellent tools and libraries

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Maintainer**: https://github.com/phindagijimana
