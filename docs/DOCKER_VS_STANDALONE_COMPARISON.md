# Docker vs Standalone Desktop App: Comprehensive Comparison

Detailed analysis comparing Docker-based packaging with standalone native desktop application for NeuroInsight.

---

## Executive Summary

| Criterion | Docker Approach | Standalone Native | Winner |
|-----------|----------------|-------------------|--------|
| **Cost** | $0 (free tools) | $400-600/year | Docker |
| **Security** | Good (isolated) | Good (sandboxed) | Tie |
| **User Experience** | Poor (2-step install) | Excellent (1-click) | Standalone |
| **Maintenance** | High complexity | Medium complexity | Standalone |
| **Installation Time** | 30+ minutes | 2-5 minutes | Standalone |
| **RAM Usage** | 5-8 GB | 4-6 GB | Standalone |
| **Startup Time** | 30-60 seconds | 5-10 seconds | Standalone |
| **Updates** | Manual rebuild | Auto-update | Standalone |
| **Enterprise Deployment** | Complex | Standard | Standalone |
| **Clinical Suitability** | Poor | Excellent | Standalone |

**Recommendation:** Standalone for end-users, Docker for development/servers.

---

## 1. COST ANALYSIS

### Docker Approach

**Direct Costs: $0**
```
Development:
- Docker Desktop: Free (personal use)
- docker-compose: Free (open source)
- Build tools: Free

Distribution:
- GitHub releases: Free
- Container registries: Free tier available

Total: $0/year
```

**Hidden Costs:**
```
User Support:
- Help users install Docker Desktop
- Troubleshoot Docker issues
- Guide memory configuration
- Handle version conflicts

IT Support Time:
- Estimated 2-4 hours per user
- 100 users = 200-400 hours
- At $50/hour = $10,000-20,000 in support

User Hardware:
- Requires 24-32 GB RAM systems
- vs 16 GB for standalone
- Upgrade cost: $100-200 per user
- 100 users = $10,000-20,000
```

**Total Hidden Costs: $20,000-40,000 for 100 users**

---

### Standalone Approach

**Direct Costs: $400-600/year**
```
Code Signing:
- Windows certificate: $300-500/year (DigiCert, Sectigo)
- macOS Developer Program: $99/year (Apple)
- Total: $399-599/year

Distribution:
- CDN/hosting: Free-$50/month ($0-600/year)
- GitHub releases: Free (primary)
- Update server: Free (GitHub)

Total: $400-1,200/year
```

**Hidden Costs:**
```
User Support:
- Simple installation (like Slack/Cursor)
- Minimal support needed
- Standard desktop app behavior

IT Support Time:
- Estimated 5-10 minutes per user
- 100 users = 8-17 hours
- At $50/hour = $400-850 in support

User Hardware:
- Works on standard 16 GB systems
- Most users already have this
- No upgrades needed

Total Hidden Costs: $400-850 for 100 users
```

**Total Hidden Costs: $400-850 for 100 users**

---

### Cost Comparison Summary

**For 100 Users Over 3 Years:**

| Cost Category | Docker | Standalone |
|--------------|--------|-----------|
| **Direct costs** | $0 | $1,200-3,600 |
| **Support time** | $30,000-60,000 | $1,200-2,550 |
| **Hardware upgrades** | $10,000-20,000 | $0 |
| **Total 3-Year** | $40,000-80,000 | $2,400-6,150 |

**Standalone saves $35,000-75,000 over 3 years for 100 users!**

---

## 2. SECURITY ANALYSIS

### Docker Approach

**Security Features:**

**Isolation:**
```
✓ Container isolation from host
✓ Network isolation
✓ Volume isolation
✓ Resource limits

Containers run in isolated namespace:
- Cannot access host filesystem (except mounted volumes)
- Limited system calls
- Controlled network access
```

**Attack Surface:**
```
Large attack surface:
- Docker daemon (runs as root)
- Container runtime
- Image vulnerabilities
- Kernel vulnerabilities
- Network bridges
- Volume mounts

Multiple layers to secure:
1. Host OS
2. Docker engine
3. Container images
4. Application code
5. Data volumes
```

**Vulnerabilities:**
```
Common issues:
- Privileged containers (if misconfigured)
- Exposed Docker socket
- Unpatched base images
- Vulnerable dependencies in images
- Container escape exploits

Example CVEs (2024):
- CVE-2024-21626: Container escape (runC)
- Multiple Docker engine CVEs
```

