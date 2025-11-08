# Overlay Generation: Finding Hippocampus & Color Coding Explained

## Part 1: Finding Where Hippocampus Exists

### The Problem

Given a 3D brain volume (256×256×256 voxels), the hippocampus only occupies a small region. We need to:
1. Find where it exists along each axis
2. Select the most relevant slices to show

### The Solution: numpy.where()

**Code** (`pipeline/utils/visualization.py`, lines 193-221):

```python
# Step 1: Create a boolean mask of ONLY hippocampus voxels
specific_labels = [17, 53]  # 17=left, 53=right hippocampus

highlight_mask = np.zeros_like(seg_data, dtype=bool)  # All False initially
for label in specific_labels:
    highlight_mask |= (seg_data == label)
    # |= means OR assignment
    # This sets True wherever seg_data equals 17 OR 53

# Now highlight_mask is a 3D boolean array:
# True = hippocampus voxel
# False = everything else
```

**Visual Example**:

```
seg_data (3D array of integer labels):
  0 = background
  2 = left cerebral white matter
  17 = LEFT HIPPOCAMPUS ← We want this!
  41 = left cerebral cortex
  53 = RIGHT HIPPOCAMPUS ← We want this!
  ...

After creating highlight_mask:
  highlight_mask[x,y,z] = True  if seg_data[x,y,z] == 17 or 53
  highlight_mask[x,y,z] = False otherwise
```

### Finding the Extent

**Code** (lines 209-221):

```python
# Step 2: Find where hippocampus exists along the slicing axis
seg_indices = np.where(highlight_mask)
# np.where returns (x_coords, y_coords, z_coords) of all True voxels

# For AXIAL orientation, we slice along axis 1 (inferior-superior)
# So we look at y_coords:
slice_axis = 1  # For axial

# Get the minimum and maximum indices where hippocampus exists
min_idx = int(np.min(seg_indices[slice_axis]))
max_idx = int(np.max(seg_indices[slice_axis]))

# Example result:
# min_idx = 82  (hippocampus starts at slice 82)
# max_idx = 118 (hippocampus ends at slice 118)
# Total span: 36 slices contain hippocampus
```

**Visual Example (Axial - Inferior to Superior)**:

```
Brain volume along axis 1 (inferior-superior):

Slice 0:    [          ] ← Bottom of brain, no hippocampus
Slice 40:   [  brain   ] ← Mid-brain, no hippocampus yet
Slice 80:   [  brain   ] ← Still no hippocampus
Slice 82:   [🔴brain  ] ← FIRST hippocampus voxel! (min_idx)
Slice 90:   [🔴🔵brain] ← More hippocampus
Slice 100:  [🔴🔵brain] ← Peak hippocampus visibility
Slice 110:  [🔴🔵brain] ← Still visible
Slice 118:  [🔴 brain ] ← LAST hippocampus voxel! (max_idx)
Slice 120:  [  brain   ] ← No more hippocampus
Slice 160:  [  brain   ] ← Upper brain
Slice 255:  [          ] ← Top of brain

np.where(highlight_mask) finds ALL voxels marked 🔴 or 🔵
Then we take min and max along axis 1:
  min_idx = 82
  max_idx = 118
```

### Selecting 10 Evenly-Spaced Slices

**Code** (lines 223-231):

```python
# Step 3: Generate 10 evenly distributed slices
num_slices = 10

slice_indices_float = np.linspace(min_idx, max_idx, num_slices)
# numpy.linspace generates evenly-spaced numbers

# Example:
# np.linspace(82, 118, 10)
# Returns: [82.0, 86.0, 90.0, 94.0, 98.0, 102.0, 106.0, 110.0, 114.0, 118.0]

slice_indices = [int(round(x)) for x in slice_indices_float]
# Rounds to integers: [82, 86, 90, 94, 98, 102, 106, 110, 114, 118]
```

**Visual Result**:

```
Hippocampus extent: slices 82-118 (36 slices total)

Selected 10 slices:
  ↓
  82  ──┐
  86    │
  90    │
  94    ├─ Evenly distributed
  98    │   (every 4 slices)
  102   │
  106   │
  110   │
  114   │
  118 ──┘

This ensures we capture the ENTIRE hippocampus
from inferior (82) to superior (118) with even sampling.
```

