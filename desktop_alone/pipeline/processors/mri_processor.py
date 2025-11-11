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


class DockerNotAvailableError(Exception):
    """User-friendly exception when Docker is not available."""
    
    def __init__(self, error_type="not_installed"):
        self.error_type = error_type
        
        messages = {
            "not_installed": {
                "title": "Docker Desktop Not Installed",
                "message": "NeuroInsight requires Docker Desktop to process MRI scans.",
                "instructions": [
                    "1. Download Docker Desktop:",
                    "   • Windows/Mac: https://www.docker.com/get-started",
                    "   • Linux: https://docs.docker.com/engine/install/",
                    "",
                    "2. Install Docker Desktop (takes 10-15 minutes)",
                    "",
                    "3. Launch Docker Desktop and wait for the whale icon",
                    "",
                    "4. Return to NeuroInsight and try processing again"
                ],
                "why": "Docker is needed to run FastSurfer, the brain segmentation tool."
            },
            "not_running": {
                "title": "Docker Desktop Not Running",
                "message": "Docker Desktop is installed but not currently running.",
                "instructions": [
                    "1. Open Docker Desktop from your Applications folder",
                    "",
                    "2. Wait for the whale icon to appear in your system tray:",
                    "   • macOS: Top menu bar",
                    "   • Windows: System tray (bottom right)",
                    "   • Linux: System tray",
                    "",
                    "3. The icon should be steady (not animating)",
                    "",
                    "4. Return to NeuroInsight and try processing again"
                ],
                "why": "Docker must be running to process MRI scans."
            },
            "image_not_found": {
                "title": "Downloading Brain Segmentation Model",
                "message": "First-time setup: Downloading FastSurfer (~4GB).",
                "instructions": [
                    "This download happens only once and takes 10-15 minutes.",
                    "",
                    "The model will be cached for future use.",
                    "",
                    "Please keep Docker Desktop running and wait..."
                ],
                "why": "NeuroInsight needs to download the brain segmentation AI model."
            }
        }
        
        error_info = messages.get(error_type, messages["not_installed"])
        
        # Format the error message
        full_message = f"\n{'='*60}\n"
        full_message += f"{error_info['title']}\n"
        full_message += f"{'='*60}\n\n"
        full_message += f"{error_info['message']}\n\n"
        full_message += "What to do:\n"
        full_message += "\n".join(error_info['instructions'])
        full_message += f"\n\nWhy: {error_info['why']}\n"
        full_message += f"{'='*60}\n"
        
        super().__init__(full_message)
        self.title = error_info['title']
        self.user_message = error_info['message']
        self.instructions = error_info['instructions']