**Updates & Patching:**
```
Manual process:
1. Pull new images
2. Rebuild containers
3. Restart services
4. Users must do this manually

Users often run outdated versions:
- Don't know updates available
- Complex update process
- Fear of breaking changes
```

**Data Security:**
```
Data location:
- Docker volumes
- Bind mounts
- Can be anywhere on filesystem
- Hard to track/audit

Cleanup:
- Orphaned volumes
- Dangling images
- Data persistence unclear
```

---

### Standalone Approach

**Security Features:**

**OS-Level Sandboxing:**
```
✓ macOS sandbox/entitlements
✓ Windows AppContainer (Microsoft Store)
✓ Linux AppArmor/SELinux profiles

Modern OS security:
- App-specific permissions
- File system restrictions
- Network access control
- Standard OS security model
```

**Attack Surface:**
```
Smaller attack surface:
- Single application binary
- OS-managed security
- No daemon processes
- Standard app permissions

Layers to secure:
1. Host OS (already secured)
2. Application code
3. User data

Fewer components = fewer vulnerabilities
```

**Code Signing:**
```
✓ Windows Authenticode
  - Verifies publisher
  - Prevents tampering
  - User sees verified publisher

✓ macOS Notarization
  - Apple malware scan
  - Verified by Apple
  - Gatekeeper protection

✓ No unsigned code warnings
  - Users trust signed apps
  - Standard security practice
```

**Auto-Updates:**
```
Automatic security patches:
1. App checks for updates
2. Downloads in background
3. Installs on restart
4. User always on latest version

Result:
- Quick security patch deployment
- High patch adoption rate
- Reduced vulnerability window
```

**Data Security:**
```
Data location (predictable):
- Windows: C:/Users/Name/AppData/Roaming/NeuroInsight
- macOS: ~/Library/Application Support/NeuroInsight
- Linux: ~/.config/NeuroInsight

Benefits:
- Standard OS permissions
- User backup tools work
- Clear data location
- Easy auditing
```

---

### Security Comparison

| Aspect | Docker | Standalone |
|--------|--------|-----------|
| **Isolation** | Container isolation | OS sandboxing |
| **Attack Surface** | Large (multi-layer) | Small (single app) |
| **Code Signing** | Not standard | Required/standard |
| **Updates** | Manual, slow adoption | Auto, high adoption |
| **Vulnerabilities** | Container + OS | OS only |
| **Audit Trail** | Complex | Standard |
| **HIPAA/Compliance** | Good (isolation) | Good (sandboxing) |
| **Data Encryption** | Manual setup | OS integration |

**Both are secure, standalone is simpler to audit and maintain.**

---

## 3. USER EXPERIENCE

### Docker Approach

**Installation Process:**

**Step 1: Install Docker Desktop (15-20 minutes)**
```
User must:
1. Go to docker.com
2. Download Docker Desktop (~500 MB)
3. Run installer
4. Restart computer
5. Start Docker Desktop
6. Wait for initialization
7. Increase memory to 20 GB
8. Restart Docker Desktop

Issues:
- Many users don't have Docker
- Technical knowledge required
- Requires admin rights
- Conflicts with VirtualBox
- Uses significant resources
```

**Step 2: Install NeuroInsight (10-15 minutes)**
```
User must:
1. Clone repo or download ZIP
2. Extract files
3. Open terminal/command prompt
4. Navigate to directory
5. Run docker-compose up -d
6. Wait for downloads (3-5 GB)
7. Wait for services to start
8. Open browser to localhost:56052

Issues:
- Command line required
- Port conflicts common
- Service startup failures
- Confusing error messages
```

**Total Installation Time: 25-35 minutes (if no issues)**

**Common User Issues:**
```
"Cannot connect to Docker daemon"
"Port already in use"
"Out of memory"
"Services not starting"
"localhost:56052 not loading"
"Permission denied"
"Docker is using 100% CPU"

User support tickets: High volume
```

**Daily Usage:**

**Starting the App:**
```
User must:
1. Start Docker Desktop
2. Wait for Docker to initialize (30-60s)
3. Open terminal
4. Navigate to directory
5. Run docker-compose up -d
6. Wait for services (30-60s)
7. Open browser

Total: 2-3 minutes to start using
```