### Different for Each Orientation

**For Axial** (horizontal slices):
```python
slice_axis = 1  # Slice along inferior-superior axis
# Find extent: np.where(highlight_mask)[1]
# Example: min=82, max=118
```

**For Coronal** (frontal slices):
```python
slice_axis = 2  # Slice along anterior-posterior axis
# Find extent: np.where(highlight_mask)[2]
# Example: min=95, max=145
```

**For Sagittal** (side slices):
```python
slice_axis = 0  # Slice along left-right axis
# Find extent: np.where(highlight_mask)[0]
# Example for LEFT hippocampus: min=90, max=115
#         for RIGHT hippocampus: min=140, max=165
# Takes the overall extent: min=90, max=165
```

---

## Part 2: How Color Coding Happens

### The Challenge

We have:
- Segmentation data with integer labels (0, 1, 2, ..., 17, ..., 53, ...)
- Need to map specific labels to specific colors
- Everything else should be transparent

### The Solution: Custom Colormap with BoundaryNorm

**Code** (`pipeline/utils/visualization.py`, lines 396-438):

```python
# Step 1: Extract ONLY hippocampus labels from the slice
overlay_data = np.zeros_like(seg_slice)  # Start with all zeros

for label in specific_labels:  # specific_labels = [17, 53]
    overlay_data[seg_slice == label] = label
    # Where seg_slice has label 17, set overlay_data to 17
    # Where seg_slice has label 53, set overlay_data to 53
    # Everything else stays 0

# Step 2: Mask the zero values (make them transparent)
overlay_masked = np.ma.masked_where(overlay_data == 0, overlay_data)
# np.ma.masked_where creates a masked array
# Masked values (0) will be transparent in the image
```

**Visual Example (One Slice)**:

```
seg_slice (original segmentation):
┌──────────────────────────┐
│ 0  0  0  0  0  0  0  0  │ ← 0 = background
│ 0  2  2  2  2  2  2  0  │ ← 2 = white matter
│ 0  2 41 41 41 41  2  0  │ ← 41 = cortex
│ 0  2 41 17 17 41  2  0  │ ← 17 = LEFT HIPPOCAMPUS!
│ 0  2 41 41 41 41  2  0  │
│ 0  2 41 53 53 41  2  0  │ ← 53 = RIGHT HIPPOCAMPUS!
│ 0  2  2  2  2  2  2  0  │
│ 0  0  0  0  0  0  0  0  │
└──────────────────────────┘

After extracting only labels 17 and 53:
overlay_data = np.zeros_like(seg_slice)
for label in [17, 53]:
    overlay_data[seg_slice == label] = label

overlay_data (filtered):
┌──────────────────────────┐
│ 0  0  0  0  0  0  0  0  │ ← Everything else becomes 0
│ 0  0  0  0  0  0  0  0  │
│ 0  0  0  0  0  0  0  0  │
│ 0  0  0 17 17  0  0  0  │ ← Only 17 remains
│ 0  0  0  0  0  0  0  0  │
│ 0  0  0 53 53  0  0  0  │ ← Only 53 remains
│ 0  0  0  0  0  0  0  0  │
│ 0  0  0  0  0  0  0  0  │
└──────────────────────────┘

After masking zeros:
overlay_masked (with transparency):
┌──────────────────────────┐
│ ✗  ✗  ✗  ✗  ✗  ✗  ✗  ✗ │ ← ✗ = masked (transparent)
│ ✗  ✗  ✗  ✗  ✗  ✗  ✗  ✗ │
│ ✗  ✗  ✗  ✗  ✗  ✗  ✗  ✗ │
│ ✗  ✗  ✗ 17 17  ✗  ✗  ✗ │ ← 17 = will be colored RED
│ ✗  ✗  ✗  ✗  ✗  ✗  ✗  ✗ │
│ ✗  ✗  ✗ 53 53  ✗  ✗  ✗ │ ← 53 = will be colored BLUE
│ ✗  ✗  ✗  ✗  ✗  ✗  ✗  ✗ │
│ ✗  ✗  ✗  ✗  ✗  ✗  ✗  ✗ │
└──────────────────────────┘
```

