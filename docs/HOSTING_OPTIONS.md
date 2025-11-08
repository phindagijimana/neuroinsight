# NeuroInsight - Hosting and Access Options

## Overview

NeuroInsight can be accessed in three ways:
1. **Local Installation** - Each user runs their own instance
2. **Shared Server** - One server, multiple users access remotely
3. **Cloud Deployment** - Professional hosting (AWS, Azure, GCP)

---

## Option 1: Local Installation (Current Setup)

### ✅ Pros
- **100% privacy**: Data never leaves user's computer
- **No hosting costs**: Free to run
- **Full control**: Users manage their own instance
- **No network required**: Works offline

### ❌ Cons
- **Setup per user**: Each person installs separately
- **Hardware requirements**: Need 16GB+ RAM
- **No collaboration**: Can't share results easily

### Best For:
- Individual researchers
- Small labs with <5 users
- Privacy-sensitive data
- Testing and development

### How to Share:
1. Push code to GitHub (already done ✓)
2. Share link: https://github.com/phindagijimana/neuroinsight
3. Users follow README to install
4. Everyone runs their own instance

---

## Option 2: Shared Server (HPC/University Server)

### ✅ Pros
- **Centralized**: One installation, multiple users
- **Shared resources**: Powerful server hardware
- **Data persistence**: Results stored centrally
- **Easier updates**: Update once, everyone benefits

### ❌ Cons
- **Network required**: Users need SSH/VPN
- **Access control**: Need user authentication
- **Single point of failure**: If server down, no one can access
- **Resource contention**: Slow if multiple users process simultaneously

### Best For:
- Research labs (5-20 users)
- University departments
- Organizations with existing HPC/servers

### How to Set Up:

#### Current Setup (Your HPC)

You're already running on a shared server! Here's how others can access:

**Option A: SSH Tunnel (Current)**
```bash
# Each user runs on their computer:
ssh -L 8000:localhost:8000 username@hpc_server

# Then open browser:
http://localhost:8000
```

**Option B: VPN + Direct Access**
```bash
# If HPC has VPN:
1. Connect to university VPN
2. Access http://hpc_server:8000
```

**Option C: Reverse Proxy (More Professional)**

Set up nginx to provide HTTPS access:

```nginx
# /etc/nginx/sites-available/neuroinsight
server {
    listen 443 ssl;
    server_name neuroinsight.youruni.edu;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Authentication
    auth_basic "NeuroInsight Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Then users access: `https://neuroinsight.youruni.edu`

### Security Considerations:

**Add User Authentication:**

1. **Basic Auth** (Simple):
   ```python
   # backend/main.py
   from fastapi import Depends, HTTPException
   from fastapi.security import HTTPBasic, HTTPBasicCredentials
   
   security = HTTPBasic()
   
   def verify_user(credentials: HTTPBasicCredentials = Depends(security)):
       if credentials.username != "admin" or credentials.password != "secure_pass":
           raise HTTPException(status_code=401)
       return credentials.username
   
   # Add to routes
   @app.get("/api/jobs", dependencies=[Depends(verify_user)])
   ```

2. **OAuth/SAML** (Enterprise):
   - Integrate with university SSO
   - Use FastAPI OAuth2
   - Connect to LDAP/Active Directory

3. **Multi-User Support**:
   - Add user_id to jobs table
   - Filter jobs by authenticated user
   - Separate data directories per user

---

## Option 3: Cloud Deployment

### ✅ Pros
- **Accessible anywhere**: Internet access only
- **Scalable**: Add resources as needed
- **Professional**: HTTPS, backups, monitoring
- **Reliable**: 99.9% uptime SLAs

### ❌ Cons
- **Cost**: $50-500/month depending on usage
- **Complexity**: Requires DevOps knowledge
- **Data privacy**: Data stored in cloud (HIPAA considerations)

### Best For:
- Large organizations (50+ users)
- Commercial products
- Wide distribution
- Professional deployments

### Cloud Options:

#### AWS (Amazon Web Services)

**Setup:**
```bash
# 1. EC2 Instance
Instance Type: t3.xlarge (4 vCPU, 16GB RAM)
Cost: ~$120/month

# 2. With GPU
Instance Type: g4dn.xlarge (4 vCPU, 16GB RAM, T4 GPU)
Cost: ~$400/month

# 3. Storage
EBS Volume: 100GB SSD
Cost: ~$10/month
```

**Services:**
- EC2: Virtual server
- RDS: Managed PostgreSQL
- S3: Object storage (instead of MinIO)
- CloudFront: CDN for static files
- Route53: DNS
- Certificate Manager: Free SSL

**Total Cost**: ~$150-500/month

#### Azure

**Setup:**
```bash
# Virtual Machine
Size: Standard_D4s_v3 (4 vCPU, 16GB RAM)
Cost: ~$140/month

# With GPU
Size: NC6 (6 vCPU, 56GB RAM, K80 GPU)
Cost: ~$900/month
```

**Services:**
- Virtual Machines
- Azure Database for PostgreSQL
- Blob Storage
- Application Gateway
- Azure AD: Authentication

#### Google Cloud Platform (GCP)

