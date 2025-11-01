#!/usr/bin/env python3
"""
Regenerate visualizations for an existing completed job.
This is useful after fixing visualization code.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from pipeline.utils import visualization
from backend.core.logging import get_logger

logger = get_logger(__name__)

def regenerate_viz(job_id: str):
    """Regenerate visualizations for a job."""
    logger.info("regenerating_visualizations", job_id=job_id)
    
    output_dir = Path(f"data/outputs/{job_id}")
    fastsurfer_dir = output_dir / "fastsurfer"
    viz_dir = output_dir / "visualizations"
    
    if not fastsurfer_dir.exists():
        logger.error("fastsurfer_output_not_found", path=str(fastsurfer_dir))
        return False
    
    viz_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract segmentation
    logger.info("extracting_segmentation")
    aseg_nii, subfields_nii = visualization.extract_hippocampus_segmentation(
        fastsurfer_dir,
        job_id
    )
    
    if not aseg_nii or not aseg_nii.exists():
        logger.error("no_segmentation_found")
        return False
    
    logger.info("aseg_found", path=str(aseg_nii))
    
    # Use orig.mgz (FastSurfer conformed space) to ensure alignment with segmentation
    # This matches the new alignment fixes in the processor
    orig_mgz = fastsurfer_dir / job_id / "mri" / "orig.mgz"
    t1_nifti = None
    
    if orig_mgz.exists():
        # Convert orig.mgz to NIfTI for visualization (ensures proper alignment)
        t1_nifti = visualization.convert_t1_to_nifti(
            orig_mgz,
            viz_dir / "whole_hippocampus"
        )
        logger.info("using_orig_mgz", path=str(orig_mgz), converted=str(t1_nifti))
    else:
        logger.warning("orig_mgz_not_found", 
                     expected=str(orig_mgz),
                     note="Will try to find original input - may have alignment issues")
        # Fallback: try to find original input
        uploads_dir = Path("data/uploads")
        upload_files = list(uploads_dir.glob("*"))
        if upload_files:
            t1_nifti = max(upload_files, key=lambda p: p.stat().st_mtime)
            logger.warning("using_original_input", path=str(t1_nifti), 
                         note="Using original input instead of orig.mgz - alignment may be imperfect")
        else:
            logger.error("no_t1_source_found", 
                        note="Neither orig.mgz nor original input found")
            return False
    
    # Generate whole hippocampus visualization
    # Show whole brain but only hippocampus in legend
    logger.info("generating_whole_hippocampus_viz")
    whole_hippo = visualization.prepare_nifti_for_viewer(
        aseg_nii,
        viz_dir / "whole_hippocampus",
        visualization.ASEG_HIPPOCAMPUS_LABELS,
        highlight_labels=[17, 53]  # Only show hippocampus in legend
    )
    
    if whole_hippo:
        logger.info("whole_hippo_viz_created", path=str(whole_hippo))
    
    # Generate overlay images with hippocampus highlighted
    # Use orig.mgz converted T1 to ensure proper spatial alignment with segmentation
    logger.info("generating_overlays_with_alignment_verification")
    overlays = visualization.generate_segmentation_overlays(
        t1_nifti,  # Use orig.mgz converted (in same space as segmentation)
        aseg_nii,
        viz_dir / "overlays",
        prefix="hippocampus",
        specific_labels=[17, 53]  # Highlight Left and Right Hippocampus
    )
    
    if overlays:
        logger.info("overlays_created", count=len(overlays))
        for view, path in overlays.items():
            logger.info("overlay_created", view=view, path=str(path))
    
    # Handle subfields if available
    if subfields_nii and subfields_nii.exists():
        logger.info("generating_subfields_viz")
        subfields = visualization.prepare_nifti_for_viewer(
            subfields_nii,
            viz_dir / "subfields",
            visualization.HIPPOCAMPAL_SUBFIELD_LABELS
        )
        
        # Generate subfield overlay images with proper alignment
        if t1_nifti:
            logger.info("generating_subfield_overlays")
            subfield_overlays = visualization.generate_segmentation_overlays(
                t1_nifti,  # Use orig.mgz converted (in same space as segmentation)
                subfields_nii,
                viz_dir / "overlays",
                prefix="subfields"
            )
            if subfield_overlays:
                logger.info("subfield_overlays_created", count=len(subfield_overlays))
        if subfields:
            logger.info("subfields_viz_created", path=str(subfields))
    
    logger.info("visualization_regeneration_complete", job_id=job_id)
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bin/regenerate_visualizations.py <job_id>")
        print("\nExample:")
        print("  python bin/regenerate_visualizations.py d1c47159-bae7-4444-9cfe-2082b3a51f48")
        sys.exit(1)
    
    job_id = sys.argv[1]
    success = regenerate_viz(job_id)
    
    if success:
        print(f"\n[OK] Visualizations regenerated for job {job_id}")
        print(f"Check: data/outputs/{job_id}/visualizations/")
    else:
        print(f"\n[ERROR] Failed to regenerate visualizations")
        sys.exit(1)

