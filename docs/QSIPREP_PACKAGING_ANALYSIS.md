# QSIprep Packaging Analysis

How QSIprep (and fMRIPrep family) packages neuroimaging pipelines, and what NeuroInsight can learn.

---

## What is QSIprep?

**QSIprep:** Preprocessing pipeline for quantitative susceptibility imaging and diffusion MRI data.

**Background:**
- Part of the fMRIPrep/NiPreps family
- Developed at Stanford/Penn
- Used for diffusion MRI preprocessing
- Designed for reproducible research
- HPC and cluster focused

**Key Stats:**
- First released: 2019
- Citations: 500+ papers
- Primary use: Research preprocessing pipelines
- Target: HPC clusters, servers, workstations

**Website:** https://qsiprep.readthedocs.io/

---

## 1. PACKAGING PHILOSOPHY

### Container-First Approach

**QSIprep's core principle:**
```
"We ONLY distribute via containers"

Why?
- Reproducibility is critical
- Complex dependency chain
- FSL, ANTs, AFNI, FreeSurfer, MRtrix3
- Version locking essential
- Cross-platform consistency
```

**Not available as:**
- ❌ Standalone executable
- ❌ Python package only (dependencies too complex)
- ❌ System installation
- ❌ Desktop application

**Only available as:**
- ✅ Docker container
- ✅ Singularity/Apptainer container
- ✅ (Can run via Python wrapper that calls container)

---

## 2. DISTRIBUTION METHODS

### Method 1: Docker Container (Primary)

**Docker Hub Distribution:**
```bash
# Pull from Docker Hub
docker pull nipreps/qsiprep:latest

# Or specific version
docker pull nipreps/qsiprep:0.19.0

# Run
docker run -it --rm \
  -v /data:/data:ro \
  -v /output:/output \
  nipreps/qsiprep:latest \
  /data /output participant
```

**Container Details:**
```
Image: nipreps/qsiprep:0.19.0
Size: 5-6 GB (compressed: ~2 GB)

Contains:
├── Ubuntu base (minimal)
├── Python 3.10
├── FSL (neuroimaging suite)
├── ANTs (registration tools)
├── AFNI (analysis tools)
├── FreeSurfer (segmentation)
├── MRtrix3 (diffusion tools)
├── QSIprep Python code
└── All dependencies
```

---

### Method 2: Singularity/Apptainer (HPC)

**For HPC Clusters:**
```bash
# Build from Docker Hub
singularity build qsiprep-0.19.0.sif \
  docker://nipreps/qsiprep:0.19.0

# Or download pre-built
singularity pull qsiprep-0.19.0.sif \
  docker://nipreps/qsiprep:0.19.0

# Run
singularity run \
  --bind /data:/data:ro \
  --bind /output:/output \
  qsiprep-0.19.0.sif \
  /data /output participant
```

**SIF File Details:**
```
File: qsiprep-0.19.0.sif
Size: 5-6 GB
Format: SquashFS (read-only)
Portable: Yes (copy to any HPC)
Root required: No (user-level)
```

---

### Method 3: Python Wrapper (Convenience)

**PyPI Package (Wrapper Only):**
```bash
# Install wrapper
pip install qsiprep

# Wrapper automatically pulls Docker container
qsiprep /data /output participant

# Under the hood, runs:
# docker run nipreps/qsiprep:latest ...
```

**What the Python package contains:**
```python
# qsiprep PyPI package is TINY (~50 KB)
# It's just a wrapper that:
1. Checks if Docker/Singularity available
2. Pulls container if needed
3. Constructs container run command
4. Handles path mounting
5. Passes arguments to container

# Actual processing happens IN container
```

---

## 3. WHY CONTAINERS FOR QSIPREP?

### Reason 1: Dependency Hell

