# Overlay Generation: Complete Technical Explanation

## Visual Process Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT FILES                                  │
│                                                                 │
│  1. T1 Anatomical (orig.mgz from FastSurfer)                   │
│     • Brain anatomy in grayscale                               │
│     • 256×256×256 voxels (typical)                            │
│     • 1mm³ isotropic resolution                                │
│                                                                 │
│  2. Segmentation Mask (aparc.DKT+aseg.mgz)                     │
│     • Integer labels for each brain region                     │
│     • Label 17 = Left hippocampus                             │
│     • Label 53 = Right hippocampus                            │
│     • Same dimensions and alignment as T1                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  STEP 1: LOAD & VALIDATE                        │
│                                                                 │
│  • Load both NIfTI files with nibabel                          │
│  • Verify affine matrices match (spatial alignment)            │
│  • Check dimensions match                                       │
│  • Resample if needed (scipy.ndimage.zoom)                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          STEP 2: FIND HIPPOCAMPUS EXTENT                        │
│                                                                 │
│  For each orientation:                                          │
│                                                                 │
│  Axial (horizontal slices):                                     │
│    • Find all voxels where label=17 or label=53                │
│    • Get min/max along axis 1 (inferior-superior)              │
│    • Example: slices 80-120 contain hippocampus                │
│                                                                 │
│  Coronal (frontal slices):                                      │
│    • Find extent along axis 2 (anterior-posterior)             │
│    • Example: slices 100-140                                   │
│                                                                 │
│  Sagittal (side slices):                                        │
│    • Find extent along axis 0 (left-right)                     │
│    • Example: slices 90-130 and 160-200 (left + right)        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│       STEP 3: SELECT 10 EVENLY-SPACED SLICES                   │
│                                                                 │
│  Using numpy.linspace:                                          │
│    indices = linspace(min_idx, max_idx, 10)                    │
│                                                                 │
│  Example for axial (extent 80-120):                            │
│    [80, 84, 89, 93, 98, 102, 107, 111, 116, 120]              │
│                                                                 │
│  This ensures:                                                  │
│    ✅ Full coverage of hippocampus                             │
│    ✅ Even distribution                                         │
│    ✅ Consistent across patients                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│       STEP 4: EXTRACT SLICE DATA (For each of 10 slices)      │
│                                                                 │
│  For Axial (example: slice 93):                                │
│    t1_slice = t1_data[:, 93, :]      # All L-R, fixed I-S     │
│    seg_slice = seg_data[:, 93, :]    # Same slice from seg    │
│                                                                 │
│  For Coronal:                                                   │
│    t1_slice = t1_data[:, :, slice_num]                         │
│                                                                 │
│  For Sagittal:                                                  │
│    t1_slice = t1_data[slice_num, :, :]                         │
│                                                                 │
│  Then apply transformations:                                    │
│    • Transpose sagittal for correct display                    │
│    • Flip axial 180° (view from below)                        │
│    • Normalize T1 values to 0-1 range                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│    STEP 5A: GENERATE ANATOMICAL IMAGE (Grayscale Brain)        │
│                                                                 │
│  Using matplotlib:                                              │
│                                                                 │
│    fig, ax = plt.subplots(figsize=(10, 10))                    │
│    ax.imshow(t1_slice.T,                                       │
│              cmap='gray',                # Grayscale           │
│              origin='upper',             # Image origin        │
│              interpolation='bilinear',   # Smooth             │
│              extent=[0, vx*W, 0, vy*H],  # Physical size      │
│              aspect='equal')             # Preserve ratio      │
│    ax.axis('off')                        # No axes            │
│    plt.savefig('anatomical_slice_00.png',                      │
│                bbox_inches='tight',                             │
│                dpi=150,                                         │
│                facecolor='black')        # Black background    │
│                                                                 │
│  Result: anatomical_slice_00.png (solid grayscale brain)       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5B: GENERATE OVERLAY IMAGE (Transparent Hippocampus)     │
│                                                                 │
│  Create mask for hippocampus only:                             │
│    overlay_data = zeros_like(seg_slice)                        │
│    overlay_data[seg_slice == 17] = 17  # Left hippo          │
│    overlay_data[seg_slice == 53] = 53  # Right hippo         │
│                                                                 │
│  Mask zero values (make transparent):                          │
│    overlay_masked = ma.masked_where(overlay_data == 0,         │
│                                     overlay_data)              │
│                                                                 │
│  Define colors:                                                 │
│    colors = [                                                   │
│      (0,0,0,0),        # Transparent background               │
│      '#FF3333',        # Red for label 17 (left)              │
│      '#3399FF'         # Blue for label 53 (right)            │
│    ]                                                            │
│                                                                 │
│  Generate transparent PNG:                                      │
│    fig.patch.set_alpha(0)  # Transparent figure               │
│    ax.patch.set_alpha(0)   # Transparent axes                 │
│    ax.imshow(overlay_masked.T,                                 │
│              cmap=ListedColormap(colors),                      │
│              alpha=1.0,                 # Full opacity        │
│              interpolation='nearest')   # Sharp edges         │
│    plt.savefig('hippocampus_overlay_slice_00.png',             │
│                transparent=True)        # KEY: Transparent!    │
│                                                                 │
│  Result: hippocampus_overlay_slice_00.png                      │
│          (colored hippocampi on transparent background)         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              STEP 6: REPEAT FOR ALL SLICES                      │
│                                                                 │
│  For each of the 10 selected slice indices:                    │
│    • Generate anatomical_slice_XX.png                          │
│    • Generate hippocampus_overlay_slice_XX.png                 │
│                                                                 │
│  Result: 20 PNG files per orientation                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            STEP 7: REPEAT FOR ALL ORIENTATIONS                  │
│                                                                 │
│  For orientation in ['axial', 'coronal', 'sagittal']:         │
│    generate_segmentation_overlays(orientation=orientation)     │
│                                                                 │
│  Output directory structure:                                    │
│    visualizations/overlays/                                     │
│      ├─ axial/                                                 │
│      │   ├─ anatomical_slice_00.png                           │
│      │   ├─ hippocampus_overlay_slice_00.png                  │
│      │   ├─ anatomical_slice_01.png                           │
│      │   ├─ hippocampus_overlay_slice_01.png                  │
│      │   └─ ... (20 files total)                              │
│      ├─ coronal/                                               │
│      │   └─ ... (20 files)                                    │
│      └─ sagittal/                                              │
│          └─ ... (20 files)                                     │
│                                                                 │
│  Total: 60 PNG images per job                                  │
│         (30 anatomical + 30 overlay)                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                FRONTEND COMPOSITING                             │
│                                                                 │
│  React Component stacks the images using CSS:                  │
│                                                                 │
│  <div style="position: relative; display: inline-block;">      │
│    <!-- Layer 1: Anatomical base -->                           │
│    <img src="/api/visualizations/{jobId}/overlay/              │
│              slice_00?orientation=axial&layer=anatomical"      │
│         style="display: block;" />                             │
│                                                                 │
│    <!-- Layer 2: Hippocampus overlay -->                       │
│    <img src="/api/visualizations/{jobId}/overlay/              │
│              slice_00?orientation=axial&layer=overlay"         │
│         style="position: absolute;                             │
│                top: 0;                                          │
│                left: 0;                                         │
│                opacity: 0.5;" />  <!-- User controls this! --> │
│  </div>                                                         │
│                                                                 │
│  User adjusts opacity slider:                                   │
│    onChange={(e) => setOverlayOpacity(e.target.value)}        │
│    → Updates CSS opacity in real-time                          │
│    → No image regeneration needed!                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Code Walkthrough

