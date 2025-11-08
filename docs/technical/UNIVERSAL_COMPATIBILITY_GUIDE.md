# Making NeuroInsight Work on Any Computer

## 🎯 Goal: Universal Compatibility

Make NeuroInsight work reliably across:
- ✅ Intel/AMD computers (x86_64)
- ✅ Apple Silicon Macs (ARM64/M1/M2/M3)
- ✅ Windows, macOS, Linux
- ✅ With or without GPU
- ✅ For technical and non-technical users

---

## 🚨 Current Compatibility Issues

### Problem 1: FastSurfer Docker Image (x86_64 Only)

**Issue:**
```
WARNING: The requested image's platform (linux/amd64) 
does not match the detected host platform (linux/arm64/v8)
```

**Affects:**
- Apple Silicon Macs (M1, M2, M3)
- ARM-based Linux systems

**Why:**
- FastSurfer Docker image: Built for x86_64 only
- No official ARM64 build available

---

## ✅ Solutions (Multiple Options)

### **Solution 1: Fix Docker Platform Compatibility** ⭐ Recommended

Enable multi-platform support with Docker's emulation layer.

#### A. Update docker-compose.yml

Add platform specification:

```yaml
# docker-compose.yml
services:
  worker:
    platform: linux/amd64  # Force x86_64 emulation on ARM
    # ... rest of config
```

#### B. Update Worker Code

Specify platform when running FastSurfer container:

```python
# pipeline/processors/mri_processor.py

# Line ~210, add platform flag:
cmd = [
    "docker", "run",
    "--platform", "linux/amd64",  # ← Add this
    "--rm",
    "-v", f"{nifti_path.parent}:/input:ro",
    "-v", f"{fastsurfer_dir}:/output",
    "deepmi/fastsurfer:latest",
    # ... rest of command
]
```

**Pros:**
- ✅ Works on ARM64 Macs
- ✅ No code changes needed
- ✅ Same Docker image

**Cons:**
- ⚠️ Slower on ARM (emulation overhead ~2x)
- ⚠️ Requires Rosetta 2 (macOS) or qemu (Linux)

---

### **Solution 2: Desktop App with Automatic Detection** ⭐⭐ Best for End Users

Package as desktop app that detects platform and handles compatibility.

Already built in `hippo_desktop/`! Just needs platform detection logic.

#### Implementation:

```javascript
// hippo_desktop/src/managers/PlatformManager.js

class PlatformManager {
  constructor() {
    this.platform = process.platform; // 'darwin', 'win32', 'linux'
    this.arch = process.arch;         // 'x64', 'arm64'
  }

  getDockerPlatform() {
    // Force x86_64 on ARM Macs for FastSurfer compatibility
    if (this.arch === 'arm64') {
      return 'linux/amd64';
    }
    return 'linux/amd64'; // Default
  }

  getRecommendedProcessingMode() {
    if (this.arch === 'arm64') {
      return {
        mode: 'cloud',
        reason: 'ARM architecture detected. Cloud processing recommended for better performance.'
      };
    }
    return {
      mode: 'local',
      reason: 'x86_64 architecture. Local processing supported.'
    };
  }

  checkCompatibility() {
    const checks = {
      docker: this.checkDocker(),
      memory: this.checkMemory(),
      disk: this.checkDisk(),
      platform: this.checkPlatformSupport()
    };
    
    return checks;
  }

  checkPlatformSupport() {
    if (this.arch === 'arm64') {
      return {
        supported: true,
        warning: 'ARM64 detected. Processing will use emulation (slower).',
        recommendation: 'Consider cloud processing for better performance.'
      };
    }
    return {
      supported: true,
      warning: null
    };
  }
}

module.exports = PlatformManager;
```

**Usage in Desktop App:**

```javascript
// hippo_desktop/src/main.js

const PlatformManager = require('./managers/PlatformManager');
const platformManager = new PlatformManager();

// On app startup
app.on('ready', async () => {
  const compat = platformManager.checkCompatibility();
  
  if (compat.platform.warning) {
    // Show user-friendly warning
    dialog.showMessageBox({
      type: 'info',
      title: 'Platform Compatibility',
      message: compat.platform.warning,
      detail: compat.platform.recommendation
    });
  }
  
  // Update docker-compose with correct platform
  updateDockerCompose(platformManager.getDockerPlatform());
  
  createWindow();
});
```

---

### **Solution 3: Multi-Backend Architecture** ⭐⭐⭐ Most Robust

Support multiple processing backends based on platform.

```
User's Computer
    ↓
Platform Detection
    ↓
┌─────────┬──────────┬────────────┐
│ Local   │ Cloud    │ HPC/Server │
│ Docker  │ API      │ SSH/API    │
└─────────┴──────────┴────────────┘
```

#### Implementation:

