# How to Access NeuroInsight from GitHub

## 🌐 Overview

NeuroInsight is available on GitHub at: **https://github.com/phindagijimana/neuroinsight**

This guide shows you how to download and run the web app on your own computer.

---

## 🚀 Quick Start (5 Steps)

### Step 1: Install Docker Desktop

**Download from**: https://www.docker.com/products/docker-desktop

**macOS:**
1. Download Docker Desktop for Mac
2. Open the `.dmg` file
3. Drag Docker to Applications
4. Open Docker Desktop
5. Wait for whale icon in menu bar

**Windows:**
1. Download Docker Desktop for Windows
2. Run the installer
3. Restart your computer
4. Start Docker Desktop
5. Wait for "Docker is running" message

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER  # Add yourself to docker group
# Log out and back in
```

**Verify Docker is running:**
```bash
docker --version
# Should show: Docker version 24.x.x or higher
```

---

### Step 2: Download NeuroInsight from GitHub

**Option A: Download ZIP (No Git Required)**

1. Go to: **https://github.com/phindagijimana/neuroinsight**
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Extract the ZIP file to your desired location
5. Open Terminal/Command Prompt
6. Navigate to the extracted folder:
   ```bash
   cd /path/to/neuroinsight-main
   ```

**Option B: Clone with Git (Recommended)**

```bash
# If you have git installed:
git clone https://github.com/phindagijimana/neuroinsight.git
cd neuroinsight
```

---

### Step 3: Start the Application

**macOS / Linux:**
```bash
# From the neuroinsight folder:
./start.sh
```

**Windows:**
```cmd
# From the neuroinsight folder:
start.bat
```

**What happens:**
- Script checks for Docker
- Creates `.env` configuration file
- Creates data directories
- Starts all services (backend, database, worker, frontend)
- Shows you the access URL

**First run takes 5-10 minutes** (downloads Docker images ~2GB)

---

### Step 4: Access the Web App

**Once started, open your browser:**
```
http://localhost:3000
```

or

```
http://localhost:8000
```

(Check the terminal output for the correct URL)

**You should see:**
```
┌────────────────────────────────────────┐
│     🧠 NeuroInsight                   │
│  Hippocampal Asymmetry Analysis       │
│                                        │
│  [Upload MRI Scan]                    │
└────────────────────────────────────────┘
```

---

### Step 5: Start Using!

1. Click **"Upload MRI Scan"**
2. Select your `.nii`, `.nii.gz`, or `.dcm` file
3. Wait for processing (2-60 minutes depending on hardware)
4. View results!

---

## 📋 Detailed Instructions

### System Requirements

**Minimum (CPU Processing):**
- **CPU**: 4 cores (Intel i5 / AMD Ryzen 5)
- **RAM**: 16GB
- **Storage**: 30GB free space
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 20.04+
- **Processing time**: ~40-60 minutes per scan

**Recommended (GPU Processing):**
- **CPU**: 8+ cores
- **RAM**: 32GB
- **Storage**: 100GB SSD
- **GPU**: NVIDIA GPU with 8GB+ VRAM
- **OS**: Same as minimum
- **Processing time**: ~2-5 minutes per scan ⚡

---

## 🔍 Step-by-Step with Screenshots

### A. Navigate to GitHub

1. Open browser
2. Go to: `https://github.com/phindagijimana/neuroinsight`
3. You'll see the repository homepage with:
   - Green "Code" button
   - List of files
   - README.md description

### B. Download the Code

**Using Download ZIP:**
```
1. Click green "Code" button
   ↓
2. Click "Download ZIP"
   ↓
3. ZIP file downloads to your Downloads folder
   ↓
4. Extract the ZIP file
   ↓
5. You now have a folder: "neuroinsight-main"
```

**Using Git Clone:**
```bash
# Open Terminal (Mac/Linux) or Command Prompt (Windows)

# Navigate to where you want the folder:
cd ~/Documents  # or C:\Users\YourName\Documents

# Clone the repository:
git clone https://github.com/phindagijimana/neuroinsight.git

# Enter the folder:
cd neuroinsight
```

### C. Start the Application

**macOS / Linux:**
```bash
# Make sure you're in the neuroinsight folder
cd /path/to/neuroinsight

# Make script executable (first time only)
chmod +x start.sh

# Run the start script
./start.sh
```

**Expected output:**
```
🧠 NeuroInsight Startup Script
==============================

✓ Docker is running
✓ Created .env configuration
✓ Created data directories
✓ Starting services...

[+] Running 5/5
 ✔ Container neuroinsight-postgres  Started
 ✔ Container neuroinsight-redis     Started
 ✔ Container neuroinsight-minio     Started
 ✔ Container neuroinsight-backend   Started
 ✔ Container neuroinsight-frontend  Started

==============================
✅ NeuroInsight is running!

📱 Access the web app at:
   http://localhost:3000

📖 Documentation: ./docs/
🛑 To stop: docker-compose down
==============================
```

**Windows:**
```cmd
REM Make sure you're in the neuroinsight folder
cd C:\Users\YourName\Documents\neuroinsight

REM Run the start script
start.bat
```

### D. Verify Services are Running

```bash
# Check status
docker-compose ps

# Should show:
# NAME                        STATUS
# neuroinsight-backend       Up
# neuroinsight-frontend      Up
# neuroinsight-postgres      Up
# neuroinsight-redis         Up
# neuroinsight-worker        Up
```

### E. Open in Browser

1. Open your web browser (Chrome, Firefox, Safari, Edge)
2. Type in address bar: `http://localhost:3000`
3. Press Enter
4. NeuroInsight interface loads

---

## 🎯 Common Issues & Solutions

### Issue 1: "Docker is not running"