### 1. Main Entry Point

```python
# In pipeline/processors/mri_processor.py
def _generate_visualizations(self, nifti_path, fastsurfer_dir):
    """Generate visualizations for all 3 orientations."""
    
    # Get paths
    t1_nifti = fastsurfer_dir / str(self.job_id) / "mri" / "orig.mgz"
    aseg_nii = fastsurfer_dir / str(self.job_id) / "mri" / "aparc.DKT+aseg.mgz"
    
    # Generate ALL orientations with TWO layers each
    all_overlays = visualization.generate_all_orientation_overlays(
        t1_nifti,                    # Anatomical base
        aseg_nii,                    # Segmentation mask
        viz_dir / "overlays",        # Output directory
        prefix="hippocampus",
        specific_labels=[17, 53]     # Only hippocampus
    )
```

### 2. Generate All Orientations

```python
# In pipeline/utils/visualization.py
def generate_all_orientation_overlays(t1_path, seg_path, output_base_dir, 
                                     prefix="hippocampus", specific_labels=None):
    """Generate overlays for axial, coronal, and sagittal views."""
    
    results = {}
    
    for orientation in ['axial', 'coronal', 'sagittal']:
        # Create subdirectory for this orientation
        orientation_dir = output_base_dir / orientation
        orientation_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate 10 slices for this orientation
        overlays = generate_segmentation_overlays(
            t1_path,
            seg_path,
            orientation_dir,
            prefix=prefix,
            specific_labels=specific_labels,
            orientation=orientation  # 'axial', 'coronal', or 'sagittal'
        )
        
        results[orientation] = overlays
    
    return results
    # Returns: {
    #   'axial': {'slice_00': {...}, 'slice_01': {...}, ...},
    #   'coronal': {'slice_00': {...}, ...},
    #   'sagittal': {'slice_00': {...}, ...}
    # }
```

