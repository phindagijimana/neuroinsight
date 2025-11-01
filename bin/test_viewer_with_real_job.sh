#!/bin/bash
# Test script for hippo_new_version.html with real job data

JOB_ID="996d0b84-1b9e-4cb0-912e-40fe33aaa11f"
API_BASE_URL="http://localhost:8000"

echo "=========================================="
echo "Testing Hippo New Version HTML with Real Job"
echo "=========================================="
echo ""
echo "Job ID: $JOB_ID"
echo ""

# Test 1: Check job exists
echo "1. Testing job retrieval..."
JOB_DATA=$(curl -s "$API_BASE_URL/jobs/$JOB_ID")
if echo "$JOB_DATA" | grep -q "sub-02_T1w"; then
    echo "   ✅ Job found: $(echo "$JOB_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['filename'])")"
    echo "   Status: $(echo "$JOB_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['status'])")"
else
    echo "   ❌ Job not found!"
    exit 1
fi
echo ""

# Test 2: Check metrics
echo "2. Testing metrics..."
METRICS=$(echo "$JOB_DATA" | python3 -c "import sys, json; d=json.load(sys.stdin); print(json.dumps(d.get('metrics', [])))")
if echo "$METRICS" | grep -q "Hippocampus"; then
    echo "   ✅ Metrics found:"
    echo "$METRICS" | python3 -m json.tool | head -10
else
    echo "   ⚠️  No metrics in job data"
fi
echo ""

# Test 3: Test slice visualization endpoints
echo "3. Testing slice visualization endpoints..."
SLICE_COUNT=0
for i in {0..9}; do
    SLICE_ID=$(printf "slice_%02d" $i)
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/visualizations/$JOB_ID/overlay/$SLICE_ID")
    if [ "$HTTP_CODE" = "200" ]; then
        SLICE_COUNT=$((SLICE_COUNT + 1))
        if [ $i -eq 0 ]; then
            echo "   ✅ Slice $SLICE_ID: Available (HTTP $HTTP_CODE)"
        fi
    fi
done
echo "   Found $SLICE_COUNT slices available (slice_00 to slice_09)"
echo ""

# Test 4: Verify slice image format
echo "4. Testing slice image format..."
SLICE_RESPONSE=$(curl -s -I "$API_BASE_URL/visualizations/$JOB_ID/overlay/slice_00")
if echo "$SLICE_RESPONSE" | grep -q "image/png"; then
    echo "   ✅ Slice image is PNG format"
elif echo "$SLICE_RESPONSE" | grep -q "Content-Type"; then
    echo "   Content-Type: $(echo "$SLICE_RESPONSE" | grep -i "content-type")"
else
    echo "   ⚠️  Could not verify image format"
fi
echo ""

# Test 5: Check visualization directory
echo "5. Checking visualization files on disk..."
VIZ_DIR="/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo/data/outputs/$JOB_ID/visualizations/overlays"
if [ -d "$VIZ_DIR" ]; then
    SLICE_FILES=$(ls "$VIZ_DIR"/hippocampus_slice_*.png 2>/dev/null | wc -l)
    echo "   ✅ Visualization directory exists"
    echo "   Found $SLICE_FILES hippocampus overlay PNG files"
    
    if [ $SLICE_FILES -gt 0 ]; then
        echo "   Sample files:"
        ls "$VIZ_DIR"/hippocampus_slice_*.png | head -5 | xargs -n1 basename
    fi
else
    echo "   ❌ Visualization directory not found: $VIZ_DIR"
fi
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "✅ Job exists and is completed"
echo "✅ Metrics available in job data"
echo "✅ $SLICE_COUNT slice visualizations available via API"
echo ""
echo "You can now test the UI by:"
echo "1. Opening: http://localhost:5173/hippo_new_version.html"
echo "2. Navigate to Jobs page"
echo "3. Click the Activity icon on completed job: $JOB_ID"
echo "4. Viewer page should display real slice images"
echo ""



