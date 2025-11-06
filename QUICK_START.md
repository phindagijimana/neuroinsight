# Quick Start Guide

## Which Method Should I Use?

### Lab Access (Recommended for Most Users)

**Best for:** Clinical staff, researchers, students at institution

**Advantages:**
- No installation required
- Ready to use immediately
- Access from any computer
- Shared infrastructure

**Requirements:** Institutional account

[Skip to Lab Access Instructions](#lab-access)

---

### Local Installation

**Best for:** Personal use, offline work, development

**Advantages:**
- Complete control
- Works without network access
- Process sensitive data locally

**Requirements:** Docker Desktop, 16GB+ RAM

[Skip to Installation Instructions](#installation)

---

## Lab Access

### Step 1: Open Terminal

**macOS:** Press `Cmd + Space`, type "terminal", press Enter

**Windows:** Press `Win + R`, type "cmd", press Enter

**Linux:** Press `Ctrl + Alt + T`

### Step 2: Connect

Type this command (replace `username` with your actual username):

```bash
ssh -L 56052:localhost:56052 username@urmc-sh.rochester.edu
```

Press Enter and enter your password when prompted.

### Step 3: Open Application

While keeping terminal open, open your web browser and go to:

```
http://localhost:56052
```

### To Disconnect

Close the terminal window or type `exit` and press Enter.

---

## Installation

### Step 1: Install Docker Desktop

1. Download: https://www.docker.com/products/docker-desktop
2. Install the downloaded file
3. Start Docker Desktop
4. Wait for initialization (whale icon appears in system tray)
5. **Important:** Increase memory allocation:
   - Open Docker Desktop
   - Go to Settings/Preferences → Resources → Memory
   - Set to at least 20GB
   - Click "Apply & Restart"

### Step 2: Download NeuroInsight

**Option A - With Git (Recommended):**

```bash
git clone https://github.com/phindagijimana/neuroinsight-web-app
cd neuroinsight-web-app
```

**Option B - Without Git:**

1. Go to: https://github.com/phindagijimana/neuroinsight-web-app
2. Click green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file
5. Open terminal in extracted folder

### Step 3: Start NeuroInsight

In terminal, run:

```bash
docker-compose up -d
```

Wait 2-3 minutes for services to start.

### Step 4: Open Application

Open browser to:

```
http://localhost:56052
```

### To Stop

In terminal, run:

```bash
docker-compose down
```

---

## First Time Use

1. **Upload** your T1-weighted MRI scan (.nii, .nii.gz, or .dcm)
2. **Process** - Click the process button and wait
3. **View** results including volumes and asymmetry
4. **Export** data as needed

---

## Need Help?

**Installation problems:** See [README.md](README.md#troubleshooting)

**Usage questions:** See [docs/USER_GUIDE.md](docs/USER_GUIDE.md)

**Technical issues:** [Open GitHub issue](https://github.com/phindagijimana/neuroinsight-web-app/issues)

---

## Next Steps

- Read full documentation: [README.md](README.md)
- View example scans and results
- Configure advanced settings
- Set up batch processing
