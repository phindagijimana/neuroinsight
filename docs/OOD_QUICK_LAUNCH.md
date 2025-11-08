# Launch NeuroInsight on Open OnDemand (Without Custom Integration)

## 🎯 Quick Method - Use OOD's Built-in Apps

You can run NeuroInsight RIGHT NOW using Open OnDemand's existing interactive apps - no IT approval needed!

---

## Method 1: Interactive Desktop Session (Best for Users) ⭐

### Step 1: Login to Open OnDemand

```
https://ondemand.urmc.rochester.edu
```
(Login with your university credentials)

### Step 2: Launch Interactive Desktop

1. Click **"Interactive Apps"** in the menu
2. Select **"Interactive Desktop"** (or "Remote Desktop")
3. Configure resources:
   - **Hours:** 4
   - **Memory:** 20 GB (minimum for processing)
   - **Cores:** 4-8
   - **Partition:** interactive (or default)
4. Click **"Launch"**
5. Wait ~1-2 minutes for session to start
6. Click **"Launch Interactive Desktop"** button

### Step 3: Start NeuroInsight in the Desktop

**In the OOD desktop that opens:**

1. **Open Terminal** (usually icon at bottom)

2. **Navigate to NeuroInsight:**
   ```bash
   cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
   ```

3. **Start services:**
   ```bash
   bash RUN_ALL.sh
   ```

4. **Open Firefox/Browser** (should be available in desktop)

5. **Go to:**
   ```
   http://localhost:8000
   ```

6. **Use NeuroInsight!** Upload scans, process, download results

### Step 4: When Done

- Close browser
- End OOD session from OOD portal
- Resources automatically freed

---

## Method 2: OOD Terminal Session (Simpler, Less Visual)

### Step 1: Launch Terminal in OOD

1. Login to Open OnDemand
2. Click **"Clusters"** → **"Shell Access"**
3. Or use **"Interactive Apps"** → **"Terminal"** (if available)

### Step 2: Start NeuroInsight

```bash
# Navigate to app
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo

# Start services
bash RUN_ALL.sh

# The terminal shows you the URL
# But you need to access it via port forwarding...
```

### Step 3: Access via Port Forward

**This still requires SSH tunnel from your computer:**

```bash
# On your local computer
ssh -L 8000:compute-node:8000 your_username@urmc-sh.rochester.edu
```

**Then open:** `http://localhost:8000`

**Limitation:** Still needs SSH tunnel (Method 1 is better)

---

## Method 3: Jupyter Notebook in OOD (Creative Approach)

If OOD has Jupyter, you can use it to launch NeuroInsight!

### Step 1: Launch Jupyter

1. Login to OOD
2. Interactive Apps → Jupyter Notebook
3. Configure: 20GB RAM, 4 cores, 4 hours
4. Launch and connect

### Step 2: Open Terminal in Jupyter

1. In Jupyter, click **"New"** → **"Terminal"**

2. Navigate and start:
   ```bash
   cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
   bash RUN_ALL.sh
   ```

### Step 3: Access NeuroInsight

**Option A: Port forwarding from Jupyter**

Create a new notebook cell:
```python
# Cell 1: Display link
from IPython.display import HTML, display

port = 8000
html = f'<a href="http://localhost:{port}" target="_blank">Open NeuroInsight</a>'
display(HTML(html))
```

Click the link - might open NeuroInsight!

**Option B: Use Jupyter's proxy** (if configured)

```
http://jupyter-session-url/proxy/8000/
```

---

## 🎯 Recommended Approach

### For You (Testing/Development):

**Use Method 1 - Interactive Desktop:**
- Full GUI environment
- Can see browser directly
- Most intuitive
- No port forwarding needed

### For Lab Members:

**Short-term (This Week):**
- Share SSH tunnel instructions (`docs/LAB_ACCESS_GUIDE.md`)
- Or guide them through OOD Interactive Desktop method

**Long-term (Next Month):**
- Request proper OOD app integration
- Much cleaner and professional

