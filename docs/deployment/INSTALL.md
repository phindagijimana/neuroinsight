# NeuroInsight - Installation Guide

**Simple 3-step installation for hippocampal asymmetry analysis**

---

## Step 1: Install Docker Desktop

### macOS
1. Download: https://www.docker.com/products/docker-desktop
2. Open the `.dmg` file and drag Docker to Applications
3. Open Docker from Applications
4. Wait for whale icon 🐋 to appear in menu bar

### Windows
1. Download: https://www.docker.com/products/docker-desktop
2. Run the installer
3. Restart your computer
4. Open Docker Desktop
5. Wait for "Docker Desktop is running" notification

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER
# Log out and log back in
```

---

## Step 2: Download NeuroInsight

### Option A: Download ZIP (No Git Required)
1. Go to: https://github.com/phindagijimana/neuroinsight
2. Click green "Code" button → "Download ZIP"
3. Extract the ZIP file to your preferred location
4. Remember where you extracted it!

### Option B: Use Git
```bash
git clone https://github.com/phindagijimana/neuroinsight.git
cd neuroinsight
```

---

## Step 3: Start NeuroInsight

### macOS / Linux
```bash
# Open Terminal
# Navigate to the neuroinsight folder
cd /path/to/neuroinsight

# Start everything with one command!
./start.sh

# Open in browser
open http://localhost:3000
```

### Windows
```cmd
# Open Command Prompt
# Navigate to the neuroinsight folder
cd C:\path\to\neuroinsight

# Start everything with one command!
start.bat

# Open browser to: http://localhost:3000
```

**The startup script automatically:**
✅ Creates `.env` file if missing  
✅ Creates data directories  
✅ Configures paths for your system  
✅ Starts all services  
✅ Shows status and URLs

---

## ✅ You're Done!

Visit **http://localhost:3000** in your browser to use NeuroInsight.

**Important:** The URL is ALWAYS `http://localhost:3000` - this is the standard port for all users.

### What you'll see:
- Upload interface for MRI scans
- Processing queue
- Results viewer with 3D visualization
- Export options (JSON, CSV)

---

## 🛑 To Stop NeuroInsight

**Using startup script:**
```bash
./start.sh stop     # macOS/Linux
start.bat stop      # Windows
```

**Or manually:**
```bash
docker-compose down
```

---

## 🔄 To Restart NeuroInsight (Next Time)

**Using startup script:**
```bash
cd /path/to/neuroinsight
./start.sh          # macOS/Linux
start.bat           # Windows
```

**Or manually:**
```bash
cd /path/to/neuroinsight
docker-compose up -d
open http://localhost:3000  # or visit in browser
```

---

## ❓ Troubleshooting

### Docker not running?
- **macOS**: Look for whale 🐋 icon in menu bar
- **Windows**: Look for whale 🐋 icon in system tray
- **Linux**: Run `sudo systemctl status docker`

### Can't access localhost:3000?
```bash
# Check if services started
docker-compose ps

# View logs
docker-compose logs frontend
```

### Need to start fresh?
```bash
docker-compose down -v  # Removes all data
docker-compose up -d    # Fresh start
```

---

## 📖 Need More Help?

See the full README.md for:
- Detailed troubleshooting
- GPU configuration
- Advanced usage
- API documentation

---

## System Requirements

**Minimum:**
- 4 CPU cores
- 16GB RAM
- 30GB free storage
- Docker Desktop

**Recommended:**
- 8+ CPU cores
- 32GB RAM
- 100GB SSD
- NVIDIA GPU (optional, 10-20x faster)

---

## Processing Times

**Without GPU (CPU):**
- ~5-15 minutes per scan

**With NVIDIA GPU:**
- ~1-3 minutes per scan

---

**Questions?** See README.md or open an issue: https://github.com/phindagijimana/neuroinsight/issues

