# Making NeuroInsight URL More Professional

## Problem
`http://localhost:3000` doesn't look professional for a research tool.

## Solutions (Choose One)

---

### ✅ **Solution 1: Custom Local Domain** (Recommended)

Access NeuroInsight as **`http://neuroinsight.local`** instead of `localhost:3000`

#### macOS/Linux Setup:

```bash
# Add to /etc/hosts
echo "127.0.0.1 neuroinsight.local" | sudo tee -a /etc/hosts

# Now you can use:
http://neuroinsight.local:3000
```

#### Windows Setup:

1. Open Notepad as Administrator
2. Open: `C:\Windows\System32\drivers\etc\hosts`
3. Add line: `127.0.0.1 neuroinsight.local`
4. Save
5. Access: `http://neuroinsight.local:3000`

---

### ⭐ **Solution 2: Remove Port Number** (Even Better!)

Make it just **`http://neuroinsight.local`** (no :3000)

#### Step 1: Update docker-compose.yml

Change frontend ports from `3000:3000` to `80:80`:

```yaml
frontend:
  ports:
    - "80:80"  # Instead of "3000:3000"
```

#### Step 2: Add to hosts file (as above)

```bash
echo "127.0.0.1 neuroinsight.local" | sudo tee -a /etc/hosts
```

#### Step 3: Access

Now just: **`http://neuroinsight.local`**

**Looks like a real website!** ✨

---

### 🚀 **Solution 3: Desktop App with Custom Protocol**

Ultimate professional solution (future v2.0)

**Appearance:** `neuroinsight://` protocol, no browser at all

**Examples:**
- 3D Slicer (double-click icon)
- ITK-SNAP (desktop app)
- FreeSurfer GUI (desktop app)

**Status:** Requires standalone migration (see desktop-app branch)

**Timeline:** 3-4 weeks development

---

### 📱 **Solution 4: Browser Extension**

Make `localhost` appear as custom name in browser only

**Localhost Renamer** extension:
- Chrome/Edge: Search "Localhost Name Resolver"
- Shows "NeuroInsight" instead of "localhost:3000" in tab

**Pros:** Easy, no code changes
**Cons:** Only cosmetic, URL bar still shows localhost

---

## Comparison

| Solution | URL | Setup Time | Professional Look |
|----------|-----|------------|-------------------|
| **localhost:3000** | http://localhost:3000 | 0 min | ⭐ |
| **Custom domain + port** | http://neuroinsight.local:3000 | 1 min | ⭐⭐⭐ |
| **Custom domain (port 80)** | http://neuroinsight.local | 2 min | ⭐⭐⭐⭐ |
| **Desktop app** | No URL (app icon) | 3-4 weeks | ⭐⭐⭐⭐⭐ |

---

## What Other Tools Actually Use

### Tools WITHOUT Web UIs (Command-Line):
- **fMRIPrep**: No web server (generates HTML reports you open as files)
- **MRIQC**: No web server (generates HTML reports)
- **FSL**: No web server (desktop GUI apps)
- **FreeSurfer**: No web server (desktop GUI apps)

### Tools WITH Web UIs (Use localhost):
- **Jupyter**: `localhost:8888` (everyone accepts this)
- **Tensorboard**: `localhost:6006`
- **MLflow**: `localhost:5000`
- **Airflow**: `localhost:8080`

**Key insight:** Professional appearance comes from the **interface quality**, not the URL.

### Tools WITH Custom Domains:
- **3D Slicer**: Desktop app (no URL)
- **Horos** (medical imaging): Desktop app (no URL)
- **OsiriX**: Desktop app (no URL)

---

## Recommendation for Your Paper

### For Research Publication (Now):

**Use:** `localhost:3000` or `neuroinsight.local:3000`

**Why:**
- Standard approach (Jupyter, MLflow, etc.)
- Reviewers familiar with this
- No one cares about URL for research tools
- Focus on functionality

**In Methods Section:**
```
"NeuroInsight is accessed via web browser at http://localhost:3000
following docker-compose startup, consistent with standard containerized
research tools (e.g., Jupyter, MLflow)."
```

### For Clinical Deployment (v2.0):

**Use:** Desktop app (no URL)

**Why:**
- Clinical users expect desktop apps
- No "localhost" confusion
- Professional appearance
- Double-click to launch

**Timeline:** 3-4 weeks (standalone migration)

---

## Quick Implementation (2 minutes)

Want `http://neuroinsight.local` right now?

### On macOS:

```bash
# 1. Add to hosts file
echo "127.0.0.1 neuroinsight.local" | sudo tee -a /etc/hosts

# 2. Restart services
cd ~/Downloads/neuroinsight-web-app
docker-compose restart

# 3. Access at:
open http://neuroinsight.local:3000
```

### To Remove Port (Make it just `neuroinsight.local`):

```bash
# Edit docker-compose.yml
# Change frontend ports to "80:80"

# Restart
docker-compose down
docker-compose up -d

# Access at:
open http://neuroinsight.local
```

---

## For Presentations/Demos

If presenting to clinicians or non-technical audience:

**Option A: Full-Screen Browser**
- Press F11 in browser
- Hides URL bar completely
- Looks like desktop app

**Option B: Browser App Mode** (Chrome/Edge)
```bash
# Create desktop shortcut that opens in app mode
# On macOS:
open -na "Google Chrome" --args --app=http://neuroinsight.local:3000
```

This opens NeuroInsight in a chromeless window (no URL bar, looks like desktop app)

---

## Summary

**Current:** `localhost:3000` (fine for research)
**Easy upgrade:** `neuroinsight.local` (2 min setup)
**Pro upgrade:** `neuroinsight.local` without port (5 min setup)
**Future:** Desktop app (3-4 weeks)

**My recommendation:** Use `neuroinsight.local` for nice middle ground.

---

*Last updated: November 2025*
