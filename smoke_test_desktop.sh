#!/bin/bash
# Automated Smoke Test for Desktop App

echo "🧠 NeuroInsight Desktop App - Automated Smoke Test"
echo "=================================================="

# Set up environment
export PATH="$HOME/bin:$PATH"

# Use a real NIfTI file for testing
NIFTI_FILE="smoke_workdir/Documents/NeuroInsight/uploads/sub-1_T1w_small.nii.gz"

if [ ! -f "$NIFTI_FILE" ]; then
    echo "❌ Test NIfTI file not found: $NIFTI_FILE"
    exit 1
fi

echo "Using test file: $NIFTI_FILE"
echo "File size: $(ls -lh "$NIFTI_FILE" | awk '{print $5}')"
echo ""

# Run the smoke test
echo "🚀 Running smoke test..."
python3 tests/smoke_test.py \
    --backend-exe hippo_desktop/installers/NeuroInsight-1.0.5.AppImage \
    --input-nii "$NIFTI_FILE" \
    --api-port 8770 \
    --timeout 2400 \
    --max-processing-time 1200 \
    --fastsurfer-mode real \
    --workspace smoke_desktop_test

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ SMOKE TEST PASSED!"
    echo "   Desktop app successfully processed the NIfTI file"
else
    echo "❌ SMOKE TEST FAILED!"
    echo "   Check the output above for error details"
fi

exit $EXIT_CODE
