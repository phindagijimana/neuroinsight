# Platform Validation Report

## Web Application (Docker Compose)

### Linux x86_64 (HPC)

**Status:** Production Ready

**Evidence:**
- Backend: Port 8000 operational
- Database: PostgreSQL on port 15432
- Worker: Singularity fallback functional
- Frontend: Port 56052 accessible
- Processing: Real FastSurfer execution (40-60 min)

**Access Method:**
```bash
ssh -L 56052:localhost:56052 username@urmc-sh.rochester.edu
```

**Rating:** Fully supported for production deployment

---

### macOS ARM64 (Apple Silicon)

**Status:** Limited Support

**Issues:**
- Requires Rosetta 2 emulation (performance impact)
- Minimum 20GB RAM allocation required
- FastSurfer may crash with insufficient memory
- Potential fallback to mock data

**Platform Configuration:**
```yaml
# docker-compose.yml
worker:
  platform: linux/amd64  # Force x86_64 emulation
```

**Rating:** Functional but not recommended for production use

**Alternative:** Use SSH tunnel to HPC infrastructure

---

### Windows x86_64

**Status:** Expected Compatible (Untested)

**Rationale:**
- Docker Desktop supports Windows
- Native x86_64 architecture (no emulation)
- Similar configuration to Linux

**Recommendation:** Requires validation testing

---

## Desktop Application (Electron)

### Current Implementation

**Status:** Docker Management Interface

**Capabilities:**
- Electron-based user interface
- Docker Compose orchestration
- Cross-platform builds (Windows, macOS, Linux)

**Limitations:**
- Requires Docker Desktop installation
- Not fully standalone
- User must manage Docker dependencies

**Rating:** Suitable for technical users

---

### Future Standalone Application

**Status:** Design Phase

**Planned Architecture:**
```
Standalone Executable
├── Electron UI Shell
├── Embedded Python Backend
├── Bundled FastSurfer Models
├── Embedded SQLite Database
└── No External Dependencies
```

**Status:** Specification complete, implementation pending (1-2 months)

**Documentation:** [docs/STANDALONE_DESKTOP_APP.md](docs/STANDALONE_DESKTOP_APP.md)

---

## Quick Start Methods

### Web Application

```bash
git clone https://github.com/phindagijimana/neuroinsight-web-app
cd neuroinsight-web-app
docker-compose up -d
# Access: http://localhost:56052
```

---

### Desktop Application (Current)

```bash
cd hippo_desktop
npm install
npm start  # Development mode
npm run dist  # Build installer
```

---

## Deployment Recommendations

| Environment | Recommended Method | Support Level |
|-------------|-------------------|---------------|
| HPC Linux (x86_64) | Docker Compose | Production Ready |
| Ubuntu/Debian | Docker Compose | Production Ready |
| macOS x86_64 | Docker Compose | Supported |
| macOS ARM64 | SSH to HPC | Recommended |
| macOS ARM64 | Docker Compose | Limited Support |
| Windows | Docker Compose | Expected Compatible |

---

## Recent Updates

**Latest Commits:**
```
9376e1a - Docker to Singularity fallback for HPC compatibility
5840987 - Frontend bug fixes (undefined variable)
ac004bd - ARM64 platform compatibility improvements
```

**Status:** All platform fixes committed to repository

---

## Support Resources

**Documentation:** [README.md](README.md)

**Platform Issues:** [GitHub Issues](https://github.com/phindagijimana/neuroinsight-web-app/issues)

**Lab Access:** [docs/LAB_ACCESS_GUIDE.md](docs/LAB_ACCESS_GUIDE.md)

---

**Report Date:** November 2025  
**Testing Platform:** URMC HPC Infrastructure
