# Apply Platform Fix to Your Mac

## Quick Manual Fix

Since you're working on your local Mac (`~/Downloads/neuroinsight-web-app`), apply these changes manually:

### Step 1: Edit docker-compose.yml

```bash
cd ~/Downloads/neuroinsight-web-app
nano docker-compose.yml
```

Find the `worker:` section and add `platform: linux/amd64` right after it:

```yaml
  worker:
    platform: linux/amd64  # ← ADD THIS LINE
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
```

Save and exit (Ctrl+O, Enter, Ctrl+X)

### Step 2: Edit pipeline/processors/mri_processor.py

```bash
nano pipeline/processors/mri_processor.py
```

Find the line that says:
```python
cmd = ["docker", "run", "--rm"]
```

Add these lines right after it:
```python
cmd = ["docker", "run", "--rm"]

# Force x86_64 platform for ARM compatibility (enables emulation)
cmd.extend(["--platform", "linux/amd64"])
```

Save and exit (Ctrl+O, Enter, Ctrl+X)

### Step 3: Rebuild and Test

```bash
# Stop services
docker-compose down

# Rebuild worker
docker-compose build --no-cache worker

# Start everything
docker-compose up -d

# Check status
docker-compose ps
```

### Step 4: Test with Real Upload

Open http://localhost:3000 and upload a test file!

## Done!

Your Mac should now process real data (slower but works).


