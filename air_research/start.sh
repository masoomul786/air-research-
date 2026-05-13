#!/bin/bash
# AIR — AI Intermediate Representation
# One-Click Setup and Launch (Linux / macOS)

set -e

# ── Colors ────────────────────────────────────────────────────
GRN='\033[0;32m'; YLW='\033[1;33m'; RED='\033[0;31m'; CYN='\033[0;36m'; NC='\033[0m'; BLD='\033[1m'

echo ""
echo -e "${CYN}${BLD}  ╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYN}${BLD}  ║   AIR — AI Intermediate Representation                   ║${NC}"
echo -e "${CYN}${BLD}  ║   One-Click Setup and Launch                             ║${NC}"
echo -e "${CYN}${BLD}  ╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: Check Python ─────────────────────────────────────
echo -e "  ${BLD}[1/4]${NC} Checking Python..."
if command -v python3 &>/dev/null; then
    PY=python3
elif command -v python &>/dev/null; then
    PY=python
else
    echo -e "  ${RED}ERROR:${NC} Python 3 not found."
    echo "  Install from https://python.org or via your package manager:"
    echo "    macOS:  brew install python3"
    echo "    Ubuntu: sudo apt install python3 python3-pip"
    exit 1
fi
PY_VER=$($PY --version 2>&1)
echo -e "        ${GRN}✓${NC} $PY_VER"
echo ""

# ── Step 2: Install dependencies ─────────────────────────────
echo -e "  ${BLD}[2/4]${NC} Installing Python dependencies..."
$PY -m pip install -q flask flask-cors requests
echo -e "        ${GRN}✓${NC} flask, flask-cors, requests installed"
echo ""

# ── Step 3: Check LM Studio ──────────────────────────────────
echo -e "  ${BLD}[3/4]${NC} Checking LM Studio on localhost:1234..."
if curl -s --max-time 2 http://localhost:1234/v1/models &>/dev/null; then
    echo -e "        ${GRN}✓${NC} LM Studio is RUNNING"
else
    echo ""
    echo -e "  ${YLW}⚠  WARNING:${NC} LM Studio not detected on port 1234"
    echo ""
    echo "     Please:"
    echo "       1. Open LM Studio"
    echo "       2. Load a Qwen 3 (or any local) model"
    echo "       3. Start the Local Server  (port 1234)"
    echo ""
    echo "     The AIR server will start anyway."
    echo "     Press Enter to continue, or Ctrl+C to cancel."
    read -r
fi
echo ""

# ── Step 4: Launch AIR server ─────────────────────────────────
echo -e "  ${BLD}[4/4]${NC} Starting AIR Flask server..."
echo ""
echo -e "  ${BLD}──────────────────────────────────────────────────────────${NC}"
echo ""
echo -e "   ${CYN}AIR Generator${NC}  →  http://localhost:5000"
echo -e "   ${CYN}Benchmark${NC}      →  http://localhost:5000/benchmark.html"
echo ""
echo -e "  ${BLD}──────────────────────────────────────────────────────────${NC}"
echo ""
echo "  Opening browser in 3 seconds... (Ctrl+C to stop server)"
echo ""

# Open browser (macOS or Linux with xdg-open)
(sleep 3 && (open http://localhost:5000 2>/dev/null || xdg-open http://localhost:5000 2>/dev/null || true)) &

# Run server
$PY server.py
