# Choosing Your Setup Method

This guide helps you decide between Lab Access and Local Installation based on your specific needs and circumstances.

---

## Quick Decision Guide

**Choose Lab Access if:**
- You have institutional HPC account access
- You need to start immediately
- You want to avoid installation
- You have limited local computing resources
- You need to share data with colleagues

**Choose Local Installation if:**
- You need offline processing capability
- You have a powerful computer (16GB+ RAM)
- You work with highly sensitive data requiring air-gapped systems
- You need complete control over the environment
- You want to modify or develop the software

---

## Detailed Comparison

### Lab Access (SSH Tunnel to HPC)

#### Advantages

**No Installation Required**
- Ready to use in under 5 minutes
- No software downloads
- No system configuration
- Works on any computer with SSH

**High Performance**
- Access to HPC computing resources
- Faster processing than most personal computers
- GPU acceleration available (when configured)
- Multiple jobs can run simultaneously

**Maintenance Free**
- Updates handled by system administrators
- No troubleshooting of Docker or dependencies
- Consistent experience across all users
- Technical support from IT staff

**Collaboration**
- Shared access to processed data
- Multiple users can work on same datasets
- Centralized storage
- Consistent results across research team

**Resource Efficient**
- No local disk space required
- Minimal RAM usage on your computer
- No impact on local system performance

#### Disadvantages

**Network Dependency**
- Requires active internet connection
- Cannot work offline
- Connection may be slower on poor networks
- Must maintain SSH tunnel during use

**Limited Control**
- Cannot modify system configuration
- Dependent on institutional infrastructure
- Processing speed limited by HPC resource allocation
- Must follow institutional policies

**Access Restrictions**
- Requires institutional credentials
- May require VPN for off-campus access
- Subject to institutional security policies
- Potential downtime for maintenance

**Data Location**
- Data stored on institutional servers
- Subject to institutional data policies
- May require data use agreements
- Less suitable for external collaborations

#### Best For

- Clinical researchers at institution
- Students and trainees
- Users with limited computing resources
- Collaborative research projects
- Users who need immediate access
- Those uncomfortable with technical installation

---

### Local Installation (Docker)

#### Advantages

**Complete Control**
- Full administrative access
- Modify configurations as needed
- Install additional tools or packages
- No dependency on external systems

**Offline Capability**
- Works without internet connection
- No network latency
- Process data anywhere
- Independent of institutional infrastructure

**Data Privacy**
- All data stays on your computer
- Complete control over data security
- Suitable for highly sensitive information
- Air-gapped processing possible

**Performance Predictability**
- Dedicated resources (no sharing)
- Consistent performance
- Can optimize for your hardware
- No queue waiting time

**Development Friendly**
- Can modify source code
- Test experimental features
- Integrate with other tools
- Contribute to development

#### Disadvantages

**Installation Complexity**
- Requires Docker Desktop installation
- Memory configuration needed
- Initial setup takes 30-60 minutes
- May need troubleshooting

**System Requirements**
- Minimum 16GB RAM required
- 30GB+ free disk space needed
- Modern operating system required
- Older computers may struggle

**Maintenance Burden**
- You handle all updates
- Troubleshoot technical issues yourself
- Monitor system resources
- Manage disk space

**Performance Limitations**
- Limited by your computer's capabilities
- CPU-only processing is slow (40-60 min/scan)
- GPU may not be available
- Single job processing at a time

**Cost Considerations**
- May need hardware upgrades
- Higher electricity usage
- Potential need for external storage
- Time cost for maintenance

#### Best For

- Users with powerful computers
- Those needing offline processing
- Highly sensitive data requiring local storage
- Developers and contributors
- Users outside the institution
- Long-term research projects
- Those comfortable with technical systems

---

## Specific Use Case Recommendations

### Clinical Research

**Recommended:** Lab Access

**Reasons:**
- Immediate availability for patient data
- Consistent with institutional data policies
- IT support available
- Collaborative access for research teams
- HIPAA compliance easier with institutional infrastructure

**Exception:** Choose Local Installation if working with de-identified data requiring air-gapped processing.

---

### Student Projects

**Recommended:** Lab Access

**Reasons:**
- No cost for computing resources
- Technical support from institution
- Fast setup allows focus on research
- Access from multiple locations (lab, home, etc.)

**Exception:** Choose Local Installation if developing the software as part of computer science project.

---

### Multi-Site Studies

**Recommended:** Depends on data sharing agreements

**Lab Access when:**
- All sites have access to same HPC system
- Centralized processing preferred
- Data sharing agreements allow central storage

**Local Installation when:**
- Each site processes own data locally
- Data cannot leave local institution
- Sites have different HPC systems
- Local regulatory requirements

---

### Method Development

**Recommended:** Local Installation

**Reasons:**
- Full control for modifications
- Can test experimental features
- Development tools integration
- Version control flexibility

**Consider:** Start with Lab Access for learning, switch to Local Installation for development.

---

