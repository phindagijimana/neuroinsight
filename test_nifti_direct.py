#!/usr/bin/env python3
"""
Direct NIfTI processing test - bypasses desktop GUI for headless testing.
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import nibabel as nib
import numpy as np
import requests
from backend.services.job_service import JobService
from backend.services.metric_service import MetricService
from backend.core.config import get_settings

def create_test_nifti(output_path: Path) -> None:
    """Create a simple test NIfTI file."""
    # Create a simple 3D brain-like volume
    data = np.zeros((64, 64, 32), dtype=np.float32)

    # Add some basic brain structure
    center = np.array([32, 32, 16])
    y, x, z = np.ogrid[:64, :64, :32]
    dist_from_center = np.sqrt((x - center[0])**2 + (y - center[1])**2 + (z - center[2])**2)
    brain_mask = dist_from_center < 25

    # Add some intensity variation
    data[brain_mask] = 100 + np.random.normal(0, 10, size=np.sum(brain_mask))

    affine = np.diag([1.0, 1.0, 1.0, 1.0])
    img = nib.Nifti1Image(data, affine)
    nib.save(img, str(output_path))
    print(f"Created test NIfTI: {output_path} ({output_path.stat().st_size} bytes)")

def test_with_real_nifti(nifti_path: Path) -> None:
    """Test processing with a real NIfTI file."""
    print(f"Testing with real NIfTI: {nifti_path}")
    print(f"File size: {nifti_path.stat().st_size} bytes")

    # Load and check the NIfTI file
    try:
        img = nib.load(str(nifti_path))
        data = img.get_fdata()
        print(f"NIfTI shape: {data.shape}")
        print(f"NIfTI data type: {data.dtype}")
        print(f"NIfTI affine:\n{img.affine}")
        print(".2f")
        print(f"Data range: [{data.min():.2f}, {data.max():.2f}]")

        # Basic validation
        if data.size == 0:
            raise ValueError("NIfTI file appears to be empty")
        if not np.isfinite(data).all():
            print("WARNING: NIfTI contains non-finite values")
        if data.min() < 0:
            print("WARNING: NIfTI contains negative values")

        print("✅ NIfTI file validation passed")

    except Exception as e:
        print(f"❌ NIfTI file validation failed: {e}")
        return False

    return True

def main():
    print("🧠 Direct NIfTI Processing Test")
    print("=" * 50)

    # Set up environment
    os.environ.setdefault("DESKTOP_MODE", "0")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("FASTSURFER_SMOKE_TEST", "1")  # Use smoke test mode

    # Test with real NIfTI file
    if len(sys.argv) > 1:
        nifti_file = Path(sys.argv[1])
        if not nifti_file.exists():
            print(f"❌ NIfTI file not found: {nifti_file}")
            return 1

        success = test_with_real_nifti(nifti_file)
        if not success:
            return 1
    else:
        # Create and test with synthetic NIfTI
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_brain.nii.gz"
            create_test_nifti(test_file)
            success = test_with_real_nifti(test_file)
            if not success:
                return 1

    print("\n✅ All tests passed!")
    print("\nNote: For full processing pipeline testing, run:")
    print("  python3 tests/smoke_test.py --backend-exe <path> --input-nii <nifti_file>")

if __name__ == "__main__":
    sys.exit(main())
