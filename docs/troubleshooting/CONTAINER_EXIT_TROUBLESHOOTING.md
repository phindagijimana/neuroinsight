# Container Exits Immediately - Troubleshooting Guide

## Issue: Containers Run for 3 Seconds Then Exit

When you run `docker-compose up -d`, containers start but immediately exit/complete.

---

## 🔍 Step 1: Check Container Status

```bash
docker-compose ps
```

**Look for:**
- Status: "Exit 0" or "Exit 1" instead of "Up"
- Containers that keep restarting

---

## 🔍 Step 2: View Container Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs worker
docker-compose logs db
```

**Common error patterns and solutions below.**

---

## 🐛 Common Issues & Fixes

### Issue 1: Database Connection Error

**Error in logs:**
```
sqlalchemy.exc.OperationalError: could not connect to server
connection refused
psycopg2.OperationalError: FATAL: database "neuroinsight" does not exist
```

**Solution:**
```bash
# 1. Make sure database container is running
docker-compose ps db

# 2. If not, start it first and wait
docker-compose up -d db
sleep 10

# 3. Create database if needed
docker-compose exec db psql -U neuroinsight -c "CREATE DATABASE neuroinsight;"

# 4. Then start other services
docker-compose up -d
```

---

### Issue 2: Missing Environment Variables

**Error in logs:**
```
KeyError: 'DATABASE_URL'
SettingsError: field required
ValidationError: 1 validation error
```

**Solution:**
```bash
# 1. Check if .env exists
ls -la .env

# 2. If missing, create it
cat > .env << 'EOF'
# Database
POSTGRES_USER=neuroinsight
POSTGRES_PASSWORD=neuroinsight_secure_password
POSTGRES_DB=neuroinsight
DATABASE_URL=postgresql://neuroinsight:neuroinsight_secure_password@db:5432/neuroinsight

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ENDPOINT=minio:9000
MINIO_BUCKET=neuroinsight

# App
SECRET_KEY=change-this-in-production
DEBUG=true
UPLOAD_DIR=/data/uploads
OUTPUT_DIR=/data/outputs
CORS_ORIGINS=*
EOF

# 3. Restart services
docker-compose down
docker-compose up -d
```

---

### Issue 3: Port Already in Use

**Error in logs:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solution:**
```bash
# 1. Find what's using the port
lsof -i :8000
# or
netstat -an | grep 8000

# 2. Kill the process
kill -9 <PID>

# 3. Or change the port in docker-compose.yml
# Edit ports section: "8001:8000" instead of "8000:8000"

# 4. Restart
docker-compose down
docker-compose up -d
```

---

### Issue 4: Volume Mount Permission Issues

**Error in logs:**
```
PermissionError: [Errno 13] Permission denied: '/data/uploads'
OSError: [Errno 30] Read-only file system
```

**Solution:**
```bash
# 1. Create directories with proper permissions
mkdir -p data/uploads data/outputs data/logs
chmod -R 777 data/

# 2. Restart services
docker-compose down
docker-compose up -d
```

---

### Issue 5: Missing Dependencies in Container

**Error in logs:**
```
ModuleNotFoundError: No module named 'fastapi'
ImportError: cannot import name 'X'
```

**Solution:**
```bash
# Rebuild containers with fresh dependencies
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

### Issue 6: Command Fails Immediately

**Error in logs:**
```
exec: "python": executable file not found
/bin/sh: 1: uvicorn: not found
```

**Solution:**
```bash
# Check Dockerfile CMD/ENTRYPOINT is correct
# Should be something like:
# CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Rebuild if needed
docker-compose build --no-cache backend
docker-compose up -d
```

---

## 🔧 Diagnostic Commands

### Check Individual Container

```bash
# Start one service at a time to isolate the issue
docker-compose up db          # Database first
docker-compose up redis       # Then Redis
docker-compose up backend     # Then backend
```

### Run Container Interactively

```bash
# Run backend container with shell access
docker-compose run --rm backend /bin/bash

# Inside container, try running the command manually:
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Check Container Events

```bash
# See what's happening with containers
docker-compose events

# In another terminal, start services:
docker-compose up
```

---

## ✅ Complete Restart Procedure

**If nothing else works, do a complete clean restart:**

```bash
# 1. Stop everything
docker-compose down -v

# 2. Remove all containers, networks, volumes
docker system prune -a --volumes
# WARNING: This removes ALL Docker data, not just NeuroInsight

# 3. Verify .env exists and is correct
cat .env

# 4. Create directories
mkdir -p data/uploads data/outputs data/logs
chmod -R 777 data/

# 5. Rebuild from scratch
docker-compose build --no-cache

# 6. Start services one by one
docker-compose up -d db
sleep 10
docker-compose up -d redis minio
sleep 5
docker-compose up -d backend worker
sleep 5
docker-compose up -d frontend

# 7. Check status
docker-compose ps

# 8. View logs
docker-compose logs -f
```

---

## 🎯 Quick Diagnosis Script

Save this as `diagnose.sh`:

```bash
#!/bin/bash

echo "=== Docker Status ==="
docker info 2>&1 | head -5

echo -e "\n=== Container Status ==="
docker-compose ps

echo -e "\n=== Recent Logs (last 50 lines) ==="
docker-compose logs --tail=50

echo -e "\n=== Environment File ==="
if [ -f .env ]; then
    echo "✓ .env exists"
    grep -v "PASSWORD\|SECRET" .env | head -10
else
    echo "✗ .env missing!"
fi

echo -e "\n=== Data Directories ==="
ls -ld data/uploads data/outputs 2>/dev/null || echo "✗ Data directories missing!"

echo -e "\n=== Port Usage ==="
lsof -i :8000 2>/dev/null || echo "Port 8000 is free"
lsof -i :3000 2>/dev/null || echo "Port 3000 is free"
```

Run it:
```bash
chmod +x diagnose.sh
./diagnose.sh
```

---

## 📋 Checklist Before Starting

- [ ] Docker Desktop is running (whale icon in menu bar)
- [ ] `.env` file exists in project root
- [ ] `data/` directories exist and are writable
- [ ] Ports 8000, 3000, 5432, 6379, 9000 are not in use
- [ ] You're in the correct directory (`docker-compose.yml` exists)
- [ ] No other instances of the app are running

---

## 🆘 If Still Not Working

**Provide these outputs for help:**

```bash
# 1. Docker version
docker --version
docker-compose --version

# 2. OS info
uname -a

# 3. Container status
docker-compose ps

# 4. Full logs
docker-compose logs > debug-logs.txt
# Share debug-logs.txt

# 5. Docker compose config
docker-compose config

# 6. Environment check
ls -la .env
cat .env | grep -v PASSWORD
```

Then open an issue with this information!