### Large-Scale Processing (100+ scans)

**Recommended:** Lab Access (HPC)

**Reasons:**
- Batch processing capabilities
- Parallel job execution
- Dedicated computational resources
- Faster overall throughput

**Exception:** Local Installation with GPU if you have high-end workstation.

---

### Pilot Studies or Demonstrations

**Recommended:** Lab Access

**Reasons:**
- Quick setup for demonstrations
- No installation time
- Professional presentation
- Easy to show colleagues

---

## Technical Considerations

### Computing Resources

**Your Computer Specifications:**

| Specification | Lab Access | Local Installation |
|--------------|------------|-------------------|
| RAM | Any | 16GB minimum, 32GB recommended |
| Storage | Any | 30GB minimum, 100GB recommended |
| CPU | Any | 4+ cores recommended |
| GPU | Not relevant | Optional but beneficial |

**Processing Performance:**

| Method | Typical Time per Scan |
|--------|---------------------|
| Lab Access (HPC CPU) | 40-60 minutes |
| Lab Access (HPC GPU) | 1-3 minutes* |
| Local (CPU only) | 40-60 minutes |
| Local (NVIDIA GPU) | 1-3 minutes* |

*When GPU acceleration is configured

---

### Network Requirements

**Lab Access:**
- Stable internet connection required
- VPN may be needed for off-campus
- Minimum 1 Mbps recommended
- Latency affects interface responsiveness

**Local Installation:**
- Internet needed for initial setup only
- No network required after installation
- Can work completely offline
- No latency issues

---

### Data Sensitivity

**Protected Health Information (PHI):**

**Lab Access:**
- Subject to institutional BAA
- Institutional security measures apply
- Must follow institutional policies
- Suitable when institution is covered entity

**Local Installation:**
- Your responsibility for security
- Can use encryption
- Suitable for air-gapped requirements
- May be required by some IRBs

**De-identified Data:**
- Either method suitable
- Choose based on other factors

---

### Budget Considerations

**Lab Access:**
- Free if institutional access available
- No hardware costs
- No electricity costs for processing
- May have institutional usage fees (rare)

**Local Installation:**
- Free software
- Potential hardware upgrade costs
- Electricity for processing
- Storage expansion if needed

---

### Time Investment

**Lab Access:**
- Setup: 5-10 minutes
- Learning curve: 15-30 minutes
- Ongoing maintenance: None

**Local Installation:**
- Setup: 30-60 minutes
- Learning curve: 1-2 hours
- Ongoing maintenance: 15-30 min/month

---

## Migration Between Methods

### Starting with Lab Access, Moving to Local

**When to migrate:**
- Need offline capability
- Want to develop features
- Institution loses HPC access
- Processing volume increases significantly

**Migration process:**
- Install Docker locally
- Download NeuroInsight
- No data migration needed (re-process or export/import)

---

### Starting Local, Moving to Lab Access

**When to migrate:**
- Computer insufficient for needs
- Need to collaborate with team
- Want to reduce maintenance burden
- Need faster processing

**Migration process:**
- Request institutional account
- Set up SSH access
- Upload existing data if needed
- Continue with shared infrastructure

---

## Hybrid Approach

Some users benefit from using both methods:

**Example scenarios:**

**Researcher with lab access + personal installation:**
- Use Lab Access for regular work
- Use Local Installation for travel or offline work
- Use Local Installation for experimental modifications

**Multi-site study:**
- Local Installation at each site for processing
- Lab Access for centralized analysis
- Combine results from both sources

---

## Decision Checklist

Use this checklist to guide your decision:

### Lab Access Checklist
- [ ] I have institutional HPC credentials
- [ ] I need to start immediately
- [ ] I prefer minimal technical setup
- [ ] I need to collaborate with colleagues
- [ ] My data can be stored on institutional servers
- [ ] I have reliable internet access
- [ ] I prefer institutional IT support

**If 4+ checked:** Lab Access is likely best for you

### Local Installation Checklist
- [ ] My computer has 16GB+ RAM
- [ ] I have 30GB+ free disk space
- [ ] I need offline processing capability
- [ ] I require complete data control
- [ ] I'm comfortable with technical setup
- [ ] I want to modify or develop features
- [ ] I process data outside the institution

**If 4+ checked:** Local Installation is likely best for you

---

## Still Unsure?

**Try Lab Access first if available:**
- Quick to set up
- No commitment required
- Can always install locally later
- Good way to learn the software

**Start with Local Installation if:**
- No institutional access available
- Immediate offline capability needed
- Specific requirement for local processing

---

## Getting Started

**Ready to proceed?**

**Lab Access:** See [docs/LAB_ACCESS_GUIDE.md](docs/LAB_ACCESS_GUIDE.md)

**Local Installation:** See [INSTALLATION.md](INSTALLATION.md)

**Still have questions?** See [README.md](README.md) or contact support@neuroinsight.app

---

**Remember:** You can always change methods later. Your choice isn't permanent, and the same data can be processed with either method.