**QSIprep depends on:**
```
Neuroimaging Tools (each complex):
├── FSL (FMRIB Software Library)
│   ├── 100+ command-line tools
│   ├── Custom libraries
│   ├── Specific versions required
│   └── ~2 GB installed
│
├── ANTs (Advanced Normalization Tools)
│   ├── C++ compiled tools
│   ├── ITK dependency
│   └── ~500 MB installed
│
├── AFNI (Analysis of Functional NeuroImages)
│   ├── 400+ programs
│   ├── R dependencies
│   └── ~1 GB installed
│
├── FreeSurfer
│   ├── Surface reconstruction
│   ├── License required
│   └── ~5 GB installed
│
└── MRtrix3
    ├── Diffusion tools
    ├── C++ compiled
    └── ~200 MB installed

Total: 8-10 GB of dependencies
Each with their own sub-dependencies
Version conflicts common
```

**Without containers:**
```
User must install:
1. Python 3.10+ with specific packages
2. FSL (complex installation)
3. ANTs (compile from source)
4. AFNI (various dependencies)
5. FreeSurfer (license, large download)
6. MRtrix3 (compile from source)
7. Configure environment variables
8. Set library paths
9. Resolve version conflicts

Time: 4-8 hours
Success rate: ~30% (many give up)
```

**With containers:**
```
User runs:
docker pull nipreps/qsiprep:latest

Time: 10-20 minutes (download)
Success rate: 95%+
```

---

### Reason 2: Reproducibility

**Scientific requirement:**
```
Problem:
- Paper says "processed with QSIprep 0.16.0"
- Reviewer needs to reproduce
- Different FSL version = different results
- Different library versions = different results

Solution:
- Container locks ALL versions
- Same container = identical results
- 5 years later, same container works
- Perfect reproducibility
```

**Version Locking:**
```dockerfile
# QSIprep Dockerfile ensures:
FROM ubuntu:20.04
RUN install FSL 6.0.5.2  # Exact version
RUN install ANTs 2.4.3   # Exact version
RUN install AFNI 23.0.05 # Exact version
# etc.

Result: Bit-for-bit reproducible results
```

---

### Reason 3: HPC Compatibility

**Target environment: HPC clusters**
```
HPC characteristics:
- Shared multi-user systems
- No root access for users
- Centralized software management
- Need for isolation
- Batch processing (SLURM, PBS)

Containers solve:
✓ Users don't need root
✓ Isolated from system
✓ Portable across clusters
✓ Consistent environment
✓ Easy batch submission
```

**Example HPC usage:**
```bash
#!/bin/bash
#SBATCH --job-name=qsiprep
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G

# Load Singularity module
module load singularity

# Run QSIprep
singularity run \
  --bind $DATA_DIR:/data \
  --bind $OUTPUT_DIR:/output \
  qsiprep-0.19.0.sif \
  /data /output participant \
  --participant-label sub-01
```

---

## 4. CONTAINER CONTENTS

### What's Inside the QSIprep Container

**Dockerfile Structure:**
```dockerfile
# Simplified QSIprep Dockerfile
FROM ubuntu:20.04

# System dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    build-essential

# Install FSL
RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fsl-6.0.5.2-centos7_64.tar.gz
RUN tar -xzf fsl-*.tar.gz -C /opt
ENV FSLDIR=/opt/fsl
ENV PATH=$FSLDIR/bin:$PATH

# Install ANTs
RUN git clone https://github.com/ANTsX/ANTs.git
RUN cd ANTs && mkdir build && cd build
RUN cmake .. && make -j8
ENV ANTSPATH=/opt/ANTs/bin
ENV PATH=$ANTSPATH:$PATH

# Install AFNI
RUN curl -O https://afni.nimh.nih.gov/pub/dist/tgz/linux_openmp_64.tgz
RUN tar -xzf linux_openmp_64.tgz -C /opt

# Install FreeSurfer
RUN wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.3.2/freesurfer-linux-centos7_x86_64-7.3.2.tar.gz
RUN tar -xzf freesurfer-*.tar.gz -C /opt
ENV FREESURFER_HOME=/opt/freesurfer

# Install MRtrix3
RUN git clone https://github.com/MRtrix3/mrtrix3.git
RUN cd mrtrix3 && ./build

# Install Python dependencies
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Install QSIprep
RUN pip install qsiprep==0.19.0

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/qsiprep"]
```

