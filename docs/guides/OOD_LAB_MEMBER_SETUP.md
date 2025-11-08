# NeuroInsight Setup for Lab Members

## 🎯 Quick Setup (One-Time, 5 Minutes)

Each lab member creates their own copy of NeuroInsight from GitHub.

---

## Step-by-Step Setup

### 1. Login to Open OnDemand

```
https://ondemand.urmc.rochester.edu
```

### 2. Launch Interactive Desktop

- Interactive Apps → Interactive Desktop
- Memory: 20 GB
- Cores: 4
- Hours: 2
- Launch

### 3. Open Terminal in Desktop

Once desktop loads, open a terminal.

### 4. Clone NeuroInsight from GitHub

```bash
# Go to your home directory
cd ~

# Clone from GitHub
git clone -b web-app https://github.com/phindagijimana/neuroinsight.git

# Enter the directory
cd neuroinsight
```

**That's it!** You now have your own copy.

### 5. Start NeuroInsight

```bash
# First time: Install dependencies (one-time, 2-3 minutes)
bash RUN_ALL.sh
```

**Wait ~30 seconds** for services to start.

### 6. Open in Browser

**In the OOD desktop:**
- Open Firefox
- Go to: `http://localhost:8000`

**NeuroInsight loads!** 🎉

---

## Daily Use (After Setup)

### Every Time You Want to Use NeuroInsight:

1. **Login to OOD:** https://ondemand.urmc.rochester.edu
2. **Launch Desktop:** 20GB RAM, 4 hours
3. **In desktop terminal:**
   ```bash
   cd ~/neuroinsight
   bash RUN_ALL.sh
   ```
4. **Open Firefox:** http://localhost:8000
5. **Upload and process scans!**

---

## Your Data Location

**Everything is in YOUR directory:**
```
~/neuroinsight/
├── data/
│   ├── uploads/    ← Your uploaded scans
│   ├── outputs/    ← Your results
│   └── logs/       ← Your processing logs
```

**Privacy:** Other users cannot see your data (unless you share the directory).

---

## Updating to Latest Version

**To get new features:**

```bash
cd ~/neuroinsight

# Stop services
docker-compose down

# Get latest code
git pull origin web-app

# Restart
bash RUN_ALL.sh
```

---

## Different Ports (If Multiple Users on Same Node)

If you and another user are on the same compute node, you might need different ports:

```bash
# Edit .env file
nano .env

# Change port numbers (add your user number):
# BACKEND_PORT=8001  (instead of 8000)
# FRONTEND_PORT=3001  (instead of 3000)

# Then access at: http://localhost:8001
```

Or the system will auto-assign ports if there's a conflict.

---

## Troubleshooting

### "Permission denied" errors

**You might need:**
```bash
chmod +x RUN_ALL.sh
```

### "Port already in use"

**Another instance is running:**
```bash
# Check what's using the port
lsof -i :8000

# Stop it
docker-compose down

# Or use different port (edit .env)
```

### "Not enough memory"

**OOD session doesn't have enough RAM:**
- Delete current session
- Launch new one with 24-32 GB

### Can't access http://localhost:8000

**Check if services are running:**
```bash
docker-compose ps
# All should say "Up"

# Check logs
docker-compose logs backend
```

---

## Advanced: Sharing Data Between Users

**If your lab wants to share scans/results:**

### Option 1: Shared Directory

```bash
# Create shared folder (done once by admin or you)
mkdir -p /mnt/nfs/shared/neuroinsight-lab

# Each user links to it
cd ~/neuroinsight
ln -s /mnt/nfs/shared/neuroinsight-lab data/shared

# Upload to shared folder
# Other users can access the same scans
```

### Option 2: Export/Import Results

```bash
# User 1: Export results
cd ~/neuroinsight/data/outputs
tar -czf results-2025-11.tar.gz */metrics.csv

# Share file with User 2
cp results-2025-11.tar.gz /mnt/nfs/shared/

# User 2: Import results
cd ~/neuroinsight/data/outputs
tar -xzf /mnt/nfs/shared/results-2025-11.tar.gz
```

---

## Best Practices

### 1. Organize Your Scans

Use clear naming:
```
~/neuroinsight/data/uploads/
├── project-A/
│   ├── patient-001_baseline_T1.nii.gz
│   └── patient-002_baseline_T1.nii.gz
└── project-B/
    └── control-001_T1.nii.gz
```

### 2. Regular Backups

```bash
# Backup your results
cd ~/neuroinsight
tar -czf ~/backups/neuroinsight-$(date +%Y%m%d).tar.gz data/outputs/

# Or just export CSV files
cp data/outputs/*/metrics.csv ~/results-backup/
```

### 3. Clean Up Old Jobs

```bash
# Delete old test jobs
cd ~/neuroinsight
python bin/cleanup_storage.py --old-completed --days 30
```

### 4. Keep Updated

```bash
# Check for updates monthly
cd ~/neuroinsight
git pull origin web-app
docker-compose down
docker-compose up -d
```

---

## 📊 Storage Considerations

Each user's installation uses:
- **Code:** ~100 MB (negligible)
- **Docker images:** Shared (not duplicated)
- **Data:** Depends on usage
  - Per scan: ~500 MB upload + ~2 GB output
  - 10 scans: ~25 GB
  - 100 scans: ~250 GB

**Recommendation:**
- Set disk quotas per user (work with HPC admin)
- Encourage regular cleanup of old jobs
- Export important results to long-term storage

---

## Summary

**Your question:** *"Can lab members get code from GitHub instead of my repository?"*

**Answer:** **Yes! And they should!**

**Each user:**
1. Clones from GitHub to `~/neuroinsight`
2. Has their own private instance
3. Their own data and results
4. No conflicts with others

**You:**
- Keep your installation for development
- Push updates to GitHub
- Lab members pull updates when ready

**This is the standard approach!** ✅

---

## 🚀 **Action Plan:**

```bash
# Commit the new user guide
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
git add OOD_LAB_MEMBER_SETUP.md OOD_USER_GUIDE.md
git commit -m "Add lab member setup guide for individual GitHub clones"
git push origin web-app
```

**Then share with lab members:**
```
"Clone NeuroInsight from GitHub to your own directory:
git clone -b web-app https://github.com/phindagijimana/neuroinsight.git ~/neuroinsight

Then follow OOD_LAB_MEMBER_SETUP.md"
```

---

**This way each person has their own isolated environment!** 🎉

Want me to commit these new user guides to GitHub?

