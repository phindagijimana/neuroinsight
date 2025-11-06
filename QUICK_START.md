# Quick Start Guide

## Deployment Methods

### Method 1: SSH Tunnel (Institutional Access)

Access shared HPC installation without local setup.

**Requirements:** SSH access to institutional HPC

**Steps:**

1. Open terminal
2. Run: `ssh -L 56052:localhost:56052 username@urmc-sh.rochester.edu`
3. Open browser to: `http://localhost:56052`

**Disconnect:** Type `exit` or close terminal

**Full guide:** [docs/LAB_ACCESS_GUIDE.md](docs/LAB_ACCESS_GUIDE.md)

---

### Method 2: Local Installation (Docker Compose)

Full deployment on your own system.

**Requirements:**
- Docker Desktop installed
- 16GB+ RAM
- 30GB+ free disk space

**Steps:**

1. Clone repository:
   ```bash
   git clone https://github.com/phindagijimana/neuroinsight-web-app
   cd neuroinsight-web-app
   ```

2. Start services:
   ```bash
   docker-compose up -d
   ```

3. Open browser to: `http://localhost:56052`

**Stop services:** `docker-compose down`

**Full guide:** [README.md](README.md#installation)

---

### Method 3: Desktop Application (Future)

**Status:** In development (estimated 1-2 months)

**Planned features:**
- Single-click installer
- No Docker or Python required
- Offline operation
- Auto-updates

**Development plan:** [docs/STANDALONE_DESKTOP_APP.md](docs/STANDALONE_DESKTOP_APP.md)

---

## Recommended Method

| User Type | Recommended Method |
|-----------|-------------------|
| Institutional lab members | SSH Tunnel |
| Developers | Docker Compose |
| Quick evaluation | SSH Tunnel |
| Offline processing | Docker Compose |
| Non-technical users | Desktop App (when available) |

---

## Support

**Documentation:** [README.md](README.md)

**Issues:** [GitHub Issues](https://github.com/phindagijimana/neuroinsight-web-app/issues)

**Email:** support@neuroinsight.app