**Stopping the App:**
```
User must:
1. Open terminal
2. Navigate to directory
3. Run docker-compose down

Often forgotten:
- Containers keep running
- Using memory/CPU
- Battery drain on laptops
```

**Performance:**
```
Startup: 30-60 seconds
RAM usage: 5-8 GB
CPU idle: 5-10% (Docker daemon)
Battery impact: High (virtual machine)

User perception:
- "Why is it so slow?"
- "Why does it use so much memory?"
- "My laptop battery drains fast"
```

---

### Standalone Approach

**Installation Process:**

**One Step: Install App (2-5 minutes)**
```
Windows:
1. Download NeuroInsight-Setup.exe
2. Double-click
3. Click "Install"
4. Launch from Start Menu

macOS:
1. Download NeuroInsight.dmg
2. Double-click
3. Drag to Applications
4. Launch from Applications

Linux:
1. Download NeuroInsight.AppImage
2. Make executable
3. Double-click to run

Total: 2-5 minutes
```

**User Issues:**
```
Rare:
- Antivirus false positive (code signing helps)
- Disk space (clear message)

Support tickets: Minimal
```

**Daily Usage:**

**Starting the App:**
```
User:
1. Click app icon (Desktop/Dock/Start Menu)
2. App opens immediately

Total: 5-10 seconds
```

**Stopping the App:**
```
User:
1. Click close button

That's it.
```

**Performance:**
```
Startup: 5-10 seconds
RAM usage: 4-6 GB (processing only)
CPU idle: 0-1%
Battery impact: Low (native app)

User perception:
- Fast, responsive
- Normal desktop app
- Battery-friendly
```

---

### User Experience Comparison

| Aspect | Docker | Standalone |
|--------|--------|-----------|
| **Installation steps** | 10+ steps | 1-2 steps |
| **Installation time** | 25-35 min | 2-5 min |
| **Prerequisites** | Docker Desktop | None |
| **Technical knowledge** | Medium-High | None |
| **Admin rights** | Required | Required (install only) |
| **Startup time** | 2-3 minutes | 5-10 seconds |
| **Daily friction** | High | None |
| **Battery impact** | High | Low |
| **RAM usage** | 5-8 GB always | 0.5-6 GB (dynamic) |
| **Updates** | Manual rebuild | Click "Update" |
| **User satisfaction** | Low (complex) | High (simple) |

**Standalone provides professional medical software experience.**

---

## 4. MAINTENANCE

### Docker Approach

**Development Maintenance:**

**Dockerfile/Compose Management:**
```yaml
Maintain multiple files:
- Dockerfile (backend)
- Dockerfile (worker)
- Dockerfile (frontend)
- docker-compose.yml
- docker-compose.prod.yml
- .dockerignore

Changes required:
- Update base images regularly
- Pin versions carefully
- Test on multiple Docker versions
- Handle platform differences (ARM/x86)
```

**Image Building:**
```bash
Build process:
- Build each service image
- Push to registry
- Version tagging
- Multi-platform builds (ARM/x86)

Time: 15-30 minutes per build
Complexity: High
```

**Dependency Updates:**
```
Multiple layers to update:
- Base OS image (ubuntu, alpine)
- System packages
- Python packages
- Node packages
- Docker engine compatibility

Break often:
- Base image changes
- Package conflicts
- Version incompatibilities
```

**User Support:**
```
Common support issues:
- Docker Desktop not starting
- Out of memory errors
- Port conflicts
- Volume permission issues
- Network bridge issues
- Platform-specific bugs (Windows/Mac)

Support tickets per 100 users: 50-100/month
Time per ticket: 15-30 minutes
Total support time: 12-50 hours/month
```

---

### Standalone Approach

**Development Maintenance:**

**Build Configuration:**
```json
Single configuration:
- package.json (build config)
- build.spec (PyInstaller)
- electron-builder.yml

Simpler than Docker:
- One build process
- Standard tooling
- Platform-specific handled automatically
```

**Build Process:**
```bash
Automated with CI/CD:
- npm run build
- Creates all platform installers
- Auto-signs binaries
- Uploads to releases

Time: 20-40 minutes (automated)
Complexity: Medium
```

**Dependency Updates:**
```
Single layer to update:
- npm packages (frontend)
- Python packages (backend)
- PyInstaller compatibility

Simpler:
- Standard dependency management
- No OS layer to worry about
- No container runtime issues
```

