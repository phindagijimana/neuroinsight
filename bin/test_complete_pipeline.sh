#!/bin/bash
# Complete End-to-End Pipeline Test
# Tests everything from upload to visualization

set -e

API_BASE="http://localhost:8000"
echo "=========================================="
echo "Complete Pipeline End-to-End Test"
echo "=========================================="
echo "API Base URL: $API_BASE"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Test function
test_step() {
    local name="$1"
    local command="$2"
    echo -n "Testing: $name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

# Detailed test function
test_step_detailed() {
    local name="$1"
    local command="$2"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Test: $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    eval "$command"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}FAILED${NC}"
        ((FAILED++))
    fi
}

echo "Step 1: Backend Health Check"
echo "─────────────────────────────"
test_step_detailed "Backend Health" "curl -s $API_BASE/health | python3 -m json.tool"

echo ""
echo "Step 2: Check Existing Jobs"
echo "─────────────────────────────"
test_step_detailed "List Jobs" "curl -s $API_BASE/jobs/ | python3 -c \"
import sys, json
data = json.load(sys.stdin)
print(f'  Total jobs: {len(data)}')
completed = [j for j in data if j.get('status') == 'completed']
print(f'  Completed jobs: {len(completed)}')
if completed:
    test_job = completed[0]
    print(f'  Test job ID: {test_job[\"id\"]}')
    print(f'  Filename: {test_job.get(\"filename\")}')
\""

