# Simple Linux Testing Commands

**Easy copy-paste commands for testing NeuroInsight on Linux** 🐧

---

## 📥 1. Download & Verify

### Download
```bash
# Download from GitHub Actions
# Go to: https://github.com/phindagijimana/neuroinsight/actions/runs/19284629791
# Scroll down → "Artifacts" → Download neuroinsight-linux
# Or use wget (if you have direct link):
# wget -O neuroinsight-linux.zip "https://github.com/phindagijimana/neuroinsight/actions/artifacts/[ID]/zip"

# Navigate to Downloads
cd ~/Downloads

# Extract
unzip neuroinsight-linux.zip -d neuroinsight-linux
cd neuroinsight-linux
```

### Verify Checksum (IMPORTANT!)
```bash
# Automatic verification
sha256sum -c checksums-linux.txt

# Expected output: NeuroInsight-*.AppImage: OK ✅
```

**If you see "OK" → Safe to install!**  
**If you see "FAILED" → DO NOT run! Re-download.**

### Manual Verification (Alternative)
```bash
# Calculate hash
sha256sum NeuroInsight-*.AppImage

# View expected hash
cat checksums-linux.txt

# Compare - they should match!
```

---

## ⚙️ 2. Make Executable & Run

```bash
# Make executable
chmod +x NeuroInsight-*.AppImage

# Run the app
./NeuroInsight-*.AppImage
```

---

## 🚀 3. Launch App (After First Run)

```bash
# Run from wherever you saved it
./NeuroInsight-*.AppImage

# Or if you moved it to a standard location:
~/Applications/NeuroInsight-*.AppImage
```

---

## ✅ 4. Quick Tests

### Check if Running
```bash
ps aux | grep -i neuroinsight
```

**Expected:** Should show NeuroInsight and neuroinsight-backend processes

### Check Logs (Last 20 Lines)
```bash
tail -20 ~/.config/neuroinsight/logs/neuroinsight.log
```

### Check for Errors
```bash
cat ~/.config/neuroinsight/logs/errors.log
```

### Open Log Folder
```bash
# Navigate to logs
cd ~/.config/neuroinsight/logs/

# List log files
ls -lh

# Or open in file manager
xdg-open ~/.config/neuroinsight/logs/
```

---

## 🔍 5. Verify It's Working

### Check Frontend Loaded
```bash
grep "Loading frontend" ~/.config/neuroinsight/logs/neuroinsight.log | tail -1
```

**Expected:** Should show path ending with `/frontend/index.html` (not `/src/frontend/`)

### Check Backend Started
```bash
grep "Backend" ~/.config/neuroinsight/logs/neuroinsight.log | tail -3
```

**Expected:** Should see "Backend is ready" or "Backend started on port 5000"

### Check for Any Errors
```bash
if [ -s ~/.config/neuroinsight/logs/errors.log ]; then
    echo "❌ Errors found:"
    cat ~/.config/neuroinsight/logs/errors.log
else
    echo "✅ No errors!"
fi
```

---

## 📊 6. System Checks

### Check Available Memory
```bash
free -h | grep Mem
```

**Need:** At least 8 GB free

### Check Disk Space
```bash
df -h ~/.config/neuroinsight/
```

**Need:** At least 10 GB free

### Check App Memory Usage
```bash
ps aux | grep -i neuroinsight | awk '{print $2, $4, $11}'
```

---

## 🛑 7. Stop/Restart

### Stop App
```bash
# Kill all NeuroInsight processes
pkill -f NeuroInsight
pkill -f neuroinsight-backend
```

### Restart App
```bash
./NeuroInsight-*.AppImage
```

---

## 🧪 8. Complete Test (Copy All)

```bash
#!/bin/bash
echo ""
echo "=== NeuroInsight Linux Test ==="
echo ""

# Test 1: Check if AppImage exists
echo "1. Checking installation..."
if [ -f NeuroInsight-*.AppImage ] || [ -f ~/Applications/NeuroInsight-*.AppImage ]; then
    echo "   ✅ AppImage found"
else
    echo "   ❌ AppImage not found"
fi

# Test 2: Check if executable
echo ""
echo "2. Checking if executable..."
if [ -x NeuroInsight-*.AppImage ] || [ -x ~/Applications/NeuroInsight-*.AppImage ]; then
    echo "   ✅ Executable"
else
    echo "   ⚠️  Not executable (run: chmod +x NeuroInsight-*.AppImage)"
fi

# Test 3: Check if running
echo ""
echo "3. Checking if running..."
if ps aux | grep -i "[n]euroinsight" > /dev/null; then
    echo "   ✅ Running"
else
    echo "   ⚠️  Not running"
fi

# Test 4: Check logs
echo ""
echo "4. Checking logs..."
if [ -d ~/.config/neuroinsight/logs/ ]; then
    echo "   ✅ Logs exist"
else
    echo "   ⚠️  No logs (app not run yet?)"
fi

# Test 5: Check for errors
echo ""
echo "5. Checking for errors..."
if [ -f ~/.config/neuroinsight/logs/errors.log ] && [ -s ~/.config/neuroinsight/logs/errors.log ]; then
    echo "   ⚠️  Errors found (check errors.log)"
    echo "   Last error:"
    tail -3 ~/.config/neuroinsight/logs/errors.log
else
    echo "   ✅ No errors"
fi

# Test 6: Check memory
echo ""
echo "6. Checking memory..."
free -h | grep Mem

# Test 7: Check disk
echo ""
echo "7. Checking disk space..."
df -h ~ | tail -1

echo ""
echo "=== Test Complete ==="
echo ""
```