### Creating the Custom Colormap

**Code** (lines 408-426):

```python
# Step 3: Define color mapping
colors = [(0, 0, 0, 0)]  # Index 0: Transparent (RGBA with alpha=0)
bounds = [0]              # Bound 0: for values < 17

for label in specific_labels:  # [17, 53]
    if label == 17:  # Left-Hippocampus
        colors.append('#FF3333')  # Bright red
    elif label == 53:  # Right-Hippocampus
        colors.append('#3399FF')  # Bright blue
    else:
        colors.append('#FFAA00')  # Orange for others
    bounds.append(label)

bounds.append(max(specific_labels) + 1)  # Upper bound

# Final result:
# colors = [(0,0,0,0), '#FF3333', '#3399FF']
# bounds = [0, 17, 53, 54]

# Create matplotlib colormap
cmap = ListedColormap(colors)
norm = BoundaryNorm(bounds, cmap.N)
```

**How BoundaryNorm Works**:

```
BoundaryNorm maps data values to color indices:

bounds = [0, 17, 53, 54]
colors = [transparent, red, blue]

Data value:    Maps to color:
─────────────────────────────
0-16           → colors[0] = transparent
17-52          → colors[1] = RED (#FF3333)
53-53          → colors[2] = BLUE (#3399FF)
54+            → (out of range)

So:
  overlay_data value 17 → RED
  overlay_data value 53 → BLUE
  overlay_data value 0  → TRANSPARENT (masked)
```

### Rendering with Transparency

**Code** (lines 389-394, 429-438):

```python
# Step 4: Set up transparent figure
fig, ax = plt.subplots(figsize=(10, 10))

# CRITICAL: Make figure and axes background transparent
fig.patch.set_alpha(0)  # Figure background alpha = 0 (transparent)
ax.patch.set_alpha(0)   # Axes background alpha = 0 (transparent)

# Step 5: Draw the overlay
ax.imshow(
    overlay_masked.T,           # Transposed for matplotlib
    cmap=cmap,                  # Our custom colormap
    norm=norm,                  # BoundaryNorm for label mapping
    alpha=1.0,                  # Full opacity for colored pixels
    origin='upper',
    interpolation='nearest',    # Sharp boundaries (no blurring)
    extent=[0, width, 0, height],
    aspect='equal'
)

ax.axis('off')  # No axes or labels

# Step 6: Save as transparent PNG
plt.savefig(
    'hippocampus_overlay_slice_00.png',
    bbox_inches='tight',
    dpi=150,
    transparent=True  # CRITICAL: Enables PNG alpha channel
)
```

---

## Real-World Example with Numbers

Let's trace through a real example for **Axial slice 100**:

### Step-by-Step Trace