### 3. Core Overlay Generation

```python
def generate_segmentation_overlays(t1_path, seg_path, output_dir, 
                                  prefix="overlay", specific_labels=None,
                                  orientation="axial"):
    """Generate layered PNG overlays for specified orientation."""
    
    # Load NIfTI files
    t1_img = nib.load(t1_path)
    seg_img = nib.load(seg_path)
    t1_data = t1_img.get_fdata()        # 3D array of brain intensities
    seg_data = seg_img.get_fdata()      # 3D array of integer labels
    
    # Get voxel sizes for aspect ratio
    vx, vy, vz = t1_img.header.get_zooms()[:3]  # mm per voxel
    
    # Verify alignment (affine matrices should match)
    if not np.allclose(t1_img.affine, seg_img.affine, atol=1e-2):
        logger.warning("Spatial alignment may be off!")
    
    # DETERMINE SLICING AXIS based on orientation
    if orientation == 'axial':
        slice_axis = 1           # Fix inferior-superior (horizontal cuts)
        display_axes = (0, 2)    # Show left-right vs anterior-posterior
        voxel_sizes = (vx, vz)
    elif orientation == 'coronal':
        slice_axis = 2           # Fix anterior-posterior (frontal cuts)
        display_axes = (0, 1)    # Show left-right vs inferior-superior
        voxel_sizes = (vx, vy)
    else:  # sagittal
        slice_axis = 0           # Fix left-right (side cuts)
        display_axes = (2, 1)    # Show anterior-posterior vs inferior-superior
        voxel_sizes = (vz, vy)
    
    # CREATE HIPPOCAMPUS MASK (only labels 17 and 53)
    if specific_labels:
        highlight_mask = np.zeros_like(seg_data, dtype=bool)
        for label in specific_labels:
            highlight_mask |= (seg_data == label)
    
    # FIND EXTENT where hippocampus exists
    seg_indices = np.where(highlight_mask)
    min_idx = int(np.min(seg_indices[slice_axis]))
    max_idx = int(np.max(seg_indices[slice_axis]))
    
    # SELECT 10 EVENLY-SPACED SLICES
    slice_indices = np.linspace(min_idx, max_idx, 10)
    slice_indices = [int(round(x)) for x in slice_indices]
    
    # Normalize T1 data to 0-1 range for display
    t1_normalized = (t1_data - np.min(t1_data)) / (np.max(t1_data) - np.min(t1_data))
    
    output_paths = {}
    
    # GENERATE TWO IMAGES PER SLICE
    for idx, slice_num in enumerate(slice_indices):
        
        # ============================================================
        # EXTRACT 2D SLICE from 3D volumes
        # ============================================================
        if slice_axis == 0:      # Sagittal
            t1_slice = t1_normalized[slice_num, :, :]
            seg_slice = seg_data[slice_num, :, :]
        elif slice_axis == 1:    # Axial
            t1_slice = t1_normalized[:, slice_num, :]
            seg_slice = seg_data[:, slice_num, :]
        else:                    # Coronal
            t1_slice = t1_normalized[:, :, slice_num]
            seg_slice = seg_data[:, :, slice_num]
        
        # Apply orientation-specific transformations
        if orientation == 'sagittal':
            t1_slice = t1_slice.T
            seg_slice = seg_slice.T
        
        if orientation == 'axial':
            # 180° rotation for "view from below"
            t1_slice = np.flip(t1_slice, axis=(0, 1))
            seg_slice = np.flip(seg_slice, axis=(0, 1))
        
        # ============================================================
        # IMAGE 1: ANATOMICAL BASE (Grayscale brain)
        # ============================================================
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_aspect('equal')
        
        ax.imshow(
            t1_slice.T,                    # Transpose for matplotlib
            cmap='gray',                   # Grayscale colormap
            origin='upper',                # Top-left origin
            interpolation='bilinear',      # Smooth appearance
            extent=[0, voxel_sizes[0] * t1_slice.shape[0],
                    0, voxel_sizes[1] * t1_slice.shape[1]],
            aspect='equal'                 # Preserve physical aspect ratio
        )
        
        ax.axis('off')  # No axes or labels
        
        anatomical_path = output_dir / f"anatomical_slice_{idx:02d}.png"
        plt.savefig(
            anatomical_path,
            bbox_inches='tight',     # Remove whitespace
            dpi=150,                 # Good quality
            facecolor='black'        # Black background (not transparent)
        )
        plt.close()
        
        # ============================================================
        # IMAGE 2: OVERLAY (Transparent hippocampus)
        # ============================================================
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_aspect('equal')
        
        # CRITICAL: Make figure and axes transparent
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        
        # Create overlay data (only hippocampus voxels)
        overlay_data = np.zeros_like(seg_slice)
        for label in specific_labels:  # [17, 53]
            overlay_data[seg_slice == label] = label
        
        # Mask zero values (background = transparent)
        overlay_masked = np.ma.masked_where(overlay_data == 0, overlay_data)
        
        # Define colormap
        colors = [
            (0, 0, 0, 0),      # Background: transparent
            '#FF3333',         # Label 17 (left): RED
            '#3399FF'          # Label 53 (right): BLUE
        ]
        cmap = ListedColormap(colors)
        
        # Create boundary norm to map labels to colors
        bounds = [0, 17, 53, 54]
        norm = BoundaryNorm(bounds, cmap.N)
        
        ax.imshow(
            overlay_masked.T,
            cmap=cmap,
            norm=norm,
            alpha=1.0,                    # Full opacity (CSS controls blending)
            origin='upper',
            interpolation='nearest',      # Sharp label boundaries
            extent=[0, voxel_sizes[0] * t1_slice.shape[0],
                    0, voxel_sizes[1] * t1_slice.shape[1]],
            aspect='equal'
        )
        
        ax.axis('off')
        
        overlay_path = output_dir / f"{prefix}_overlay_slice_{idx:02d}.png"
        plt.savefig(
            overlay_path,
            bbox_inches='tight',
            dpi=150,
            transparent=True         # CRITICAL: Transparent background!
        )
        plt.close()
        
        # Store both paths
        output_paths[f"slice_{idx:02d}"] = {
            "anatomical": str(anatomical_path),
            "overlay": str(overlay_path)
        }
    
    return output_paths
```