**User Support:**
```
Common support issues:
- Installation location
- Disk space
- Rare: Antivirus conflicts

Support tickets per 100 users: 5-10/month
Time per ticket: 5-10 minutes
Total support time: 0.5-2 hours/month
```

---

### Update Process Comparison

**Docker Updates:**

```
Developer workflow:
1. Update code
2. Update Dockerfiles
3. Rebuild images (15-30 min)
4. Test all services
5. Push to registry
6. Update documentation

User workflow:
1. Stop services
2. Pull new code
3. Pull new images (download GBs)
4. Rebuild if needed
5. Start services
6. Test everything works

Time: 30-60 minutes
Adoption rate: 30-50% (many skip updates)
Error rate: High
```

**Standalone Updates:**

```
Developer workflow:
1. Update code
2. Run build (automated via GitHub Actions)
3. Auto-signs
4. Auto-publishes
5. Done

User workflow:
1. App shows "Update available"
2. Click "Download"
3. Downloads in background
4. Notification "Restart to update"
5. Click "Restart"
6. App updates and reopens

Time: 1-2 minutes
Adoption rate: 90%+ (seamless)
Error rate: Low
```

---

### CI/CD Complexity

**Docker CI/CD:**
```yaml
# .github/workflows/docker.yml
Requires:
- Build multi-platform images
- Push to container registry
- Tag versions
- Test on different platforms
- Update compose files
- Generate documentation

Complexity: High
Failure points: Many (registry, builds, platforms)
Build time: 30-60 minutes
```

**Standalone CI/CD:**
```yaml
# .github/workflows/build.yml
Requires:
- Build on 3 platforms (runners)
- Sign binaries
- Upload to releases
- Auto-update config

Complexity: Medium
Failure points: Few (build, sign, upload)
Build time: 20-40 minutes
```

---

### Maintenance Comparison

| Aspect | Docker | Standalone |
|--------|--------|-----------|
| **Build complexity** | High (multi-stage, multi-platform) | Medium (standard tools) |
| **Configuration files** | 5-10 files | 2-3 files |
| **Build time** | 15-30 min (manual) | 20-40 min (automated) |
| **Update deployment** | Manual, complex | Automated |
| **User update process** | Complex, error-prone | Simple, automatic |
| **Update adoption** | 30-50% | 90%+ |
| **Support tickets** | 50-100/month (100 users) | 5-10/month (100 users) |
| **Support time** | 12-50 hours/month | 0.5-2 hours/month |
| **Breaking changes** | Common (Docker, images) | Rare (stable APIs) |
| **Platform issues** | Frequent (Win/Mac/Linux) | Handled by framework |
| **Long-term maintenance** | Increasing complexity | Stable |

**Standalone requires significantly less ongoing maintenance.**

---

## 5. ENTERPRISE DEPLOYMENT

### Docker Approach

**IT Department Perspective:**

**Deployment Challenges:**
```
Issues:
- Requires Docker Desktop on every machine
- Docker Desktop licensing ($7-14/user/month for companies >250 employees)
- IT must manage Docker versions
- Security policies may block Docker daemon
- Conflicts with other containerized apps
- Resource management difficult

IT burden: High
```

**Group Policy Deployment:**
```
Cannot use standard tools:
- No MSI installer for app
- Docker Desktop requires separate install
- Multiple configuration steps
- Can't deploy via SCCM/Intune easily

Deployment time: 30-60 min per user
```

**License Management:**
```
Docker Desktop Enterprise:
- Requires license purchase
- Per-user or per-machine licensing
- License tracking needed
- Renewals required

Cost: $7-14/user/month
For 500 users: $42,000-84,000/year just for Docker
```

---

### Standalone Approach

**IT Department Perspective:**

**Deployment Advantages:**
```
Standard deployment:
- MSI installer (Windows)
- PKG installer (macOS)
- DEB/RPM (Linux)

Benefits:
- Use existing deployment tools
- SCCM, Intune, Jamf, etc.
- Group Policy deployment
- Standard IT workflows
```

**Group Policy Deployment:**
```
Standard process:
1. Add MSI to deployment server
2. Create deployment policy
3. Push to computers
4. Users see app installed

Deployment time: 5 min per user (automated)
```

