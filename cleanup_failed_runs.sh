#!/bin/bash
# Bulk delete failed GitHub Actions workflow runs
# Run this script from your local machine (not on the cluster)

set -euo pipefail

REPO="phindagijimana/neuroinsight"

echo "🔍 Checking for GitHub CLI..."
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo ""
    echo "Install it from: https://cli.github.com/"
    echo ""
    echo "macOS:   brew install gh"
    echo "Windows: winget install --id GitHub.cli"
    echo "Linux:   See https://github.com/cli/cli/blob/trunk/docs/install_linux.md"
    exit 1
fi

echo "✅ GitHub CLI found"
echo ""

# Authenticate if needed
echo "🔐 Checking authentication..."
if ! gh auth status &> /dev/null; then
    echo "⚠️  Not authenticated. Running 'gh auth login'..."
    gh auth login
fi

echo "✅ Authenticated"
echo ""

# Function to delete runs
delete_runs() {
    local filter=$1
    local description=$2
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🗑️  Deleting: $description"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local runs=$(gh run list --repo "$REPO" $filter --limit 100 --json databaseId --jq '.[].databaseId')
    
    if [ -z "$runs" ]; then
        echo "✅ No runs found to delete"
        echo ""
        return
    fi
    
    local count=$(echo "$runs" | wc -l | tr -d ' ')
    echo "📊 Found $count runs to delete"
    echo ""
    
    read -p "❓ Delete these $count runs? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$runs" | while read -r run_id; do
            echo "  🗑️  Deleting run $run_id..."
            gh run delete "$run_id" --repo "$REPO" 2>/dev/null || echo "  ⚠️  Failed to delete $run_id"
        done
        echo "✅ Deletion complete"
    else
        echo "⏭️  Skipped"
    fi
    echo ""
}

# Main menu
echo "╔════════════════════════════════════════════╗"
echo "║  GitHub Actions Cleanup Script             ║"
echo "║  Repository: $REPO  ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "What would you like to delete?"
echo ""
echo "1) All failed runs"
echo "2) All runs from old workflows (v1-v7)"
echo "3) All runs from a specific workflow"
echo "4) All runs (failed + successful)"
echo "5) Cancel"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        delete_runs "--status failure" "All failed runs"
        ;;
    2)
        for version in v1 v2 v3 v4 v5 v6 v7; do
            delete_runs "--workflow \"Desktop Nightly Validation $version\"" "Workflow $version"
        done
        ;;
    3)
        echo ""
        echo "Available workflows:"
        gh workflow list --repo "$REPO"
        echo ""
        read -p "Enter workflow name: " workflow_name
        delete_runs "--workflow \"$workflow_name\"" "Workflow: $workflow_name"
        ;;
    4)
        echo ""
        echo "⚠️  WARNING: This will delete ALL workflow runs!"
        read -p "Are you ABSOLUTELY sure? (type 'yes' to confirm): " confirm
        if [ "$confirm" = "yes" ]; then
            delete_runs "" "All workflow runs"
        else
            echo "⏭️  Cancelled"
        fi
        ;;
    5)
        echo "👋 Cancelled"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo "✨ Done!"