**Error:**
```
❌ Docker is not running
Please start Docker Desktop and try again.
```

**Solution:**
```bash
# macOS: Open Docker Desktop from Applications
# Windows: Open Docker Desktop from Start Menu
# Linux: sudo systemctl start docker

# Wait for Docker to fully start (30 seconds)
# Then run ./start.sh again
```

---

### Issue 2: "Port already in use"

**Error:**
```
Error: Bind for 0.0.0.0:3000 failed: port is already allocated
```

**Solution:**
```bash
# Something else is using port 3000
# Option 1: Stop other service
lsof -i :3000  # See what's using port 3000
kill <PID>     # Stop it

# Option 2: Change NeuroInsight port
# Edit docker-compose.yml:
# Change "3000:3000" to "3001:3000"
# Then access at http://localhost:3001
```

---

### Issue 3: "Cannot connect to Docker daemon"

**Error:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solution:**
```bash
# Make sure Docker Desktop is fully started
# Check the whale icon (Mac) or system tray (Windows)
# Should say "Docker Desktop is running"

# Linux: Add yourself to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

---

### Issue 4: Downloads are very slow

**Problem:** First-time setup downloading images very slowly

**Solution:**
```bash
# This is normal for first run (~2GB download)
# Depends on your internet speed:
# - Fast internet: 5-10 minutes
# - Slow internet: 20-30 minutes

# Subsequent starts are instant (images cached)
```

---

### Issue 5: "Cannot access http://localhost:3000"

**Problem:** Page doesn't load in browser

**Checklist:**
```bash
# 1. Check services are running
docker-compose ps
# All should say "Up"

# 2. Wait longer
# First start takes time (images downloading)
# Wait 2-3 minutes after "Started" messages

# 3. Try different port
http://localhost:8000  # Backend direct access

# 4. Check logs
docker-compose logs frontend
docker-compose logs backend

# 5. Restart services
docker-compose down
./start.sh
```

---

## 📚 After Installation

### Upload Your First Scan

1. Click **"Upload MRI Scan"** on homepage
2. Select a NIfTI file (`.nii` or `.nii.gz`)
3. Click **"Open"**
4. Upload begins automatically
5. Processing starts when upload completes

### Monitor Processing

1. Go to **"Jobs"** tab in navigation
2. See your scan with status: **"Running"**
3. Page refreshes every 5 seconds automatically
4. Wait for status to change to: **"Completed"**

**Processing time:**
- With GPU: 2-5 minutes
- CPU only: 40-60 minutes

### View Results

1. Click on completed job
2. See hippocampal volumes (left/right)
3. View asymmetry index
4. Click **"View 3D"** for interactive brain viewer
5. Click **"Download CSV"** to export results

---

## 🛑 Stopping the Application

**When done:**
```bash
# Stop all services
docker-compose down

# Or use the stop script (if available)
./stop.sh  # macOS/Linux
stop.bat   # Windows
```

**To free up disk space (removes all data):**
```bash
docker-compose down -v
```
⚠️ **Warning**: This deletes all uploaded scans and results!

---

## 🔄 Updating to Latest Version

**If you downloaded ZIP:**
```bash
# Download latest ZIP from GitHub
# Extract to new folder
# Copy your old .env file if you made changes
# Start with ./start.sh
```

**If you used Git clone:**
```bash
cd neuroinsight

# Stop current services
docker-compose down

# Get latest code
git pull origin main

# Restart services
./start.sh
```

---

## 💾 Your Data

**Where files are stored:**
```
neuroinsight/
├── data/
│   ├── uploads/     ← Your uploaded MRI scans
│   ├── outputs/     ← Processing results
│   └── database/    ← Job metadata
└── logs/            ← Application logs
```

**Backup your data:**
```bash
# Create backup
tar -czf neuroinsight-backup.tar.gz data/

# Restore backup
tar -xzf neuroinsight-backup.tar.gz
```

---

## 🆘 Getting Help

### Check Documentation

- **User Guide**: `docs/USER_GUIDE.md`
- **Quick Start**: `QUICK_USER_GUIDE.md`
- **README**: `README.md`

### Check Logs

```bash
# View all logs
docker-compose logs

# View specific service
docker-compose logs backend
docker-compose logs worker

# Follow logs in real-time
docker-compose logs -f
```

### Ask for Help

- **GitHub Issues**: https://github.com/phindagijimana/neuroinsight/issues
- **GitHub Discussions**: https://github.com/phindagijimana/neuroinsight/discussions

When asking for help, include:
1. Your operating system
2. Output of `docker --version`
3. Error messages from logs
4. What you were trying to do

---

## ✅ Summary Checklist

- [ ] Docker Desktop installed and running
- [ ] NeuroInsight downloaded from GitHub
- [ ] Services started with `./start.sh` or `start.bat`
- [ ] Browser opened to `http://localhost:3000`
- [ ] First MRI scan uploaded
- [ ] Processing completed successfully
- [ ] Results viewed and exported

**Congratulations! You're ready to analyze hippocampal asymmetry! 🧠**

---

## 🔗 Quick Links

- **GitHub Repository**: https://github.com/phindagijimana/neuroinsight
- **Download Docker**: https://www.docker.com/products/docker-desktop
- **User Guide**: `docs/USER_GUIDE.md` (after download)
- **Report Issues**: https://github.com/phindagijimana/neuroinsight/issues

---

## 📝 Notes

- **Privacy**: All data stays on your computer. Nothing is uploaded to the internet.
- **Offline**: Works without internet after initial Docker image download.
- **Free**: Completely free and open source.
- **Updates**: Check GitHub occasionally for new features and bug fixes.

**Need the desktop app instead?** See `hippo_desktop/README.md` for installer-based installation (easier for non-technical users).

