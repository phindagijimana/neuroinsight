# NeuroInsight - Open OnDemand Integration

## Overview

Deploy NeuroInsight as an interactive app in Open OnDemand, allowing users to access it via web browser with university authentication.

---

## Prerequisites

- Open OnDemand installed at your institution (check with IT)
- Access to OOD app directory (usually `/var/www/ood/apps/sys/`)
- NeuroInsight running on HPC
- Permission to add custom apps (contact OOD admin)

---

## Architecture

```
User Browser
    ↓
https://ondemand.urmc.rochester.edu
    ↓
Open OnDemand Portal (login with university credentials)
    ↓
Launch NeuroInsight App
    ↓
OOD starts/connects to NeuroInsight on HPC
    ↓
User sees NeuroInsight in browser tab
```

**Benefits:**
- No SSH tunnels needed
- Automatic authentication
- Professional interface
- Works from any device
- Easy to share (just send URL)

---

## Quick Setup (If You Have OOD Admin Access)

### Option 1: Contact Your OOD Administrator

**Email template:**

```
Subject: Request to Add NeuroInsight App to Open OnDemand

Hi [OOD Admin],

I'd like to add a new interactive app called "NeuroInsight" to our 
Open OnDemand portal for hippocampal MRI analysis.

Details:
- Name: NeuroInsight
- Type: Web application (runs on port 8000)
- Backend: Currently running on [HPC node/path]
- Docker-based: Yes (already configured)
- Users: Research lab members (neuroscience)
- Documentation: https://github.com/phindagijimana/neuroinsight

Can you help me set this up or provide access to the app directory?
The app is already running successfully via SSH tunnels, I just need
to make it accessible through OOD.

Thanks!
[Your Name]
```

---

## Option 2: Self-Service Setup (If You Have Access)

### Step 1: Create App Directory

```bash
# Navigate to OOD apps directory (path may vary)
cd /var/www/ood/apps/sys/

# Create NeuroInsight app directory
sudo mkdir -p neuroinsight
cd neuroinsight

# Create required files
sudo touch manifest.yml form.yml template/script.sh.erb
sudo mkdir -p template
```

### Step 2: Create manifest.yml

```bash
sudo nano manifest.yml
```

```yaml
---
name: NeuroInsight
category: Interactive Apps
subcategory: Neuroimaging
role: batch_connect
description: |
  Automated hippocampal asymmetry analysis from T1-weighted MRI scans.
  Uses FastSurfer for brain segmentation and calculates hippocampal volumes.
```

### Step 3: Create form.yml

```bash
sudo nano form.yml
```

```yaml
---
cluster: "cluster_name"  # Your HPC cluster name

attributes:
  bc_num_hours:
    label: "Number of hours"
    value: 4
    min: 1
    max: 24
    step: 1
    help: "Maximum time the NeuroInsight session will run"
  
  bc_num_cores:
    label: "Number of CPU cores"
    value: 4
    min: 2
    max: 16
    step: 2
    help: "More cores = faster processing"
  
  bc_memory:
    label: "Memory (GB)"
    value: 20
    min: 16
    max: 64
    step: 4
    help: "Minimum 16GB required for processing"
  
  custom_queue:
    label: "Queue/Partition"
    value: "interactive"
    help: "HPC queue to submit job to"

form:
  - bc_num_hours
  - bc_num_cores
  - bc_memory
  - custom_queue
  - bc_email_on_started
```

### Step 4: Create Launch Script

```bash
sudo nano template/script.sh.erb
```

```bash
#!/bin/bash

# Load required modules (adjust for your system)
module purge
module load singularity/3.8.0 || true
module load docker/20.10 || true

# Set working directory
export NEUROINSIGHT_HOME="/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo"
cd $NEUROINSIGHT_HOME

# Ensure services are running
echo "Starting NeuroInsight services..."

# Start Docker Compose (if not already running)
if ! docker-compose ps | grep -q "Up"; then
    echo "Starting Docker containers..."
    docker-compose up -d
    sleep 10
fi

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
timeout=60
while [ $timeout -gt 0 ]; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo "Backend is ready!"
        break
    fi
    sleep 2
    timeout=$((timeout-2))
done

if [ $timeout -eq 0 ]; then
    echo "ERROR: Backend did not start in time"
    exit 1
fi

# Set connection info for OOD
export host=$(hostname -f)
export port=8000

echo "NeuroInsight is ready at http://${host}:${port}"

# Keep session alive
# OOD will proxy the connection and handle cleanup
sleep infinity
```

### Step 5: Create connection.yml

```bash
sudo nano template/connection.yml.erb
```

```yaml
---
host: "<%= host %>"
port: <%= port %>
password: ""
```

