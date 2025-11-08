# Share NeuroInsight with Your Lab - Quick Start

## 📧 Email Template for Lab Members

---

**Subject:** NeuroInsight Now Available - Hippocampal Analysis Tool

**Body:**

Hi Team,

NeuroInsight is now available for hippocampal asymmetry analysis! Here's how to access it:

### Quick Access (5 minutes)

**1. Open Terminal** (macOS/Linux) or PowerShell (Windows)

**2. Run this command:**
```bash
ssh -L 8000:localhost:8000 YOUR_HPC_USERNAME@urmc-sh.rochester.edu
```
Replace `YOUR_HPC_USERNAME` with your HPC username.

**3. Enter your HPC password**

**4. Open your web browser to:**
```
http://localhost:8000
```

**5. Start analyzing!**
- Upload your T1-weighted MRI scans (.nii or .nii.gz)
- Processing takes 40-60 minutes per scan
- Download results as CSV or JSON

### Important Notes

- **Keep the terminal window open** while using the app
- **All jobs are visible to all users** (we're working on user accounts)
- **Processing is queued** - one scan at a time
- **Supported formats**: NIfTI (.nii, .nii.gz), DICOM (.dcm)

### Documentation

- **Quick User Guide**: See attached `QUICK_USER_GUIDE.md`
- **Full User Manual**: See attached `USER_GUIDE.md`
- **Troubleshooting**: See attached `LAB_ACCESS_GUIDE.md`

### Getting Help

- **Technical Issues**: Contact me (pndagiji@rochester.edu)
- **HPC Access**: Contact IT
- **Questions**: Reply to this email

### Tips

- Name your files descriptively (e.g., `patient-001_baseline_T1w.nii`)
- You can monitor your job status in real-time
- Download results before deleting jobs
- Close other applications if your computer is low on RAM

Looking forward to seeing your results!

Best,
[Your Name]

---

**Attachments:**
1. docs/LAB_ACCESS_GUIDE.md
2. QUICK_USER_GUIDE.md
3. docs/USER_GUIDE.md

---



