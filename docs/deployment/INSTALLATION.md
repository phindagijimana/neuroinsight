# Installation Guide

## Before You Start

Check that your computer meets these requirements:

- **Memory:** 16GB RAM minimum, 32GB recommended
- **Storage:** 30GB free space
- **Operating System:** Windows 10+, macOS 10.15+, or Linux
- **Network:** Internet connection for initial setup only

---

## Step 1: Install Docker Desktop

### For Windows

1. Download: https://www.docker.com/products/docker-desktop
2. Run the installer
3. Restart your computer when prompted
4. Start Docker Desktop from Start menu
5. Wait for "Docker Desktop is running" message

### For macOS

1. Download: https://www.docker.com/products/docker-desktop
2. Open the .dmg file
3. Drag Docker to Applications folder
4. Open Docker from Applications
5. Wait for whale icon to appear in menu bar

### For Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER
```

Log out and log back in for changes to take effect.

---

## Step 2: Configure Docker Memory

**Critical:** Docker needs more memory than default settings.

### Windows and macOS

1. Open Docker Desktop
2. Click Settings (gear icon)
3. Go to Resources → Memory
4. Move slider to at least 20GB
5. Click "Apply & Restart"
6. Wait for Docker to restart

### Linux

No configuration needed - uses system memory directly.

---

## Step 3: Download NeuroInsight

### Method A: Using Git (Recommended)

If you have Git installed:

```bash
git clone https://github.com/phindagijimana/neuroinsight-web-app
cd neuroinsight-web-app
```

### Method B: Direct Download

If you don't have Git:

1. Open: https://github.com/phindagijimana/neuroinsight-web-app
2. Click green "Code" button
3. Select "Download ZIP"
4. Extract ZIP to desired location
5. Open terminal/command prompt
6. Navigate to extracted folder:
   ```bash
   cd path/to/neuroinsight-web-app
   ```

---

## Step 4: Start NeuroInsight

In your terminal/command prompt:

```bash
docker-compose up -d
```

**What happens:**
- Downloads required software (first time only - may take 10-15 minutes)
- Starts all services
- Shows "done" when ready

---

## Step 5: Verify Installation

1. Wait 2-3 minutes after `docker-compose up -d` completes
2. Open web browser
3. Go to: `http://localhost:56052`
4. You should see the NeuroInsight interface

**If page doesn't load:**
- Wait another minute and refresh
- Check Docker Desktop shows all containers running
- See [Troubleshooting](#troubleshooting) section

---

## Using NeuroInsight

Once installed:

**To Start:**
```bash
cd neuroinsight-web-app
docker-compose up -d
```

**To Stop:**
```bash
docker-compose down
```

**To Access:**

Open browser to `http://localhost:56052`

---

## Troubleshooting

### "Cannot connect to Docker daemon"

**Cause:** Docker Desktop not running

**Solution:**
- Start Docker Desktop application
- Wait for initialization (whale icon appears)
- Try command again

### "Port 56052 already in use"

**Cause:** Previous instance still running or another app using port

**Solution:**
```bash
docker-compose down
docker-compose up -d
```

### "Error response from daemon: Get timeout"

**Cause:** Network issue during download

**Solution:**
- Check internet connection
- Retry: `docker-compose pull`
- Then: `docker-compose up -d`

### Page loads but shows errors

**Cause:** Services still starting or insufficient memory

**Solution:**
- Wait 1-2 more minutes
- Check Docker memory allocation (Step 2)
- Restart: `docker-compose restart`

### Application very slow or crashes

**Cause:** Insufficient memory allocation

**Solution:**
- Increase Docker memory to 24GB or 32GB
- Close other applications
- Restart Docker Desktop

---

## Updating NeuroInsight

To get the latest version:

```bash
cd neuroinsight-web-app
docker-compose down
git pull origin web-app
docker-compose pull
docker-compose up -d
```

---

## Uninstallation

### Remove NeuroInsight

```bash
cd neuroinsight-web-app
docker-compose down -v
cd ..
rm -rf neuroinsight-web-app
```

### Remove Docker (Optional)

**Windows/macOS:** Uninstall Docker Desktop from Control Panel/Applications

**Linux:**
```bash
sudo apt-get remove docker.io docker-compose
```

---

## Next Steps

- Read user guide: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)
- Process your first scan
- Configure advanced settings
- Set up batch processing

---

## Getting Help

**Installation issues:** Check troubleshooting section above

**Other questions:** [README.md](README.md)

**Report bugs:** [GitHub Issues](https://github.com/phindagijimana/neuroinsight-web-app/issues)

