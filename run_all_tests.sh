#!/bin/bash
# Fortes Education - Run All Tests and Evaluation

echo "================================================"
echo "Fortes Education - Comprehensive Test Suite"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test
run_test() {
    echo -e "${YELLOW}Running: $1${NC}"
    if $2; then
        echo -e "${GREEN}✓ $1 PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ $1 FAILED${NC}"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# Navigate to backend
cd backend

# Run tests
echo "1. Running Chunker Tests..."
run_test "Chunker Tests" "pytest tests/test_chunker.py -v"

echo "2. Running Guardrails Tests..."
run_test "Guardrails Tests" "pytest tests/test_guardrails.py -v"

echo "3. Running Retriever Tests..."
run_test "Retriever Tests" "pytest tests/test_retriever.py -v"

echo "4. Running Evaluation Math Tests..."
run_test "Eval Math Tests" "pytest tests/test_eval_math.py -v"

echo "5. Running Full Evaluation Harness..."
run_test "Evaluation Harness" "python run_eval.py"

# Summary
echo "================================================"
echo "TEST SUMMARY"
echo "================================================"
echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    exit 1
fi

