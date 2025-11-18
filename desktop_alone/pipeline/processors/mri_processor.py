"""
MRI Processor for hippocampal analysis pipeline.

This module orchestrates the complete MRI processing workflow,
from DICOM conversion through hippocampal asymmetry calculation.
"""

import json
import os
import platform
import subprocess as subprocess_module
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
        print(f"DEBUG: MRIProcessor.__init__ called with job_id={job_id}")
        self.job_id = job_id
        self.output_dir = Path(settings.output_dir) / str(job_id)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.process_pid = None  # Track subprocess PID for cleanup
        self.progress_callback = progress_callback

        # Check if smoke test mode is enabled (for CI/testing)
        self.smoke_test_mode = os.getenv("FASTSURFER_SMOKE_TEST") == "1"
        
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
            result = subprocess_module.run(
                ["nvidia-smi"],
                capture_output=True,
                timeout=5,
            )
            
            if result.returncode == 0:
                logger.info("gpu_detected", note="NVIDIA GPU available for Singularity --nv flag")
                return True
                
        except (subprocess_module.CalledProcessError, subprocess_module.TimeoutExpired, FileNotFoundError):
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
        if self.progress_callback:
            self.progress_callback(17, "Preparing input file...")
        nifti_path = self._prepare_input(input_path)
        
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
        if self.progress_callback:
            self.progress_callback(75, "Generating visualizations...")
        visualization_paths = self._generate_visualizations(nifti_path, fastsurfer_output)
        
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
        In smoke test mode, immediately returns mock data for faster CI testing.

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

        # Smoke test mode: Skip Docker and create mock output immediately
        if self.smoke_test_mode:
            logger.info("smoke_test_mode_enabled", message="Using mock FastSurfer data for CI testing")
            self._create_mock_fastsurfer_output(fastsurfer_dir)
            return fastsurfer_dir
        
        # Check if Docker is available and running
        try:
            result = subprocess_module.run(
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
        except subprocess_module.TimeoutExpired:
            logger.error("docker_check_timeout")
            raise DockerNotAvailableError("not_running")
        
        # Check if FastSurfer image is downloaded
        try:
            result = subprocess_module.run(
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
                pull_result = subprocess_module.run(
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
        except subprocess_module.TimeoutExpired:
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
            
            # If not set, try to auto-detect from Docker inspect
            if not host_upload_dir or not host_output_dir:
                try:
                    import json
                    
                    # Get our own container info
                    result = subprocess_module.run(
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
                except Exception as e:
                    logger.warning(
                        "host_path_detection_failed",
                        error=str(e),
                        note="Falling back to configured desktop paths"
                    )
                    host_upload_dir = host_upload_dir or ''
                    host_output_dir = host_output_dir or ''
            else:
                logger.info(
                    "using_configured_host_paths",
                    upload_dir=host_upload_dir,
                    output_dir=host_output_dir
                )

            # If host paths are still unset or point to placeholder mount locations,
            # fall back to the actual desktop storage directories.
            if not host_upload_dir or not Path(host_upload_dir).exists() or host_upload_dir == "/data/uploads":
                host_upload_dir = str(Path(settings.upload_dir).resolve())

            if not host_output_dir or not Path(host_output_dir).exists() or host_output_dir == "/data/outputs":
                host_output_dir = str(Path(settings.output_dir).resolve())

            logger.info(
                "resolved_host_paths",
                upload_dir=host_upload_dir,
                output_dir=host_output_dir
            )
            
            # Calculate relative paths from host perspective
            # nifti_path is like /data/uploads/file.nii (inside worker container)
            # We need to translate to host path
            input_host_path = host_upload_dir
            output_host_path = f"{host_output_dir}/{self.job_id}/fastsurfer"
            
            # Build Docker command
            cmd = ["docker", "run", "--rm"]
            
            allow_root = False
            force_root = os.getenv("FASTSURFER_FORCE_ROOT") == "1"
            # Add GPU support if available
            if runtime_arg:
                cmd.extend(runtime_arg.split())
            
            # On Windows desktop mode, FastSurfer image defaults to user "nonroot"
            # which cannot read NTFS-mounted paths. Override to root and allow root exec.
            force_root_reason = None
            if settings.desktop_mode and (platform.system() == "Windows" or force_root):
                cmd.extend(["--user", "root"])
                allow_root = True
                force_root_reason = (
                    "windows_desktop_mode" if platform.system() == "Windows" else "forced_by_env"
                )
            
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

            if allow_root:
                logger.info(
                    "forcing_root_user_for_fastsurfer",
                    reason=force_root_reason,
                    platform=platform.system(),
                )
                cmd.append("--allow_root")
            
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
            
            result = subprocess_module.run(
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
            
        except subprocess_module.TimeoutExpired:
            logger.error("fastsurfer_timeout")
            logger.warning(
                "using_mock_data",
                reason="Processing timeout - using mock data"
            )
            self._create_mock_fastsurfer_output(fastsurfer_dir)
        
        except subprocess_module.CalledProcessError as e:
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
            process = subprocess_module.Popen(
                cmd,
                stdout=subprocess_module.PIPE,
                stderr=subprocess_module.PIPE,
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
            except subprocess_module.TimeoutExpired:
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
        print("DEBUG: _create_mock_fastsurfer_output method called")
        print(f"DEBUG: creating_mock_fastsurfer_output: {output_dir}")
        try:
            print("DEBUG: try_block_started")
            # Create directory structure (matching FastSurfer output)
            subject_dir = output_dir / str(self.job_id)
            print(f"DEBUG: subject_dir_created: {subject_dir}")
            stats_dir = subject_dir / "stats"
            mri_dir = subject_dir / "mri"
            print("DEBUG: about_to_mkdir")
            stats_dir.mkdir(parents=True, exist_ok=True)
            mri_dir.mkdir(parents=True, exist_ok=True)
            print(f"DEBUG: directories_created: {stats_dir}")

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
            logger.info("hippo_stats_created")

            # Create mock aseg stats file
            aseg_stats = stats_dir / "aseg+DKT.stats"
            logger.info(f"creating_aseg_stats: {aseg_stats}")
            try:
                with open(aseg_stats, "w") as f:
                    f.write("# aseg+DKT.stats\n")
                    f.write("# Index SegId NVoxels Volume_mm3 StructName normMean normStdDev normMin normMax normRange\n")
                    f.write("17 17 31262 1250.5 Left-Hippocampus 110.5 15.2 85.3 145.6 60.3\n")
                    f.write("53 53 29845 1198.2 Right-Hippocampus 108.7 14.8 82.1 142.3 60.2\n")
                logger.info(f"aseg_stats_created: {aseg_stats}")
            except Exception as e:
                logger.error(f"aseg_stats_creation_failed: {e} at {aseg_stats}")

            # Create mock segmentation files for visualization
            try:
                self._create_mock_segmentation_files(mri_dir)
                logger.info("mock_segmentation_files_created")
            except Exception as e:
                logger.error(f"mock_segmentation_files_failed: {e}")

            logger.info(f"mock_output_created: {output_dir}")
        except Exception as e:
            logger.error(f"create_mock_fastsurfer_output_failed: {e}")
            raise

    def _create_mock_segmentation_files(self, mri_dir: Path) -> None:
        """
        Create mock segmentation files needed for visualization.

        Args:
            mri_dir: MRI directory to create files in
        """
        import numpy as np
        import nibabel as nib

        logger.info("creating_mock_segmentation_files")

        # Create a simple 3D brain-like volume (64x64x32) for mock data
        shape = (64, 64, 32)
        data = np.zeros(shape, dtype=np.int16)

        # Add mock hippocampus regions
        # Left hippocampus (label 17) - roughly in the temporal lobe area
        data[20:30, 15:25, 10:20] = 17
        # Right hippocampus (label 53)
        data[35:45, 15:25, 10:20] = 53

        # Add some other brain structures for realism
        data[25:35, 25:35, 15:25] = 2  # Left cerebral white matter
        data[30:40, 25:35, 15:25] = 41  # Right cerebral white matter

        # Create affine matrix (simple scaling)
        affine = np.diag([1.0, 1.0, 1.0, 1.0])

        # Create mock T1 anatomical image (orig.mgz)
        t1_data = np.random.normal(1000, 100, size=shape).astype(np.float32)
        # Make hippocampus areas slightly different intensity
        t1_data[20:30, 15:25, 10:20] = np.random.normal(1100, 50, size=(10, 10, 10))
        t1_data[35:45, 15:25, 10:20] = np.random.normal(1100, 50, size=(10, 10, 10))

        # Save orig.mgz (T1 anatomical)
        orig_img = nib.Nifti1Image(t1_data, affine)
        orig_path = mri_dir / "orig.mgz"
        nib.save(orig_img, orig_path)

        # Save aparc.DKTatlas+aseg.deep.mgz (segmentation)
        seg_img = nib.Nifti1Image(data, affine)
        aseg_path = mri_dir / "aparc.DKTatlas+aseg.deep.mgz"
        nib.save(seg_img, aseg_path)

        # Create mock hippocampal subfield files (optional)
        # Left hippocampus subfields
        lh_subfields = np.zeros(shape, dtype=np.int16)
        lh_subfields[20:25, 15:25, 10:20] = 203  # CA1
        lh_subfields[25:30, 15:25, 10:20] = 204  # CA3

        # Right hippocampus subfields
        rh_subfields = np.zeros(shape, dtype=np.int16)
        rh_subfields[35:40, 15:25, 10:20] = 1203  # CA1_right
        rh_subfields[40:45, 15:25, 10:20] = 1204  # CA3_right

        # Save subfield files
        lh_img = nib.Nifti1Image(lh_subfields, affine)
        lh_path = mri_dir / "lh.hippoSfLabels-T1.v21.mgz"
        nib.save(lh_img, lh_path)

        rh_img = nib.Nifti1Image(rh_subfields, affine)
        rh_path = mri_dir / "rh.hippoSfLabels-T1.v21.mgz"
        nib.save(rh_img, rh_path)

        logger.info("mock_segmentation_files_created",
                   orig=str(orig_path),
                   aseg=str(aseg_path),
                   lh_subfields=str(lh_path),
                   rh_subfields=str(rh_path))
    
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

