# NeuroInsight - Publication Readiness Checklist

## Overview

To use NeuroInsight in a published scientific paper, you need to address:
1. Validation of accuracy
2. Scientific documentation
3. Code/data availability
4. Method transparency
5. Quality assurance

---

## ✅ Already Publication-Ready

### Technical Foundation
- ✅ Based on FastSurfer (Henschel et al., 2020)
- ✅ Reproducible pipeline (Docker)
- ✅ Standard file formats (NIfTI)
- ✅ Version-controlled (Git/GitHub)
- ✅ Open source (MIT license)

### Scientific Validity
- ✅ Uses validated segmentation (FastSurfer)
- ✅ Standard hippocampal volume calculation
- ✅ Established asymmetry metric
- ✅ Peer-reviewed algorithms

---

## ⚠️ Critical Requirements (Must Complete)

### 1. Validation Study ⚠️ **REQUIRED**

**Problem:** You haven't validated that NeuroInsight produces accurate results.

**What to do:**

#### A. Compare Against Gold Standard

Test NeuroInsight on **10-20 scans** with known ground truth:

1. **Use public datasets with manual segmentations:**
   - ADNI (Alzheimer's Disease Neuroimaging Initiative)
   - HCP (Human Connectome Project)
   - OASIS (Open Access Series of Imaging Studies)

2. **Compare your results to:**
   - Manual segmentations (gold standard)
   - FreeSurfer outputs (established method)
   - Published hippocampal volumes

3. **Calculate metrics:**
   - Dice coefficient (overlap with manual)
   - Correlation with FreeSurfer (r > 0.95 expected)
   - Mean absolute error in volumes
   - Bland-Altman plots

**Example validation table:**

| Scan | Manual Vol (mm³) | NeuroInsight (mm³) | Difference | % Error |
|------|------------------|-------------------|------------|---------|
| sub-01 | 3,845 | 3,862 | +17 | 0.44% |
| sub-02 | 4,021 | 3,998 | -23 | 0.57% |
| ... | ... | ... | ... | ... |
| **Mean** | **3,912** | **3,918** | **+6** | **0.52%** |

**Validation script:**

```python
# validation/validate_accuracy.py
import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

def validate_against_ground_truth():
    """Compare NeuroInsight results to manual segmentations"""
    
    # Load your results
    neuroinsight = pd.read_csv('neuroinsight_results.csv')
    
    # Load ground truth (manual or FreeSurfer)
    ground_truth = pd.read_csv('ground_truth.csv')
    
    # Calculate correlation
    r, p = pearsonr(neuroinsight['left_volume'], 
                    ground_truth['left_volume'])
    
    print(f"Correlation: r={r:.3f}, p={p:.4f}")
    
    # Bland-Altman plot
    plot_bland_altman(neuroinsight, ground_truth)
    
    # Calculate metrics
    calculate_metrics(neuroinsight, ground_truth)

# Run validation
validate_against_ground_truth()
```

**Expected outcomes:**
- Correlation r > 0.95 (excellent)
- Mean error < 5% (acceptable)
- No systematic bias (Bland-Altman)

---

### 2. Method Documentation ⚠️ **REQUIRED**

**Problem:** Need formal methods section text for papers.

**What to do:**

Create `docs/METHODS_SECTION.md` with standard text researchers can cite:

```markdown
# Methods Section for Publications

## Hippocampal Segmentation and Asymmetry Analysis

Hippocampal segmentation was performed using NeuroInsight v1.0 
(https://github.com/phindagijimana/neuroinsight), an automated pipeline 
based on FastSurfer v2.4.2 (Henschel et al., 2020). 

T1-weighted MRI scans were processed using the following pipeline:
1. Image conforming to 1mm³ isotropic resolution
2. Whole-brain segmentation using FastSurfer's deep learning network
3. Hippocampal subfield extraction from aparc+aseg segmentation
4. Volume calculation in mm³

Hippocampal asymmetry index (AI) was calculated as:
AI = ((Left - Right) / (Left + Right)) × 100

Where positive values indicate left > right hemisphere.

Processing was performed on [describe your system: CPU/GPU, RAM, OS].
Average processing time was [X] minutes per scan.

Quality control included visual inspection of all segmentations and 
exclusion of scans with motion artifacts or poor image quality.

## References
Henschel L, Conjeti S, Estrada S, Diers K, Fischl B, Reuter M. 
FastSurfer - A fast and accurate deep learning based neuroimaging 
pipeline. NeuroImage. 2020 Oct 15;219:117012.
```

**Include in your paper:**
- Software version (tag releases on GitHub)
- Processing environment
- Quality control procedures
- Statistical methods used

---

### 3. Code Availability Statement ⚠️ **REQUIRED**

**Problem:** Journals require code/data availability.

**What to do:**

#### A. Add to your paper (usually in Methods):

```
## Code Availability
The NeuroInsight pipeline is freely available at 
https://github.com/phindagijimana/neuroinsight under MIT license.
Version 1.0.0 used in this study is archived at 
[Zenodo DOI: 10.5281/zenodo.XXXXXX].

Installation instructions and documentation are provided in the 
repository. Docker containers ensure reproducibility across platforms.
```

#### B. Create a GitHub Release

```bash
# Tag a specific version for the paper
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
git tag -a v1.0.0 -m "Version used in [Paper Title]"
git push origin v1.0.0

# Go to GitHub → Releases → Create Release
# Upload the tag as a release
```

#### C. Archive on Zenodo (permanent DOI)

1. Go to https://zenodo.org/
2. Link your GitHub repository
3. Create a new release
4. Get a permanent DOI
5. Cite this DOI in your paper

**Example:**
> Ndagijimana, P. (2025). NeuroInsight: Automated Hippocampal Analysis 
> Pipeline v1.0.0. Zenodo. https://doi.org/10.5281/zenodo.XXXXXX

---

### 4. Quality Assurance ⚠️ **IMPORTANT**

**Problem:** Need to ensure results are reliable.

**What to do:**

#### A. Test-Retest Reliability

Process the same scan multiple times:
```bash
# Process same scan 3 times
for i in {1..3}; do
  # Upload same file
  # Compare results
done
```

**Expected:** Identical results (deterministic processing)

#### B. Visual QC Protocol

Create quality control checklist:

```markdown
## Quality Control Checklist

For each processed scan, verify:
- [ ] Segmentation covers full hippocampus
- [ ] No obvious misclassifications
- [ ] Volumes within normal range (2500-5000 mm³)
- [ ] Left-right symmetry is reasonable (<15% asymmetry)
- [ ] No processing artifacts

Exclude scans with:
- Motion artifacts
- Incomplete brain coverage  
- Severe pathology affecting segmentation
- Processing failures
```

#### C. Statistical Power Analysis

Document in your paper:
```
Sample size was determined by power analysis (α=0.05, β=0.80) 
to detect a 10% difference in hippocampal volume with effect 
size d=0.8, requiring n=26 participants per group.
```

---

### 5. Testing on Your Actual Data ⚠️ **CRITICAL**

**Problem:** Must verify it works on YOUR research scans.

**What to do:**

#### A. Pilot Study (5-10 scans)

```bash
# Process pilot scans
# Upload to NeuroInsight
# Download results
# Manually inspect each segmentation
# Calculate statistics
```

#### B. Check Results Make Sense

Compare to literature:
- Normal adult hippocampus: 3,000-4,500 mm³
- Left usually slightly larger (0-5%)
- Should correlate with age, sex, head size

#### C. Visual Inspection

For each scan in your study:
1. View the segmentation overlay
2. Check for obvious errors
3. Note any quality issues
4. Decide inclusion/exclusion

---

## ✅ Optional (Recommended for High-Impact Journals)

### 6. Independent Validation

**Gold standard:** Have another lab validate your tool.

**Options:**
- Share code with collaborator
- Ask them to process test dataset
- Compare results
- Include in supplementary materials

### 7. Comparison to Existing Tools

**Show NeuroInsight is equivalent/better:**

| Method | Processing Time | Accuracy | GPU Required |
|--------|----------------|----------|--------------|
| FreeSurfer | 8-12 hours | Gold standard | No |
| FastSurfer (standalone) | 1-5 min | 0.95 correlation | Yes |
| **NeuroInsight** | **2-5 min** | **0.95+ correlation** | **Optional** |

**Advantages to highlight:**
- Faster than FreeSurfer
- User-friendly web interface
- No command-line expertise needed
- Automated pipeline reduces human error
- Works on any platform (Docker)

### 8. Sensitivity Analysis

**Test robustness:**
- Different scan parameters (resolution, field strength)
- Different populations (age ranges, pathologies)
- Different scanner manufacturers (GE, Siemens, Philips)

### 9. Statistical Analysis Documentation

**Include in methods:**
```python
# Example statistical analysis
from scipy.stats import ttest_ind, mannwhitneyu
import pandas as pd

# Load results
df = pd.read_csv('neuroinsight_results.csv')

# Compare groups
group1 = df[df['group'] == 'control']['left_volume']
group2 = df[df['group'] == 'patient']['left_volume']

# T-test
t, p = ttest_ind(group1, group2)
print(f"t={t:.2f}, p={p:.4f}")

# Effect size (Cohen's d)
d = (group1.mean() - group2.mean()) / pooled_std
```

---

## 📊 Publication-Ready Checklist

Before submitting your paper, complete:

### Required for ALL journals:
- [ ] Validation against ground truth (10+ scans)
- [ ] Methods section written
- [ ] Code on GitHub with clear README
- [ ] GitHub release created and tagged
- [ ] Code availability statement in paper
- [ ] Quality control protocol documented
- [ ] Tested on your actual research data
- [ ] Visual inspection of all results
- [ ] Statistical analysis documented

### Required for HIGH-IMPACT journals (Nature, Science, Cell):
- [ ] Independent validation by another lab
- [ ] Comparison to existing tools (FreeSurfer)
- [ ] Sensitivity analysis across scanners/populations
- [ ] Code archived on Zenodo (permanent DOI)
- [ ] Supplementary data/code repository
- [ ] Response to potential reviewer concerns prepared

### Strongly Recommended:
- [ ] Test-retest reliability demonstrated
- [ ] Bland-Altman plots vs. FreeSurfer
- [ ] Sample size/power analysis
- [ ] Pre-registration (if prospective study)
- [ ] Data sharing plan (if possible)

---

## 🎯 Minimum Viable Publication Package

**For a standard neuroscience journal, you need:**

1. **Validation (2-3 days work):**
   - Process 10-20 public dataset scans
   - Compare to FreeSurfer or manual segmentations
   - Calculate correlation (r > 0.95)
   - Create Bland-Altman plot

2. **Methods text (1 hour):**
   - Use template from this document
   - Adapt to your specific study
   - Cite FastSurfer properly

3. **Code availability (30 minutes):**
   - GitHub release tagged
   - README updated
   - Installation instructions clear

4. **Your study results (your research):**
   - Process all your scans
   - QC all results
   - Run statistics
   - Interpret findings

---

## 📝 Example Publications Using Similar Tools

### Study your citations:

**FastSurfer papers to cite:**
```
Henschel L, et al. FastSurfer - A fast and accurate deep learning 
based neuroimaging pipeline. NeuroImage. 2020;219:117012.

Henschel L, et al. FastSurferVINN: Building resolution-independence 
into deep learning segmentation methods. NeuroImage. 2022;251:118933.
```

**How others describe automated methods:**
> "Automated hippocampal segmentation was performed using... 
> This approach has been validated against manual segmentation with 
> high agreement (Dice coefficient > 0.85)..."

### Example methods from published papers:

**Nature Neuroscience style:**
> "T1-weighted MRI scans were processed using NeuroInsight 
> (version 1.0.0, github.com/username/neuroinsight), an automated 
> pipeline based on the FastSurfer algorithm. Bilateral hippocampal 
> volumes were extracted and normalized to total intracranial volume..."

**Journal of Neuroscience style:**
> "Hippocampal volumes were quantified using automated segmentation 
> (NeuroInsight v1.0; FastSurfer 2.4.2). The pipeline has been validated 
> against manual tracing (r=0.96, p<0.001; Supplementary Fig. 1)..."

---

## ⏱️ Timeline to Publication-Ready

### This Week (5-10 hours):
- [ ] Download public dataset (ADNI, OASIS)
- [ ] Process 10-20 scans through NeuroInsight
- [ ] Download comparison data (FreeSurfer or manual)
- [ ] Calculate correlation and make plots

### Next Week (3-5 hours):
- [ ] Write methods section
- [ ] Create GitHub release
- [ ] Document QC protocol
- [ ] Test on pilot data from your study

### Within Month:
- [ ] Process all your research scans
- [ ] Complete QC
- [ ] Run statistical analyses
- [ ] Ready to submit paper!

---

## 🚀 Quick Start Validation Protocol

### Step 1: Get Test Data (1 hour)

```bash
# Download OASIS-1 dataset (public, has manual traces)
wget https://www.oasis-brains.org/files/oasis_cross-sectional_disc1.tar.gz

# Or use ADNI if you have access
```

### Step 2: Process with NeuroInsight (2 hours)

```bash
# Upload 10 scans to NeuroInsight
# Download results CSV
```

### Step 3: Compare Results (2 hours)

```python
# validation_script.py
import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

# Your results
neuro = pd.read_csv('neuroinsight_results.csv')

# Ground truth
truth = pd.read_csv('oasis_manual_volumes.csv')

# Correlation
r_left, p = pearsonr(neuro['left_volume'], truth['left_volume'])
r_right, _ = pearsonr(neuro['right_volume'], truth['right_volume'])

print(f"Left hippocampus: r={r_left:.3f}, p={p:.4f}")
print(f"Right hippocampus: r={r_right:.3f}")

# Plot
plt.figure(figsize=(10, 5))
plt.subplot(121)
plt.scatter(truth['left_volume'], neuro['left_volume'])
plt.xlabel('Manual Segmentation (mm³)')
plt.ylabel('NeuroInsight (mm³)')
plt.title(f'Left Hippocampus (r={r_left:.3f})')
plt.plot([2500, 5000], [2500, 5000], 'r--')

plt.subplot(122)
plt.scatter(truth['right_volume'], neuro['right_volume'])
plt.xlabel('Manual Segmentation (mm³)')
plt.ylabel('NeuroInsight (mm³)')
plt.title(f'Right Hippocampus (r={r_right:.3f})')
plt.plot([2500, 5000], [2500, 5000], 'r--')

plt.tight_layout()
plt.savefig('validation_plot.png', dpi=300)
print("Saved validation_plot.png")
```

### Step 4: Create Supplementary Figure

Include in your paper's supplementary materials:
- Correlation plots
- Bland-Altman plots
- Table of validation results

---

## 📚 Resources

### Validation Datasets:
- **OASIS**: https://www.oasis-brains.org/
- **ADNI**: https://adni.loni.usc.edu/
- **HCP**: https://www.humanconnectome.org/

### Statistical Tools:
- **Python**: scipy, statsmodels, pingouin
- **R**: cor.test(), lm(), ggplot2

### Example Papers:
Search PubMed for: "automated hippocampal segmentation validation"

---

## ✅ Summary

**Is NeuroInsight publication-ready?**

**Answer:** **Almost!** You need validation first.

**Minimum requirements:**
1. Validate on 10-20 public scans (1 day work)
2. Write methods section (1 hour)
3. Create GitHub release (15 minutes)
4. Process your research data with QC (ongoing)

**Once you complete validation, you can confidently:**
- Use NeuroInsight results in your paper
- Cite it as a validated method
- Share it with reviewers
- Publish your findings

**Timeline:** 1-2 weeks to fully publication-ready

---

## 🎯 Next Steps

1. **This week:** Run validation study
2. **Next week:** Write methods section
3. **This month:** Process your research scans
4. **Submit paper!**

Good luck with your publication! 🎉


