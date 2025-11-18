#!/usr/bin/env python3
"""
Cross-platform smoke test for the NeuroInsight desktop backend.

Steps:
1. Create (or copy) a NIfTI T1 file suitable for upload.
2. Launch the PyInstaller-built backend executable in desktop mode.
3. Wait for /health to respond.
4. Upload the scan, poll until completion, verify metrics.json exists.
5. Shut down the backend gracefully.

Features:
- Timeout detection (30-60 minutes max for processing)
- Docker health checks during processing
- Early failure detection for hung processes
- Progress monitoring with reasonable expectations
"""

import argparse
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any

import nibabel as nib
import numpy as np
import requests


def create_sample_t1(path: Path) -> None:
    """Create a synthetic NIfTI T1-weighted volume."""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.zeros((48, 48, 48), dtype=np.float32)
    z_indices = np.linspace(0, 1, data.shape[2], dtype=np.float32)
    for z, val in enumerate(z_indices):
        data[:, :, z] = val
    affine = np.diag([1.0, 1.0, 1.0, 1.0])
    img = nib.Nifti1Image(data, affine)
    nib.save(img, str(path))


def wait_for_health(
    port: int,
    timeout: int = 600,
    initial_delay: float = 2.0,
    poll_interval: float = 1.0,
) -> None:
    """Wait until /health endpoint responds with 200 within timeout."""
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.time() + timeout
    last_error = None
    if initial_delay > 0:
        time.sleep(initial_delay)
    while time.time() < deadline:
        try:
            resp = requests.get(f"{base_url}/health", timeout=5)
            if resp.status_code == 200:
                elapsed = int(time.time() - (deadline - timeout))
                print(f"[smoke-test] Backend health check passed after {elapsed}s")
                return
            last_error = f"HTTP {resp.status_code}"
        except requests.RequestException as e:
            last_error = str(e)
        time.sleep(poll_interval)
    raise RuntimeError(f"Backend did not become healthy within timeout. Last error: {last_error}")


def upload_scan(port: int, file_path: Path) -> str:
    """Upload scan and return job_id."""
    base_url = f"http://127.0.0.1:{port}"
    with file_path.open("rb") as fh:
        files = {"file": (file_path.name, fh, "application/octet-stream")}
        resp = requests.post(f"{base_url}/upload/", files=files, timeout=60)
    if resp.status_code >= 400:
        try:
            error_payload = resp.json()
        except ValueError:
            error_payload = resp.text
        print(
            f"[smoke-test] ERROR: upload failed ({resp.status_code}) "
            f"{error_payload}",
            flush=True,
        )
    resp.raise_for_status()
    payload = resp.json()
    job_id = payload.get("job_id") or payload.get("id")
    if not job_id:
        raise RuntimeError(f"Upload succeeded but no job_id returned: {payload}")
    return str(job_id)