**Setup:**
```bash
# Compute Engine
Machine Type: n2-standard-4 (4 vCPU, 16GB RAM)
Cost: ~$120/month

# With GPU
Machine Type: n1-standard-4 + NVIDIA T4
Cost: ~$350/month
```

**Services:**
- Compute Engine
- Cloud SQL
- Cloud Storage
- Cloud Load Balancing
- Identity Platform

### Deployment Steps (AWS Example):

**1. Launch EC2 Instance:**
```bash
# Create instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \  # Ubuntu 22.04
  --instance-type t3.xlarge \
  --key-name your-key \
  --security-group-ids sg-xxx \
  --subnet-id subnet-xxx

# SSH in
ssh -i your-key.pem ubuntu@ec2-xxx.compute.amazonaws.com

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone repository
git clone https://github.com/phindagijimana/neuroinsight.git
cd neuroinsight

# Start services
./start.sh
```

**2. Configure Security Group:**
```
Inbound Rules:
- Port 22 (SSH): Your IP only
- Port 443 (HTTPS): 0.0.0.0/0
- Port 80 (HTTP): 0.0.0.0/0 (redirect to 443)
```

**3. Set up Domain:**
```bash
# Register domain: neuroinsight.com
# Point A record to EC2 IP
# Add SSL certificate (Let's Encrypt)
sudo certbot --nginx -d neuroinsight.com
```

**4. Configure Nginx:**
```nginx
server {
    listen 443 ssl http2;
    server_name neuroinsight.com;
    
    ssl_certificate /etc/letsencrypt/live/neuroinsight.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/neuroinsight.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**5. Set up Monitoring:**
```bash
# CloudWatch for AWS
# or use Prometheus + Grafana
docker run -d -p 9090:9090 prom/prometheus
docker run -d -p 3001:3000 grafana/grafana
```

---

## Option 4: Hybrid Approach

### Desktop App + Cloud Processing

**Idea**: Users run desktop app locally, but processing happens in cloud

**Architecture:**
```
User's Computer (Desktop App)
    ↓ Upload MRI (HTTPS)
Cloud Server (Processing)
    ↓ Process with GPU
User's Computer (Results)
    ↓ Download & Visualize
```

**Benefits:**
- Easy installation (just desktop app)
- No local hardware requirements
- Fast GPU processing in cloud
- Data deleted after processing (privacy)

**Implementation:**
```python
# Add cloud backend option
# backend/core/config.py
class Settings(BaseSettings):
    processing_mode: str = "local"  # or "cloud"
    cloud_api_url: Optional[str] = None
    cloud_api_key: Optional[str] = None

# Workers can run in cloud
# Desktop app connects to cloud API
```

---

## Comparison Table

| Feature | Local | Shared Server | Cloud |
|---------|-------|---------------|-------|
| **Setup Complexity** | Easy | Medium | Hard |
| **Cost** | Free | Free (if HPC) | $150-500/mo |
| **Privacy** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Collaboration** | ❌ | ✅ | ✅ |
| **Accessibility** | Local only | VPN/SSH | Anywhere |
| **Performance** | User's hardware | Server hardware | Scalable |
| **Maintenance** | User | Admin | Managed |
| **Best For** | 1-5 users | 5-20 users | 50+ users |

---

## Recommendations

### For Your Current Situation:

**You're already on a shared HPC server**, which is perfect for a research lab!

**Immediate improvements:**

1. **Add User Authentication**:
   ```python
   # Simple username check
   # Each user gets their own view of jobs
   ```

2. **Set up Nginx Reverse Proxy**:
   ```bash
   # Makes access easier: https://neuroinsight.lab.edu
   # No SSH tunnels needed
   ```

3. **Document Access for Lab Members**:
   ```markdown
   # Lab Members:
   1. Connect to VPN
   2. Open https://neuroinsight.lab.edu
   3. Login with your credentials
   4. Upload and process scans
   ```

### For Wider Distribution:

**Build Desktop App Installers**:
```bash
cd hippo_desktop
npm run dist
```

Upload to GitHub Releases:
- Windows: `NeuroInsight-Setup.exe`
- macOS: `NeuroInsight.dmg`
- Linux: `NeuroInsight.AppImage`

Users download and run locally. No server needed!

---

## Security Checklist

For any shared deployment:

- [ ] HTTPS enabled (SSL certificate)
- [ ] User authentication
- [ ] Input validation (file size, format)
- [ ] Rate limiting (prevent abuse)
- [ ] Backups configured
- [ ] Monitoring/alerts set up
- [ ] Firewall rules configured
- [ ] Regular updates scheduled
- [ ] Data retention policy
- [ ] Access logs enabled
- [ ] HIPAA compliance (if medical data)

---

## Next Steps

**For Your Lab (Current Setup):**
1. Document SSH tunnel access
2. Train lab members
3. Consider adding nginx proxy

**For Public Release:**
1. Build desktop installers
2. Upload to GitHub Releases
3. Write user documentation

**For Enterprise/Commercial:**
1. Deploy to cloud
2. Set up authentication
3. Add billing/usage tracking
4. Professional support

---

## Questions?

- **GitHub Repo**: https://github.com/phindagijimana/neuroinsight
- **Issues**: https://github.com/phindagijimana/neuroinsight/issues
- **Discussions**: GitHub Discussions tab

**Ready to deploy?** Choose the option that best fits your use case!