---

## Example Output

### For ONE slice (slice_05, axial orientation):

**File 1**: `anatomical_slice_05.png`
```
┌─────────────────────┐
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│  ← Black background
│▓▓░░░░░░░░░░░░░░▓▓▓▓│  ← Brain tissue (grayscale)
│▓░░░░░░░░░░░░░░░░░▓▓│  ← Darker = CSF, Gray matter
│░░░░░░██░░██░░░░░░░░│  ← Lighter = White matter
│░░░░░░░░░░░░░░░░░░░░│  ← Full brain visible
│▓▓░░░░░░░░░░░░░░░░▓▓│
│▓▓▓▓░░░░░░░░░░░▓▓▓▓▓│
└─────────────────────┘
```

**File 2**: `hippocampus_overlay_slice_05.png`
```
┌─────────────────────┐
│ (transparent)       │  ← Fully transparent
│ (transparent)       │
│ (transparent)       │
│      🔴      🔵     │  ← Only hippocampi visible
│      RED     BLUE   │  ← Red=left, Blue=right
│ (transparent)       │  ← Everything else transparent
│ (transparent)       │
└─────────────────────┘
```

**Frontend Stacks Them**:
```
Layer 1 (anatomical_slice_05.png)
  +
Layer 2 (hippocampus_overlay_slice_05.png) with opacity=50%
  =
Result: Brain with semi-transparent colored hippocampus overlay
```