**Build time:** 2-4 hours (one-time)  
**Image size:** 5-6 GB  
**User download time:** 10-20 minutes

---

## 5. USER WORKFLOW

### Typical User Experience

**Setup (One-Time):**
```bash
# Option 1: Docker
docker pull nipreps/qsiprep:0.19.0
# Downloads 2 GB, extracts to 5-6 GB

# Option 2: Singularity (HPC)
singularity pull qsiprep.sif docker://nipreps/qsiprep:0.19.0
# Creates single 5-6 GB file
```

**Running QSIprep:**
```bash
# Prepare data
/data/
├── sub-01/
│   └── dwi/
│       ├── sub-01_dwi.nii.gz
│       └── sub-01_dwi.bval/bvec
└── dataset_description.json

# Run processing
docker run --rm -it \
  -v /data:/data:ro \
  -v /output:/output \
  -v /freesurfer_license:/license:ro \
  nipreps/qsiprep:0.19.0 \
  /data /output participant \
  --participant-label sub-01 \
  --fs-license-file /license/license.txt \
  --output-resolution 2

# Wait 6-24 hours (depending on data)
# Results in /output/
```

**What user needs to know:**
```
Required knowledge:
- Docker/Singularity basics
- Command line
- Data organization (BIDS format)
- Volume mounting concept

Learning curve: Medium-High
```

---

## 6. COMPARISON WITH OTHER APPROACHES

### QSIprep vs 3D Slicer

| Aspect | QSIprep | 3D Slicer | NeuroInsight (Should Be) |
|--------|---------|-----------|-------------------------|
| **Distribution** | Containers only | Standalone installer | Standalone installer |
| **Size** | 5-6 GB | 500-550 MB | 1.5-2 GB |
| **Installation** | Docker pull | Download + Install | Download + Install |
| **Prerequisites** | Docker/Singularity | None | None |
| **Target User** | Researchers, CLI | Clinicians, GUI | Clinicians, GUI |
| **Primary Use** | Batch HPC processing | Interactive analysis | Interactive analysis |
| **Interface** | Command line | Graphical | Graphical + Web |
| **Reproducibility** | Perfect (containers) | Good (versioning) | Good (versioning) |
| **Ease of Use** | Complex | Simple | Simple |
| **Updates** | Pull new image | Download installer | Auto-update |

---

## 7. WHEN CONTAINERS MAKE SENSE

### QSIprep's Use Case (Containers Perfect)

**Why containers work for QSIprep:**
```
✅ HPC/Server environment
✅ Batch processing (no GUI)
✅ Technical users (researchers)
✅ Reproducibility critical
✅ Complex dependencies (FSL, ANTs, etc.)
✅ Long-running jobs (6-24 hours)
✅ Command-line workflow
✅ Version locking essential
```

**Target user:**
```
Researcher/Data scientist who:
- Comfortable with command line
- Has access to HPC/workstation
- Processing many subjects
- Publishing research (needs reproducibility)
- Running overnight batches
```

---

### Desktop Medical Software (Containers Poor)

**Why containers DON'T work for desktop:**
```
❌ End users (clinicians, students)
❌ Interactive GUI needed
❌ Quick results expected
❌ Non-technical users
❌ Simple dependencies possible
❌ Short processing times
❌ Point-and-click workflow
❌ Ease of use critical
```

**Target user:**
```
Clinician/Student who:
- Not comfortable with command line
- Uses laptop/desktop
- Processing one scan at a time
- Needs quick results
- Wants simple interface
- Expects app to "just work"
```

---

## 8. HYBRID APPROACHES

### fMRIPrep-Docker Wrapper

**Convenience layer over containers:**
```python
# Install wrapper
pip install fmriprep-docker

# User runs simple command
fmriprep-docker /data /output participant

# Under the hood:
# 1. Checks if Docker installed
# 2. Pulls container if needed
# 3. Handles volume mounts automatically
# 4. Runs container
# 5. Shows output
```

**Benefits:**
```
✓ Simpler command
✓ Hides Docker complexity
✓ Still gets container benefits
✓ Cross-platform
```