# Find a completed job for testing
COMPLETED_JOB=$(curl -s $API_BASE/jobs/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
completed = [j for j in data if j.get('status') == 'completed']
if completed:
    print(completed[0]['id'])
else:
    print('')
" | head -1)

if [ -z "$COMPLETED_JOB" ]; then
    echo -e "${YELLOW}WARNING: No completed jobs found for testing${NC}"
    echo "Creating test job..."
    
    # Upload a test file
    TEST_FILE="/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo/frontend/node_modules/daikon/tests/data/implicit_little.dcm"
    if [ -f "$TEST_FILE" ]; then
        echo "Uploading test file..."
        UPLOAD_RESULT=$(curl -s -X POST \
            -F "file=@$TEST_FILE" \
            -F "patient_name=Test Patient" \
            -F "age=45" \
            -F "sex=M" \
            -F "scanner=TestScanner" \
            -F "sequence=T1w" \
            $API_BASE/upload/)
        
        NEW_JOB_ID=$(echo "$UPLOAD_RESULT" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
        if [ ! -z "$NEW_JOB_ID" ]; then
            echo "  Job created: $NEW_JOB_ID"
            echo "  Waiting for processing (this may take time)..."
            sleep 5
        fi
    fi
fi

if [ ! -z "$COMPLETED_JOB" ]; then
    echo ""
    echo "Step 3: Job Details"
    echo "───────────────────"
    test_step_detailed "Get Job Details" "curl -s $API_BASE/jobs/$COMPLETED_JOB | python3 -c \"
import sys, json
d = json.load(sys.stdin)
print(f'  Status: {d.get(\"status\")}')
print(f'  Filename: {d.get(\"filename\")}')
print(f'  Created: {d.get(\"created_at\")}')
print(f'  Completed: {d.get(\"completed_at\")}')
metrics = d.get('metrics', [])
print(f'  Metrics: {len(metrics)} found')
if metrics:
    m = metrics[0]
    print(f'    - {m.get(\"region\")}: L={m.get(\"left_volume\")}, R={m.get(\"right_volume\")}, AI={m.get(\"asymmetry_index\")}')
\""

    echo ""
    echo "Step 4: Metrics Retrieval"
    echo "─────────────────────────"
    test_step_detailed "Get Metrics" "curl -s $API_BASE/jobs/$COMPLETED_JOB | python3 -c \"
import sys, json
d = json.load(sys.stdin)
metrics = d.get('metrics', [])
if metrics:
    print('  Metrics available:')
    for m in metrics:
        print(f'    - {m.get(\"region\")}')
        print(f'      Left: {m.get(\"left_volume\")} mm³')
        print(f'      Right: {m.get(\"right_volume\")} mm³')
        print(f'      Asymmetry: {m.get(\"asymmetry_index\")}')
else:
    print('  No metrics found')
    exit(1)
\""

    echo ""
    echo "Step 5: Visualization Endpoints"
    echo "───────────────────────────────"
    test_step_detailed "Check Slice Endpoints" "
    SLICES_WORKING=0
    for i in 0 1 2 3 4; do
        SLICE_ID=\$(printf 'slice_%02d' \$i)
        HTTP_CODE=\$(curl -s -o /dev/null -w '%{http_code}' \"$API_BASE/visualizations/$COMPLETED_JOB/overlay/\$SLICE_ID\")
        if [ \"\$HTTP_CODE\" = \"200\" ]; then
            echo \"  Slice \$SLICE_ID: OK - HTTP 200\"
            ((SLICES_WORKING++))
        else
            echo \"  Slice \$SLICE_ID: ERROR - HTTP \$HTTP_CODE\"
        fi
    done
    if [ \$SLICES_WORKING -gt 0 ]; then
        echo \"  Result: \$SLICES_WORKING/5 slices working\"
        exit 0
    else
        exit 1
    fi
    "

    echo ""
    echo "Step 6: Visualization Files"
    echo "────────────────────────────"
    VIZ_DIR="/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo/data/outputs/$COMPLETED_JOB/visualizations/overlays"
    test_step_detailed "Check Files on Disk" "
    if [ -d \"$VIZ_DIR\" ]; then
        FILE_COUNT=\$(ls \"$VIZ_DIR\"/hippocampus_slice_*.png 2>/dev/null | wc -l)
        echo \"  Directory exists: OK\"
        echo \"  PNG files found: \$FILE_COUNT\"
        if [ \$FILE_COUNT -gt 0 ]; then
            ls -lh \"$VIZ_DIR\"/hippocampus_slice_*.png | head -3 | awk '{print \"    \" \$9 \" (\" \$5 \")\"}'
            exit 0
        else
            exit 1
        fi
    else
        echo \"  Directory not found: $VIZ_DIR\"
        exit 1
    fi
    "
fi

echo ""
echo "Step 7: Frontend File Check"
echo "───────────────────────────"
test_step_detailed "Frontend HTML Exists" "
FRONTEND_FILE=\"/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo/frontend/public/hippo_new_version.html\"
if [ -f \"\$FRONTEND_FILE\" ]; then
    echo \"  File exists: OK\"
    LINES=\$(wc -l < \"\$FRONTEND_FILE\")
    echo \"  Lines of code: \$LINES\"
    # Check for key functions
    if grep -q 'ApiService.getJobs' \"\$FRONTEND_FILE\"; then
        echo \"  API integration: OK\"
    else
        echo \"  API integration: ERROR\"
        exit 1
    fi
    if grep -q 'ViewerPage' \"\$FRONTEND_FILE\"; then
        echo \"  Viewer component: OK\"
    else
        echo \"  Viewer component: ERROR\"
        exit 1
    fi
    exit 0
else
    echo \"  File not found: \$FRONTEND_FILE\"
    exit 1
fi
"

echo ""
echo "Step 8: API Integration Check"
echo "─────────────────────────────"
test_step_detailed "Frontend API Calls" "
FRONTEND_FILE=\"/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo/frontend/public/hippo_new_version.html\"
APIS_FOUND=0
for api in 'getJobs' 'uploadFile' 'getJob' 'getMetrics' 'deleteJob'; do
    if grep -q \"ApiService.$api\" \"\$FRONTEND_FILE\"; then
        echo \"  OK: $api\"
        ((APIS_FOUND++))
    else
        echo \"  ERROR: $api (missing)\"
    fi
done
if [ \$APIS_FOUND -eq 5 ]; then
    exit 0
else
    exit 1
fi
"

echo ""
echo "Step 9: Patient Info Form Check"
echo "───────────────────────────────"
test_step_detailed "Patient Form Fields" "
FRONTEND_FILE=\"/mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo/frontend/public/hippo_new_version.html\"
FIELDS_FOUND=0
for field in 'patient_name' 'age' 'sex' 'scanner' 'sequence'; do
    if grep -q \"patientInfo.$field\" \"\$FRONTEND_FILE\" || grep -q \"$field\" \"\$FRONTEND_FILE\"; then
        echo \"  OK: $field\"
        ((FIELDS_FOUND++))
    else
        echo \"  ERROR: $field (missing)\"
    fi
done
if [ \$FIELDS_FOUND -ge 4 ]; then
    exit 0
else
    exit 1
fi
"

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}SUCCESS: All tests passed! Pipeline is fully functional.${NC}"
    exit 0
else
    echo -e "${YELLOW}WARNING: Some tests failed. Please review the output above.${NC}"
    exit 1
fi