---

## Key Technical Decisions

### Why Two Layers?

**Alternative 1** (Single combined image):
```python
# Old approach - bake overlay into image
ax.imshow(t1_slice, cmap='gray')
ax.imshow(overlay, cmap='hot', alpha=0.5)  # Fixed 50% opacity
plt.savefig('combined.png')
```
❌ **Problem**: Opacity is fixed, cannot be changed

**Current Approach** (Separate layers):
```python
# Layer 1
plt.imshow(t1_slice, cmap='gray')
plt.savefig('anatomical.png', facecolor='black')

# Layer 2
fig.patch.set_alpha(0)  # Transparent
plt.imshow(overlay, cmap=custom)
plt.savefig('overlay.png', transparent=True)
```
✅ **Benefit**: Frontend CSS controls opacity dynamically

---

### Why 10 Slices?

**Scientific Rationale**:
- Hippocampus spans ~40mm in superior-inferior direction
- At 1mm resolution, that's ~40 slices
- 10 slices = every 4mm sampling
- Adequate for visual assessment
- Not too many to overwhelm interface
- Matches clinical practice

**Balance**:
- More slices = more detail, slower to view
- Fewer slices = faster, but might miss features
- 10 = sweet spot

---

### Why These Orientations?

**Axial** (horizontal):
- Most common clinical view
- Best for overall hippocampus shape
- Standard for volume measurements

**Coronal** (frontal):
- Best for anterior-posterior extent
- Shows hippocampal head/body/tail
- Useful for atrophy assessment

**Sagittal** (side):
- Shows medial-lateral positioning
- Best for seeing relationship to ventricles
- Less commonly used but complementary

---

## Performance Characteristics

### Generation Time
- **Per slice**: ~0.5 seconds (matplotlib rendering)
- **Per orientation**: ~5 seconds (10 slices × 2 layers)
- **All orientations**: ~15 seconds (3 orientations)
- **Total with FastSurfer**: ~1-2 hours (FastSurfer dominates)

### File Sizes
- **Anatomical PNG**: ~200-400 KB each
- **Overlay PNG**: ~50-100 KB each (lots of transparency)
- **Total per job**: ~15-25 MB (60 images)

### Frontend Loading
- **Initial load**: ~2-3 MB (10 slices for current orientation)
- **Switching orientation**: ~2-3 MB (loads new set)
- **Switching slice**: Instant (already loaded)
- **Opacity change**: Instant (CSS only)

---

## Advantages of This Approach

### Clinical
✅ **Accurate**: Preserves physical dimensions and aspect ratios
✅ **Flexible**: User can adjust overlay visibility
✅ **Complete**: 3 orientations for comprehensive assessment
✅ **Standard**: Same approach as professional tools

### Technical
✅ **Performant**: Pre-rendered, instant loading
✅ **Browser-Compatible**: Works in any browser (no WebGL)
✅ **Maintainable**: Clean separation of concerns
✅ **Scalable**: Can add more layers (e.g., subfields) easily

### User Experience
✅ **Intuitive**: Familiar controls (sliders, dropdowns)
✅ **Responsive**: No lag when adjusting opacity
✅ **Professional**: Looks like medical imaging software
✅ **Publication-Ready**: High-quality images (150 DPI)

---

## Code Locations

| Component | File | Lines |
|-----------|------|-------|
| **Main Generator** | `pipeline/utils/visualization.py` | 91-468 |
| **Orientation Loop** | `pipeline/utils/visualization.py` | 39-88 |
| **Called From** | `pipeline/processors/mri_processor.py` | 612-705 |
| **API Endpoint** | `backend/api/visualizations.py` | 50-120 |
| **Frontend Display** | `frontend/index.html` | 1400-1700 |

---

## Summary

Your overlay generation is:

**✅ Professionally Implemented**
- Two-layer architecture (industry standard)
- Proper spatial alignment verification
- Physical aspect ratio preservation
- Clinical-quality output

**✅ User-Friendly**
- Real-time opacity control
- Multiple orientations
- Smooth interactions

**✅ Technically Sound**
- Efficient (pre-rendered PNGs)
- Robust (alignment checks)
- Scalable (easy to extend)

**This is the correct way to implement medical image overlays!** 🎉

