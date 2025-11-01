# Storage Management & Cleanup

## Overview

The application includes automated storage cleanup to prevent disk space issues and orphaned files. This system manages the lifecycle of uploaded files and processing outputs.

## Configuration

Settings in `.env` or `backend/core/config.py`:

```bash
# Enable/disable automatic cleanup
CLEANUP_ENABLED=true

# How often to run cleanup (in hours)
CLEANUP_INTERVAL_HOURS=24  # Daily

# Retention policies
RETENTION_COMPLETED_DAYS=30   # Keep completed jobs 30 days
RETENTION_FAILED_DAYS=7        # Keep failed jobs 7 days
```

## Automatic Cleanup

### Celery Beat Schedule

The cleanup task runs automatically via Celery Beat:

- **Schedule**: Runs daily by default (`CLEANUP_INTERVAL_HOURS=24`)
- **Task**: `workers.tasks.cleanup.run_cleanup`
- **What it does**:
  1. Deletes old completed jobs (default: 30 days old)
  2. Deletes old failed jobs (default: 7 days old)
  3. Removes orphaned files (files with no database records)

To enable Celery Beat, run:
```bash
celery -A workers.celery_app:celery_app beat
```

## Manual Cleanup

### CLI Tool

Run cleanup manually using the CLI tool:

```bash
# Show what would be deleted (dry run)
python bin/cleanup_storage.py --dry-run

# Clean up only orphaned files
python bin/cleanup_storage.py --orphaned-only

# Clean up old completed jobs only
python bin/cleanup_storage.py --old-completed

# Clean up old failed jobs only
python bin/cleanup_storage.py --old-failed

# Run full cleanup
python bin/cleanup_storage.py

# Custom retention periods
python bin/cleanup_storage.py --completed-days 60 --failed-days 14
```

### API Endpoints

**Get Storage Statistics:**
```bash
GET /cleanup/stats
```

**Run Manual Cleanup:**
```bash
POST /cleanup/run?dry_run=false&orphaned_only=false
```

Parameters:
- `dry_run`: If true, only reports what would be deleted
- `orphaned_only`: Only clean orphaned files
- `old_completed`: Only clean old completed jobs
- `old_failed`: Only clean old failed jobs
- `completed_days`: Override retention for completed jobs
- `failed_days`: Override retention for failed jobs

## Cleanup Behavior

### When Jobs Are Deleted

1. **Job record** removed from database
2. **Associated metrics** removed from database
3. **Uploaded file** deleted from `data/uploads/`
4. **Output directory** deleted from `data/outputs/`

### What Gets Cleaned Up

1. **Old Completed Jobs**: Jobs completed more than `RETENTION_COMPLETED_DAYS` ago
2. **Old Failed Jobs**: Jobs that failed more than `RETENTION_FAILED_DAYS` ago
3. **Orphaned Files**: Files/directories with no corresponding database record

### What Is Preserved

- Currently running jobs
- Recently completed jobs (within retention period)
- Recently failed jobs (within retention period)
- Jobs without completion timestamps (pending/running)

## Best Practices

1. **Monitor Storage**: Check `/cleanup/stats` regularly
2. **Adjust Retention**: Adjust `RETENTION_*_DAYS` based on your needs
3. **Review Before Deletion**: Use `--dry-run` to preview deletions
4. **Keep Celery Beat Running**: For automatic cleanup
5. **Manual Cleanup**: Run cleanup after major changes or issues

## Troubleshooting

**Cleanup not running automatically?**
- Ensure Celery Beat is running: `celery -A workers.celery_app:celery_app beat`
- Check `CLEANUP_ENABLED=true` in configuration

**Storage still growing?**
- Check if Celery Beat is actually running
- Review retention periods (may be too long)
- Run manual cleanup to clear orphaned files

**Want to keep jobs longer?**
- Increase `RETENTION_COMPLETED_DAYS`
- Use `--dry-run` to see what would be deleted before changing