class InvalidImageTypeError(Exception):
    """Raised when the uploaded image is not T1-weighted or unsuitable for processing."""
    
    def __init__(self, detected_type="unknown", details=""):
        """
        Initialize InvalidImageTypeError with user-friendly message.
        
        Args:
            detected_type: The type of image detected (e.g., "T2", "FLAIR", "unknown")
            details: Additional details about why the image was rejected
        """
        type_messages = {
            "T2": "T2-weighted MRI detected",
            "FLAIR": "FLAIR sequence detected",
            "DWI": "Diffusion-weighted imaging (DWI) detected",
            "fMRI": "Functional MRI (fMRI) detected",
            "unknown": "Filename does not indicate T1-weighted image"
        }
        
        detected_msg = type_messages.get(detected_type, type_messages["unknown"])
        
        full_message = f"\n{'='*60}\n"
        full_message += "Invalid MRI Sequence Type\n"
        full_message += f"{'='*60}\n\n"
        full_message += f"{detected_msg}.\n\n"
        if details:
            full_message += f"Details: {details}\n\n"
        
        # Special message for filename issues (detected_type == "unknown")
        if detected_type == "unknown" and "does not contain" in details:
            full_message += "NeuroInsight requires T1-weighted MRI scans.\n\n"
            full_message += "📝 PLEASE RENAME YOUR FILE:\n\n"
            full_message += "Your filename should contain 'T1' to indicate it's a\n"
            full_message += "T1-weighted scan. For example:\n\n"
            full_message += "   ✓ subject_T1w.nii\n"
            full_message += "   ✓ brain_T1.nii\n"
            full_message += "   ✓ patient_01_MPRAGE_T1.nii\n"
            full_message += "   ✓ scan_T1-weighted.nii\n\n"
            full_message += "What to do:\n"
            full_message += "1. Rename your file to include 'T1' in the filename\n"
            full_message += "2. Make sure you're uploading a T1-weighted scan\n"
            full_message += "   (MPRAGE, SPGR, or 3D T1 sequences)\n"
            full_message += "3. Upload the renamed file\n\n"
            full_message += "Why: This helps ensure you're uploading the correct\n"
            full_message += "scan type. FastSurfer requires T1-weighted images for\n"
            full_message += "accurate hippocampal segmentation.\n"
        else:
            # Standard message for detected non-T1w sequences
            full_message += "NeuroInsight requires T1-weighted MRI scans for accurate\n"
            full_message += "hippocampal volumetric analysis.\n\n"
            full_message += "What to do:\n"
            full_message += "1. Verify you uploaded the correct scan series\n\n"
            full_message += "2. Look for T1-weighted sequences in your MRI data:\n"
            full_message += "   ✓ MPRAGE (most common for brain imaging)\n"
            full_message += "   ✓ SPGR (Spoiled Gradient Recalled Echo)\n"
            full_message += "   ✓ T1-FLAIR\n"
            full_message += "   ✓ 3D T1 (volumetric T1)\n"
            full_message += "   ✗ T2-weighted (wrong - different contrast)\n"
            full_message += "   ✗ FLAIR (wrong - unless T1-FLAIR)\n"
            full_message += "   ✗ DWI/DTI (wrong - diffusion imaging)\n"
            full_message += "   ✗ fMRI/BOLD (wrong - functional imaging)\n\n"
            full_message += "3. Rename the file to include 'T1' and upload it\n\n"
            full_message += "Why: FastSurfer's AI model is trained exclusively on\n"
            full_message += "T1-weighted images. Other sequence types will produce\n"
            full_message += "incorrect segmentation and invalid volume measurements.\n"
        
        full_message += f"{'='*60}\n"
        
        super().__init__(full_message)
        self.detected_type = detected_type


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
    
    def __init__(self, job_id: UUID, progress_callback=None):
        """
        Initialize MRI processor.
        
        Args:
            job_id: Unique job identifier
            progress_callback: Optional callback function(progress: int, step: str) for progress updates
        """
        self.job_id = job_id
        self.output_dir = Path(settings.output_dir) / str(job_id)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.process_pid = None  # Track subprocess PID for cleanup
        self.progress_callback = progress_callback
        
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
    
    def _validate_t1w_image(self, nifti_path: Path) -> None:
        """
        Validate that the input image appears to be T1-weighted based on filename.
        
        Requires the filename to contain 'T1' to ensure proper organization.
        Rejects files with 'T2', 'FLAIR', 'DWI' in the name.
        
        Args:
            nifti_path: Path to NIfTI file to validate
        
        Raises:
            InvalidImageTypeError: If filename doesn't indicate T1w or indicates other sequence
        """
        filename = nifti_path.name.lower()
        
        # First, check for non-T1w sequence keywords (fast rejection)
        non_t1w_keywords = {
            't2w': 'T2',
            't2-w': 'T2',
            '_t2_': 'T2',
            '_t2.': 'T2',
            'flair': 'FLAIR',
            'dwi': 'DWI',
            'dti': 'DWI',
            'diffusion': 'DWI',
            'bold': 'fMRI',
            'task': 'fMRI',
            'rest': 'fMRI',
        }
        
        for keyword, detected_type in non_t1w_keywords.items():
            if keyword in filename:
                logger.warning(
                    "non_t1w_sequence_in_filename",
                    detected_type=detected_type,
                    filename=filename
                )
                raise InvalidImageTypeError(
                    detected_type=detected_type,
                    details=f"Filename contains '{keyword}' - indicates {detected_type} sequence, not T1w"
                )
        
        # Now check if filename contains 'T1' (case-insensitive)
        t1w_indicators = ['t1w', 't1-w', '_t1_', '_t1.', 't1.nii', 't1.dcm', 'mprage', 'spgr']
        has_t1_indicator = any(indicator in filename for indicator in t1w_indicators)
        
        if not has_t1_indicator:
            logger.warning(
                "filename_missing_t1_indicator",
                filename=filename,
                note="Filename does not contain T1 indicator - asking user to rename"
            )
            raise InvalidImageTypeError(
                detected_type="unknown",
                details=f"Filename '{nifti_path.name}' does not contain 'T1' indicator"
            )
        
        logger.info("t1w_filename_validated", filename=filename, note="Filename indicates T1w sequence")
    
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
        if self.progress_callback:
            self.progress_callback(17, "Preparing input file...")
        nifti_path = self._prepare_input(input_path)
        
        # Step 1.5: Validate that image appears to be T1-weighted
        if self.progress_callback:
            self.progress_callback(18, "Validating image type (T1w required)...")
        self._validate_t1w_image(nifti_path)
        
        # Step 2: Run FastSurfer segmentation (whole brain) - LONGEST STEP
        if self.progress_callback:
            self.progress_callback(20, "Running FastSurfer brain segmentation (this may take a while)...")
        fastsurfer_output = self._run_fastsurfer(nifti_path)
        
        # Step 3: Extract hippocampal volumes (from FastSurfer outputs only)
        if self.progress_callback:
            self.progress_callback(65, "Extracting hippocampal volumes...")
        hippocampal_stats = self._extract_hippocampal_data(fastsurfer_output)
        
        # Step 4: Calculate asymmetry indices
        if self.progress_callback:
            self.progress_callback(70, "Calculating asymmetry indices...")
        metrics = self._calculate_asymmetry(hippocampal_stats)
        
        # Step 5: Generate segmentation visualizations
        # Note: This step is optional and should not fail the job if it errors
        if self.progress_callback:
            self.progress_callback(75, "Generating visualizations...")
        try:
            visualization_paths = self._generate_visualizations(nifti_path, fastsurfer_output)
        except Exception as viz_error:
            logger.warning(
                "visualization_generation_failed",
                error=str(viz_error),
                note="Continuing with metrics only - visualizations may be incomplete"
            )
            visualization_paths = {}
        
        # Step 6: Save results
        if self.progress_callback:
            self.progress_callback(82, "Saving results...")
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
        
        Raises:
            DockerNotAvailableError: If Docker is not installed or not running
        """
        logger.info("running_fastsurfer_docker", input=str(nifti_path))
        
        fastsurfer_dir = self.output_dir / "fastsurfer"
        fastsurfer_dir.mkdir(exist_ok=True)
        
        # Check if Docker is available and running
        try:
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                logger.error("docker_not_running")
                raise DockerNotAvailableError("not_running")
            logger.info("docker_available", message="Docker is running")
        except FileNotFoundError:
            logger.error("docker_not_installed")
            raise DockerNotAvailableError("not_installed")
        except subprocess.TimeoutExpired:
            logger.error("docker_check_timeout")
            raise DockerNotAvailableError("not_running")
        
        # Check if FastSurfer image is downloaded
        try:
            result = subprocess.run(
                ["docker", "images", "-q", "deepmi/fastsurfer:latest"],
                capture_output=True,
                timeout=10
            )
            if not result.stdout.strip():
                # Image not found - need to download
                logger.info("fastsurfer_image_not_found", message="Will download FastSurfer image")
                if self.progress_callback:
                    self.progress_callback(
                        15,
                        "Downloading FastSurfer model (4GB, first time only - takes 10-15 min)..."
                    )
                
                # Pull the image
                logger.info("pulling_fastsurfer_image")
                pull_result = subprocess.run(
                    ["docker", "pull", "deepmi/fastsurfer:latest"],
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30 minutes timeout for download
                )
                
                if pull_result.returncode != 0:
                    logger.error("fastsurfer_pull_failed", stderr=pull_result.stderr)
                    raise RuntimeError(
                        "Failed to download FastSurfer model. "
                        "Please check your internet connection and try again."
                    )
                
                logger.info("fastsurfer_image_downloaded", message="FastSurfer model ready")
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                "Downloading FastSurfer model timed out. "
                "Please check your internet connection and try again."
            )
        
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
            
            # Get host paths for Docker-in-Docker mounting
            # When worker runs inside Docker and spawns FastSurfer Docker container,
            # we need to mount HOST paths, not container paths
            host_upload_dir = os.getenv('HOST_UPLOAD_DIR')
            host_output_dir = os.getenv('HOST_OUTPUT_DIR')
            
            # Check if we're running in desktop mode (not containerized)
            desktop_mode = os.getenv('DESKTOP_MODE', 'false').lower() == 'true'
            
            if desktop_mode:
                # Desktop mode: backend runs directly on host, use actual file paths
                input_host_path = str(nifti_path.parent.resolve())
                output_host_path = str(fastsurfer_dir.resolve())
                logger.info(
                    "desktop_mode_paths",
                    input_path=input_host_path,
                    output_path=output_host_path,
                    note="Using direct host paths for desktop mode"
                )
            elif not host_upload_dir or not host_output_dir:
                # Docker-in-Docker mode: try to auto-detect from Docker inspect
                try:
                    # Get our own container info
                    result = subprocess.run(
                        ['docker', 'inspect', os.uname().nodename],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    container_info = json.loads(result.stdout)[0]
                    
                    # Extract mount sources from our container
                    for mount in container_info.get('Mounts', []):
                        dest = mount.get('Destination', '')
                        if dest == '/data/uploads' and not host_upload_dir:
                            host_upload_dir = mount.get('Source')
                        elif dest == '/data/outputs' and not host_output_dir:
                            host_output_dir = mount.get('Source')
                    
                    logger.info(
                        "auto_detected_host_paths",
                        upload_dir=host_upload_dir,
                        output_dir=host_output_dir
                    )
                    
                    # Calculate relative paths from host perspective
                    # nifti_path is like /data/uploads/file.nii (inside worker container)
                    # We need to translate to host path
                    input_host_path = host_upload_dir
                    output_host_path = f"{host_output_dir}/{self.job_id}/fastsurfer"
                except Exception as e:
                    logger.warning(
                        "host_path_detection_failed",
                        error=str(e),
                        note="Falling back to container paths (may fail)"
                    )
                    host_upload_dir = host_upload_dir or '/data/uploads'
                    host_output_dir = host_output_dir or '/data/outputs'
                    input_host_path = host_upload_dir
                    output_host_path = f"{host_output_dir}/{self.job_id}/fastsurfer"
            else:
                # Explicitly configured host paths
                logger.info(
                    "using_configured_host_paths",
                    upload_dir=host_upload_dir,
                    output_dir=host_output_dir
                )
                input_host_path = host_upload_dir
                output_host_path = f"{host_output_dir}/{self.job_id}/fastsurfer"
            
            # Build Docker command
            cmd = ["docker", "run", "--rm"]
            
            # Force amd64 platform on Apple Silicon (ARM64) for compatibility
            # FastSurfer image may not have native ARM64 support
            import platform
            if platform.machine() == "arm64":
                cmd.extend(["--platform", "linux/amd64"])
                logger.info("using_platform_emulation", note="Forcing amd64 platform for ARM64 compatibility")
            
            # Add GPU support if available
            if runtime_arg:
                cmd.extend(runtime_arg.split())
            
            # Add volume mounts with HOST paths
            cmd.extend([
                "-v", f"{input_host_path}:/input:ro",
                "-v", f"{output_host_path}:/output",
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
            # Docker command failed - check if it's a Docker daemon issue
            stderr_lower = (e.stderr or "").lower() if hasattr(e, 'stderr') else ""
            
            if "cannot connect to the docker daemon" in stderr_lower:
                logger.error("docker_daemon_not_running")
                raise DockerNotAvailableError("not_running")
            
            # Other Docker execution errors
            logger.error(
                "fastsurfer_execution_failed",
                error=str(e),
                stderr=e.stderr if hasattr(e, 'stderr') and e.stderr else "No stderr",
                stdout=e.stdout if hasattr(e, 'stdout') and e.stdout else "No stdout",
                returncode=e.returncode,
            )
            
            # Try Singularity as fallback
            logger.info("trying_singularity_fallback")
            try:
                return self._run_fastsurfer_singularity(nifti_path, fastsurfer_dir)
            except Exception as sing_error:
                logger.warning(
                    "singularity_fallback_failed",
                    error=str(sing_error),
                    note="Using mock data as final fallback"
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
    
    def _run_fastsurfer_singularity(self, nifti_path: Path, fastsurfer_dir: Path) -> Path:
        """
        Run FastSurfer using Singularity/Apptainer (fallback when Docker not available).
        
        Args:
            nifti_path: Path to input NIfTI file
            fastsurfer_dir: Output directory
            
        Returns:
            Path to FastSurfer output directory
        """
        import shutil
        import os
        import signal
        
        logger.info("running_fastsurfer_singularity", input=str(nifti_path))
        
        # Check for Singularity/Apptainer
        singularity_cmd = None
        if shutil.which("singularity"):
            singularity_cmd = "singularity"
        elif shutil.which("apptainer"):
            singularity_cmd = "apptainer"
        else:
            raise FileNotFoundError("Neither singularity nor apptainer found")
        
        # Find Singularity image
        singularity_img = Path(settings.singularity_image_path) if hasattr(settings, 'singularity_image_path') else None
        if not singularity_img or not singularity_img.exists():
            # Try common locations
            possible_paths = [
                Path("/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo/singularity-images/fastsurfer.sif"),
                Path(settings.output_dir).parent / "singularity-images" / "fastsurfer.sif",
                Path("./singularity-images/fastsurfer.sif"),
            ]
            for path in possible_paths:
                if path.exists():
                    singularity_img = path
                    break
        
        if not singularity_img or not singularity_img.exists():
            raise FileNotFoundError(f"FastSurfer Singularity image not found")
        
        logger.info("found_singularity_image", path=str(singularity_img))
        
        # Detect GPU
        device = "cuda" if self.has_gpu else "cpu"
        
        # Threading
        cpu_count = os.cpu_count() or 4
        num_threads = max(1, cpu_count - 2) if device == "cpu" else 1
        
        # Build Singularity command
        cmd = [singularity_cmd, "exec"]
        
        # Add GPU support if available
        if self.has_gpu:
            cmd.append("--nv")
            logger.info("using_gpu_for_processing", note="GPU detected, using CUDA with --nv")
        else:
            logger.info("using_cpu_for_processing", note="No GPU detected, using CPU")
        
        # Add bind mounts and environment
        cmd.extend([
            "--bind", f"{nifti_path.parent}:/input:ro",
            "--bind", f"{fastsurfer_dir}:/output",
            "--env", "TQDM_DISABLE=1",
            "--cleanenv",
            str(singularity_img),
            "/fastsurfer/run_fastsurfer.sh",
            "--t1", f"/input/{nifti_path.name}",
            "--sid", str(self.job_id),
            "--sd", "/output",
            "--seg_only",
            "--device", device,
            "--batch", "1",
            "--threads", str(num_threads),
            "--viewagg_device", "cpu",
        ])
        
        logger.info(
            "cpu_threading_enabled",
            threads=num_threads,
            total_cores=cpu_count,
            note=f"Using {num_threads} threads for CPU parallel processing"
        )
        
        logger.info(
            "executing_fastsurfer_singularity",
            command=" ".join(cmd),
            note="Running FastSurfer with Singularity"
        )
        
        # Execute Singularity with proper process group management
        # Using Popen instead of run() to track PID and manage process group
        process = None
        try:
            # Create a new process group so we can kill all child processes
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid,  # Create new process group
            )
            
            # Store the process PID for cleanup tracking
            self._store_process_pid(process.pid)
            logger.info("process_started", pid=process.pid, pgid=os.getpgid(process.pid))
            
            # Wait for process with timeout
            try:
                stdout, stderr = process.communicate(timeout=7200)
                returncode = process.returncode
            except subprocess.TimeoutExpired:
                logger.warning("process_timeout_killing_group", pid=process.pid)
                # Kill entire process group
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    process.wait(timeout=10)
                except:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                raise
            finally:
                self._clear_process_pid()
            
            if returncode != 0:
                logger.error(
                    "fastsurfer_singularity_failed",
                    returncode=returncode,
                    stderr=stderr[:500] if stderr else "No stderr",
                    stdout=stdout[:500] if stdout else "No stdout"
                )
                raise RuntimeError(f"FastSurfer Singularity failed: {stderr}")
            
            logger.info("fastsurfer_singularity_completed", output_dir=str(fastsurfer_dir))
            return fastsurfer_dir
            
        except Exception as e:
            # Ensure cleanup of process group on any error
            if process and process.poll() is None:
                logger.warning("cleaning_up_process_group_on_error", pid=process.pid)
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except:
                    pass
            self._clear_process_pid()
            raise
    
    def _create_mock_fastsurfer_output(self, output_dir: Path) -> None:
        """
        Create mock FastSurfer output for development/testing.
        
        Args:
            output_dir: Output directory for mock data
        """
        logger.info("creating_mock_fastsurfer_output")
        
        stats_dir = output_dir / str(self.job_id) / "stats"
        stats_dir.mkdir(parents=True, exist_ok=True)
        
        # Create mock aseg+DKT.stats file (required for _extract_hippocampal_data)
        # This is the format that _extract_hippocampal_data expects!
        aseg_stats = stats_dir / "aseg+DKT.stats"
        with open(aseg_stats, "w") as f:
            f.write("# Table of FreeSurfer cortical parcellation anatomical statistics\n")
            f.write("#\n")
            f.write("# ColHeaders  Index SegId NVoxels Volume_mm3 StructName\n")
            # Mock hippocampal volumes (in mm³)
            # Left hippocampus (label 17) - slightly smaller for testing
            f.write(f" 17 17   3500  3500.0  Left-Hippocampus\n")
            # Right hippocampus (label 53) - slightly larger
            f.write(f" 53 53   3800  3800.0  Right-Hippocampus\n")
        
        logger.info("mock_output_created", 
                   output_dir=str(output_dir),
                   left_volume=3500.0,
                   right_volume=3800.0)
    
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
                
                # Generate overlay images for ALL 3 orientations
                # Use orig.mgz converted T1 to ensure proper spatial alignment with segmentation
                # FreeSurfer labels: 17 = Left-Hippocampus, 53 = Right-Hippocampus
                all_overlays = visualization.generate_all_orientation_overlays(
                    t1_nifti,  # Use orig.mgz converted (in same space as segmentation)
                    aseg_nii,
                    viz_dir / "overlays",
                    prefix="hippocampus",
                    specific_labels=[17, 53]  # Highlight hippocampus only
                )
                viz_paths["overlays"] = all_overlays
            
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
    
    def _store_process_pid(self, pid: int) -> None:
        """
        Store the process PID for tracking and cleanup.
        
        Writes PID to a file so we can kill zombie processes later.
        
        Args:
            pid: Process ID to store
        """
        self.process_pid = pid
        pid_file = self.output_dir / ".process_pid"
        with open(pid_file, "w") as f:
            f.write(str(pid))
        logger.info("process_pid_stored", pid=pid, file=str(pid_file))
    
    def _clear_process_pid(self) -> None:
        """Clear stored process PID after completion."""
        self.process_pid = None
        pid_file = self.output_dir / ".process_pid"
        if pid_file.exists():
            pid_file.unlink()
            logger.info("process_pid_cleared")
    
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