### Step 6: Set Permissions

```bash
# Make executable
sudo chmod +x template/script.sh.erb

# Set ownership (adjust user as needed)
sudo chown -R apache:apache /var/www/ood/apps/sys/neuroinsight

# Or for some systems:
# sudo chown -R ondemand:ondemand /var/www/ood/apps/sys/neuroinsight
```

### Step 7: Restart OOD

```bash
# Restart OOD to recognize new app
sudo systemctl restart ondemand-nginx
# Or
sudo /opt/ood/nginx_stage/sbin/nginx_stage nginx -s reload
```

---

## Option 3: User-Level App (No Admin Access)

If you don't have admin access, create a **user-level app**:

### Step 1: Create in Your Home Directory

```bash
# Create app directory
mkdir -p ~/ondemand/dev/neuroinsight
cd ~/ondemand/dev/neuroinsight

# Create same files as above (manifest.yml, form.yml, etc.)
```

### Step 2: Enable Developer Mode

1. Login to Open OnDemand
2. Click "Help" → "Develop" → "My Sandbox Apps (Development)"
3. Your app should appear there

### Step 3: Test and Share

- Test the app yourself
- Share the URL with lab members
- Once tested, request admin to move it to production

---

## Alternative: Passenger App (Simpler)

If NeuroInsight is already running, create a **Passenger app** that just proxies:

### Create ~/ondemand/dev/neuroinsight/config.ru

```ruby
# config.ru - Rack proxy to NeuroInsight
require 'net/http'

class NeuroInsightProxy
  def call(env)
    # Proxy all requests to running NeuroInsight instance
    uri = URI("http://localhost:8000#{env['PATH_INFO']}")
    
    http = Net::HTTP.new(uri.host, uri.port)
    request = Net::HTTP::Get.new(uri.request_uri)
    
    # Forward headers
    env.each do |key, value|
      if key.start_with?('HTTP_')
        header = key.sub(/^HTTP_/, '').split('_').map(&:capitalize).join('-')
        request[header] = value
      end
    end
    
    response = http.request(request)
    
    [response.code.to_i, response.to_hash, [response.body]]
  end
end

run NeuroInsightProxy.new
```

---

## Testing Your OOD App

### Step 1: Access OOD Portal

```
https://ondemand.urmc.rochester.edu
# (or your institution's OOD URL)
```

### Step 2: Find Your App

- Click "Interactive Apps" in menu
- Look for "NeuroInsight" under "Neuroimaging"

### Step 3: Launch

1. Select resources:
   - Hours: 4
   - Cores: 4
   - Memory: 20 GB
2. Click "Launch"
3. Wait for session to start (1-2 minutes)
4. Click "Connect to NeuroInsight"

### Step 4: Use NeuroInsight

- Upload MRI scans
- Monitor processing
- Download results
- Session stays active for selected hours

---

## User Access Guide

Once deployed, users access it simply:

### Step 1: Login to OnDemand

```
https://ondemand.urmc.rochester.edu
```

Use university credentials

### Step 2: Launch NeuroInsight

1. Click "Interactive Apps" → "NeuroInsight"
2. Choose resources (defaults are fine)
3. Click "Launch"
4. Wait ~1 minute
5. Click "Connect to NeuroInsight"

### Step 3: Start Working

- Interface opens in new tab
- Upload scans
- Process data
- No SSH needed!

---

## Advantages Over SSH Tunnel

| Feature | SSH Tunnel | Open OnDemand |
|---------|------------|---------------|
| **User Setup** | Install SSH client, configure | None - just browser |
| **Authentication** | SSH keys/passwords | University SSO |
| **Access** | Command line needed | Click to launch |
| **From Home** | VPN + SSH | Just VPN (or none) |
| **User-Friendly** | Technical | Non-technical OK |
| **Session Management** | Manual | Automatic |
| **Resource Allocation** | Manual | GUI selection |
| **Multiple Users** | Each SSH separately | Concurrent sessions |

**Bottom line:** OOD is **much** easier for users! 🎉

---

## Troubleshooting

### App Doesn't Appear

**Check:**
```bash
# Verify app files exist
ls -la /var/www/ood/apps/sys/neuroinsight/

# Check OOD logs
sudo tail -f /var/log/ondemand-nginx/*/error.log

# Restart OOD
sudo systemctl restart ondemand-nginx
```

### Session Fails to Start

**Common issues:**
- Not enough resources available
- Backend not starting
- Docker not accessible
- Permissions issues

**Check batch job logs:**
- In OOD, click "My Interactive Sessions"
- Click "Session ID" → View logs

### Can't Connect to NeuroInsight