```python
# INPUT DATA
t1_data.shape = (256, 256, 256)  # 3D brain volume
seg_data.shape = (256, 256, 256)  # 3D segmentation labels

# HIPPOCAMPUS LABELS
specific_labels = [17, 53]

# ============================================================
# PART 1: FIND HIPPOCAMPUS EXTENT
# ============================================================

# Create mask
highlight_mask = np.zeros((256, 256, 256), dtype=bool)

# Find all voxels with label 17 (left hippocampus)
highlight_mask |= (seg_data == 17)
# Count: ~40,000 voxels (typical left hippocampus volume ~4000 mm³)

# Find all voxels with label 53 (right hippocampus)
highlight_mask |= (seg_data == 53)
# Count: ~40,000 voxels (right hippocampus)

# Total: ~80,000 voxels marked True (hippocampus)
#        ~16,700,000 voxels marked False (everything else)

# Find extent along axis 1 (axial slicing)
seg_indices = np.where(highlight_mask)
# Returns: (array of x coords, array of y coords, array of z coords)

# seg_indices[1] = all y-coordinates where hippocampus exists
# Example values: [82, 82, 82, 83, 83, 84, ..., 117, 118, 118]

min_idx = np.min(seg_indices[1])  # Result: 82
max_idx = np.max(seg_indices[1])  # Result: 118

# Interpretation:
# - Hippocampus exists from slice 82 to 118
# - That's 36 slices total (118 - 82 = 36)
# - We'll select 10 evenly-spaced slices from this range

# ============================================================
# SELECT 10 EVENLY-SPACED SLICES
# ============================================================

slice_indices = np.linspace(82, 118, 10)
# Result: [82.0, 86.0, 90.0, 94.0, 98.0, 102.0, 106.0, 110.0, 114.0, 118.0]

slice_indices = [int(round(x)) for x in slice_indices]
# Result: [82, 86, 90, 94, 98, 102, 106, 110, 114, 118]

# ============================================================
# EXTRACT ONE SLICE (slice 100 as example)
# ============================================================

# For axial, we fix axis 1 and take all of axes 0 and 2
slice_num = 100

t1_slice = t1_data[:, 100, :]      # Shape: (256, 256)
seg_slice = seg_data[:, 100, :]    # Shape: (256, 256)

# This gives us a 2D slice at y=100 (horizontal cut through brain)

# ============================================================
# PART 2: COLOR CODING
# ============================================================

# Extract only hippocampus labels from this 2D slice
overlay_data = np.zeros_like(seg_slice)  # All zeros initially

for label in [17, 53]:
    overlay_data[seg_slice == label] = label

# BEFORE (seg_slice at y=100):
# [[0, 0, 0, ..., 0],
#  [0, 2, 2, 2, ..., 0],
#  [0, 2, 41, 17, 17, 41, 53, 53, 2, 0],  ← Mixed labels
#  [0, 2, 41, 17, 17, 41, 53, 53, 2, 0],
#  [0, 2, 2, 2, ..., 0],
#  [0, 0, 0, ..., 0]]

# AFTER (overlay_data):
# [[0, 0, 0, ..., 0],
#  [0, 0, 0, 0, ..., 0],
#  [0, 0, 0, 17, 17, 0, 53, 53, 0, 0],  ← Only 17 and 53 remain
#  [0, 0, 0, 17, 17, 0, 53, 53, 0, 0],
#  [0, 0, 0, 0, ..., 0],
#  [0, 0, 0, ..., 0]]

# Mask zeros (make transparent)
overlay_masked = np.ma.masked_where(overlay_data == 0, overlay_data)

# Create colormap
colors = [
    (0, 0, 0, 0),    # For value 0: transparent
    '#FF3333',       # For value 17: RED
    '#3399FF'        # For value 53: BLUE
]
bounds = [0, 17, 53, 54]

cmap = ListedColormap(colors)
norm = BoundaryNorm(bounds, cmap.N)

# When matplotlib renders overlay_masked with this colormap:
# - Value 0:  → Masked (transparent in PNG)
# - Value 17: → RED pixel in PNG
# - Value 53: → BLUE pixel in PNG
```

---

## Visual Demonstration

### Example Slice Through Hippocampus

**Original Segmentation Labels**:
```
Cross-section at axial slice 100:

     Front (Anterior)
           ↑
           │
    ┌──────┴──────┐
    │   0  0  0   │ ← 0 = background/CSF
    │ 2  2  2  2  │ ← 2 = white matter
    │ 2 41 41 41 2│ ← 41 = cortex
L ──│ 2 41 17 41 2│── R
e   │ 2 41 17 53 2│   i
f   │ 2 41 53 53 2│   g
t   │ 2  2  2  2  │   h
    │   0  0  0   │   t
    └─────────────┘
           │
           ↓
    Back (Posterior)

Legend:
  17 = Left hippocampus
  53 = Right hippocampus
  41 = Cortex
  2 = White matter
  0 = Background
```

**After Extracting Only Labels 17 & 53**:
```
overlay_data:

     Front
       ↑
       │
    ┌──┴──┐
    │ 0 0 │
    │ 0 0 │
    │ 0 0 │
L ──│ 17 0│── R
    │ 17 53│
    │ 0 53│
    │ 0 0 │
    └─────┘
       │
       ↓
    Back

Everything except 17 and 53 → 0
```

