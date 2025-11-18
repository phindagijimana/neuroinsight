#!/bin/bash
# Post-removal script for NeuroInsight

set -e

# Remove desktop entry
if [ -f "/usr/share/applications/neuroinsight-standalone.desktop" ]; then
    rm -f "/usr/share/applications/neuroinsight-standalone.desktop"
fi

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database
fi

echo "NeuroInsight removal completed successfully!"