```python
# backend/core/config.py

class Settings(BaseSettings):
    # Processing backend options
    processing_backend: str = Field(
        default="auto",  # auto, docker, singularity, cloud, remote
        env="PROCESSING_BACKEND"
    )
    
    # Cloud processing (optional)
    cloud_processing_url: Optional[str] = Field(
        default=None,
        env="CLOUD_PROCESSING_URL"
    )
    cloud_api_key: Optional[str] = Field(
        default=None,
        env="CLOUD_API_KEY"
    )
    
    # Remote server (optional)
    remote_server_url: Optional[str] = Field(
        default=None,
        env="REMOTE_SERVER_URL"
    )
```

```python
# pipeline/processors/processor_factory.py

class ProcessorFactory:
    """Factory to create appropriate processor based on platform"""
    
    @staticmethod
    def create_processor(job_id: UUID, settings: Settings) -> BaseProcessor:
        backend = ProcessorFactory._determine_backend(settings)
        
        if backend == "docker":
            return DockerFastSurferProcessor(job_id)
        elif backend == "singularity":
            return SingularityFastSurferProcessor(job_id)
        elif backend == "cloud":
            return CloudProcessor(job_id, settings)
        elif backend == "remote":
            return RemoteProcessor(job_id, settings)
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    @staticmethod
    def _determine_backend(settings: Settings) -> str:
        if settings.processing_backend != "auto":
            return settings.processing_backend
        
        # Auto-detect
        import platform
        arch = platform.machine()
        
        # Check if Singularity available
        if shutil.which("singularity") or shutil.which("apptainer"):
            return "singularity"
        
        # Check if Docker available
        if shutil.which("docker"):
            # Check if ARM - recommend cloud
            if arch in ["arm64", "aarch64"]:
                if settings.cloud_processing_url:
                    logger.info("ARM detected, using cloud processing")
                    return "cloud"
                else:
                    logger.warning("ARM detected, using Docker with emulation")
                    return "docker"
            return "docker"
        
        # Fallback to cloud if configured
        if settings.cloud_processing_url:
            return "cloud"
        
        raise RuntimeError("No processing backend available")
```

---

### **Solution 4: Cloud Processing Service** ⭐⭐⭐ Best for Non-Technical Users

Host a central processing server that anyone can use.

#### Architecture:

```
User's Browser/Desktop App
    ↓ HTTPS
Central Processing Server (x86_64)
    ↓
FastSurfer GPU Processing
    ↓
Results sent back to user
```

#### Benefits:
- ✅ Works on ANY device (even tablets/phones)
- ✅ No Docker installation needed
- ✅ Fast GPU processing
- ✅ No platform issues

#### Implementation:

```python
# backend/services/cloud_processor.py

class CloudProcessor(BaseProcessor):
    """Send processing to cloud service"""
    
    def __init__(self, job_id: UUID, cloud_url: str, api_key: str):
        super().__init__(job_id)
        self.cloud_url = cloud_url
        self.api_key = api_key
    
    async def process(self, file_path: Path) -> Dict[str, Any]:
        """Upload to cloud and wait for results"""
        
        # 1. Upload MRI file
        upload_url = f"{self.cloud_url}/api/v1/upload"
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=file_path.name)
                data.add_field('api_key', self.api_key)
                
                async with session.post(upload_url, data=data) as resp:
                    result = await resp.json()
                    job_id = result['job_id']
        
        # 2. Poll for completion
        status_url = f"{self.cloud_url}/api/v1/jobs/{job_id}"
        while True:
            async with session.get(
                status_url,
                headers={'Authorization': f'Bearer {self.api_key}'}
            ) as resp:
                status = await resp.json()
                
                if status['status'] == 'completed':
                    break
                elif status['status'] == 'failed':
                    raise ProcessingError(status['error'])
                
                await asyncio.sleep(5)  # Check every 5 seconds
        
        # 3. Download results
        results_url = f"{self.cloud_url}/api/v1/jobs/{job_id}/results"
        async with session.get(
            results_url,
            headers={'Authorization': f'Bearer {self.api_key}'}
        ) as resp:
            results = await resp.json()
        
        return results
```

---

## 🔧 Immediate Fix for Current Setup

**Quick fix to make it work on your Mac right now:**

### Step 1: Update docker-compose.yml

```bash
cd ~/Downloads/neuroinsight-web-app

# Edit docker-compose.yml
nano docker-compose.yml
```

Add `platform` to worker service:

```yaml
services:
  worker:
    platform: linux/amd64  # ← ADD THIS LINE
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    # ... rest stays the same
```

### Step 2: Update MRI Processor

```bash
# Edit the processor file
nano pipeline/processors/mri_processor.py
```

Find line ~210 where Docker command is built, add `--platform`:

```python
# Around line 210
cmd = [
    "docker", "run",
    "--platform", "linux/amd64",  # ← ADD THIS
    "--rm",
    # ... rest of command
]
```

### Step 3: Rebuild and Restart

```bash
# Rebuild worker with new config
docker-compose down
docker-compose build --no-cache worker
docker-compose up -d

# Check logs
docker-compose logs -f worker
```