**After Color Mapping & Rendering**:
```
Final PNG:

     Front
       ↑
       │
    ┌──┴──┐
    │ □ □ │ ← □ = transparent
    │ □ □ │
    │ □ □ │
L ──│ 🔴 □│── R
    │ 🔴 🔵│
    │ □ 🔵│
    │ □ □ │
    └─────┘
       │
       ↓
    Back

Legend:
  □ = Transparent (0 values, masked)
  🔴 = RED pixels (label 17)
  🔵 = BLUE pixels (label 53)
```

---

## The Complete Pipeline (One Slice)

```python
# INPUT
t1_data: 3D array (256, 256, 256) - brain intensities
seg_data: 3D array (256, 256, 256) - label integers

# STEP 1: Find hippocampus extent
highlight_mask = (seg_data == 17) | (seg_data == 53)
# Boolean 3D array: True where hippocampus, False elsewhere

seg_indices = np.where(highlight_mask)
# Returns coordinates of all True voxels
# seg_indices = (x_coords[], y_coords[], z_coords[])

min_y = np.min(seg_indices[1])  # 82
max_y = np.max(seg_indices[1])  # 118

# STEP 2: Select 10 slices
selected_slices = np.linspace(82, 118, 10)
# [82, 86, 90, 94, 98, 102, 106, 110, 114, 118]

# STEP 3: For slice 100 (example)
t1_slice = t1_data[:, 100, :]      # 2D: (256, 256)
seg_slice = seg_data[:, 100, :]    # 2D: (256, 256)

# STEP 4: Extract hippocampus only
overlay_data = np.zeros_like(seg_slice)
overlay_data[seg_slice == 17] = 17  # Keep left hippo
overlay_data[seg_slice == 53] = 53  # Keep right hippo
# Now overlay_data has: 0s, 17s, and 53s

# STEP 5: Mask zeros
overlay_masked = np.ma.masked_where(overlay_data == 0, overlay_data)
# Masked values will be transparent

# STEP 6: Create color mapping
colors = [(0,0,0,0), '#FF3333', '#3399FF']  # transparent, red, blue
bounds = [0, 17, 53, 54]

# This creates a mapping:
#   0-16   → transparent
#   17-52  → RED
#   53-53  → BLUE

cmap = ListedColormap(colors)
norm = BoundaryNorm(bounds, cmap.N)

# STEP 7: Render
fig.patch.set_alpha(0)  # Transparent background
ax.imshow(overlay_masked.T, cmap=cmap, norm=norm, alpha=1.0)
plt.savefig('overlay.png', transparent=True)

# OUTPUT: PNG with red and blue pixels where hippocampus exists,
#         transparent everywhere else
```

---

## Why This Approach is Clever

### 1. Efficient Label Filtering
```python
# Instead of checking every voxel in a loop (slow):
for x in range(256):
    for y in range(256):
        for z in range(256):
            if seg_data[x,y,z] in [17, 53]:
                highlight_mask[x,y,z] = True  # SLOW!

# We use vectorized numpy operations (fast):
highlight_mask = (seg_data == 17) | (seg_data == 53)  # FAST!
# Processes entire 3D array in one operation
```

### 2. Smart Extent Finding
```python
# np.where() gives us ALL coordinates at once
seg_indices = np.where(highlight_mask)

# Then we can query any axis efficiently:
min_along_axis_0 = np.min(seg_indices[0])  # Left-most hippocampus
max_along_axis_0 = np.max(seg_indices[0])  # Right-most hippocampus
min_along_axis_1 = np.min(seg_indices[1])  # Inferior-most
max_along_axis_1 = np.max(seg_indices[1])  # Superior-most
min_along_axis_2 = np.min(seg_indices[2])  # Anterior-most
max_along_axis_2 = np.max(seg_indices[2])  # Posterior-most

# This tells us exactly where hippocampus exists in 3D space!
```

