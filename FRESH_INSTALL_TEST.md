# Fresh User Installation Test

## Simulating a Brand New User

This document tests the COMPLETE user experience from scratch.

---

## Fresh User Experience (3 Commands, Zero Manual Fixes)

```bash
# Step 1: Download NeuroInsight
git clone -b web-app https://github.com/phindagijimana/neuroinsight.git
cd neuroinsight

# Step 2: Setup environment
cp .env.example .env

# Step 3: Start
docker-compose up -d
```

**That's it! No manual directory creation, no sed commands, no fixes.**

---

## What Happens Automatically

### When user runs `docker-compose up -d`:

1. **Init container starts**
   - Creates `data/uploads/` directory
   - Creates `data/outputs/` directory  
   - Creates `data/logs/` directory
   - Sets permissions to 777
   - Exits successfully

2. **Database starts** (PostgreSQL)
   - Creates tables automatically
   - Becomes healthy

3. **Redis starts** (Cache)
   - Becomes healthy

4. **MinIO starts** (Object storage)
   - Creates buckets automatically
   - Becomes healthy

5. **Backend starts** (FastAPI)
   - Waits for init, db, redis, minio
   - Uses paths from .env: `/data/uploads`, `/data/outputs`
   - Directories already exist (created by init)
   - Becomes healthy

6. **Worker starts** (Celery)
   - Ready to process jobs

7. **Frontend starts** (React/Nginx)
   - Accessible at http://localhost:3000

**User opens http://localhost:3000 → Uploads work immediately!**

---

## Configuration

### .env.example (Correct Settings):
```bash
UPLOAD_DIR=/data/uploads  # Absolute path for container
OUTPUT_DIR=/data/outputs  # Absolute path for container
```

### docker-compose.yml (Auto-creates directories):
```yaml
init:
  image: busybox
  command: sh -c "mkdir -p /data/uploads /data/outputs /data/logs && chmod -R 777 /data"
  volumes:
    - ./data:/data
```

### Volume Mounts:
```yaml
backend:
  volumes:
    - ./data/uploads:/data/uploads  # Host → Container
    - ./data/outputs:/data/outputs
```

---

## Verification Checklist

After running the 3 commands above, verify:

```bash
# ✓ Directories created on host
ls -la data/
# Should show: uploads/, outputs/, logs/

# ✓ Directories visible in container
docker exec neuroinsight-backend ls -la /data/
# Should show: uploads/, outputs/

# ✓ Backend healthy
docker-compose ps backend
# Should show: Up X minutes (healthy)

# ✓ Backend API working
curl http://localhost:8000/health
# Should return: {"status":"healthy",...}

# ✓ Frontend accessible
curl -I http://localhost:3000
# Should return: HTTP/1.1 200 OK

# ✓ Upload works
# Open http://localhost:3000
# Upload MRI file
# Should succeed!
```

---

## If Something Fails

### Backend shows unhealthy:
```bash
docker-compose logs backend
# Check for errors
```

### Upload fails:
```bash
docker-compose logs backend | tail -50
# Look for FileNotFoundError or other errors
```

### Frontend not accessible:
```bash
docker-compose logs frontend
docker-compose ps frontend
```

---

## Clean Start (If Needed)

```bash
# Complete reset
docker-compose down -v
rm -rf data/

# Fresh start
docker-compose up -d

# Everything recreated automatically!
```

---

## Expected Timeline

- **First time:** 5-10 minutes (building images)
- **After first time:** 30 seconds (containers already built)

---

## Success Criteria

✅ User runs 3 commands only
✅ No manual directory creation
✅ No sed/awk/manual edits
✅ No debugging needed
✅ Upload works immediately
✅ Everything automatic

---

*This is the standard we're aiming for.*

