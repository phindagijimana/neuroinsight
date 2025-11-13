#!/usr/bin/env python3
"""
Cross-platform smoke test for the NeuroInsight desktop backend.

Steps:
1. Create (or copy) a NIfTI T1 file suitable for upload.
2. Launch the PyInstaller-built backend executable in desktop mode.
3. Wait for /health to respond.
4. Upload the scan, poll until completion, verify metrics.json exists.
5. Shut down the backend gracefully.
"""

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

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


def wait_for_health(port: int, timeout: int = 120) -> None:
    """Wait until /health endpoint responds with 200 within timeout."""
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(f"{base_url}/health", timeout=5)
            if resp.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    raise RuntimeError("Backend did not become healthy within timeout")


def upload_scan(port: int, file_path: Path) -> str:
    """Upload scan and return job_id."""
    base_url = f"http://127.0.0.1:{port}"
    with file_path.open("rb") as fh:
        files = {"file": (file_path.name, fh, "application/octet-stream")}
        resp = requests.post(f"{base_url}/upload/", files=files, timeout=60)
    resp.raise_for_status()
    payload = resp.json()
    job_id = payload.get("job_id") or payload.get("id")
    if not job_id:
        raise RuntimeError(f"Upload succeeded but no job_id returned: {payload}")
    return str(job_id)


def poll_job(port: int, job_id: str, timeout: int = 600) -> dict:
    """Poll job endpoint until completion or timeout."""
    base_url = f"http://127.0.0.1:{port}"
    deadline = time.time() + timeout
    while time.time() < deadline:
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
        if status in {"COMPLETED", "FAILED"}:
            return payload
        time.sleep(3)
    raise RuntimeError("Job did not finish within timeout")


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
    parser.add_argument("--timeout", type=int, default=600, help="Overall timeout seconds")
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

    try:
        wait_for_health(args.api_port)
        job_id = upload_scan(args.api_port, sample_path)
        job_info = poll_job(args.api_port, job_id, timeout=args.timeout)
        status = job_info.get("status")
        if status != "COMPLETED":
            raise RuntimeError(f"Job finished with unexpected status: {status}")
        ensure_metrics(output_dir, job_id)
        print(f"Smoke test passed: job {job_id} completed.")
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
        if backend_proc.stdout:
            backend_output = backend_proc.stdout.read()
            print("=== Backend output ===")
            print(backend_output)


if __name__ == "__main__":
    main()

