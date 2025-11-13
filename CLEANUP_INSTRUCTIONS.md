# GitHub Actions Cleanup Instructions

## Quick Start (Run from your local machine)

### Option 1: Interactive Script (Recommended)

```bash
# Pull the latest changes
git pull

# Run the cleanup script
./cleanup_failed_runs.sh
```

The script will:
- ✅ Check if GitHub CLI is installed
- ✅ Authenticate if needed
- ✅ Show you what will be deleted
- ✅ Ask for confirmation before deleting

---

## Option 2: One-Line Commands

### Delete all failed runs:
```bash
gh run list --repo phindagijimana/neuroinsight --status failure --limit 100 --json databaseId --jq '.[].databaseId' | xargs -I {} gh run delete {} --repo phindagijimana/neuroinsight
```

### Delete all runs from old workflows (v1-v7):
```bash
for version in v1 v2 v3 v4 v5 v6 v7; do
  gh run list --repo phindagijimana/neuroinsight --workflow "Desktop Nightly Validation $version" --limit 100 --json databaseId --jq '.[].databaseId' | xargs -I {} gh run delete {} --repo phindagijimana/neuroinsight
done
```

### Delete runs from a specific workflow:
```bash
# Replace "v8" with the version you want to delete
gh run list --repo phindagijimana/neuroinsight --workflow "Desktop Nightly Validation v8" --limit 100 --json databaseId --jq '.[].databaseId' | xargs -I {} gh run delete {} --repo phindagijimana/neuroinsight
```

### Delete ALL runs (use with caution):
```bash
gh run list --repo phindagijimana/neuroinsight --limit 100 --json databaseId --jq '.[].databaseId' | xargs -I {} gh run delete {} --repo phindagijimana/neuroinsight
```

---

## Prerequisites

### Install GitHub CLI

**macOS:**
```bash
brew install gh
```

**Windows:**
```powershell
winget install --id GitHub.cli
```

**Linux:**
```bash
# Debian/Ubuntu
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

### Authenticate GitHub CLI

```bash
gh auth login
```

Follow the prompts to authenticate with your GitHub account.

---

## Verify Before Deleting

### List failed runs:
```bash
gh run list --repo phindagijimana/neuroinsight --status failure --limit 20
```

### List runs from a specific workflow:
```bash
gh run list --repo phindagijimana/neuroinsight --workflow "Desktop Nightly Validation v8" --limit 20
```

### Count failed runs:
```bash
gh run list --repo phindagijimana/neuroinsight --status failure --limit 100 --json databaseId --jq '. | length'
```

---

## Troubleshooting

### "gh: command not found"
- GitHub CLI is not installed. Follow the installation instructions above.

### "authentication required"
- Run: `gh auth login`

### "rate limit exceeded"
- GitHub API has rate limits. Wait a few minutes and try again.
- Or delete in smaller batches (reduce `--limit`)

### Script doesn't delete all runs
- GitHub API limits results to 100 per request
- Run the script multiple times to delete more runs
- Or increase `--limit` in the script

---

## Alternative: Manual Deletion via Web UI

1. Go to: https://github.com/phindagijimana/neuroinsight/actions
2. Filter by status: "Failure"
3. Click on each run → "..." menu → "Delete workflow run"

---

## Recommended Cleanup Strategy

1. **Keep v8 and v9 runs** (latest with all fixes)
2. **Delete all failed runs from v1-v7**
3. **Delete successful runs from v1-v7** (optional - to reduce clutter)

```bash
# Run the interactive script and choose option 2
./cleanup_failed_runs.sh
```