**Verify:**
```bash
# Is NeuroInsight running?
docker-compose ps

# Can you access locally?
curl http://localhost:8000

# Check port is not blocked
netstat -tuln | grep 8000
```

---

## Advanced Configuration

### Auto-Start NeuroInsight for Each User

Create per-user instances:

```bash
# In script.sh.erb
export NEUROINSIGHT_PORT=$((8000 + RANDOM % 1000))
export USER_DATA_DIR="$HOME/.neuroinsight"

mkdir -p $USER_DATA_DIR

# Start user-specific instance
docker-compose -p "neuroinsight-${USER}" up -d
```

### Resource Limits

```yaml
# In form.yml - set limits based on your HPC
bc_memory:
  value: 20
  min: 16
  max: 128  # Adjust to your node capacity
```

### Email Notifications

```yaml
# In form.yml
attributes:
  bc_email_on_started:
    label: "Email when session starts"
    value: 1
```

Users get email when NeuroInsight is ready!

---

## Security Considerations

### Network Access

OOD typically runs on internal network only:
- Campus network: Direct access
- Off-campus: VPN required
- This is good for protected health information (PHI)

### Authentication

- Uses university SSO (Shibboleth, CAS, etc.)
- No separate login needed
- Audit trail of who accessed

### Data Privacy

- Each user's data stays in their session
- No cross-user access (unless shared directory)
- Sessions auto-terminate after time limit

---

## Best Practices

### 1. Resource Defaults

Set reasonable defaults:
- Hours: 4 (enough for several scans)
- Memory: 20GB (sufficient for processing)
- Cores: 4 (good balance)

### 2. User Quotas

Work with HPC admin to set:
- Max concurrent sessions per user
- Max total resources per group
- Priority queues for different user classes

### 3. Documentation

Create OOD-specific help:
- Add "Help" link in form.yml
- Point to user guide
- Include troubleshooting tips

### 4. Monitoring

Track usage:
```bash
# Check OOD access logs
sudo tail -f /var/log/ondemand-nginx/*/access.log | grep neuroinsight

# Monitor resource usage
squeue -u all | grep neuroinsight
```

---

## Example: URMC-Specific Setup

### Contact Information

**At URMC, contact:**
- **HPC Support:** researchcomputing@urmc.rochester.edu
- **OOD Admin:** IT Research Computing team

**Request:**
> "I'd like to add NeuroInsight to our Open OnDemand portal.
> The app is already running on the HPC cluster and has been
> tested successfully. Can you help integrate it into OOD?"

### Expected Timeline

- Submit request: Day 1
- IT review: 1-3 days
- Testing: 2-3 days
- Deployment: 1 week total

### What IT Needs From You

1. App name and description
2. Resource requirements
3. Which users should have access
4. Any special software dependencies
5. Support contact (you!)

---

## Documentation for Users

### Quick Start Guide

Create this for your lab:

```markdown
# Accessing NeuroInsight via Open OnDemand

## 1. Login
Go to: https://ondemand.urmc.rochester.edu
Login with your URMC credentials

## 2. Launch NeuroInsight
- Click "Interactive Apps" menu
- Select "NeuroInsight"
- Use default settings
- Click "Launch"

## 3. Connect
- Wait 1-2 minutes for session to start
- Click "Connect to NeuroInsight" button
- NeuroInsight opens in new tab

## 4. Upload & Process
- Click "Upload MRI Scan"
- Select your .nii or .nii.gz file
- Processing takes 40-60 minutes
- Download results when complete

## 5. End Session
- Close NeuroInsight tab when done
- Click "Delete" in OOD Sessions page to free resources

Questions? Contact: pndagiji@rochester.edu
```

---

## Summary

### Quick Steps to Deploy:

1. **Contact URMC IT/HPC support** ✉️
2. **Request OOD app integration** 📝
3. **Provide app details** (use templates above)
4. **Test with pilot users** 🧪
5. **Share with whole lab** 🎉

### Benefits for Your Lab:

- ✅ One-click access (no SSH)
- ✅ University authentication
- ✅ Works from anywhere (with VPN)
- ✅ Professional interface
- ✅ Automatic resource management
- ✅ Non-technical users can use it

### Timeline:

- IT setup: 1 week
- Pilot testing: 3-5 days
- Full deployment: 2 weeks total

---

## Next Steps

**This week:**
1. Email URMC HPC support (use template above)
2. Share NeuroInsight GitHub link
3. Describe your use case

**Next week:**
4. Work with IT on configuration
5. Test the OOD integration
6. Create user documentation

**Within month:**
7. Launch to lab members
8. Gather feedback
9. Iterate and improve

---

**Want me to help draft the email to your IT department?** 📧