def check_docker_health() -> bool:
    """Check if Docker daemon is responsive and containers are healthy."""
    try:
        # Check if Docker daemon is running
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            print("[smoke-test] WARNING: Docker daemon not responsive")
            return False

        # Check for running containers (should be FastSurfer)
        result = subprocess.run(
            ["docker", "ps", "--filter", "ancestor=deepmi/fastsurfer:latest", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout.strip():
            # Check if container status indicates it's running (not exited)
            status_lines = result.stdout.strip().split('\n')
            for status in status_lines:
                if 'Up' in status or 'running' in status.lower():
                    return True
            print(f"[smoke-test] WARNING: FastSurfer container found but not running: {result.stdout.strip()}")
            return False

        return True  # No containers found, which is OK (might not have started yet)

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"[smoke-test] WARNING: Docker health check failed: {e}")
        return False


def poll_job(port: int, job_id: str, timeout: int = 7200, stalled_threshold: int = 3600) -> dict:
    """
    Poll job endpoint until completion or timeout with intelligent monitoring.

    Features:
    - Maximum timeout of 2 hours (7200 seconds) for real processing
    - Progress monitoring to detect hung processes
    - Docker health checks during processing
    - Early failure detection
    """
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.time() + min(timeout, 7200)  # Cap at 2 hours max
    start_time = time.time()
    last_progress = None
    last_progress_time = start_time

    print(f"[smoke-test] Starting job monitoring with {min(timeout, 7200)}s timeout")

    while time.time() < deadline:
        elapsed = time.time() - start_time

        try:
            resp = requests.get(f"{base_url}/jobs/{job_id}", timeout=20)
            resp.raise_for_status()
            payload = resp.json()
        except requests.Timeout:
            print(f"[smoke-test] WARNING: Polling {base_url}/jobs/{job_id} timed out; retrying...")
            time.sleep(3)
            continue
        except requests.RequestException as exc:
            print(f"[smoke-test] WARNING: Polling request error: {exc}; retrying...")
            time.sleep(3)
            continue

        status = payload.get("status")
        progress = payload.get("progress", 0)
        current_step = payload.get("current_step", "")

        # Progress monitoring to detect hung processes
        if progress != last_progress:
            last_progress = progress
            last_progress_time = time.time()
            print(f"[smoke-test] Progress: {progress}% - {current_step}")
        elif time.time() - last_progress_time > stalled_threshold:
            # Check if Docker container is still running before declaring hung
            if check_docker_health():
                print(f"[smoke-test] WARNING: Progress stalled at {progress}% for {stalled_threshold}s, but Docker container appears healthy. Continuing to monitor...")
                # Reset the timer to give more time
                last_progress_time = time.time()
            else:
                # No progress and Docker unhealthy - likely hung
                raise RuntimeError(
                    f"Job appears hung: no progress for {stalled_threshold}s "
                    f"(stuck at {progress}% - {current_step}) and Docker container unhealthy"
                )

        # Check Docker health during active processing
        if elapsed > 60 and status == "running":  # After 1 minute, during processing
            if not check_docker_health():
                print("[smoke-test] WARNING: Docker health check failed during processing")

        if status in {"completed", "failed"}:
            total_time = time.time() - start_time
            print(f"[smoke-test] Job finished in {total_time:.1f}s with status: {status}")
            return payload

        time.sleep(3)

    total_time = time.time() - start_time
    raise RuntimeError(f"Job did not finish within {min(timeout, 7200)}s timeout (ran for {total_time:.1f}s)")


def ensure_metrics(output_dir: Path, job_id: str) -> None:
    """Verify metrics.json exists for completed job."""
    metrics_path = output_dir / job_id / "metrics.json"
    if not metrics_path.exists():
        raise RuntimeError(f"metrics.json not found at {metrics_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="NeuroInsight smoke test runner")
    parser.add_argument("--backend-exe", required=True, help="Path to backend executable")
    parser.add_argument("--api-port", type=int, default=8765, help="API port to bind")
    parser.add_argument("--workspace", default="smoke_workdir", help="Working directory base")
    parser.add_argument(
        "--timeout",
        type=int,
        default=2400,  # 40 minutes default (reasonable for real processing)
        help="Overall timeout seconds (max 7200s/2hrs for real processing).",
    )
    parser.add_argument(
        "--health-timeout",
        type=int,
        default=600,
        help="Seconds to wait for backend /health to respond before failing.",
    )
    parser.add_argument(
        "--health-initial-delay",
        type=float,
        default=2.0,
        help="Seconds to sleep before starting health polling (gives backend time to boot).",
    )
    parser.add_argument(
        "--fastsurfer-mode",
        choices=("smoke", "real"),
        default="smoke",
        help="Select FastSurfer execution mode. 'smoke' uses mock outputs, 'real' runs the container.",
    )
    parser.add_argument(
        "--input-nii",
        help="Optional path to an existing NIfTI file to upload instead of generating a synthetic volume.",
    )
    parser.add_argument(
        "--max-processing-time",
        type=int,
        default=7200,  # 2 hours max for real processing
        help="Maximum time allowed for actual processing (after upload).",
    )
    parser.add_argument(
        "--stalled-threshold",
        type=int,
        default=3600,  # 1 hour default
        help="Seconds without progress before considering job hung (default: 3600s/1hr).",
    )
    args = parser.parse_args()

    backend_path = Path(args.backend_exe).resolve()
    if not backend_path.exists():
        raise FileNotFoundError(f"Backend executable not found: {backend_path}")

    workspace = Path(args.workspace).resolve()
    docs_dir = workspace / "Documents"
    home_dir = workspace / "home"
    upload_dir = docs_dir / "NeuroInsight" / "uploads"
    output_dir = docs_dir / "NeuroInsight" / "outputs"
    for directory in [workspace, docs_dir, home_dir, upload_dir, output_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    sample_path = upload_dir / "smoke_patient_T1w.nii.gz"
    if args.input_nii:
        source_path = Path(args.input_nii).resolve()
        if source_path.exists():
            sample_path = upload_dir / source_path.name
            shutil.copy(source_path, sample_path)
        else:
            print(
                f"[smoke-test] WARNING: Input NIfTI file not found at {source_path}; "
                "falling back to generated synthetic volume."
            )
            create_sample_t1(sample_path)
    else:
        create_sample_t1(sample_path)

    env = os.environ.copy()
    env["DESKTOP_MODE"] = "1"
    if args.fastsurfer_mode == "smoke":
        env["FASTSURFER_SMOKE_TEST"] = "1"
    else:
        env.pop("FASTSURFER_SMOKE_TEST", None)
    force_root_flag = os.environ.get("FASTSURFER_FORCE_ROOT")
    if force_root_flag is not None:
        env["FASTSURFER_FORCE_ROOT"] = force_root_flag
    else:
        env.pop("FASTSURFER_FORCE_ROOT", None)
    env["PORT"] = str(args.api_port)
    env["API_PORT"] = str(args.api_port)
    env["HOST"] = "127.0.0.1"
    env["LOG_LEVEL"] = env.get("LOG_LEVEL", "INFO")
    env["XDG_RUNTIME_DIR"] = str(workspace / "runtime")
    env["HOME"] = str(home_dir)
    env["USERPROFILE"] = str(home_dir)  # Windows compatibility

    if sys.platform == "darwin":
        env.setdefault("XDG_DOCUMENTS_DIR", str(docs_dir))

    backend_cwd = backend_path.parent
    creationflags = 0
    if os.name == "nt" and hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    backend_proc = subprocess.Popen(
        [str(backend_path)],
        cwd=str(backend_cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=creationflags,
    )

    # Thread to print backend output in real-time
    backend_output_lines = []
    def read_output():
        for line in backend_proc.stdout:
            backend_output_lines.append(line)
            print(line, end='', flush=True)
    
    output_thread = threading.Thread(target=read_output, daemon=True)
    output_thread.start()

    try:
        print(f"[smoke-test] Starting smoke test with timeout: {args.timeout}s, max processing: {args.max_processing_time}s")
        print(f"[smoke-test] FastSurfer mode: {args.fastsurfer_mode}")
        print(f"[smoke-test] Test image: {sample_path}")

        wait_for_health(
            args.api_port,
            timeout=args.health_timeout,
            initial_delay=args.health_initial_delay,
        )

        job_id = upload_scan(args.api_port, sample_path)

        # Use more restrictive timeout for real processing
        processing_timeout = min(args.max_processing_time, 7200)  # Cap at 2 hours
        if args.fastsurfer_mode == "real":
            processing_timeout = min(processing_timeout, 7200)  # 2 hours for real mode

        print(f"[smoke-test] Using processing timeout: {processing_timeout}s")

        job_info = poll_job(args.api_port, job_id, timeout=processing_timeout, stalled_threshold=args.stalled_threshold)
        status = job_info.get("status")

        if status == "completed":
            ensure_metrics(output_dir, job_id)
            print(f"[smoke-test] ✅ SUCCESS: Job {job_id} completed successfully")
            return  # Success!
        elif status == "failed":
            error_msg = job_info.get("error_message", "Unknown error")
            raise RuntimeError(f"Job failed with error: {error_msg}")
        else:
            raise RuntimeError(f"Job finished with unexpected status: {status}")

    except Exception as e:
        print(f"[smoke-test] ❌ FAILED: {e}", file=sys.stderr)
        raise  # Re-raise to ensure non-zero exit code
    finally:
        if backend_proc.poll() is None:
            if os.name == "nt":
                backend_proc.send_signal(signal.CTRL_BREAK_EVENT)
                time.sleep(2)
            backend_proc.terminate()
            try:
                backend_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                backend_proc.kill()
        # Backend output is already printed in real-time by the output thread


if __name__ == "__main__":
    main()