**Expected result:**
- ✅ FastSurfer runs (with emulation)
- ⚠️ Slower (~2x) but works
- ✅ Real results (not mock data)

---

## 📋 Cross-Platform Testing Checklist

Before releasing to users, test on:

- [ ] **Windows 10/11 (x86_64)**
  - With GPU (NVIDIA)
  - CPU only
  
- [ ] **macOS Intel (x86_64)**
  - With eGPU
  - CPU only
  
- [ ] **macOS Apple Silicon (ARM64)**
  - M1/M2/M3
  - CPU only (no NVIDIA GPU support)
  
- [ ] **Linux Ubuntu (x86_64)**
  - With GPU
  - CPU only
  
- [ ] **Linux ARM64**
  - Raspberry Pi 4
  - ARM servers

### Automated Testing

```yaml
# .github/workflows/platform-test.yml

name: Platform Compatibility Test

on: [push, pull_request]

jobs:
  test-platforms:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        arch: [x64, arm64]
        exclude:
          - os: windows-latest
            arch: arm64  # Windows ARM not common yet
    
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker
        uses: docker/setup-buildx-action@v2
        with:
          platforms: linux/amd64,linux/arm64
      
      - name: Test Docker Compose
        run: |
          docker-compose up -d
          sleep 30
          docker-compose ps
          docker-compose down
      
      - name: Test FastSurfer (mock)
        run: |
          # Run with test data
          python -m pytest tests/integration/test_platform_compat.py
```

---

## 📦 System Requirements Documentation

**Clear requirements prevent user frustration:**

### Minimum Requirements (CPU Processing)

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **CPU** | 4 cores (any architecture) | ARM64 works with emulation |
| **RAM** | 16GB | Required for FastSurfer |
| **Storage** | 30GB free | For Docker images + data |
| **OS** | Windows 10+, macOS 10.15+, Ubuntu 20.04+ | |
| **Docker** | Docker Desktop 4.0+ | Automatic emulation on ARM |
| **Processing Time** | 40-60 min/scan | ARM: ~80-120 min (emulation) |

### Recommended (GPU Processing)

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **CPU** | 8+ cores x86_64 | ARM not supported for GPU |
| **RAM** | 32GB | |
| **GPU** | NVIDIA with 8GB+ VRAM | CUDA-capable only |
| **Storage** | 100GB SSD | |
| **Processing Time** | 2-5 min/scan | **GPU not available on ARM** |

### Platform-Specific Notes

**Apple Silicon (M1/M2/M3):**
- ✅ CPU processing: Works (via emulation)
- ❌ GPU processing: Not supported (NVIDIA only)
- ⚠️ 2-3x slower than Intel Mac
- 💡 Recommendation: Use cloud processing

**Windows ARM:**
- ⚠️ Limited Docker support
- 💡 Recommendation: Use Desktop App with cloud processing

**Linux ARM (Raspberry Pi):**
- ⚠️ Not enough RAM (typically 8GB max)
- ❌ Not recommended for local processing
- 💡 Use as client only, process on server

---

## 🎯 Deployment Strategy for Universal Access

### Tier 1: Technical Users (Developers/Researchers)

**Docker Compose (Current)**
- Platform flags for ARM compatibility
- Clear documentation
- Works everywhere with Docker

### Tier 2: Semi-Technical Users (Lab Members)

**Desktop App**
- Electron wrapper
- Automatic platform detection
- One-click install
- Handles Docker automatically

### Tier 3: Non-Technical Users (Clinicians)

**Web Service (Cloud Hosted)**
- No installation needed
- Just open browser
- Upload → Process → Download
- Works on any device

---

## ✅ Final Recommendation

**For maximum compatibility, implement all three:**

1. **Fix Docker setup** (Immediate - 1 hour)
   ```bash
   # Add platform flags to docker-compose.yml and processor code
   ```

2. **Update Desktop App** (Short term - 1 day)
   ```bash
   # Add platform detection and user guidance
   ```

3. **Deploy Cloud Service** (Long term - 1 week)
   ```bash
   # Host on AWS/Azure for universal access
   ```

This ensures:
- ✅ Works on Intel/AMD
- ✅ Works on Apple Silicon
- ✅ Works on ARM Linux
- ✅ Options for all user types
- ✅ Graceful fallbacks

---

## 🚀 Quick Implementation Priority

**Phase 1: Fix Current Issue (Today)**
```bash
# Add --platform linux/amd64 to Docker commands
# Test on your Mac
# Update documentation
```

**Phase 2: Desktop App Update (This Week)**
```bash
# Add platform detection
# Build installers for all platforms
# Upload to GitHub Releases
```

**Phase 3: Cloud Option (Future)**
```bash
# Deploy processing server
# Add cloud backend option
# Update UI with processing mode selector
```

Want me to implement Phase 1 (the immediate fix) right now?


