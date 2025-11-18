#!/bin/bash

# Script to delete old GitHub Actions workflow runs except v15
# Requires GitHub CLI (gh) to be installed and authenticated

set -e

echo "🧹 Deleting old GitHub Actions workflow runs (keeping v15)..."

# Get all workflow runs for Desktop Nightly Validation workflows
echo "📋 Finding workflow runs to delete..."

# Delete runs that contain "Desktop Nightly Validation" but don't contain "v15"
gh run list --limit 100 --json databaseId,name,workflowName,status | \
  jq -r '.[] | select(.workflowName | contains("Desktop Nightly Validation")) | select(.name | contains("v15") | not) | select(.status == "completed") | .databaseId' | \
  while read -r run_id; do
    if [ -n "$run_id" ]; then
      echo "🗑️ Deleting completed run ID: $run_id"
      gh run delete "$run_id"
    fi
  done

echo "✅ Cleanup complete! Only v15 runs remain."