**Limitations:**
```
✗ Still requires Docker installed
✗ Still command-line
✗ Still technical
✗ Not for end users
```

---

## 9. WHAT NEUROINSIGHT CAN LEARN

### From QSIprep's Approach

**1. Use Containers for Development/HPC:**
```
Development:
✓ Docker Compose (current approach)
✓ Consistent dev environment
✓ Easy team collaboration

HPC Deployment:
✓ Singularity container
✓ Batch processing
✓ Server deployment
```

**2. Avoid Containers for End Users:**
```
Desktop Distribution:
✓ Standalone installer (like Slicer)
✗ Not Docker (too complex)

Why:
- Clinical users not technical
- Interactive use case
- Need simple installation
- GUI-based workflow
```

**3. Version Locking is Important:**
```
Learn from QSIprep:
✓ Lock dependency versions
✓ Document exact versions
✓ Ensure reproducibility

Implement:
- Requirements.txt with pinned versions
- Bundle specific library versions
- Version info in app
```

---

### QSIprep's Container Strategy Applied to NeuroInsight

**Multi-Distribution Strategy:**

```
Development:
Use: Docker Compose
Why: Easy local development

HPC/Server:
Use: Singularity container
Why: Batch processing, reproducibility
Distribution: Docker Hub → Singularity convert

End Users (Desktop):
Use: Standalone executable
Why: Simplicity, professional UX
Distribution: GitHub releases, installers

Web Service (Future):
Use: Kubernetes/Docker
Why: Scalability, cloud deployment
```

**Example:**
```
Same NeuroInsight codebase:

├── docker-compose.yml → Development
├── Dockerfile → Server/HPC deployment
├── build.spec → Desktop packaging
└── kubernetes.yaml → Cloud deployment

Choose distribution method based on use case
```

---

## 10. TECHNICAL DETAILS

### How QSIprep Builds Containers

**Build Process:**
```bash
# CircleCI automated build
.circleci/config.yml:
  build_docker:
    - checkout code
    - docker build -t nipreps/qsiprep:latest .
    - run tests in container
    - docker push to Docker Hub

# Versioning
- Every commit: latest tag
- Every release: version tag (0.19.0)
- Long-term support: LTS tag
```

**Multi-Stage Build:**
```dockerfile
# Stage 1: Build tools
FROM ubuntu:20.04 as builder
RUN install build dependencies
RUN compile ANTs
RUN compile MRtrix3

# Stage 2: Runtime
FROM ubuntu:20.04
COPY --from=builder /opt/ants /opt/ants
COPY --from=builder /opt/mrtrix3 /opt/mrtrix3
# etc.

# Result: Smaller final image
```

---

### Container Optimization

**Size Optimization:**
```dockerfile
# Use multi-stage builds
# Clean up after installations
RUN apt-get update && \
    apt-get install -y package && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Use .dockerignore
.git/
*.pyc
__pycache__/
tests/

# Result: 5-6 GB instead of 8-10 GB
```

**Layer Caching:**
```dockerfile
# Order matters for build speed
# Rarely changing dependencies first
RUN install system packages (rarely changes)
RUN install FSL (rarely changes)
RUN install ANTs (rarely changes)
COPY requirements.txt (changes sometimes)
RUN pip install -r requirements.txt
COPY . /app (changes often)

# Rebuilds only changed layers
```

---

## 11. REAL-WORLD USAGE PATTERNS

### Academic Research Lab

**Scenario:** Process 100 subjects
```bash
# One-time setup
singularity pull qsiprep.sif docker://nipreps/qsiprep:0.19.0

# SLURM batch script
for subject in sub-{01..100}; do
  sbatch --wrap="singularity run qsiprep.sif \
    /data /output participant \
    --participant-label $subject"
done

# Runs overnight on cluster
# Perfect for this use case
```

**Why it works:**
- Technical users (grad students, postdocs)
- HPC access available
- Batch processing needed
- Reproducibility important

---

### Clinical Deployment

