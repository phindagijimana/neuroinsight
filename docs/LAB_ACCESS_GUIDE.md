# NeuroInsight - Lab Member Access Guide

## Quick Access (SSH Tunnel Method)

### For macOS/Linux Users:

**Step 1: Open Terminal**

**Step 2: Run this command:**
```bash
ssh -L 8000:localhost:8000 YOUR_USERNAME@urmc-sh.rochester.edu

# Replace YOUR_USERNAME with your HPC username
# Example: ssh -L 8000:localhost:8000 jdoe@urmc-sh.rochester.edu
```

**Step 3: Enter your HPC password when prompted**

**Step 4: Open your web browser and go to:**
```
http://localhost:8000
```

**Step 5: Start using NeuroInsight!**
- Upload MRI scans
- Monitor processing
- Download results

---

### For Windows Users:

**Option A: Using PowerShell (Windows 10+)**
1. Open PowerShell
2. Run:
   ```powershell
   ssh -L 8000:localhost:8000 YOUR_USERNAME@urmc-sh.rochester.edu
   ```
3. Open browser to: `http://localhost:8000`

**Option B: Using PuTTY**
1. Download PuTTY: https://www.putty.org/
2. Open PuTTY
3. Configure:
   - **Host Name:** `urmc-sh.rochester.edu`
   - **Port:** 22
   - **Connection → SSH → Tunnels:**
     - Source port: `8000`
     - Destination: `localhost:8000`
     - Click "Add"
4. Click "Open"
5. Login with your HPC credentials
6. Open browser to: `http://localhost:8000`

---

## Troubleshooting

### "Connection refused"
- Make sure NeuroInsight is running on the HPC server
- Contact admin if server is down

### "Port already in use"
- Close other SSH tunnels
- Or use a different port: `-L 8001:localhost:8000` and access `http://localhost:8001`

### "Permission denied"
- Check your HPC username and password
- Make sure you have HPC access

### Can't see the app
- Verify the tunnel is active (keep SSH terminal open)
- Check you're going to `http://localhost:8000` (not https)
- Try refreshing the page

---

## Tips

- **Keep SSH terminal open** while using the app
- **Don't close the terminal** or connection will drop
- **Processing takes time**: 40-60 minutes per scan (CPU mode)
- **Jobs are shared**: All lab members see all jobs (for now)

---

## Getting Help

- **Technical issues:** Contact pndagiji@rochester.edu
- **HPC access:** Contact your IT department
- **Questions:** Check the User Guide at the bottom of the web interface

---

## Advanced: Create a Shortcut (Optional)

### macOS/Linux - Create alias:
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
alias neuroinsight='ssh -L 8000:localhost:8000 YOUR_USERNAME@urmc-sh.rochester.edu'
```

Then just type: `neuroinsight` to connect!

### Windows - Create batch file:
Create `neuroinsight.bat`:
```batch
@echo off
ssh -L 8000:localhost:8000 YOUR_USERNAME@urmc-sh.rochester.edu
pause
```

Double-click to run!


