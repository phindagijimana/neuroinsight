#!/usr/bin/env python3
"""
Script to automatically delete old GitHub Actions workflow runs except v15.
Requires GitHub CLI (gh) to be installed and authenticated.
"""

import subprocess
import json
import sys

def run_command(cmd):
    """Run a command and return its output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def main():
    print("🧹 Deleting old GitHub Actions workflow runs (keeping v15)...")
    
    # Get all workflow runs for Desktop Nightly Validation
    print("📋 Finding workflow runs to delete...")
    
    returncode, stdout, stderr = run_command(
        'gh run list --workflow="Desktop Nightly Validation" --limit 100 --json databaseId,name,headBranch'
    )
    
    if returncode != 0:
        print(f"❌ Error getting workflow runs: {stderr}")
        sys.exit(1)
    
    try:
        runs = json.loads(stdout)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        sys.exit(1)
    
    deleted_count = 0
    
    for run in runs:
        run_name = run.get('name', '')
        run_id = run.get('databaseId')
        
        # Skip if it's a v15 run
        if 'v15' in run_name:
            print(f"⏭️ Skipping v15 run: {run_name}")
            continue
        
        if run_id:
            print(f"🗑️ Deleting run: {run_name} (ID: {run_id})")
            returncode, _, stderr = run_command(f'gh run delete {run_id}')
            
            if returncode == 0:
                deleted_count += 1
            else:
                print(f"❌ Failed to delete run {run_id}: {stderr}")
    
    print(f"✅ Cleanup complete! Deleted {deleted_count} runs. Only v15 runs remain.")

if __name__ == "__main__":
    main()