### 3. Transparent PNG Magic
```python
# The combination of:
fig.patch.set_alpha(0)           # Transparent figure
ax.patch.set_alpha(0)            # Transparent axes
masked_where(data == 0, data)    # Mask background
plt.savefig(..., transparent=True)  # Enable PNG alpha

# Produces a PNG where:
# - Red pixels (label 17) are opaque
# - Blue pixels (label 53) are opaque
# - Everything else is fully transparent
# - No white or black background!
```

---

## Summary

### Finding Hippocampus:
1. **Create boolean mask**: `(seg_data == 17) | (seg_data == 53)`
2. **Find coordinates**: `np.where(mask)` returns all (x,y,z) where True
3. **Get extent**: `min/max` of coordinates along slicing axis
4. **Select slices**: `np.linspace(min, max, 10)` for even distribution

### Color Coding:
1. **Extract labels**: Keep only 17 and 53, set rest to 0
2. **Mask zeros**: Use `np.ma.masked_where` for transparency
3. **Custom colormap**: Map 17→RED, 53→BLUE, 0→transparent
4. **BoundaryNorm**: Maps integer labels to discrete colors
5. **Render**: `plt.savefig(transparent=True)` creates PNG with alpha channel

### Why It Works:
- ✅ Vectorized numpy operations (fast)
- ✅ Discrete color mapping (perfect for integer labels)
- ✅ PNG alpha channel (true transparency)
- ✅ Separate layers (enables frontend opacity control)

**This is the professional way to do medical image overlays!** 🎉

---

## Part 3: Same Process for All 3 Orientations

### The Key Insight

The **exact same algorithms** are used for all 3 orientations. The **only difference** is which axis we query to find the hippocampus extent.

### Unified Code Path

```
                    ┌─────────────────────┐
                    │   START: One Job    │
                    │   One 3D MRI scan   │
                    └──────────┬──────────┘
                               │
                               ↓
              ┌────────────────────────────────┐
              │  STEP 1: Find ALL Hippocampus  │
              │  (Done ONCE for all 3)         │
              │                                │
              │  mask = (seg==17) | (seg==53)  │
              │  coords = np.where(mask)       │
              │                                │
              │  Result:                       │
              │  coords[0] = X: [88...168]     │
              │  coords[1] = Y: [82...118]     │
              │  coords[2] = Z: [95...145]     │
              └────────────────┬───────────────┘
                               │
                     ┌─────────┴─────────┐
                     │   FOR EACH OF 3   │
                     │   ORIENTATIONS    │
                     └─────────┬─────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ↓                    ↓                    ↓
    ┌──────────┐         ┌──────────┐        ┌──────────┐
    │  AXIAL   │         │ CORONAL  │        │SAGITTAL  │
    └────┬─────┘         └────┬─────┘        └────┬─────┘
         │                    │                    │
         ↓                    ↓                    ↓
  ┌─────────────┐      ┌─────────────┐     ┌─────────────┐
  │ Query axis 1│      │ Query axis 2│     │ Query axis 0│
  │ (Y coords)  │      │ (Z coords)  │     │ (X coords)  │
  │             │      │             │     │             │
  │ min = 82    │      │ min = 95    │     │ min = 88    │
  │ max = 118   │      │ max = 145   │     │ max = 168   │
  └─────┬───────┘      └─────┬───────┘     └─────┬───────┘
        │                    │                    │
        ↓                    ↓                    ↓
  ┌─────────────┐      ┌─────────────┐     ┌─────────────┐
  │ linspace    │      │ linspace    │     │ linspace    │
  │ (82,118,10) │      │ (95,145,10) │     │ (88,168,10) │
  │             │      │             │     │             │
  │ 10 slices   │      │ 10 slices   │     │ 10 slices   │
  └─────┬───────┘      └─────┬───────┘     └─────┬───────┘
        │                    │                    │
        ↓                    ↓                    ↓
  ┌─────────────┐      ┌─────────────┐     ┌─────────────┐
  │Extract slice│      │Extract slice│     │Extract slice│
  │data[:,s,:]  │      │data[:,:,s]  │     │data[s,:,:]  │
  └─────┬───────┘      └─────┬───────┘     └─────┬───────┘
        │                    │                    │
        └────────────────────┴────────────────────┘
                             │
                             ↓
                ┌────────────────────────┐
                │ COLOR CODING (SAME!)   │
                │                        │
                │ overlay[seg==17] = 17  │
                │ overlay[seg==53] = 53  │
                │                        │
                │ Mask zeros             │
                │ Map: 17→RED, 53→BLUE   │
                └────────┬───────────────┘
                         │
                         ↓
            ┌────────────────────────────┐
            │ Generate 2 PNGs per slice: │
            │  • anatomical.png (solid)  │
            │  • overlay.png (transparent)│
            └────────┬───────────────────┘
                     │
                     ↓
              ┌──────────────┐
              │ OUTPUT: 60   │
              │ PNG files    │
              │ (~23 MB)     │
              └──────────────┘
```

