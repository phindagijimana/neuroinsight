#!/usr/bin/env python3
"""
Script to regenerate metrics and visualizations for existing processed jobs.
This is useful when the processing completed but metrics generation failed.
"""

import sys
from pathlib import Path
from uuid import UUID

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.core.config import get_settings
from backend.core.logging import get_logger
from pipeline.processors.mri_processor import MRIProcessor

logger = get_logger(__name__)
settings = get_settings()


def regenerate_for_job(job_id: str):
    """Regenerate metrics and visualizations for a completed job."""
    
    logger.info("regenerating_metrics", job_id=job_id)
    
    # Initialize processor
    processor = MRIProcessor(UUID(job_id))
    
    # Check if FastSurfer output exists
    fastsurfer_dir = Path(settings.output_dir) / job_id / "fastsurfer"
    if not fastsurfer_dir.exists():
        logger.error("fastsurfer_output_not_found", job_id=job_id, path=str(fastsurfer_dir))
        return False
    
    # Find the original input file
    uploads_dir = Path("data/uploads")
    input_files = list(uploads_dir.glob(f"*{job_id}*"))
    
    if not input_files:
        logger.error("input_file_not_found", job_id=job_id)
        return False
    
    input_path = input_files[0]
    logger.info("found_input_file", path=str(input_path))
    
    try:
        # Extract hippocampal data
        hippocampal_stats = processor._extract_hippocampal_data(fastsurfer_dir)
        
        # Calculate asymmetry
        metrics = processor._calculate_asymmetry(hippocampal_stats)
        
        # Generate visualizations
        visualization_paths = processor._generate_visualizations(input_path, fastsurfer_dir)
        
        # Save results
        processor._save_results(metrics)
        
        logger.info("regeneration_complete", 
                   job_id=job_id,
                   metrics_count=len(metrics),
                   visualizations=list(visualization_paths.keys()))
        
        print(f"\n[OK] Successfully regenerated metrics for job {job_id}")
        print(f"Metrics: {len(metrics)} asymmetry measurements")
        print(f"Visualizations: {list(visualization_paths.keys())}")
        
        return True
        
    except Exception as e:
        logger.error("regeneration_failed", job_id=job_id, error=str(e))
        print(f"\n[ERROR] Failed to regenerate metrics: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bin/regenerate_metrics.py <job_id>")
        print("\nExample:")
        print("  python bin/regenerate_metrics.py 91555c6d-84e6-49fb-a197-09cab389a32d")
        sys.exit(1)
    
    job_id = sys.argv[1]
    success = regenerate_for_job(job_id)
    sys.exit(0 if success else 1)


