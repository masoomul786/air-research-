#!/bin/bash
# AIR Benchmark Runner (Linux / macOS)

GRN='\033[0;32m'; CYN='\033[0;36m'; BLD='\033[1m'; NC='\033[0m'

echo ""
echo -e "${CYN}${BLD}  AIR Benchmark Runner${NC}"
echo -e "  ════════════════════"
echo ""
echo "  Make sure the AIR server (start.sh) is running first."
echo ""
echo "  Run modes:"
echo "    1  Unit tests only (fast — ~30s)"
echo "    2  Full benchmark  (all 24 prompts — ~20 min)"
echo ""
read -p "  Choose [1/2]: " MODE

if command -v python3 &>/dev/null; then PY=python3; else PY=python; fi

if [ "$MODE" = "2" ]; then
    echo ""
    echo "  Running full benchmark (24 prompts)..."
    echo "  Results → benchmark/results/"
    echo ""
    $PY benchmark/run_benchmark.py --full --output benchmark/results
else
    echo ""
    echo "  Running unit tests..."
    echo ""
    $PY benchmark/run_benchmark.py --unit-only
fi