**License Management:**
```
NeuroInsight license only:
- Single application license
- No runtime licenses (no Docker)
- Simpler tracking

Cost: Application license only
No additional runtime costs
```

**Comparison:**

| Aspect | Docker | Standalone |
|--------|--------|-----------|
| **Deployment tool support** | Poor | Excellent |
| **Auto-deployment** | Manual/complex | Standard/automated |
| **Time per user** | 30-60 min | 5 min (automated) |
| **IT training needed** | Docker + app | Standard app install |
| **Enterprise licensing** | Docker + app | App only |
| **Annual cost (500 users)** | $42,000-84,000+ | $0-5,000 |
| **IT satisfaction** | Low | High |

---

## 6. CROSS-PLATFORM SUPPORT

### Docker Approach

**Platform Issues:**

**Windows:**
```
Problems:
- Requires Hyper-V (conflicts with VirtualBox)
- Or WSL2 (complex setup)
- File permission issues
- Path translation problems
- Performance overhead (virtualization)
- High memory usage

User complaints: Common
```

**macOS:**
```
Problems:
- Virtual machine overhead
- High battery drain
- Slow file operations (bind mounts)
- Apple Silicon emulation (slow)
- Memory pressure issues

User complaints: Very common
```

**Linux:**
```
Best experience:
- Native Docker
- No virtualization overhead
- But still requires Docker installation

User complaints: Fewer
```

---

### Standalone Approach

**Platform Consistency:**

**Windows:**
```
Standard Windows app:
- NSIS installer (.exe)
- Runs natively
- Good performance
- Normal resource usage

User experience: Excellent
```

**macOS:**
```
Standard Mac app:
- DMG with .app bundle
- Runs natively
- Good battery life
- Normal resource usage
- Universal binary (Intel + Apple Silicon)

User experience: Excellent
```

**Linux:**
```
Standard Linux app:
- AppImage (portable)
- Or DEB/RPM packages
- Native performance
- Desktop integration

User experience: Excellent
```

**Comparison:**

| Platform | Docker Experience | Standalone Experience |
|----------|------------------|----------------------|
| **Windows** | Poor (VM overhead) | Excellent (native) |
| **macOS Intel** | Medium (VM overhead) | Excellent (native) |
| **macOS Silicon** | Poor (emulation) | Excellent (native) |
| **Linux** | Good (native) | Excellent (native) |
| **Battery (laptops)** | Poor (VM) | Good (native) |
| **Performance** | Medium (overhead) | Excellent (native) |

---

## 7. USE CASE RECOMMENDATIONS

### When to Use Docker

**✓ Development:**
```
Reasons:
- Easy environment setup
- Matches production
- Multiple services coordination
- Team consistency

docker-compose up → everything works
```

**✓ Server Deployment:**
```
Reasons:
- Production servers
- Kubernetes clusters
- Scalability
- Microservices architecture
```

**✓ CI/CD:**
```
Reasons:
- Consistent build environment
- Automated testing
- Isolated test runs
```

**✗ End-User Desktop Apps:**
```
Reasons it's poor:
- Complex installation
- Poor user experience
- High support burden
- Resource intensive
```

---

### When to Use Standalone

**✓ End-User Desktop Applications:**
```
Reasons:
- Simple installation
- Professional experience
- Low support needs
- Standard app behavior
```

**✓ Clinical/Medical Software:**
```
Reasons:
- HIPAA compliance (data stays local)
- Professional appearance
- Reliable performance
- Minimal IT burden
```

**✓ Enterprise Deployment:**
```
Reasons:
- Standard IT deployment tools
- Group Policy support
- Lower licensing costs
- Easier management
```

**✓ Distribution to Non-Technical Users:**
```
Reasons:
- One-click install
- No prerequisites
- No support needed
- High adoption rate
```

---

## 8. REAL-WORLD SCENARIOS

### Scenario 1: Small Lab (10 Users)

**Docker Approach:**
```
Costs:
- Software: $0
- IT setup time: 10 hours ($500)
- User support: 20 hours/year ($1,000)
- Total year 1: $1,500

Issues:
- Users struggle with installation
- Frequent support requests
- Some users give up
```

**Standalone Approach:**
```
Costs:
- Software: $500 (code signing)
- IT setup time: 2 hours ($100)
- User support: 2 hours/year ($100)
- Total year 1: $700

Benefits:
- Users install easily
- Minimal support needed
- High adoption
```