**Scenario:** Process one patient scan
```
Problem:
- Clinician needs quick result
- No command line experience
- No HPC access
- Needs GUI

Container approach FAILS:
1. Install Docker Desktop (confused)
2. Open terminal (uncomfortable)
3. Type complex command (errors)
4. Wait hours (frustrated)
5. Find results in mounted volume (lost)

Standalone app approach WORKS:
1. Click NeuroInsight icon
2. Upload scan (drag & drop)
3. Click "Process"
4. View results in app
5. Export report
```

**Lesson: Different use cases need different packaging**

---

## 12. SUMMARY

### QSIprep's Packaging Philosophy

**Core Principles:**
```
1. Containers for reproducibility
2. Lock all dependencies
3. Target HPC/research use
4. Command-line first
5. Version everything
```

**Success Metrics:**
```
✓ 500+ citations (reproducible research)
✓ Standard in diffusion MRI preprocessing
✓ Works across all HPC systems
✓ Perfect reproducibility
```

**Trade-offs:**
```
✓ Excellent for research/HPC
✗ Poor for clinical/desktop use
✓ Perfect reproducibility
✗ Complex for non-technical users
✓ Works everywhere Docker works
✗ Requires Docker installation
```

---

### Lessons for NeuroInsight

**What to Copy:**
```
✓ Version locking (reproducibility)
✓ Container option for HPC/servers
✓ Automated builds (CI/CD)
✓ Clear documentation
✓ Testing in containers
```

**What NOT to Copy:**
```
✗ Container-only distribution
✗ Command-line only interface
✗ No desktop/GUI version
✗ Complex installation for end users
```

**Best Strategy for NeuroInsight:**
```
Development:
- Use Docker Compose (like QSIprep)

HPC/Server Deployment:
- Provide Singularity container (like QSIprep)

End-User Desktop:
- Standalone installer (like Slicer)
- NOT containers

Choose packaging based on use case
```

---

## 13. COMPARISON TABLE

### Packaging Approaches Compared

| Aspect | QSIprep | 3D Slicer | NeuroInsight (Recommended) |
|--------|---------|-----------|---------------------------|
| **Primary Distribution** | Docker/Singularity | Standalone installer | Standalone installer |
| **Target User** | Researchers | Clinicians/Researchers | Clinicians/Researchers |
| **Interface** | CLI | GUI | GUI + Web |
| **Installation** | docker pull | Download + Install | Download + Install |
| **Prerequisites** | Docker | None | None |
| **Size** | 5-6 GB | 500-550 MB | 1.5-2 GB |
| **Complexity** | High | Low | Low |
| **Reproducibility** | Perfect | Good | Good |
| **HPC Suitable** | Excellent | No | Yes (with container) |
| **Desktop Suitable** | No | Excellent | Excellent |
| **Learning Curve** | Steep | Gentle | Gentle |
| **Updates** | Pull new image | Download | Auto-update |
| **Best For** | Batch HPC | Interactive desktop | Interactive desktop |

---

## CONCLUSION

**QSIprep's Container Approach:**
```
Perfect for:
✓ Research pipelines
✓ HPC batch processing
✓ Reproducible science
✓ Technical users
✓ Complex dependencies

Poor for:
✗ Desktop end users
✗ Clinical applications
✗ Interactive use
✗ Non-technical users
```

**NeuroInsight Should:**
```
✓ Use containers for development (current approach)
✓ Provide containers for HPC/server deployment
✓ Use standalone packaging for end users (like Slicer)
✗ Avoid container-only distribution

Result: Best of both worlds
- Researchers can use containers
- Clinicians get simple desktop app
```

**Key Insight:**
Packaging method should match use case:
- QSIprep: HPC batch → Containers ✓
- Slicer: Desktop interactive → Standalone ✓
- NeuroInsight: Both → Hybrid approach ✓

---

**Related Documentation:**
- [3D Slicer Architecture](3D_SLICER_ARCHITECTURE.md) - Desktop packaging approach
- [Docker vs Standalone](DOCKER_VS_STANDALONE_COMPARISON.md) - Detailed comparison
- [One-Click Packaging](ONE_CLICK_PACKAGING_GUIDE.md) - Implementation guide

