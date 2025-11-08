# NeuroInsight Desktop - Logs & Troubleshooting

## 📍 Where Are Logs Stored?

Logs are automatically saved to your local system:

**Linux**: `~/.config/neuroinsight/logs/`

**Full Path Example**:
```
/home/username/.config/neuroinsight/logs/
```

---

## 📂 Log Files

NeuroInsight creates three log files:

### 1. `neuroinsight.log` (Main Log)
- All application events
- Startup/shutdown
- Backend activity
- User actions
- File: Rotates at 10 MB

### 2. `errors.log` (Error Log)
- All errors encountered
- Processing failures
- File format issues
- Memory problems

### 3. `crashes.log` (Crash Log)
- Critical failures only
- Application crashes
- Backend crashes
- System state at crash time

---

## 🔍 Accessing Logs

### Method 1: Through the Application

1. Launch NeuroInsight
2. Go to **Help** → **View Logs** (or press `Ctrl+L` / `Cmd+L`)
3. Log folder opens in your file explorer

### Method 2: Through File Explorer

Navigate to: `~/.config/neuroinsight/logs/`

```bash
# On Linux
cd ~/.config/neuroinsight/logs/
ls -lh
```

### Method 3: Through About Dialog

1. Go to **Help** → **About NeuroInsight**
2. Log path is shown at the bottom

---

## 📖 Reading Logs

Logs are saved in JSON format, one entry per line.

### Example Log Entry

```json
{
  "timestamp": "2025-11-07T18:45:23.456Z",
  "level": "ERROR",
  "message": "Processing failed for job",
  "pid": 12345,
  "data": {
    "jobId": "abc-123",
    "error": {
      "message": "Out of memory",
      "stack": "Error: Out of memory\n    at process..."
    }
  }
}
```

### Log Levels

- `INFO`: Normal operations
- `WARN`: Warnings (not critical)
- `ERROR`: Errors (recoverable)
- `CRASH`: Critical failures (unrecoverable)

---

## 🐛 Reporting Issues

If NeuroInsight crashes or fails, please:

### 1. Locate Your Logs

```bash
cd ~/.config/neuroinsight/logs/
```

### 2. Find the Relevant File

- For crashes: Check `crashes.log`
- For errors: Check `errors.log`
- For general issues: Check `neuroinsight.log`

### 3. Share the Logs

**Option A**: Copy the entire log file

```bash
cat neuroinsight.log
# Copy output and paste in issue report
```

**Option B**: Share the last 50 lines

```bash
tail -n 50 neuroinsight.log
```

**Option C**: Attach log files to email/issue

```bash
# Create a zip file with all logs
cd ~/.config/neuroinsight/
zip -r neuroinsight-logs.zip logs/
```

### 4. Include System Information

When reporting issues, also include:

- **OS**: Linux distribution & version
- **RAM**: Available memory
- **Disk Space**: Free space on drive
- **What you were doing**: Steps to reproduce

---

## 🔧 Common Issues & Solutions

### Issue: "Application won't start"

**Check Logs**:
```bash
cat ~/.config/neuroinsight/logs/crashes.log | tail -n 20
```

**Common Causes**:
- Insufficient disk space (need 10 GB free)
- Insufficient RAM (need 8 GB minimum)
- Port 8000 already in use

**Solutions**:
1. Check disk space: `df -h`
2. Check memory: `free -h`
3. Check port: `lsof -i :8000`

---

### Issue: "Processing fails"

**Check Logs**:
```bash
cat ~/.config/neuroinsight/logs/errors.log | grep -i "processing"
```

**Common Causes**:
- Invalid MRI file format
- Corrupted scan data
- Out of memory during processing

**Solutions**:
1. Verify file is T1-weighted MRI (.nii or .nii.gz)
2. Check file size is reasonable (< 500 MB)
3. Ensure 8+ GB RAM available

---

### Issue: "Backend crashed"

**Check Logs**:
```bash
cat ~/.config/neuroinsight/logs/crashes.log | grep -i "backend"
```

**Common Causes**:
- Out of memory
- Corrupted FastSurfer models
- GPU driver issues (if using GPU)

**Solutions**:
1. Restart application
2. Close other memory-intensive applications
3. Try processing with CPU only

---

## 🗑️ Clearing Logs

### Method 1: Through Application

1. Go to **Help** → **Clear Logs**
2. Confirm deletion
3. Logs are cleared (fresh start)

### Method 2: Manual Deletion

```bash
rm ~/.config/neuroinsight/logs/*.log
rm ~/.config/neuroinsight/logs/*.log.old
```

---

## 📊 Log Rotation

Logs automatically rotate when they reach 10 MB:

- Current log: `neuroinsight.log`
- Old log: `neuroinsight.log.old`

When `neuroinsight.log` reaches 10 MB:
1. `neuroinsight.log.old` is deleted (if exists)
2. `neuroinsight.log` → `neuroinsight.log.old`
3. New `neuroinsight.log` is created

**Why?** Prevents logs from consuming too much disk space.

---

## 🔒 Privacy

**All logs are stored locally on your computer.**

- No data is sent to external servers
- No telemetry or analytics
- Logs contain only operational data
- You can delete logs anytime

---

## 💡 Tips

### 1. Check Logs After Every Crash

Get in the habit of checking logs immediately after a crash:

```bash
cat ~/.config/neuroinsight/logs/crashes.log | tail -n 50
```

### 2. Keep Recent Logs

Before clearing logs, save any that might be useful:

```bash
cp ~/.config/neuroinsight/logs/errors.log ~/Desktop/errors-backup.log
```

### 3. Monitor Log Size

Check log size occasionally:

```bash
du -h ~/.config/neuroinsight/logs/
```

### 4. Search for Specific Errors

Use `grep` to find specific issues:

```bash
# Find all memory errors
grep -i "memory" ~/.config/neuroinsight/logs/errors.log

# Find all processing errors
grep -i "processing" ~/.config/neuroinsight/logs/errors.log

# Find errors from today
grep "2025-11-07" ~/.config/neuroinsight/logs/errors.log
```

---

## 📞 Getting Support

If you encounter issues:

1. **Check logs** first
2. **Try common solutions** above
3. **Report issue** with logs attached

**Contact**:
- GitHub Issues: [repository-url]
- Email: [support-email]

**Include in your report**:
- Log files (especially `crashes.log` or `errors.log`)
- System information
- Steps to reproduce
- Expected vs actual behavior

---

## ✅ Verification

To verify logging is working:

1. Launch NeuroInsight
2. Go to **Help** → **View Logs**
3. Open `neuroinsight.log`
4. Should see recent entries with timestamps

**Example**:
```json
{"timestamp":"2025-11-07T18:45:00.000Z","level":"INFO","message":"Application started",...}
```

If you see entries, logging is working! ✅

---

**Last Updated**: November 7, 2025  
**Version**: 1.1.0

