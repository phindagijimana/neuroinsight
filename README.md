NeuroInsight (Current App)

Overview
This repository hosts the NeuroInsight application for uploading T1-weighted MRI scans, running FastSurfer segmentation, and visualizing hippocampal overlays and volumetric metrics. The current frontend is a single-file HTML React app served by Vite with a proxy to the FastAPI backend. Processing is executed asynchronously by a Celery worker. Files are stored in MinIO (S3-compatible), and job/metric metadata is stored in Postgres. Redis is used as the Celery broker and result backend.

Key Components
- Frontend (single-file React):
  - File: frontend/public/hippo_new_version.html
  - Served by Vite dev server; all API requests go through /api proxy to the backend.
- Backend (FastAPI):
  - Entry: backend/main.py
  - APIs: backend/api/upload.py, backend/api/jobs.py, backend/api/visualizations.py, backend/api/metrics.py
  - Settings: backend/core/config.py
  - DB: backend/core/database.py (Postgres)
- Processing pipeline:
  - Celery app: workers/celery_app.py
  - Task: workers/tasks/processing.py
  - MRI processing: pipeline/processors/mri_processor.py
  - Visualization utilities: pipeline/utils/visualization.py
- Storage & Infrastructure:
  - MinIO (S3): saves uploads and outputs (via StorageService)
  - Redis: Celery broker/result
  - Postgres: jobs/metrics
  - Singularity images: singularity-images/*.sif (FastSurfer, Redis, MinIO, Postgres)

One-command local run
Use the helper script to start everything (Redis, MinIO, backend, worker, frontend):

  ./RUN_ALL_LOCAL.sh

What it does
- Starts Redis and MinIO via Apptainer/Singularity when available
- Starts backend (uvicorn) on 0.0.0.0:8000
- Starts Celery worker
- Starts Vite on 0.0.0.0:56052 with a proxy so the UI can call /api/… on the same port

Accessing the app
- Open your browser at:
  - http://localhost:56052/hippo_new_version.html
- If accessing from a remote HPC node, tunnel ports 56052 and 8000 to your laptop, or use OOD Desktop’s browser. Example:

  ssh -N -L 56052:127.0.0.1:56052 -L 8000:127.0.0.1:8000 <user>@<node>

Frontend details
- The UI is implemented in frontend/public/hippo_new_version.html to simplify deployment on HPC environments without a full frontend build pipeline.
- Vite dev server provides Live Reload; the proxy maps /api/* → http://127.0.0.1:8000/* (see frontend/vite.config.ts).
- The Viewer loads hippocampus overlay PNGs from /api/visualizations/{jobId}/overlay/slice_XX with cache-busting to avoid stale images.

Backend details
- Upload endpoint: POST /upload/
  - Strict pre-validation for T1-weighted input:
    - File size limits and emptiness checks
    - For NIfTI: nibabel load test, 3D/4D shape sanity, voxel spacing sanity (0.2–5.0 mm), non-zero finite data, filename/header markers for T1 (t1/mprage/spgr/tfl/tfe)
    - For DICOM: SeriesDescription/ProtocolName/SequenceName checked when pydicom is available; else filename markers
  - On success: file is saved to MinIO, a Job record is created, and Celery enqueues processing.
- Jobs endpoints: /jobs/, /jobs/{id}
- Visualizations: /visualizations/{jobId}/overlay/slice_XX serve upright, voxel-correct overlays

Processing details
- workers/tasks/processing.py creates an MRIProcessor for each job:
  - Detects GPU (via nvidia-smi) and uses Singularity --nv when available; otherwise CPU.
  - Runs FastSurfer whole-brain segmentation in a container (singularity-images/fastsurfer.sif).
  - Extracts hippocampal metrics from FastSurfer stats.
  - Generates overlays using pipeline/utils/visualization.py (upright orientation, correct aspect ratio based on voxel sizes).

Metrics and thresholds
- The Stats page computes total hippocampal volume and Asymmetry Index (AI):
  - AI = (Left − Right) / ((Left + Right) / 2) [raw value, not %]
  - Thresholds displayed for reference:
    - Left HS (Right-dominant) if AI < -0.068471917756097
    - Right HS (Left-dominant) if AI > 0.047289139210141
    - No HS (Balanced) otherwise

File locations
- Uploads: data/uploads/
- Outputs: data/outputs/<jobId>/
  - fastsurfer/… (container outputs)
  - visualizations/overlays/hippocampus_slice_00..09.png
  - visualizations/whole_hippocampus/*
- Logs: logs/

Cleanup utilities
- Safe cleanup for caches and logs:

  bin/cleanup.sh

- Archival of deprecated/unused files uses a timestamped _trash/ folder. Nothing is permanently deleted by the helper moves.

Troubleshooting
- App not reachable at 56052:
  - Ensure Vite dev server is listening (see logs/vite-56052.out)
  - If remote: verify SSH tunnel or use OOD Desktop browser
- API 500/connection refused:
  - Confirm backend health: curl -sI http://127.0.0.1:8000/health
  - Vite proxy: curl -sI http://127.0.0.1:56052/api/health
- Worker not processing:
  - Check logs/worker.out; verify Redis running
- Overlays upside-down or stretched:
  - Fixed in visualization pipeline: images saved upright with voxel-correct aspect
- Regenerate overlays for an existing job: python3 bin/regenerate_visualizations.py <job_id>
- Regenerate metrics for an existing job: python3 bin/regenerate_metrics.py <job_id>
- Upload rejected (T1 validation):
  - Ensure file is a valid T1 NIfTI/DICOM with typical T1 markers; verify nibabel can load it locally

Ports
- Frontend (Vite): 56052
- Backend (FastAPI): 8000
- MinIO (S3): 9000
- Redis: 6379

Environment and images
- Singularity images are in singularity-images/ (fastsurfer.sif, minio.sif, redis.sif, postgres.sif, freesurfer.sif). RUN_ALL_LOCAL.sh will pull/create if missing.

Development notes
- The single-file frontend is intentionally used for HPC simplicity. If/when you want to migrate to a modular TSX app, the archived frontend/src can be restored from _trash and wired via Vite’s main.tsx entry.

License
- See license.txt (if applicable in your environment).

# NeuroInsight Dev

**Advanced Hippocampal Asymmetry Analysis Platform**

NeuroInsight is a neuroimaging web application that processes T1-weighted MRI scans to compute hippocampal asymmetry indices. Built with modern web technologies and containerized for reproducibility, it provides an end-to-end pipeline from MRI upload to interactive visualization.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Code Documentation](#code-documentation)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

**Core Capabilities**

- **MRI Upload**: Support for DICOM and NIfTI formats
- **Automated Processing**: FastSurfer-based brain segmentation
- **Hippocampal Analysis**: Subfield extraction and volumetric measurements
- **Asymmetry Calculation**: Left-right asymmetry index computation
- **Interactive Dashboard**: Real-time results visualization with charts
- **Asynchronous Processing**: Queue-based job management
- **Containerized**: Fully Dockerized for reproducibility
- **Type-Safe**: TypeScript frontend and Python type hints

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│              Vite + TypeScript + Tailwind                │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│                 Backend API (FastAPI)                    │
│        Python 3.11 + Pydantic + SQLAlchemy              │
└────────┬───────────────────────────┬────────────────────┘
         │                           │
         ▼                           ▼
┌────────────────┐         ┌─────────────────────┐
│   PostgreSQL   │         │  Celery Workers     │
│   (Database)   │         │  (Task Processing)  │
└────────────────┘         └──────────┬──────────┘
                                      │
                           ┌──────────▼──────────┐
                           │  Processing Engine  │
                           │  (FastSurfer + AI)  │
                           └─────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, TypeScript, Vite | User interface |
| **Styling** | Tailwind CSS | Modern responsive design |
| **Visualization** | Plotly.js | Interactive charts |
| **Backend** | FastAPI, Python 3.11 | REST API server |
| **Database** | PostgreSQL 15 | Job and metrics storage |
| **Queue** | Celery + Redis | Asynchronous task processing |
| **Storage** | MinIO | S3-compatible object storage |
| **Processing** | FastSurfer, nibabel | MRI analysis pipeline |
| **Containerization** | Docker, Docker Compose | Service orchestration |

---

## Prerequisites

### Required Software

- **Docker** 24.0+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.20+ (included with Docker Desktop)
- **Git** (for cloning the repository)

### Optional (for local development)

- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 15+
- **Redis** 7+

### System Requirements

- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 20GB free space
- **CPU**: Multi-core processor recommended for processing
- **OS**: Linux, macOS, or Windows (with WSL2)

---

## Quick Start

### 1. Clone the Repository

```bash
cd /path/to/your/workspace
cd general_code/hippo
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your preferred settings (optional for development)
# The defaults are suitable for local development
```

### 3. Start All Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001

### 5. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

---

## Detailed Setup

### Environment Configuration

The `.env` file controls all application settings. Key variables:

```bash
# Database
POSTGRES_USER=neuroinsight
POSTGRES_PASSWORD=change_in_production
POSTGRES_DB=neuroinsight

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# MinIO Storage
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=neuroinsight-data

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
API_PORT=8000

# Processing
FASTSURFER_CONTAINER=fastsurfer/fastsurfer:latest
PROCESSING_TIMEOUT=3600
MAX_CONCURRENT_JOBS=2
```

### Building from Source

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend

# Build without cache
docker-compose build --no-cache
```

### Development Mode

For local development with hot-reload:

```bash
# Start with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Backend will auto-reload on code changes
# Frontend will have HMR (Hot Module Replacement)
```

---

## Usage Guide

### Uploading an MRI Scan

1. **Navigate to Upload Page**
   - Click "Upload" in the navigation bar
   - Or go directly to http://localhost:5173/upload

2. **Select File**
   - Click "Choose a file" or drag and drop
   - Supported formats: `.nii`, `.nii.gz`, `.dcm`, `.dicom`
   - Maximum size: 500MB

3. **Submit**
   - Click "Upload and Process"
   - You'll be redirected to the job detail page

### Monitoring Processing

1. **Job List**
   - Go to http://localhost:5173/jobs
   - View all processing jobs with their status

2. **Job Details**
   - Click on any job to view details
   - Status updates automatically (polls every 5 seconds)

3. **Processing Stages**
   - **Pending**: Job queued, waiting to start
   - **Running**: Currently processing
   - **Completed**: Results available
   - **Failed**: Error occurred (see error message)

### Viewing Results

Once processing completes, the job detail page shows:

1. **Hippocampal Metrics Table**
   - Region names (CA1, CA3, subiculum, etc.)
   - Left and right hemisphere volumes (mm³)
   - Asymmetry indices
   - Laterality classification

2. **Visualizations**
   - Asymmetry index bar chart
   - Volume comparison (left vs right)
   - Interactive Plotly charts (zoom, pan, download)

3. **Export Options**
   - Data available in JSON and CSV formats
   - Located in output directory

---

## Project Structure

```
hippo/
├── backend/                    # FastAPI backend application
│   ├── api/                   # API route handlers
│   │   ├── jobs.py           # Job management endpoints
│   │   ├── metrics.py        # Metrics retrieval endpoints
│   │   └── upload.py         # File upload endpoint
│   ├── core/                 # Core configuration
│   │   ├── config.py         # Settings management
│   │   ├── database.py       # Database connection
│   │   └── logging.py        # Structured logging
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── job.py           # Job model
│   │   └── metric.py        # Metric model
│   ├── schemas/              # Pydantic validation schemas
│   │   ├── job.py           # Job schemas
│   │   └── metric.py        # Metric schemas
│   ├── services/             # Business logic layer
│   │   ├── job_service.py   # Job operations
│   │   ├── metric_service.py # Metric operations
│   │   └── storage_service.py # File storage
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
│
├── workers/                   # Celery task workers
│   ├── tasks/
│   │   └── processing.py    # MRI processing task
│   └── celery_app.py        # Celery configuration
│
├── pipeline/                  # MRI processing pipeline
│   ├── processors/
│   │   └── mri_processor.py # Main processing orchestrator
│   └── utils/
│       ├── asymmetry.py     # Asymmetry calculations
│       ├── file_utils.py    # File operations
│       └── segmentation.py  # Segmentation parsing
│
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Layout.tsx   # App layout wrapper
│   │   │   ├── HomePage.tsx # Home page
│   │   │   ├── UploadPage.tsx # Upload interface
│   │   │   ├── JobsPage.tsx # Jobs list
│   │   │   └── JobDetailPage.tsx # Job details & viz
│   │   ├── services/
│   │   │   └── api.ts       # API client
│   │   ├── types/
│   │   │   └── index.ts     # TypeScript definitions
│   │   ├── App.tsx          # Root component
│   │   └── main.tsx         # Entry point
│   ├── package.json         # Node dependencies
│   ├── tsconfig.json        # TypeScript config
│   └── vite.config.ts       # Vite configuration
│
├── docker/                    # Docker configuration
│   ├── Dockerfile.backend   # Backend image
│   ├── Dockerfile.worker    # Worker image
│   ├── Dockerfile.frontend  # Frontend image
│   └── nginx.conf           # Nginx configuration
│
├── data/                      # Data directories
│   ├── uploads/             # Uploaded MRI files
│   └── outputs/             # Processing results
│
├── docs/                      # Documentation
│   └── ARCHITECTURE.md      # Architecture details
│
├── docker-compose.yml         # Production compose file
├── docker-compose.dev.yml     # Development overrides
├── .env.example              # Environment template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

---

## Code Documentation

### Backend Architecture

#### API Layer (`backend/api/`)

**Purpose**: Handles HTTP requests and responses

**Key Files**:
- `jobs.py`: Job CRUD operations
  - `GET /jobs/`: List all jobs (with pagination)
  - `GET /jobs/{id}`: Get specific job
  - `DELETE /jobs/{id}`: Delete job
  - `GET /jobs/{id}/status`: Quick status check

- `metrics.py`: Metric retrieval
  - `GET /metrics/?job_id={id}`: Get job metrics
  - `GET /metrics/{id}`: Get specific metric
  - `GET /metrics/region/{name}`: Get by region

- `upload.py`: File upload handling
  - `POST /upload/`: Upload MRI and start processing

#### Services Layer (`backend/services/`)

**Purpose**: Business logic and data operations

**JobService** (`job_service.py`):
```python
# Create new job
job = JobService.create_job(db, JobCreate(...))

# Update job status
JobService.start_job(db, job_id)
JobService.complete_job(db, job_id, result_path)
JobService.fail_job(db, job_id, error_msg)
```

**MetricService** (`metric_service.py`):
```python
# Store metrics
MetricService.create_metrics_bulk(db, metrics_data)

# Retrieve metrics
metrics = MetricService.get_metrics_by_job(db, job_id)
```

**StorageService** (`storage_service.py`):
```python
# Save uploaded file
path = storage_service.save_upload(file, filename)

# Get file for processing
local_path = storage_service.get_file_path(storage_path)
```

#### Database Models (`backend/models/`)

**Job Model**:
- Tracks processing jobs
- Status: pending → running → completed/failed
- Relationships: One-to-many with metrics

**Metric Model**:
- Stores hippocampal measurements
- Links to parent job
- Contains left/right volumes and asymmetry index

### Processing Pipeline

#### MRIProcessor (`pipeline/processors/mri_processor.py`)

**Main workflow**:

1. **Input Preparation**
   ```python
   nifti_path = processor._prepare_input(input_path)
   # Converts DICOM to NIfTI if needed
   # Validates file format
   ```

2. **FastSurfer Segmentation**
   ```python
   fastsurfer_output = processor._run_fastsurfer(nifti_path)
   # Runs containerized FastSurfer
   # Or creates mock output for development
   ```

3. **Hippocampal Data Extraction**
   ```python
   hippocampal_stats = processor._extract_hippocampal_data(fastsurfer_output)
   # Parses .stats files
   # Extracts bilateral volumes
   ```

4. **Asymmetry Calculation**
   ```python
   metrics = processor._calculate_asymmetry(hippocampal_stats)
   # Computes AI = (L - R) / ((L + R) / 2)
   # For each hippocampal region
   ```

5. **Results Storage**
   ```python
   processor._save_results(metrics)
   # Saves JSON and CSV
   # Returns metrics for database
   ```

#### Utility Functions

**Asymmetry** (`pipeline/utils/asymmetry.py`):
```python
# Calculate asymmetry index
ai = calculate_asymmetry_index(left_volume, right_volume)
# Returns: (L - R) / mean(L, R)

# Classify laterality
laterality = classify_laterality(ai, threshold=0.05)
# Returns: "Left > Right", "Right > Left", or "Symmetric"
```

**File Utils** (`pipeline/utils/file_utils.py`):
```python
# Validate NIfTI
is_valid = validate_nifti(file_path)

# Convert DICOM
nifti_path = convert_dicom_to_nifti(dicom_path, output_path)
```

**Segmentation** (`pipeline/utils/segmentation.py`):
```python
# Parse FastSurfer stats
volumes = parse_hippo_stats(stats_file)
# Returns: {"CA1": volume, "CA3": volume, ...}
```

### Frontend Architecture

#### Components

**Layout** (`Layout.tsx`):
- Navigation bar with routing
- Content area with `<Outlet />`
- Footer

**HomePage** (`HomePage.tsx`):
- Welcome message
- System status check
- Feature cards
- Quick start guide

**UploadPage** (`UploadPage.tsx`):
- File selection with drag-drop
- Format validation
- Size checking
- Upload progress
- Redirects to job detail on success

**JobsPage** (`JobsPage.tsx`):
- Lists all jobs in table
- Status badges with colors
- Refresh functionality
- Links to detail pages

**JobDetailPage** (`JobDetailPage.tsx`):
- Job information card
- Status tracking with auto-refresh
- Metrics table
- Asymmetry index chart (Plotly)
- Volume comparison chart (Plotly)

#### API Client (`services/api.ts`)

**Usage**:
```typescript
// Upload file
const job = await ApiService.uploadFile(file);

// Get jobs
const jobs = await ApiService.getJobs();

// Get specific job
const job = await ApiService.getJob(jobId);

// Delete job
await ApiService.deleteJob(jobId);

// Health check
const health = await ApiService.healthCheck();
```

---

## API Documentation

### Interactive Documentation

Access the auto-generated API docs:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Upload

```http
POST /upload/
Content-Type: multipart/form-data

file: <MRI file>

Response: 201 Created
{
  "id": "uuid",
  "filename": "scan.nii.gz",
  "status": "pending",
  "created_at": "2025-10-10T12:00:00Z",
  ...
}
```

#### List Jobs

```http
GET /jobs/?skip=0&limit=100&status=completed

Response: 200 OK
[
  {
    "id": "uuid",
    "filename": "scan.nii.gz",
    "status": "completed",
    "metrics": [...]
  }
]
```

#### Get Job

```http
GET /jobs/{job_id}

Response: 200 OK
{
  "id": "uuid",
  "filename": "scan.nii.gz",
  "status": "completed",
  "metrics": [
    {
      "region": "CA1",
      "left_volume": 1250.5,
      "right_volume": 1198.2,
      "asymmetry_index": 0.0426
    }
  ]
}
```

---

## Development

### Local Backend Development

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
export POSTGRES_HOST=localhost
export REDIS_HOST=localhost
# ... other variables

# Run backend
uvicorn backend.main:app --reload --port 8000
```

### Local Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

### Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Quality

```bash
# Backend linting
cd backend
black .
flake8 .
mypy .

# Frontend linting
cd frontend
npm run lint
```

---

## Testing

### Backend Tests

```bash
cd backend
pytest
pytest --cov=backend --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage
```

### Integration Tests

```bash
# Start services
docker-compose up -d

# Run integration tests
pytest tests/integration

# Cleanup
docker-compose down
```

---

## Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Check what's using the port
lsof -i :8000  # or :5173, :5432, etc.

# Kill the process or change port in .env
```

**2. Database Connection Failed**
```bash
# Check if PostgreSQL is running
docker-compose ps db

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

**3. Worker Not Processing Jobs**
```bash
# Check worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker

# Check Redis connection
docker-compose exec redis redis-cli ping
```

**4. FastSurfer Not Available**
```bash
# The application uses mock data in development
# Check worker logs for "using_mock=True"

# To use real FastSurfer, ensure Docker socket is mounted
# and FastSurfer image is available
```

**5. Frontend Can't Connect to Backend**
```bash
# Check backend health
curl http://localhost:8000/health

# Check CORS settings in backend/.env
# Ensure frontend URL is in CORS_ORIGINS
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend

# Last N lines
docker-compose logs --tail=100 backend
```

### Cleanup

```bash
# Stop all containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Full cleanup
docker system prune -a --volumes
```

---

## Performance Optimization

### Production Recommendations

1. **Database**
   - Use connection pooling
   - Add indexes on frequently queried columns
   - Regular VACUUM operations

2. **Backend**
   - Use Gunicorn with multiple workers
   - Enable caching for repeated queries
   - Implement rate limiting

3. **Worker**
   - Scale horizontally (multiple worker containers)
   - Adjust concurrency based on CPU cores
   - Monitor queue length

4. **Frontend**
   - Enable CDN for static assets
   - Implement lazy loading
   - Optimize bundle size

### Monitoring

```bash
# Resource usage
docker stats

# Service health
curl http://localhost:8000/health

# Database connections
docker-compose exec db psql -U neuroinsight -c "SELECT count(*) FROM pg_stat_activity;"

# Redis queue length
docker-compose exec redis redis-cli LLEN celery
```

---

## Security Considerations

**WARNING: Development Version - Not Production Ready**

This development version includes:
- Default credentials
- Debug mode enabled
- No authentication
- HTTP only (no TLS)
- Exposed service ports

### For Production:

1. **Change all default passwords**
2. **Enable HTTPS/TLS**
3. **Implement authentication** (JWT, OAuth)
4. **Use secrets management** (AWS Secrets Manager, Vault)
5. **Enable rate limiting**
6. **Implement input validation**
7. **Use network isolation**
8. **Enable audit logging**
9. **Regular security updates**
10. **Vulnerability scanning**

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run linters and tests
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8, use Black formatter
- **TypeScript**: Follow Airbnb style guide
- **Commits**: Use conventional commits format

---

## License

This project is for educational and development purposes. Please ensure compliance with all relevant software licenses, particularly:
- FastSurfer licensing terms
- FreeSurfer licensing terms
- Medical imaging data regulations (HIPAA, GDPR)

---

## Support

For questions, issues, or contributions:

- **Issues**: [GitHub Issues](#)
- **Documentation**: See `docs/ARCHITECTURE.md`
- **API Docs**: http://localhost:8000/docs

---

## Acknowledgments

- FastSurfer team for neuroimaging segmentation
- FreeSurfer for hippocampal subfield algorithms
- Open source community for excellent tools and libraries

---

**Version**: 0.1.0-dev  
**Last Updated**: October 2025

---

Made with love for neuroscience research