---

## 📋 Step-by-Step: Try It Right Now

### Test Interactive Desktop Method Yourself:

**1. Go to URMC Open OnDemand:**
```
https://ondemand.urmc.rochester.edu
```

**2. Find Interactive Desktop:**
- Look for "Interactive Apps" or "Interactive Sessions"
- Look for "Desktop", "Remote Desktop", or "VNC"

**3. Launch with these settings:**
```
Duration: 4 hours
Memory: 20 GB
CPU Cores: 4
Partition: interactive
```

**4. Once desktop loads:**
```bash
# In the terminal
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
bash RUN_ALL.sh

# In the browser (Firefox or Chrome in the desktop)
http://localhost:8000
```

**5. It should just work!** ✅

---

## 🚀 User Guide for Lab Members

Create this simple guide:

```markdown
# Accessing NeuroInsight via Open OnDemand

## Quick Start (5 minutes)

1. **Login:** https://ondemand.urmc.rochester.edu

2. **Launch Desktop:**
   - Interactive Apps → Interactive Desktop
   - Memory: 20 GB
   - Hours: 4
   - Click "Launch"

3. **Wait:** ~1 minute for desktop to start

4. **Connect:** Click "Launch Interactive Desktop"

5. **In the desktop, open Terminal and run:**
   ```bash
   cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
   bash RUN_ALL.sh
   ```

6. **Open Firefox in the desktop, go to:**
   ```
   http://localhost:8000
   ```

7. **Upload and process your MRI scans!**

**Note:** Keep the OOD session active while processing. 
Session will auto-terminate after selected hours.
```

---

## 📊 Comparison

| Aspect | Current GitHub Method | OOD Interactive Desktop | Custom OOD App |
|--------|----------------------|------------------------|----------------|
| **Setup Time** | Hours (install Docker) | Minutes | Weeks (IT approval) |
| **User Ease** | Hard (technical) | Medium (click & terminal) | Easy (just click) |
| **Works From** | Local computer only | Any browser | Any browser |
| **RAM Needed** | User's computer | HPC resources | HPC resources |
| **Availability** | **Now** | **Now** | 1-2 weeks (needs IT) |
| **Platform Issues** | ARM64 problems | None (HPC is x86_64) | None |

---

## ✅ **My Recommendation:**

### **Immediate (Today):**

**Use OOD Interactive Desktop** - No IT approval needed!

1. Test it yourself right now
2. If it works, share instructions with lab
3. Users can start using it today

### **Long Term (This Month):**

**Request custom OOD app integration:**
- Even easier for users (one click)
- More professional
- Better resource management
- But takes 1-2 weeks to set up

---

## 🎯 **Action Plan:**

### **Right Now (15 minutes):**

```bash
# Commit the OOD documentation
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
git add docs/OPEN_ONDEMAND_SETUP.md docs/OOD_QUICK_LAUNCH.md REQUEST_OOD_INTEGRATION.md
git commit -m "Add Open OnDemand launch documentation"
git push origin web-app

# Test it yourself
# Go to: https://ondemand.urmc.rochester.edu
# Launch Interactive Desktop
# Follow steps above
```

### **This Week:**

1. ✅ Test OOD Desktop method
2. ✅ Share with 1-2 colleagues
3. ✅ Email IT about custom integration (optional)

---

## 🎉 **Summary:**

**Question:** *"Can I run the GitHub web app on OOD without custom integration?"*

**Answer:** **YES!** Use OOD's Interactive Desktop:
- ✅ Available now (no IT needed)
- ✅ Works with current GitHub code
- ✅ No modifications needed
- ✅ Users launch desktop, run terminal commands
- ✅ Access NeuroInsight in OOD's browser

**Even better:**
- All processing on HPC (x86_64, plenty of RAM)
- No local computer limitations
- Works from any device

**Try it right now at: `https://ondemand.urmc.rochester.edu`** 🚀

Let me know if you successfully launch it via OOD Interactive Desktop!
