# Email Template: Request Open OnDemand Integration

## To: URMC Research Computing / HPC Support

---

**Subject:** Request to Add NeuroInsight to Open OnDemand Portal

**To:** researchcomputing@urmc.rochester.edu (or your HPC support email)

**CC:** Your PI / Lab Director

---

**Body:**

Hi Research Computing Team,

I am writing to request the addition of a new interactive application called **NeuroInsight** to our Open OnDemand portal.

## Application Overview

**Name:** NeuroInsight  
**Purpose:** Automated hippocampal asymmetry analysis from T1-weighted MRI scans  
**Type:** Web-based interactive application  
**Technology:** Docker-compose based, FastAPI backend, React frontend  
**Current Status:** Successfully running on HPC cluster via command line

## Why Open OnDemand?

Currently, lab members access the tool via SSH tunnels, which requires:
- Technical knowledge of SSH port forwarding
- Command-line comfort
- Manual connection setup each time

Open OnDemand integration would:
- Provide one-click browser access
- Use university authentication
- Make it accessible to non-technical researchers
- Improve adoption across the neuroscience department

## Technical Details

**Resource Requirements:**
- Memory: 16-20 GB minimum, 32 GB recommended
- CPU: 4-8 cores
- Runtime: 1-4 hours per session typical
- Port: 8000 (backend API)
- Storage: Uses shared NFS storage at `/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo`

**Software Dependencies:**
- Docker / Singularity (already available on cluster)
- Currently runs using docker-compose
- All application dependencies containerized

**Current Deployment:**
- Location: HPC cluster node
- Path: `/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo`
- Already tested and working via SSH access
- Documentation: https://github.com/phindagijimana/neuroinsight

## Proposed Implementation

I envision users would:
1. Login to Open OnDemand portal with university credentials
2. Navigate to Interactive Apps → NeuroInsight
3. Select resources (hours, memory, cores)
4. Click "Launch"
5. Connect to web interface when ready

Similar to how Jupyter, RStudio, and other interactive apps work in OOD.

## Expected Users

- **Primary:** Neuroscience research lab (5-10 users initially)
- **Potential:** Could expand to broader neuroscience department
- **Usage Pattern:** Intermittent (not continuous), processing MRI datasets

## Security/Compliance

- Processes medical imaging data (MRI scans)
- Data remains on HPC cluster (no external transfer)
- University authentication via OOD
- HIPAA considerations may apply (de-identified data typically)

## Support

I am willing to:
- Provide detailed configuration files
- Assist with initial setup and testing
- Create user documentation
- Serve as primary contact for app-specific questions
- Work with your team on implementation

## Timeline

No strict deadline, but would be beneficial to have available this semester for ongoing research projects.

## Next Steps

What information do you need from me to proceed? I'm happy to:
- Provide more technical details
- Set up a meeting to discuss implementation
- Create draft OOD app configuration files
- Test the integration during development

## Additional Information

The application is:
- Open source (MIT license)
- Based on peer-reviewed methods (FastSurfer)
- Well-documented
- Currently stable and production-ready

GitHub repository: https://github.com/phindagijimana/neuroinsight  
Documentation: See `docs/` folder in repository

Thank you for considering this request. Please let me know if you need any additional information or would like to schedule a meeting to discuss further.

Best regards,

[Your Name]  
[Your Title/Position]  
[Department]  
[Email]  
[Phone]

---

## Alternative: Shorter Version

If you prefer a more concise email:

---

**Subject:** OOD Integration Request - NeuroInsight MRI Analysis Tool

Hi Team,

I'd like to add **NeuroInsight**, a hippocampal MRI analysis tool, to our Open OnDemand portal.

**Quick Facts:**
- Web app for automated brain MRI analysis
- Currently runs successfully on HPC via SSH
- Docker-based, needs 16-20GB RAM, 4-8 cores
- 5-10 users in neuroscience lab initially
- GitHub: https://github.com/phindagijimana/neuroinsight

**Why OOD?**
Make it accessible to non-technical lab members without SSH setup.

**What I need:**
Guidance on creating the OOD app configuration or assistance with integration.

Happy to provide more details or meet to discuss!

Thanks,
[Your Name]

---