### The Loop in Code

```python
# From pipeline/utils/visualization.py (lines 67-83)

# STEP 1: Find all hippocampus (ONCE)
highlight_mask = (seg_data == 17) | (seg_data == 53)
seg_indices = np.where(highlight_mask)

# STEP 2: Loop through orientations (3 TIMES)
for orientation in ['axial', 'coronal', 'sagittal']:
    
    # Set which axis to query
    if orientation == 'axial':
        slice_axis = 1    # Query seg_indices[1] for Y extent
    elif orientation == 'coronal':
        slice_axis = 2    # Query seg_indices[2] for Z extent
    else:  # sagittal
        slice_axis = 0    # Query seg_indices[0] for X extent
    
    # Find extent along THIS axis
    min_idx = np.min(seg_indices[slice_axis])
    max_idx = np.max(seg_indices[slice_axis])
    
    # Select 10 slices (SAME METHOD)
    slice_indices = np.linspace(min_idx, max_idx, 10)
    
    # Generate overlays (SAME PROCESS)
    generate_segmentation_overlays(
        orientation=orientation,
        slice_indices=slice_indices
    )
```

### Comparison Table

| Step | Axial | Coronal | Sagittal | How Many Times? |
|------|-------|---------|----------|-----------------|
| Create mask | ✅ | ✅ | ✅ | **1× (shared)** |
| Find coords | ✅ | ✅ | ✅ | **1× (shared)** |
| Query axis | axis 1 (Y) | axis 2 (Z) | axis 0 (X) | **3× (different)** |
| Find extent | 82-118 | 95-145 | 88-168 | **3× (different)** |
| Select slices | linspace | linspace | linspace | **3× (same method)** |
| Extract 2D | `[:,s,:]` | `[:,:,s]` | `[s,:,:]` | **30× (different syntax)** |
| Color code | 17→RED, 53→BLUE | 17→RED, 53→BLUE | 17→RED, 53→BLUE | **30× (identical)** |
| Generate PNGs | 10×2 | 10×2 | 10×2 | **60× (identical)** |

### What's Identical (95% of the code)

✅ **Finding hippocampus**: `np.where()` - runs **once**  
✅ **Color mapping**: 17→RED, 53→BLUE - **always the same**  
✅ **Slice selection**: `np.linspace()` - **same algorithm**  
✅ **Transparency**: Masked arrays - **same technique**  
✅ **PNG generation**: matplotlib - **same settings**

### What's Different (5% of the code)

❇️ **Axis to query**: 0, 1, or 2  
❇️ **How to slice 3D→2D**: `[s,:,:]` vs `[:,s,:]` vs `[:,:,s]`  
❇️ **Minor transforms**: Rotation (axial) or transpose (sagittal)

---

## The Elegance of This Design

This is **excellent software engineering** because:

1. **DRY Principle** (Don't Repeat Yourself)
   - One function handles all 3 orientations
   - No code duplication
   - Easy to maintain

2. **Parameterized Logic**
   - Just pass `orientation="axial"` or `"coronal"` or `"sagittal"`
   - Function adapts automatically
   - Clean, readable code

3. **Efficient**
   - Hippocampus mask created **once**
   - Reused for all 3 orientations
   - No redundant computation

4. **Extensible**
   - Want to add a 4th orientation? Just add to the loop
   - Want different colors? Change the colormap
   - Want more slices? Change `num_slices`

**This is professional-grade code architecture!** 🎉