---

## 🗑️ 9. Uninstall (if needed)

```bash
# Remove AppImage
rm NeuroInsight-*.AppImage

# Remove data and logs
rm -rf ~/.config/neuroinsight/

# Remove cache
rm -rf ~/.cache/neuroinsight/
```

---

## 📝 10. Generate Diagnostic Report

```bash
#!/bin/bash
cat << EOF > ~/neuroinsight-diagnostic-report.txt
=== NeuroInsight Diagnostic Report ===
Date: $(date)
OS: $(uname -s) $(uname -r)
Distribution: $(lsb_release -d 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME)

--- Installation ---
AppImage: $(ls -lh NeuroInsight-*.AppImage 2>/dev/null || echo "Not found in current directory")

--- Running Processes ---
$(ps aux | grep -i [n]euroinsight || echo "Not running")

--- Logs Directory ---
$(ls -lh ~/.config/neuroinsight/logs/ 2>/dev/null || echo "No logs")

--- Recent Log (Last 10 lines) ---
$(tail -10 ~/.config/neuroinsight/logs/neuroinsight.log 2>/dev/null || echo "No log file")

--- Errors (Last 5 lines) ---
$(tail -5 ~/.config/neuroinsight/logs/errors.log 2>/dev/null || echo "No errors")

--- System Resources ---
Memory:
$(free -h | grep Mem)

Disk:
$(df -h ~ | tail -1)

=== End Report ===
EOF

echo "Report saved to: ~/neuroinsight-diagnostic-report.txt"
cat ~/neuroinsight-diagnostic-report.txt
```

---

## 🎯 Common Issues & Quick Fixes

### AppImage Won't Run

#### Check FUSE
```bash
# Check if FUSE is available
fusermount --version

# If not installed (Ubuntu/Debian):
sudo apt install fuse libfuse2

# If not installed (Fedora/RHEL):
sudo dnf install fuse fuse-libs

# If not installed (Arch):
sudo pacman -S fuse2
```

#### Extract and Run Manually
```bash
# Extract AppImage
./NeuroInsight-*.AppImage --appimage-extract

# Run from extracted files
./squashfs-root/AppRun
```

---

### Frontend Not Loading (Black Window)

```bash
# Check frontend path in logs
grep "Loading frontend" ~/.config/neuroinsight/logs/neuroinsight.log | tail -1
```

If it shows `/src/frontend/`, download latest version (v1.3.9+)

---

### Backend Won't Start

```bash
# Check if port 5000 is in use
sudo netstat -tulpn | grep 5000

# Or using ss
ss -tulpn | grep 5000

# If something is using it, stop that process
```

---

### Permission Denied

```bash
# Make sure it's executable
chmod +x NeuroInsight-*.AppImage

# Check permissions
ls -lh NeuroInsight-*.AppImage

# Should show: -rwxr-xr-x (executable)
```

---

## 📋 Quick Test Checklist

```bash
cat << 'EOF'
📋 Quick Checklist:
[ ] Downloaded artifact from GitHub Actions
[ ] Extracted zip file
[ ] Verified checksum (sha256sum -c checksums-linux.txt)
[ ] Made AppImage executable (chmod +x)
[ ] AppImage runs without errors
[ ] Main window shows 3 tabs
[ ] Status bar says "Backend: Ready"
[ ] No black/dark window
[ ] Logs accessible (~/.config/neuroinsight/logs/)
[ ] No errors in error log
EOF
```

---

## 🔗 Quick Links

- **Latest Build**: https://github.com/phindagijimana/neuroinsight/actions/runs/19284629791
- **All Actions**: https://github.com/phindagijimana/neuroinsight/actions
- **Releases**: https://github.com/phindagijimana/neuroinsight/releases

---

## 💡 Pro Tips

### Add to Applications Menu
```bash
# Copy to Applications folder
mkdir -p ~/Applications
cp NeuroInsight-*.AppImage ~/Applications/

# Create desktop entry
cat > ~/.local/share/applications/neuroinsight.desktop << 'EOF'
[Desktop Entry]
Name=NeuroInsight
Exec=/home/YOUR_USERNAME/Applications/NeuroInsight-1.3.9.AppImage
Icon=neuroinsight
Type=Application
Categories=Science;Medical;
EOF

# Replace YOUR_USERNAME with your actual username
sed -i "s/YOUR_USERNAME/$USER/" ~/.local/share/applications/neuroinsight.desktop
```

### Run with Debug Output
```bash
# Run and capture all output
./NeuroInsight-*.AppImage 2>&1 | tee ~/neuroinsight-debug.log

# Watch logs in real-time (in another terminal)
tail -f ~/.config/neuroinsight/logs/neuroinsight.log
```

### Monitor Resource Usage
```bash
# Watch memory usage
watch -n 5 'ps aux | grep -i neuroinsight | grep -v grep'

# Or use top
top -p $(pgrep -d',' -f neuroinsight)
```

---

## 🚀 Quick Start (All-in-One)

```bash
# Complete installation and test
cd ~/Downloads/neuroinsight-linux
sha256sum -c checksums-linux.txt && \
chmod +x NeuroInsight-*.AppImage && \
./NeuroInsight-*.AppImage &
sleep 10 && \
ps aux | grep -i [n]euroinsight && \
tail -5 ~/.config/neuroinsight/logs/neuroinsight.log
```

---

**Last Updated**: November 12, 2025  
**Version**: 1.3.9  
**Tested on**: Ubuntu 20.04+, Fedora 35+, Debian 11+

---

**Happy testing! 🐧**


