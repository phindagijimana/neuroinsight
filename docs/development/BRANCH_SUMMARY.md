# NeuroInsight Repository Branches

## Active Branches

### web-app (Main Production)
**Purpose:** Docker-based deployment for HPC and servers  
**Status:** Production ready, actively used  
**Access:** SSH tunnel or Docker Compose  
**Target:** Researchers, HPC users, developers

### desktop-standalone (New)
**Purpose:** Standalone desktop application development  
**Status:** Initial setup complete, development starting  
**Target:** Clinical users, end-users, non-technical users  
**Directory:** `desktop_alone/`

### desktop-app (Legacy)
**Purpose:** Docker manager Electron app  
**Status:** Superseded by desktop-standalone  
**Note:** Old approach, new standalone is better

---

## Which Branch to Use?

**For current production use:** `web-app`

**For standalone app development:** `desktop-standalone`

**For contributing to either:** Choose appropriate branch

---

## Repository Overview

**Main codebase:** ~50,000 lines (backend, frontend, pipeline)  
**Standalone additions:** ~1,000 lines (config, Electron, build)  
**Code reuse:** 85-90% between versions

**Both versions share:** Pipeline processing, Frontend UI, Core algorithms

