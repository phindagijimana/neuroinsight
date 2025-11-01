"""Visualization utilities for MRI segmentation.

Responsibilities
- Extract and convert FastSurfer outputs for visualization
- Generate overlay PNGs with hippocampus highlighted
- Preserve physical aspect ratio and upright orientation for images/text
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from matplotlib.colors import ListedColormap, BoundaryNorm

from backend.core.logging import get_logger
import subprocess

logger = get_logger(__name__)


# Color map for hippocampal subfields
SUBFIELD_COLORS = {
    "whole_hippocampus": [255, 0, 0],      # Red
    "CA1": [255, 100, 100],                # Light red
    "CA3": [100, 100, 255],                # Blue
    "CA4_DG": [100, 255, 100],             # Green (dentate gyrus)
    "subiculum": [255, 255, 100],          # Yellow
    "presubiculum": [255, 150, 100],       # Orange
    "fimbria": [200, 100, 255],            # Purple
    "HATA": [100, 200, 200],               # Cyan
}


def generate_segmentation_overlays(
    t1_path: Path,
    seg_path: Path,
    output_dir: Path,
    prefix: str = "overlay",
    specific_labels: list = None
) -> Dict[str, str]:
    """
    Generate PNG overlay images showing segmentation on T1 scan.
    
    Creates multiple axial slices (every 10 slices) with segmentation overlay.
    Generates 5-6 images showing the extent of the segmented structure.
    
    Args:
        t1_path: Path to T1 NIfTI file
        seg_path: Path to segmentation NIfTI file
        output_dir: Output directory for images
        prefix: Filename prefix
        specific_labels: Optional list of label values to display (e.g., [17, 53] for hippocampus)
                        If None, shows all labels
    
    Returns:
        Dictionary with paths to generated images (e.g., {'slice_00': 'path/to/image.png', ...})
    """
    logger.info("generating_segmentation_overlays", 
                t1=str(t1_path), 
                seg=str(seg_path), 
                labels=specific_labels)
    
    try:
        # Load images
        t1_img = nib.load(t1_path)
        seg_img = nib.load(seg_path)
        
        t1_data = t1_img.get_fdata()
        # Voxel sizes (mm) to preserve physical aspect ratio
        # For coronal visualization we use X (left-right) and Z (inferior-superior)
        vx, _, vz = t1_img.header.get_zooms()[:3]
        seg_data = seg_img.get_fdata()
        
        # Verify spatial alignment - check affine matrices match
        # This ensures T1 and segmentation are in the same coordinate system
        affine_t1 = t1_img.affine
        affine_seg = seg_img.affine
        
        if not np.allclose(affine_t1, affine_seg, atol=1e-2):
            logger.warning("affine_mismatch",
                          t1_affine=str(affine_t1),
                          seg_affine=str(affine_seg),
                          max_diff=str(np.abs(affine_t1 - affine_seg).max()),
                          note="T1 and segmentation may not be properly aligned spatially")
        else:
            logger.info("affine_verified", 
                       note="T1 and segmentation are in the same coordinate space")
        
        # Check if dimensions match, if not resample segmentation to T1 space
        if t1_data.shape != seg_data.shape:
            logger.warning("dimension_mismatch", 
                          t1_shape=t1_data.shape, 
                          seg_shape=seg_data.shape)
            
            # If affine matrices match, dimensions should match for proper alignment
            # If they don't match but affine is the same, there's an issue
            if np.allclose(affine_t1, affine_seg, atol=1e-2):
                logger.warning("dimension_mismatch_despite_aligned_affine",
                              note="Affine matches but dimensions differ - this may indicate a problem")
            
            from scipy.ndimage import zoom
            zoom_factors = [t1_data.shape[i] / seg_data.shape[i] for i in range(3)]
            seg_data = zoom(seg_data, zoom_factors, order=0)  # Nearest neighbor
            logger.info("resampled_segmentation", new_shape=seg_data.shape)
            
            # After resampling, affine matrices should still match for proper alignment
            # But note that resampling may introduce small alignment errors
            logger.info("resampling_complete",
                       note="Segmentation resampled to match T1 dimensions")
        
        # Create a mask for specific labels if requested (for hippocampus highlighting)
        highlight_mask = None
        if specific_labels is not None:
            logger.info("filtering_segmentation_labels", labels=specific_labels)
            highlight_mask = np.zeros_like(seg_data, dtype=bool)
            for label in specific_labels:
                highlight_mask |= (seg_data == label)
                count = np.sum(seg_data == label)
                logger.info("label_voxel_count", label=label, count=int(count))
        
        # Normalize T1 data for display
        t1_normalized = (t1_data - np.min(t1_data)) / (np.max(t1_data) - np.min(t1_data))
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find the range of slices containing the segmentation
        slice_indices = []
        if highlight_mask is not None:
            # For hippocampus, find the extent in y-direction (coronal slices)
            seg_indices = np.where(highlight_mask)
            if len(seg_indices[1]) > 0:  # y-axis indices
                min_y = int(np.min(seg_indices[1]))
                max_y = int(np.max(seg_indices[1]))
                
                logger.info("hippocampus_extent_coronal", min_y=min_y, max_y=max_y, total_slices=max_y-min_y+1)
                
                # Generate exactly 10 coronal slices evenly distributed across the hippocampus extent
                num_slices = 10
                total_range = max_y - min_y + 1
                
                if total_range >= num_slices:
                    # Generate evenly spaced slices including endpoints (min_y and max_y)
                    # Use numpy linspace for clean distribution across coronal extent
                    slice_indices_float = np.linspace(min_y, max_y, num_slices)
                    slice_indices_raw = [int(round(y)) for y in slice_indices_float]
                    
                    # Remove duplicates while preserving order, but ensure we get exactly 10 slices
                    seen = set()
                    slice_indices = []
                    for y in slice_indices_raw:
                        if y not in seen:
                            slice_indices.append(y)
                            seen.add(y)
                    
                    # If we have fewer than 10 due to duplicates, add more slices
                    # by filling in gaps or extending the range slightly
                    if len(slice_indices) < num_slices:
                        # Try to add slices by expanding range slightly or finding gaps
                        current_slices = set(slice_indices)
                        additional_needed = num_slices - len(slice_indices)
                        
                        # Add slices from the extended range if available
                        extended_min = max(0, min_y - additional_needed)
                        extended_max = min(t1_data.shape[1] - 1, max_y + additional_needed)
                        for y in range(extended_min, extended_max + 1):
                            if y not in current_slices and len(slice_indices) < num_slices:
                                if y < min_y:
                                    slice_indices.insert(0, y)
                                elif y > max_y:
                                    slice_indices.append(y)
                                else:
                                    # Insert in sorted position
                                    slice_indices.append(y)
                                    slice_indices.sort()
                                current_slices.add(y)
                    
                    # Ensure we have exactly 10 slices, truncate if we somehow got more
                    if len(slice_indices) > num_slices:
                        # Keep the first 10 that span the hippocampus extent
                        slice_indices = slice_indices[:num_slices]
                    
                    # Final sort to ensure order and ensure exactly 10 slices
                    slice_indices = sorted(list(set(slice_indices)))
                    
                    # Final check: ensure we have exactly 10 slices
                    if len(slice_indices) < num_slices:
                        # Fill remaining slots with evenly spaced slices from the extended range
                        all_available = set(range(max(0, min_y - 10), min(t1_data.shape[1], max_y + 10)))
                        missing = num_slices - len(slice_indices)
                        candidates = sorted(list(all_available - set(slice_indices)))
                        if candidates:
                            # Add missing slices evenly from candidates
                            step = len(candidates) // missing if missing > 0 else 1
                            for i in range(0, len(candidates), max(1, step)):
                                if len(slice_indices) >= num_slices:
                                    break
                                slice_indices.append(candidates[i])
                            slice_indices = sorted(slice_indices[:num_slices])
                    
                else:
                    # If range is smaller than requested slices, include all slices in range
                    # and pad with nearby slices to get 10 total
                    slice_indices = list(range(min_y, max_y + 1))
                    
                    # Pad to get 10 slices by extending the range symmetrically
                    if len(slice_indices) < num_slices:
                        additional_needed = num_slices - len(slice_indices)
                        # Add slices before and after to pad to 10
                        pre_slices = additional_needed // 2
                        post_slices = additional_needed - pre_slices
                        
                        # Add slices before min_y
                        for i in range(pre_slices):
                            y = max(0, min_y - i - 1)
                            if y not in slice_indices:
                                slice_indices.insert(0, y)
                        
                        # Add slices after max_y
                        for i in range(post_slices):
                            y = min(t1_data.shape[1] - 1, max_y + i + 1)
                            if y not in slice_indices and len(slice_indices) < num_slices:
                                slice_indices.append(y)
                        
                        slice_indices = sorted(slice_indices[:num_slices])
                    
                # Final verification: we should have exactly 10 coronal slices (or fewer if data doesn't allow)
                actual_count = len(slice_indices)
                if actual_count == num_slices:
                    logger.info("generating_coronal_slices", 
                              indices=slice_indices, 
                              count=actual_count,
                              expected=num_slices,
                              note=f"Successfully generating {actual_count} coronal slices in y-direction (coronal plane)")
                else:
                    logger.warning("coronal_slice_count_mismatch",
                                 actual=actual_count,
                                 expected=num_slices,
                                 indices=slice_indices,
                                 note=f"Generated {actual_count} coronal slices instead of {num_slices} (data range may be limited)")
            else:
                # Fallback: use center slice
                slice_indices = [t1_data.shape[1] // 2]
        else:
            # No specific labels, use evenly spaced slices (coronal -> y-axis)
            slice_indices = list(range(0, t1_data.shape[1], 10))[:6]
        
        output_paths = {}
        
        # Generate overlay for each slice
        for idx, y_slice in enumerate(slice_indices):
            # Get T1 and segmentation data for this coronal slice (x-z plane)
            t1_slice = t1_normalized[:, y_slice, :]
            seg_slice = seg_data[:, y_slice, :]
            
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 10))
            ax.set_aspect('equal')
            
            # Show whole brain T1 slice in grayscale (coronal: x vs z)
            # Save overlays upright for new jobs (top-left origin in PNG)
            ax.imshow(
                t1_slice.T,
                cmap='gray',
                origin='upper',
                interpolation='bilinear',
                extent=[0, vx * t1_slice.shape[0], 0, vz * t1_slice.shape[1]],
                aspect='equal',
            )
            
            # Overlay segmentation with label-specific colors
            if specific_labels is not None:
                # Create a colored overlay preserving label values
                # Only show voxels that match specific labels (e.g., 17, 53 for hippocampus)
                overlay_data = np.zeros_like(seg_slice)
                for label in specific_labels:
                    overlay_data[seg_slice == label] = label
                
                # Mask zero values (background)
                overlay_masked = np.ma.masked_where(overlay_data == 0, overlay_data)
                
                if np.any(overlay_masked):
                    # Create custom colormap for hippocampus labels
                    # Label 17 (Left-Hippocampus) -> Red
                    # Label 53 (Right-Hippocampus) -> Blue
                    
                    # Define colors for each label
                    colors = ['none']  # Background
                    bounds = [0]
                    for label in specific_labels:
                        if label == 17:  # Left-Hippocampus
                            colors.append('#FF3333')  # Bright red
                        elif label == 53:  # Right-Hippocampus
                            colors.append('#3399FF')  # Bright blue
                        else:
                            colors.append('#FFAA00')  # Orange for other labels
                        bounds.append(label)
                    
                    bounds.append(max(specific_labels) + 1)
                    cmap = ListedColormap(colors)
                    norm = BoundaryNorm(bounds, cmap.N)
                    
                    # Display overlay with label-specific colors
                    ax.imshow(
                        overlay_masked.T,
                        cmap=cmap,
                        norm=norm,
                        alpha=0.6,
                        origin='upper',
                        interpolation='nearest',
                        extent=[0, vx * t1_slice.shape[0], 0, vz * t1_slice.shape[1]],
                        aspect='equal',
                    )
            else:
                # Show all labels with generic hot colormap
                overlay_masked = np.ma.masked_where(seg_slice == 0, seg_slice)
                if np.any(overlay_masked):
                    ax.imshow(
                        overlay_masked.T,
                        cmap='hot',
                        alpha=0.6,
                        origin='upper',
                        interpolation='nearest',
                        extent=[0, vx * t1_slice.shape[0], 0, vz * t1_slice.shape[1]],
                        aspect='equal',
                    )
            
            ax.axis('off')
            title = f'Coronal Slice {y_slice}'
            if specific_labels:
                title += ' - Hippocampus (Red: Left, Blue: Right)'
            ax.set_title(title, fontsize=16, fontweight='bold')
            
            # Save with slice number in filename
            output_path = output_dir / f"{prefix}_slice_{idx:02d}.png"
            plt.savefig(output_path, bbox_inches='tight', dpi=150)
            plt.close()
            
            output_paths[f"slice_{idx:02d}"] = str(output_path)
            logger.info("saved_slice_overlay", slice_num=y_slice, idx=idx, path=str(output_path))
        
        return output_paths
    
    except Exception as e:
        logger.error("overlay_generation_failed", error=str(e))
        return {}


def convert_t1_to_nifti(
    t1_mgz_path: Path,
    output_dir: Path
) -> Path:
    """
    Convert T1-weighted anatomical image from MGZ to NIfTI format.
    
    Args:
        t1_mgz_path: Path to orig.mgz or similar T1 image
        output_dir: Output directory
        
    Returns:
        Path to converted NIfTI file
    """
    logger.info("converting_t1_to_nifti", input=str(t1_mgz_path))
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "anatomical.nii.gz"
    
    try:
        # Load MGZ and save as NIfTI
        img = nib.load(t1_mgz_path)
        nib.save(img, output_path)
        
        logger.info("t1_conversion_complete", output=str(output_path))
        return output_path
        
    except Exception as e:
        logger.error("t1_conversion_failed", error=str(e))
        raise


def prepare_nifti_for_viewer(
    seg_path: Path,
    output_dir: Path,
    label_map: Dict[int, str],
    highlight_labels: list = None
) -> Dict[str, str]:
    """
    Prepare NIfTI segmentation file for web-based viewer.
    
    Creates a compressed NIfTI file and associated metadata JSON.
    
    Args:
        seg_path: Path to segmentation NIfTI file
        output_dir: Output directory
        label_map: Mapping of label values to names
        highlight_labels: Optional list of labels to show in legend (e.g., [17, 53] for hippocampus)
                         If None, shows all labels. Other labels still visible but not in legend.
    
    Returns:
        Dictionary with paths to files
    """
    logger.info("preparing_nifti_for_viewer", 
                seg=str(seg_path),
                highlight_labels=highlight_labels)
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load segmentation
        seg_img = nib.load(seg_path)
        seg_data = seg_img.get_fdata()
        
        # Get unique labels
        unique_labels = np.unique(seg_data[seg_data > 0])
        
        # If highlight_labels specified, only include those in metadata legend
        if highlight_labels is not None:
            labels_for_legend = [l for l in unique_labels if int(l) in highlight_labels]
            logger.info("filtering_legend_labels", 
                       total_labels=len(unique_labels),
                       legend_labels=len(labels_for_legend))
        else:
            labels_for_legend = unique_labels
        
        # Create metadata
        metadata = {
            "labels": {},
            "colormap": {}
        }
        
        # Build metadata only for labels that should appear in legend
        for label_val in labels_for_legend:
            label_val_int = int(label_val)
            label_name = label_map.get(label_val_int, f"Label_{label_val_int}")
            
            metadata["labels"][label_val_int] = label_name
            
            # Assign color based on structure
            # Hippocampus gets bright, distinct colors
            if label_val_int == 17:  # Left Hippocampus
                color = [255, 50, 50]  # Bright Red
                alpha = 255
            elif label_val_int == 53:  # Right Hippocampus
                color = [50, 150, 255]  # Bright Blue
                alpha = 255
            # Other structures get subtle gray tones
            else:
                # Vary gray levels slightly based on label for better visualization
                gray_level = 150 + (label_val_int % 80)
                color = [gray_level, gray_level, gray_level]
                alpha = 100  # More transparent for non-hippocampus
            
            metadata["colormap"][label_val_int] = {
                "r": color[0],
                "g": color[1],
                "b": color[2],
                "a": alpha
            }
        
        # Save compressed NIfTI
        output_nii_path = output_dir / "segmentation.nii.gz"
        nib.save(seg_img, output_nii_path)
        
        # Save metadata
        metadata_path = output_dir / "segmentation_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("nifti_prepared_for_viewer", 
                   nifti=str(output_nii_path),
                   metadata=str(metadata_path))
        
        return {
            "nifti": str(output_nii_path),
            "metadata": str(metadata_path),
            "label_count": len(unique_labels)
        }
    
    except Exception as e:
        logger.error("nifti_preparation_failed", error=str(e))
        return {}


def extract_hippocampus_segmentation(
    fastsurfer_dir: Path,
    job_id: str
) -> Tuple[Path, Path]:
    """
    Extract hippocampus segmentation files from FastSurfer output.
    
    Args:
        fastsurfer_dir: FastSurfer output directory
        job_id: Job identifier
    
    Returns:
        Tuple of (whole_hippocampus_path, subfields_path)
    """
    logger.info("extracting_hippocampus_segmentation", job_id=job_id)
    
    subject_dir = fastsurfer_dir / job_id
    mri_dir = subject_dir / "mri"
    
    # Whole brain segmentation (contains hippocampus labels)
    # FastSurfer outputs this as aparc.DKTatlas+aseg.deep.mgz
    aseg_path = mri_dir / "aparc.DKTatlas+aseg.deep.mgz"
    if not aseg_path.exists():
        # Fallback to older naming convention
        aseg_path = mri_dir / "aparc+aseg.mgz"
    
    # Hippocampal subfields (if available)
    # FastSurfer outputs these in separate files
    left_hippo_path = mri_dir / "lh.hippoSfLabels-T1.v21.mgz"
    right_hippo_path = mri_dir / "rh.hippoSfLabels-T1.v21.mgz"
    
    # Convert MGZ to NIfTI if needed
    if aseg_path.exists():
        logger.info("found_aseg_file", path=str(aseg_path))
        aseg_nii = convert_mgz_to_nifti(aseg_path, mri_dir / "aseg_for_viz.nii.gz")
    else:
        logger.warning("aseg_file_not_found", expected=str(aseg_path))
        aseg_nii = None
    
    # Combine left and right hippocampal subfields
    if left_hippo_path.exists() and right_hippo_path.exists():
        subfields_nii = combine_hippocampal_subfields(
            left_hippo_path,
            right_hippo_path,
            mri_dir / "hippocampal_subfields.nii.gz"
        )
    else:
        subfields_nii = None
    
    return aseg_nii, subfields_nii


def convert_mgz_to_nifti(mgz_path: Path, output_path: Path) -> Path:
    """
    Convert MGZ file to NIfTI format.
    
    Args:
        mgz_path: Input MGZ file
        output_path: Output NIfTI path
    
    Returns:
        Path to converted file
    """
    try:
        img = nib.load(mgz_path)
        nib.save(img, output_path)
        logger.info("mgz_converted_to_nifti", input=str(mgz_path), output=str(output_path))
        return output_path
    except Exception as e:
        logger.error("mgz_conversion_failed", error=str(e))
        return None


def combine_hippocampal_subfields(
    left_path: Path,
    right_path: Path,
    output_path: Path
) -> Path:
    """
    Combine left and right hippocampal subfield segmentations.
    
    Args:
        left_path: Left hemisphere segmentation
        right_path: Right hemisphere segmentation
        output_path: Combined output path
    
    Returns:
        Path to combined segmentation
    """
    try:
        left_img = nib.load(left_path)
        right_img = nib.load(right_path)
        
        left_data = left_img.get_fdata()
        right_data = right_img.get_fdata()
        
        # Combine (right labels offset to avoid overlap)
        combined_data = left_data.copy()
        right_mask = right_data > 0
        # Offset right labels by 1000 to distinguish from left
        combined_data[right_mask] = right_data[right_mask] + 1000
        
        # Create new image
        combined_img = nib.Nifti1Image(combined_data, left_img.affine, left_img.header)
        nib.save(combined_img, output_path)
        
        logger.info("hippocampal_subfields_combined", output=str(output_path))
        return output_path
    
    except Exception as e:
        logger.error("subfield_combination_failed", error=str(e))
        return None


# FreeSurfer/FastSurfer label mappings
ASEG_HIPPOCAMPUS_LABELS = {
    # FreeSurfer DKT Atlas + ASEG labels
    0: "Unknown",
    2: "Left-Cerebral-White-Matter",
    3: "Left-Cerebral-Cortex",
    4: "Left-Lateral-Ventricle",
    5: "Left-Inf-Lat-Vent",
    7: "Left-Cerebellum-White-Matter",
    8: "Left-Cerebellum-Cortex",
    10: "Left-Thalamus",
    11: "Left-Caudate",
    12: "Left-Putamen",
    13: "Left-Pallidum",
    14: "3rd-Ventricle",
    15: "4th-Ventricle",
    16: "Brain-Stem",
    17: "Left-Hippocampus",
    18: "Left-Amygdala",
    24: "CSF",
    26: "Left-Accumbens-area",
    28: "Left-VentralDC",
    30: "Left-vessel",
    31: "Left-choroid-plexus",
    41: "Right-Cerebral-White-Matter",
    42: "Right-Cerebral-Cortex",
    43: "Right-Lateral-Ventricle",
    44: "Right-Inf-Lat-Vent",
    46: "Right-Cerebellum-White-Matter",
    47: "Right-Cerebellum-Cortex",
    49: "Right-Thalamus",
    50: "Right-Caudate",
    51: "Right-Putamen",
    52: "Right-Pallidum",
    53: "Right-Hippocampus",
    54: "Right-Amygdala",
    58: "Right-Accumbens-area",
    60: "Right-VentralDC",
    62: "Right-vessel",
    63: "Right-choroid-plexus",
    77: "WM-hypointensities",
    85: "Optic-Chiasm",
    # DKT cortical labels (left hemisphere)
    1002: "ctx-lh-caudalanteriorcingulate",
    1003: "ctx-lh-caudalmiddlefrontal",
    1005: "ctx-lh-cuneus",
    1006: "ctx-lh-entorhinal",
    1007: "ctx-lh-fusiform",
    1008: "ctx-lh-inferiorparietal",
    1009: "ctx-lh-inferiortemporal",
    1010: "ctx-lh-isthmuscingulate",
    1011: "ctx-lh-lateraloccipital",
    1012: "ctx-lh-lateralorbitofrontal",
    1013: "ctx-lh-lingual",
    1014: "ctx-lh-medialorbitofrontal",
    1015: "ctx-lh-middletemporal",
    1016: "ctx-lh-parahippocampal",
    1017: "ctx-lh-paracentral",
    1018: "ctx-lh-parsopercularis",
    1019: "ctx-lh-parsorbitalis",
    1020: "ctx-lh-parstriangularis",
    1021: "ctx-lh-pericalcarine",
    1022: "ctx-lh-postcentral",
    1023: "ctx-lh-posteriorcingulate",
    1024: "ctx-lh-precentral",
    1025: "ctx-lh-precuneus",
    1026: "ctx-lh-rostralanteriorcingulate",
    1027: "ctx-lh-rostralmiddlefrontal",
    1028: "ctx-lh-superiorfrontal",
    1029: "ctx-lh-superiorparietal",
    1030: "ctx-lh-superiortemporal",
    1031: "ctx-lh-supramarginal",
    1034: "ctx-lh-transversetemporal",
    1035: "ctx-lh-insula",
    # DKT cortical labels (right hemisphere)
    2002: "ctx-rh-caudalanteriorcingulate",
    2003: "ctx-rh-caudalmiddlefrontal",
    2005: "ctx-rh-cuneus",
    2006: "ctx-rh-entorhinal",
    2007: "ctx-rh-fusiform",
    2008: "ctx-rh-inferiorparietal",
    2009: "ctx-rh-inferiortemporal",
    2010: "ctx-rh-isthmuscingulate",
    2011: "ctx-rh-lateraloccipital",
    2012: "ctx-rh-lateralorbitofrontal",
    2013: "ctx-rh-lingual",
    2014: "ctx-rh-medialorbitofrontal",
    2015: "ctx-rh-middletemporal",
    2016: "ctx-rh-parahippocampal",
    2017: "ctx-rh-paracentral",
    2018: "ctx-rh-parsopercularis",
    2019: "ctx-rh-parsorbitalis",
    2020: "ctx-rh-parstriangularis",
    2021: "ctx-rh-pericalcarine",
    2022: "ctx-rh-postcentral",
    2023: "ctx-rh-posteriorcingulate",
    2024: "ctx-rh-precentral",
    2025: "ctx-rh-precuneus",
    2026: "ctx-rh-rostralanteriorcingulate",
    2027: "ctx-rh-rostralmiddlefrontal",
    2028: "ctx-rh-superiorfrontal",
    2029: "ctx-rh-superiorparietal",
    2030: "ctx-rh-superiortemporal",
    2031: "ctx-rh-supramarginal",
    2034: "ctx-rh-transversetemporal",
    2035: "ctx-rh-insula",
}

HIPPOCAMPAL_SUBFIELD_LABELS = {
    # Left hemisphere
    203: "CA1",
    204: "CA3",
    205: "CA4_DG",
    206: "subiculum",
    207: "presubiculum",
    208: "fimbria",
    209: "HATA",
    # Right hemisphere (offset by 1000)
    1203: "CA1_right",
    1204: "CA3_right",
    1205: "CA4_DG_right",
    1206: "subiculum_right",
    1207: "presubiculum_right",
    1208: "fimbria_right",
    1209: "HATA_right",
}