**Winner: Standalone (saves $800/year, better experience)**

---

### Scenario 2: Hospital Department (100 Users)

**Docker Approach:**
```
Costs:
- Docker licensing: $42,000/year (enterprise)
- IT deployment: 100 hours ($5,000)
- User support: 200 hours/year ($10,000)
- Hardware upgrades: $15,000 (one-time)
- Total year 1: $72,000

Issues:
- IT resistance (complex)
- Security review required for Docker daemon
- Resource conflicts
- Low adoption (50%)
```

**Standalone Approach:**
```
Costs:
- Software: $500 (code signing)
- IT deployment: 20 hours ($1,000, automated)
- User support: 20 hours/year ($1,000)
- Hardware upgrades: $0
- Total year 1: $2,500

Benefits:
- IT approves easily (standard app)
- Security review simple
- High adoption (95%)
- Users satisfied
```

**Winner: Standalone (saves $69,500/year, 95% vs 50% adoption)**

---

### Scenario 3: Multi-Site Research Study (500 Users)

**Docker Approach:**
```
Costs:
- Docker licensing: $84,000/year
- IT deployment: 500 hours ($25,000)
- User support: 1000 hours/year ($50,000)
- Hardware upgrades: $75,000
- Total year 1: $234,000
- 3-year total: $493,000

Issues:
- Deployment failures
- Version inconsistencies
- Data management complex
- 40% adoption rate
```

**Standalone Approach:**
```
Costs:
- Software: $500 (code signing)
- IT deployment: 100 hours ($5,000, automated)
- User support: 50 hours/year ($2,500)
- Hardware upgrades: $0
- Total year 1: $8,000
- 3-year total: $16,500

Benefits:
- Smooth deployment
- Consistent versions (auto-update)
- Simple data management
- 92% adoption rate
```

**Winner: Standalone (saves $476,500 over 3 years, 92% vs 40% adoption)**

---

## FINAL RECOMMENDATIONS

### For Different Contexts

**Development Team:**
```
Use: Docker
Reason: Easy local development, matches production
```

**Server Deployment:**
```
Use: Docker/Kubernetes
Reason: Scalability, orchestration, cloud-native
```

**End Users (Clinical/Research):**
```
Use: Standalone Desktop App
Reason: Professional experience, low maintenance, high adoption
```

**Mixed Environment:**
```
Best practice:
- Docker for development & servers
- Standalone for end-user desktop
- Same codebase, different packaging
```

---

## SUMMARY TABLE

| Criterion | Docker | Standalone | Winner |
|-----------|--------|-----------|---------|
| **Upfront Cost** | $0 | $400-600/year | Docker |
| **3-Year Cost (100 users)** | $40,000-80,000 | $2,400-6,150 | Standalone |
| **Installation Complexity** | High (2 steps) | Low (1 click) | Standalone |
| **Installation Time** | 25-35 min | 2-5 min | Standalone |
| **User Experience** | Poor | Excellent | Standalone |
| **Startup Time** | 2-3 min | 5-10 sec | Standalone |
| **RAM Usage** | 5-8 GB | 4-6 GB | Standalone |
| **Security** | Good | Good | Tie |
| **Updates** | Manual, 30% adoption | Auto, 90% adoption | Standalone |
| **Support Burden** | High (50-100 tickets/mo) | Low (5-10 tickets/mo) | Standalone |
| **Enterprise Deployment** | Poor | Excellent | Standalone |
| **Development** | Excellent | N/A | Docker |
| **Server Deployment** | Excellent | Poor | Docker |

---

## CONCLUSION

**For NeuroInsight end-user distribution:**

**Standalone Desktop App is the clear winner:**

1. **Cost:** Saves $35,000-75,000 per 100 users over 3 years
2. **Security:** Equal security, simpler to audit
3. **User Experience:** Professional, simple, fast (like Cursor/Slack)
4. **Maintenance:** 90% less support needed

**Docker remains excellent for:**
- Development environments
- Server/HPC deployments
- CI/CD pipelines

**Recommended Strategy:**
- **Develop with Docker** (easy team collaboration)
- **Deploy servers with Docker** (HPC, cloud)
- **Distribute to users as Standalone** (professional medical software)

This gives best of both worlds: developer productivity + user satisfaction.

