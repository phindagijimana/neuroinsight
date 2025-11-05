# NeuroInsight Portability Checklist

**Ensuring the app works for ALL users on ANY system**

---

## ✅ Completed Audit (November 2025)

### Issues Found and Fixed

#### 1. FastSurfer Integration (CRITICAL) ✅
- **Issue:** Hardcoded Singularity path to server-specific location
- **File:** `pipeline/processors/mri_processor.py`
- **Was:** `/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo/singularity-images/fastsurfer.sif`
- **Now:** Uses `deepmi/fastsurfer:latest` Docker image
- **Impact:** App actually processes MRIs instead of mock data

#### 2. Docker Volume Mounts ✅
- **Issue:** Absolute paths to developer's machine
- **File:** `docker-compose.yml`
- **Was:** `/Users/pndagiji/Documents/.../hippo/data/uploads`
- **Now:** `./data/uploads` (relative paths)
- **Impact:** Uploads now work for all users

#### 3. Frontend Port ✅
- **Issue:** Port mismatch with documentation
- **File:** `docker-compose.yml`
- **Was:** `5173:80`
- **Now:** `3000:80`
- **Impact:** URL matches documentation (localhost:3000)

#### 4. Development Server Names ✅
- **Issue:** Server-specific hostnames in config
- **File:** `frontend/vite.config.ts`
- **Was:** `smdodwork05.urmc-sh.rochester.edu` in allowedHosts
- **Now:** Removed (not needed)
- **Impact:** Dev mode portable

#### 5. Database Configuration ✅
- **Issue:** Wrong port in migration config
- **File:** `backend/alembic.ini`
- **Was:** `localhost:15432`
- **Now:** `localhost:5432`
- **Impact:** Database migrations work

#### 6. Environment Paths ✅
- **Issue:** Relative paths in .env template
- **File:** `.env.example`
- **Was:** `UPLOAD_DIR=./data/uploads`
- **Now:** `UPLOAD_DIR=/data/uploads`
- **Impact:** Backend finds directories inside container

#### 7. Directory Creation ✅
- **Issue:** Required manual directory creation
- **File:** `docker-compose.yml`
- **Added:** Init service that auto-creates directories
- **Impact:** Zero manual setup needed

---

## ✅ Portable Code (No Issues)

### Already Portable:

✅ **Frontend API Detection**
- Automatically detects if running on localhost or remote
- Works with any hostname
- Smart URL construction

✅ **Database Connections**
- Uses environment variables
- No hardcoded credentials

✅ **Redis/MinIO Configuration**
- All via environment variables
- Portable by design

✅ **Container Networking**
- Uses Docker networks
- No hardcoded IPs

---

## 🔍 Ongoing Monitoring

### What to Check Before Each Release:

1. **Search for absolute paths:**
   ```bash
   grep -r "/mnt/" . --exclude-dir=node_modules
   grep -r "/Users/" . --exclude-dir=node_modules
   grep -r "C:\\Users" . --exclude-dir=node_modules
   ```

2. **Search for server-specific names:**
   ```bash
   grep -ri "urmc-sh" . --exclude-dir=node_modules
   grep -ri "smdodwork" . --exclude-dir=node_modules
   ```

3. **Search for hardcoded ports:**
   ```bash
   grep -r ":15432\|:8001" . --exclude-dir=node_modules
   ```

4. **Verify .env.example:**
   - All paths absolute for containers (`/data/...`)
   - No personal passwords
   - Default values work out of box

5. **Test fresh installation:**
   ```bash
   # Simulate new user
   rm -rf test-install
   git clone -b web-app https://github.com/phindagijimana/neuroinsight.git test-install
   cd test-install
   cp .env.example .env
   docker-compose up -d
   # Should work with zero manual fixes!
   ```

---

## 📋 Fresh Install Test Checklist

Run this before each release:

```bash
# Fresh clone
git clone -b web-app https://github.com/phindagijimana/neuroinsight.git test-neuroinsight
cd test-neuroinsight

# Setup
cp .env.example .env

# Start
docker-compose up -d

# Wait
sleep 60

# Test upload
curl -F "file=@test.nii" http://localhost:8000/upload/

# Check logs for errors
docker-compose logs backend | grep -i error
docker-compose logs worker | grep -i error

# Clean up
docker-compose down -v
cd ..
rm -rf test-neuroinsight
```

**Expected:** Zero errors, upload succeeds, processing starts

---

## 🎯 Portability Principles

### DO:
✅ Use environment variables for all configuration
✅ Use relative paths in docker-compose (./data/...)
✅ Use absolute paths in .env for containers (/data/...)
✅ Use standard ports (3000, 8000, 5432, 6379, 9000)
✅ Auto-create required directories
✅ Use official Docker images (deepmi/fastsurfer)
✅ Document all prerequisites

### DON'T:
❌ Hardcode absolute paths from your machine
❌ Reference specific servers or hostnames
❌ Use non-standard ports without documentation
❌ Require manual directory creation
❌ Assume specific OS paths (/Users, C:\Users, /mnt)
❌ Use custom/private Docker images
❌ Skip documentation

---

## ✅ Current Status

**Web App (web-app branch):** Fully portable ✅

**Can be installed on:**
- ✅ macOS (Intel and Apple Silicon)
- ✅ Windows 10/11
- ✅ Linux (Ubuntu, Debian, Fedora, etc.)

**Requirements:**
- Docker Desktop
- 3 commands to run
- Zero manual configuration

**Works for:**
- ✅ Random GitHub user
- ✅ Colleague at another university  
- ✅ Clinical researcher
- ✅ Student on laptop
- ✅ HPC cluster admin

---

## 📞 Verification

**How to verify portability:**

1. Ask colleague to install
2. Test on fresh VM
3. Test on Windows, Mac, Linux
4. Fresh git clone (no cached data)
5. Upload real MRI and verify processing
6. Check all results appear correctly

---

*Last audited: November 4, 2025*
*Next audit: Before v1.0.0 release*

