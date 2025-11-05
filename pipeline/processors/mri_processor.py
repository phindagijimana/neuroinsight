"""
MRI Processor for hippocampal analysis pipeline.

This module orchestrates the complete MRI processing workflow,
from DICOM conversion through hippocampal asymmetry calculation.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List
from uuid import UUID

import nibabel as nib
import numpy as np
import pandas as pd

from backend.core.config import get_settings
from backend.core.logging import get_logger
from pipeline.utils import asymmetry, file_utils, segmentation, visualization

logger = get_logger(__name__)
settings = get_settings()


class MRIProcessor:
    """
    Main processor for MRI hippocampal analysis.
    
    Orchestrates the complete pipeline:
    1. File format validation/conversion
    2. FastSurfer segmentation
    3. Hippocampal subfield extraction
    4. Volumetric analysis
    5. Asymmetry index calculation
    """
    
    def __init__(self, job_id: UUID):
        """
        Initialize MRI processor.
        
        Args:
            job_id: Unique job identifier
        """
        self.job_id = job_id
        self.output_dir = Path(settings.output_dir) / str(job_id)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Detect GPU availability
        self.has_gpu = self._detect_gpu()
        
        logger.info(
            "processor_initialized", 
            job_id=str(job_id),
            gpu_available=self.has_gpu
        )
    
    def _detect_gpu(self) -> bool:
        """
        Detect if NVIDIA GPU is available for Singularity containers.
        
        Returns:
            True if GPU is available and working, False otherwise
        """
        # Check if nvidia-smi exists and works
        try:
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                timeout=5,
            )
            
            if result.returncode == 0:
                logger.info("gpu_detected", note="NVIDIA GPU available for Singularity --nv flag")
                return True
                
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        logger.info("gpu_not_detected", note="No GPU found - will use CPU for processing")
        return False
    
    def process(self, input_path: str) -> Dict:
        """
        Execute the complete processing pipeline.
        
        Args:
            input_path: Path to input MRI file (DICOM or NIfTI)
        
        Returns:
            Dictionary containing processing results and metrics
        """
        logger.info("processing_pipeline_started", job_id=str(self.job_id))
        
        # Step 1: Convert to NIfTI if needed
        nifti_path = self._prepare_input(input_path)
        
        # Step 2: Run FastSurfer segmentation (whole brain)
        fastsurfer_output = self._run_fastsurfer(nifti_path)
        
        # Step 3: Extract hippocampal volumes (from FastSurfer outputs only)
        hippocampal_stats = self._extract_hippocampal_data(fastsurfer_output)
        
        # Step 4: Calculate asymmetry indices
        metrics = self._calculate_asymmetry(hippocampal_stats)
        
        # Step 5: Generate segmentation visualizations
        visualization_paths = self._generate_visualizations(nifti_path, fastsurfer_output)
        
        # Step 6: Save results
        self._save_results(metrics)
        
        logger.info(
            "processing_pipeline_completed",
            job_id=str(self.job_id),
            metrics_count=len(metrics),
        )
        
        return {
            "job_id": str(self.job_id),
            "output_dir": str(self.output_dir),
            "metrics": metrics,
            "visualizations": visualization_paths,
        }
    
    def _prepare_input(self, input_path: str) -> Path:
        """
        Prepare input file for processing.
        
        Converts DICOM to NIfTI if needed, validates format.
        
        Args:
            input_path: Path to input file
        
        Returns:
            Path to NIfTI file
        """
        input_file = Path(input_path)
        
        # If already NIfTI, validate and return
        if input_file.suffix in [".nii", ".gz"]:
            if file_utils.validate_nifti(input_file):
                logger.info("input_validated", format="NIfTI")
                return input_file
        
        # Convert DICOM to NIfTI
        elif input_file.suffix in [".dcm", ".dicom"]:
            logger.info("converting_dicom_to_nifti")
            output_path = self.output_dir / "input.nii.gz"
            file_utils.convert_dicom_to_nifti(input_file, output_path)
            return output_path
        
        else:
            raise ValueError(f"Unsupported file format: {input_file.suffix}")
    
    def _run_fastsurfer(self, nifti_path: Path) -> Path:
        """
        Run FastSurfer segmentation using Docker.
        
        Executes FastSurfer container for whole brain segmentation.
        
        Args:
            nifti_path: Path to input NIfTI file
        
        Returns:
            Path to FastSurfer output directory
        """
        logger.info("running_fastsurfer_docker", input=str(nifti_path))
        
        fastsurfer_dir = self.output_dir / "fastsurfer"
        fastsurfer_dir.mkdir(exist_ok=True)
        
        try:
            # Detect GPU support
            if self.has_gpu:
                device = "cuda"
                runtime_arg = "--gpus all"
                logger.info("using_gpu_for_processing", note="GPU detected, using CUDA")
            else:
                device = "cpu"
                runtime_arg = ""
                logger.info("using_cpu_for_processing", note="No GPU detected, using CPU")
            
            # Determine optimal thread count for CPU processing
            import os
            cpu_count = os.cpu_count() or 4
            if device == "cpu":
                num_threads = max(1, cpu_count - 2)  # Leave 2 cores free
            else:
                num_threads = 1
            
            # Build Docker command
            cmd = ["docker", "run", "--rm"]
            
            # Add GPU support if available
            if runtime_arg:
                cmd.extend(runtime_arg.split())
            
            # Add volume mounts
            cmd.extend([
                "-v", f"{nifti_path.parent}:/input:ro",
                "-v", f"{fastsurfer_dir}:/output",
                "--user", f"{os.getuid()}:{os.getgid()}",
                "deepmi/fastsurfer:latest",
                "--t1", f"/input/{nifti_path.name}",
                "--sid", str(self.job_id),
                "--sd", "/output",
                "--seg_only",  # Only segmentation, skip surface reconstruction
                "--device", device,
                "--batch", "1",
                "--threads", str(num_threads),
                "--viewagg_device", "cpu",
            ])
            
            if device == "cpu":
                logger.info(
                    "cpu_threading_enabled",
                    threads=num_threads,
                    total_cores=cpu_count,
                    note=f"Using {num_threads} threads for CPU processing"
                )
            
            logger.info(
                "executing_fastsurfer",
                command=" ".join(cmd),
                note="Running FastSurfer with Docker"
            )
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=settings.processing_timeout,
            )
            
            logger.info(
                "fastsurfer_completed",
                output_dir=str(fastsurfer_dir),
                note="Brain segmentation complete"
            )
            
        except subprocess.TimeoutExpired:
            logger.error("fastsurfer_timeout")
            logger.warning(
                "using_mock_data",
                reason="Processing timeout - using mock data"
            )
            self._create_mock_fastsurfer_output(fastsurfer_dir)
        
        except subprocess.CalledProcessError as e:
            logger.error(
                "fastsurfer_execution_failed",
                error=str(e),
                stderr=e.stderr if hasattr(e, 'stderr') and e.stderr else "No stderr",
                stdout=e.stdout if hasattr(e, 'stdout') and e.stdout else "No stdout",
                returncode=e.returncode,
            )
            logger.warning("using_mock_data", reason="FastSurfer execution failed")
            self._create_mock_fastsurfer_output(fastsurfer_dir)
        
        except FileNotFoundError:
            logger.warning(
                "docker_not_found",
                note="Docker not available - using mock data"
            )
            self._create_mock_fastsurfer_output(fastsurfer_dir)
        
        except Exception as e:
            logger.error(
                "fastsurfer_unexpected_error",
                error=str(e),
                error_type=type(e).__name__
            )
            logger.warning("using_mock_data", reason=f"Unexpected error: {str(e)}")
            self._create_mock_fastsurfer_output(fastsurfer_dir)
        
        return fastsurfer_dir
    
    def _create_mock_fastsurfer_output(self, output_dir: Path) -> None:
        """
        Create mock FastSurfer output for development/testing.
        
        Args:
            output_dir: Output directory for mock data
        """
        logger.info("creating_mock_fastsurfer_output")
        
        stats_dir = output_dir / str(self.job_id) / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        
        # Create mock hippocampal subfields stats file
        mock_data = {
            "CA1": {"left": 1250.5, "right": 1198.2},
            "CA3": {"left": 450.3, "right": 465.1},
            "subiculum": {"left": 580.7, "right": 555.9},
            "dentate_gyrus": {"left": 380.2, "right": 395.6},
        }
        
        # Write left hemisphere stats
        left_stats = stats_dir / "lh.hippoSfVolumes-T1.v21.txt"
        with open(left_stats, "w") as f:
            f.write("# Hippocampal subfield volumes (left hemisphere)\n")
            f.write("# Region Volume\n")
            for region, volumes in mock_data.items():
                f.write(f"{region} {volumes['left']:.2f}\n")
        
        # Write right hemisphere stats
        right_stats = stats_dir / "rh.hippoSfVolumes-T1.v21.txt"
        with open(right_stats, "w") as f:
            f.write("# Hippocampal subfield volumes (right hemisphere)\n")
            f.write("# Region Volume\n")
            for region, volumes in mock_data.items():
                f.write(f"{region} {volumes['right']:.2f}\n")
        
        logger.info("mock_output_created", output_dir=str(output_dir))
    
    def _extract_hippocampal_data(self, fastsurfer_dir: Path) -> Dict:
        """
        Extract hippocampal volumes from FastSurfer output.
        
        Tries SegmentHA subfield data first, falls back to FastSurfer's total
        hippocampal volumes from aseg+DKT if subfields are not available.
        
        Args:
            fastsurfer_dir: FastSurfer output directory
        
        Returns:
            Dictionary of hippocampal volumes by region and hemisphere
        """
        logger.info("extracting_hippocampal_data")
        
        stats_dir = fastsurfer_dir / str(self.job_id) / "stats"
        
        # Use FastSurfer stats only (SegmentHA removed)
        logger.info("using_fastsurfer_aseg_data")
        aseg_file = stats_dir / "aseg+DKT.stats"
        
        if aseg_file.exists():
            volumes = segmentation.parse_aseg_stats(aseg_file)
            if volumes:
                hippocampal_data = {
                    "Hippocampus": {
                        "left": volumes.get("left", 0.0),
                        "right": volumes.get("right", 0.0),
                    }
                }
                logger.info(
                    "fastsurfer_hippocampal_data_found",
                    left=volumes.get("left"),
                    right=volumes.get("right")
                )
            else:
                logger.warning("no_hippocampal_volumes_found")
                hippocampal_data = {}
        else:
            logger.error("no_stats_files_found", stats_dir=str(stats_dir))
            hippocampal_data = {}
        
        logger.info(
            "hippocampal_data_extracted",
            regions=list(hippocampal_data.keys()),
        )
        
        return hippocampal_data
    
    def _calculate_asymmetry(self, hippocampal_data: Dict) -> List[Dict]:
        """
        Calculate asymmetry indices for each hippocampal region.
        
        Args:
            hippocampal_data: Dictionary of volumes by region
        
        Returns:
            List of metric dictionaries
        """
        logger.info("calculating_asymmetry_indices")
        
        metrics = []
        
        for region, volumes in hippocampal_data.items():
            left = volumes["left"]
            right = volumes["right"]
            
            # Calculate asymmetry index
            ai = asymmetry.calculate_asymmetry_index(left, right)
            
            metrics.append({
                "region": region,
                "left_volume": left,
                "right_volume": right,
                "asymmetry_index": ai,
            })
        
        logger.info("asymmetry_calculated", metrics_count=len(metrics))
        
        return metrics
    
    def _generate_visualizations(self, nifti_path: Path, fastsurfer_dir: Path) -> Dict[str, any]:
        """
        Generate segmentation visualizations for web viewer.
        
        Args:
            nifti_path: Path to original T1 NIfTI
            fastsurfer_dir: FastSurfer output directory
        
        Returns:
            Dictionary with visualization file paths
        """
        logger.info("generating_visualizations")
        
        viz_dir = self.output_dir / "visualizations"
        viz_dir.mkdir(parents=True, exist_ok=True)
        
        viz_paths = {
            "whole_hippocampus": None,
            "subfields": None,
            "overlays": {}
        }
        
        try:
            # Extract segmentation files from FastSurfer output
            aseg_nii, subfields_nii = visualization.extract_hippocampus_segmentation(
                fastsurfer_dir,
                str(self.job_id)
            )
            
            # Convert anatomical T1 image for viewer base layer
            # Use orig.mgz (FastSurfer conformed space) to ensure alignment with segmentation
            orig_mgz = fastsurfer_dir / str(self.job_id) / "mri" / "orig.mgz"
            t1_nifti = None
            if orig_mgz.exists():
                t1_nifti = visualization.convert_t1_to_nifti(
                    orig_mgz,
                    viz_dir / "whole_hippocampus"
                )
                logger.info("t1_anatomical_converted", path=str(t1_nifti))
            else:
                logger.warning("orig_mgz_not_found", 
                             expected=str(orig_mgz),
                             note="Will use original input - may have alignment issues")
                # Fallback to original input, but log warning about potential misalignment
                t1_nifti = nifti_path
            
            # Prepare whole hippocampus for viewer
            # Show whole brain but only highlight hippocampus in legend
            if aseg_nii and aseg_nii.exists():
                whole_hippo = visualization.prepare_nifti_for_viewer(
                    aseg_nii,
                    viz_dir / "whole_hippocampus",
                    visualization.ASEG_HIPPOCAMPUS_LABELS,
                    highlight_labels=[17, 53]  # Only show hippocampus in legend
                )
                viz_paths["whole_hippocampus"] = whole_hippo
                
                # Generate overlay images with hippocampus highlighted
                # Use orig.mgz converted T1 to ensure proper spatial alignment with segmentation
                # FreeSurfer labels: 17 = Left-Hippocampus, 53 = Right-Hippocampus
                overlays = visualization.generate_segmentation_overlays(
                    t1_nifti,  # Use orig.mgz converted (in same space as segmentation)
                    aseg_nii,
                    viz_dir / "overlays",
                    prefix="hippocampus",
                    specific_labels=[17, 53]  # Highlight hippocampus only
                )
                viz_paths["overlays"]["whole"] = overlays
            
            # Prepare subfields for viewer
            if subfields_nii and subfields_nii.exists():
                subfields = visualization.prepare_nifti_for_viewer(
                    subfields_nii,
                    viz_dir / "subfields",
                    visualization.HIPPOCAMPAL_SUBFIELD_LABELS
                )
                viz_paths["subfields"] = subfields
                
                # Generate subfield overlay images
                # Use orig.mgz converted T1 to ensure proper spatial alignment
                subfield_overlays = visualization.generate_segmentation_overlays(
                    t1_nifti,  # Use orig.mgz converted (in same space as segmentation)
                    subfields_nii,
                    viz_dir / "overlays",
                    prefix="subfields"
                )
                viz_paths["overlays"]["subfields"] = subfield_overlays
            
            logger.info("visualizations_generated", paths=viz_paths)
        
        except Exception as e:
            logger.error("visualization_generation_failed", error=str(e))
        
        return viz_paths
    
    def _save_results(self, metrics: List[Dict]) -> None:
        """
        Save processing results to files.
        
        Args:
            metrics: List of metric dictionaries
        """
        logger.info("saving_results")
        
        # Save as JSON
        json_path = self.output_dir / "metrics.json"
        with open(json_path, "w") as f:
            json.dump(metrics, f, indent=2)
        
        # Save as CSV
        csv_path = self.output_dir / "metrics.csv"
        df = pd.DataFrame(metrics)
        df.to_csv(csv_path, index=False)
        
        logger.info(
            "results_saved",
            json=str(json_path),
            csv=str(csv_path),
        )

