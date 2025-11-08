# NeuroInsight on Open OnDemand - Simple User Guide

## 🎯 What This Does

Run NeuroInsight from **any computer** using your web browser - no installation, no Docker, no technical setup!

**All processing happens on HPC** (fast, plenty of RAM, no ARM issues).

---

## 🚀 For Users: How to Access NeuroInsight

### Step 1: Go to Open OnDemand

```
https://ondemand.urmc.rochester.edu
```

Login with your URMC username and password.

### Step 2: Launch an Interactive Desktop

1. Click **"Interactive Apps"** in the top menu
2. Click **"Interactive Desktop"** (or "Remote Desktop", "VNC Desktop")
3. Fill in the form:
   - **Number of hours:** 4 (enough for several scans)
   - **Memory (GB):** 20 (required for processing)
   - **Number of cores:** 4-8
   - **Partition:** interactive (or your default queue)
4. Click **"Launch"**

**Wait 1-2 minutes** for the session to start.

### Step 3: Connect to Desktop

When the card says "Running":
1. Click **"Launch Interactive Desktop"** button
2. A desktop environment opens in your browser

### Step 4: Start NeuroInsight

**In the desktop that just opened:**

1. **Find and open a Terminal** 
   - Look for terminal icon in the taskbar
   - Or right-click desktop → "Open Terminal"

2. **Type these commands:**
   ```bash
   cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
   bash RUN_ALL.sh
   ```

3. **Wait ~30 seconds** for services to start

4. **Open a web browser in the desktop:**
   - Look for Firefox or Chrome icon
   - Or in terminal type: `firefox http://localhost:8000`

5. **NeuroInsight loads!** 🎉

### Step 5: Use NeuroInsight

Now you can:
- Upload MRI scans
- Monitor processing (40-60 minutes per scan)
- View results
- Download data

**Keep the OOD session open** while processing!

### Step 6: When Done

1. Download any results you need
2. Close the browser in OOD desktop
3. Go back to OOD portal
4. Click "My Interactive Sessions"
5. Click "Delete" on your session to free resources

---

## 📋 Visual Guide

```
Your Computer (any device)
    ↓ Browser
https://ondemand.urmc.rochester.edu
    ↓ Login
Interactive Apps → Desktop
    ↓ Launch (Memory: 20GB)
Desktop opens in browser
    ↓ Terminal
cd /mnt/nfs/.../hippo && bash RUN_ALL.sh
    ↓ Firefox in desktop
http://localhost:8000
    ↓
NeuroInsight running!
```

---

## 💡 Key Advantages

✅ **No local installation** - Everything in browser  
✅ **Any device works** - Even tablets/Chromebooks  
✅ **HPC resources** - 20GB RAM, fast x86_64 processors  
✅ **No platform issues** - No ARM64/Mac problems  
✅ **University login** - Automatic authentication  
✅ **Available NOW** - No IT approval needed  

---

## 🔧 Troubleshooting

### Can't find "Interactive Desktop"?

**Your OOD might call it:**
- "Remote Desktop"
- "VNC Desktop"  
- "Linux Desktop"
- "Xfce Desktop"

**Look under "Interactive Apps" menu.**

### Desktop session fails to start?

**Check:**
- Resources available? (20GB might be high, try 16GB)
- Right partition selected?
- Job limits not exceeded?

**View job details:**
- Click session card
- Check error messages
- Adjust resources and retry

### NeuroInsight won't start in desktop?

**Check the path:**
```bash
# Make sure you're in the right directory
pwd
# Should show: /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo

# Check services
bash RUN_ALL.sh --status
```

### Browser won't open localhost:8000?

**Try:**
```bash
# In OOD desktop terminal
firefox http://localhost:8000 &

# Or check if backend is running
curl http://localhost:8000
```

---

## 👥 Sharing with Lab Members

### Simple Instructions for Users:

**Email them this:**

```
Hi team,

To use NeuroInsight for hippocampal analysis:

1. Go to: https://ondemand.urmc.rochester.edu
2. Interactive Apps → Interactive Desktop
3. Memory: 20 GB, Cores: 4, Hours: 4
4. Click Launch and wait for desktop to start
5. In the desktop, open Terminal and run:
   
   cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
   bash RUN_ALL.sh

6. Open Firefox and go to: http://localhost:8000

7. Upload your MRI scans and start processing!

Processing takes ~45-60 minutes per scan.

Questions? Reply to this email.
```

---

## ⏱️ Session Management

### How Long Should Users Request?

**For uploading only:**
- 1 hour (just to queue jobs)

**For processing 1-2 scans:**
- 4 hours

**For processing 5+ scans:**
- 8-12 hours (or overnight)

**For batch processing:**
- 24 hours (process many scans)

### Can Multiple Users Run Simultaneously?

**Yes!** Each user gets their own:
- OOD desktop session
- NeuroInsight instance
- Processing queue

**But note:**
- All users share the same database
- All users see all jobs (for now)
- One scan processes at a time per instance

---

## 🆚 Comparison

### This Method (OOD Desktop) vs Local Install:

| Aspect | Local PC | OOD Desktop |
|--------|----------|-------------|
| **Setup** | Install Docker, hours | Click "Launch", 2 min |
| **Works From** | That computer only | Any device, anywhere |
| **RAM Needed** | 16-20GB on YOUR PC | 0GB local, uses HPC |
| **CPU** | Your CPU (might be slow) | HPC CPUs (fast) |
| **Platform Issues** | ARM64 problems | None (HPC is x86_64) |
| **Processing Speed** | Varies | Consistent (HPC) |
| **Storage** | Your disk | HPC storage |
| **Available** | After setup | Immediately |

**Winner:** OOD Desktop for most users! ⭐

---

## 🔮 Future: Custom OOD App Integration

Eventually, you can request IT to make it even easier:

**Current (OOD Desktop method):**
```
1. Launch desktop
2. Open terminal
3. Run commands
4. Open browser
5. Use NeuroInsight
```

**Future (Custom OOD App):**
```
1. Click "NeuroInsight"
2. Click "Launch"
3. Use NeuroInsight
```

**But the desktop method works perfectly RIGHT NOW!**

---

## ✅ Action Items

### For You (Today):

```bash
# 1. Try it yourself
# Go to: https://ondemand.urmc.rochester.edu
# Launch Interactive Desktop
# Test NeuroInsight

# 2. If it works, document the exact steps
# Note which desktop option works
# Note any special settings needed

# 3. Share with one colleague as pilot test
```

### For Your Lab (This Week):

```bash
# 1. Create simple guide based on your test
# 2. Email lab members with instructions
# 3. Offer to help first few users
# 4. Gather feedback
```

### Optional (Next Month):

```bash
# 1. Email IT for custom OOD integration
# 2. Makes it even easier for users
# 3. More professional presentation
```

---

## 🎉 Summary

**YES!** You can run the current GitHub web app on Open OnDemand **RIGHT NOW** without any integration!

**How:**
- Use OOD's Interactive Desktop
- Run startup commands in terminal
- Access via browser in desktop
- Everything runs on HPC (no local issues!)

**Benefits:**
- ✅ No local installation
- ✅ No RAM problems
- ✅ No ARM64 issues
- ✅ Works from any device
- ✅ Available immediately

**Try it now:** `https://ondemand.urmc.rochester.edu` → Interactive Desktop → Launch! 🚀


