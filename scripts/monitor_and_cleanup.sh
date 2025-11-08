#!/bin/bash
#
# Monitor and Cleanup Script
# 
# Automatically detects and kills zombie FastSurfer processes.
# Can be run manually or via cron job.
#
# Usage:
#   ./scripts/monitor_and_cleanup.sh          # Kill zombie processes
#   ./scripts/monitor_and_cleanup.sh --dry-run    # Check without killing
#

cd "$(dirname "$0")/.." || exit 1

echo "========================================"
echo "🔍 FastSurfer Zombie Process Monitor"
echo "========================================"
date
echo ""

# Run the cleanup script
python3 scripts/cleanup_zombie_processes.py "$@"

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ Cleanup completed successfully"
else
    echo "❌ Cleanup failed with exit code $exit_code"
fi

exit $exit_code


