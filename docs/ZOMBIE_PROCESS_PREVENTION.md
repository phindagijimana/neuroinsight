# Zombie Process Prevention Guide

## Problem

When FastSurfer jobs run via Singularity/Apptainer, the Python subprocess can fail or be marked complete while the actual FastSurfer process continues running in the background. These "zombie" processes consume significant resources (CPU and RAM) and can block new jobs from processing.

## Root Cause

The issue occurs when:
1. `subprocess.run()` is used without process group management
2. Parent process dies or returns early
3. Child processes (Singularity → FastSurfer → Python model) are not properly tracked
4. No cleanup mechanism exists to kill orphaned processes

## Solution

### 1. Process Group Management

**File: `pipeline/processors/mri_processor.py`**

Changed from:
```python
result = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
```

To:
```python
process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    preexec_fn=os.setsid,  # Create new process group
)
```

This creates a new process group that can be killed as a unit using `os.killpg()`.

### 2. PID Tracking

Each FastSurfer process now:
- Stores its PID in a `.process_pid` file in the job output directory
- Logs the PID and process group ID (PGID)
- Cleans up the PID file on completion

### 3. Proper Cleanup

The code now handles cleanup in multiple scenarios:
- **Normal completion**: PID file is removed
- **Timeout**: Process group is killed with SIGTERM, then SIGKILL if needed
- **Error/exception**: Process group is force-killed in finally block

### 4. Monitoring Script

**File: `scripts/cleanup_zombie_processes.py`**

Automatically detects and kills zombie processes by:
1. Scanning for running FastSurfer processes
2. Extracting job IDs from command lines
3. Checking job status in database
4. Killing processes for completed/failed/cancelled jobs

**Usage:**
```bash
# Check for zombies without killing (dry run)
python3 scripts/cleanup_zombie_processes.py --dry-run

# Kill zombie processes for completed jobs
python3 scripts/cleanup_zombie_processes.py

# Kill ALL FastSurfer processes
python3 scripts/cleanup_zombie_processes.py --kill-all
```

**Shell wrapper:**
```bash
# Run monitoring and cleanup
./scripts/monitor_and_cleanup.sh

# Dry run
./scripts/monitor_and_cleanup.sh --dry-run
```

## Prevention Strategies

### Manual Cleanup (As Needed)

When you notice high CPU/memory usage or multiple jobs stuck:

```bash
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
./scripts/monitor_and_cleanup.sh
```

### Automated Cleanup (Recommended)

Set up a cron job to run cleanup periodically:

```bash
# Edit crontab
crontab -e

# Add this line to run every 30 minutes
*/30 * * * * /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo/scripts/monitor_and_cleanup.sh >> /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo/logs/zombie_cleanup.log 2>&1
```

### Monitoring System Resources

Check for zombie processes:
```bash
# List FastSurfer processes
ps aux | grep -E "FastSurferCNN|fastsurfer"

# Check memory usage
free -h

# Check CPU usage
top -bn1 | head -20
```

## Testing the Fix

After implementing these changes:

1. **Start fresh services:**
   ```bash
   cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
   ./restart_services.sh all
   ```

2. **Upload a test MRI scan**

3. **Monitor the process:**
   ```bash
   # Watch for PID file creation
   ls -la data/outputs/*/. process_pid
   
   # Check worker logs
   tail -f logs/worker.out
   ```

4. **Verify cleanup:**
   - Process should complete normally
   - PID file should be deleted
   - No zombie processes should remain

5. **Test forced cleanup:**
   ```bash
   # Check for any zombies
   ./scripts/monitor_and_cleanup.sh --dry-run
   ```

## Benefits

### Before Fix
- ❌ Zombie processes consumed 25+ GB RAM
- ❌ Multiple CPU cores blocked
- ❌ New jobs couldn't start
- ❌ Manual `pkill` required
- ❌ No tracking of running processes

### After Fix
- ✅ Process groups properly managed
- ✅ Automatic cleanup on error/timeout
- ✅ PID tracking for monitoring
- ✅ Automated zombie detection
- ✅ Graceful SIGTERM before SIGKILL
- ✅ Resources freed immediately

## Technical Details

### Process Group Structure

```
Celery Worker (parent)
  └─ Python MRI Processor
      └─ Singularity/Apptainer (process group leader)
          └─ FastSurfer container
              └─ Python neural network processes
```

With `preexec_fn=os.setsid`:
- Singularity becomes process group leader
- All child processes share the same PGID
- `os.killpg(pgid, signal)` kills entire tree

### Signal Handling

1. **SIGTERM** (graceful, 2-second grace period)
   - Allows processes to cleanup
   - Save partial results if possible

2. **SIGKILL** (force, immediate)
   - Used if SIGTERM didn't work
   - Guaranteed to kill process

### Error Recovery

If process cleanup fails:
1. Logged as error
2. Job marked as failed
3. Monitoring script will catch it next run
4. User can manually run cleanup

## Troubleshooting

### Zombies Still Present After Cleanup?

```bash
# Check if processes are truly orphaned
ps -ef | grep FastSurfer

# Force kill by PID
kill -9 <PID>

# Or use the nuclear option
pkill -9 -f "FastSurferCNN"
```

### Cleanup Script Not Working?

```bash
# Run with verbose logging
python3 scripts/cleanup_zombie_processes.py --dry-run

# Check database connection
python3 -c "from backend.core.database import SessionLocal; db = SessionLocal(); print('DB OK')"

# Check permissions
ls -la scripts/cleanup_zombie_processes.py
```

### Process Group Not Created?

On some systems, `os.setsid()` might fail. Check:
```bash
# Verify process groups
ps -eo pid,pgid,cmd | grep FastSurfer

# All processes should have same PGID as parent
```

## Future Improvements

1. **Job-level PID storage**: Store PID in database Job model
2. **Real-time monitoring**: WebSocket updates for job process status
3. **Resource limits**: Use cgroups to limit CPU/memory per job
4. **Queue management**: Limit concurrent FastSurfer jobs to prevent OOM
5. **Health checks**: Periodic checks that running jobs are still active

## Related Files

- `pipeline/processors/mri_processor.py` - Main processing logic with fixes
- `scripts/cleanup_zombie_processes.py` - Zombie detection and cleanup
- `scripts/monitor_and_cleanup.sh` - Shell wrapper for cron jobs
- `workers/tasks/processing.py` - Celery task orchestration

## References

- Python subprocess documentation: https://docs.python.org/3/library/subprocess.html
- Process groups: `man 2 setpgid`
- Signals: `man 7 signal`
- Singularity process management: https://sylabs.io/docs/


