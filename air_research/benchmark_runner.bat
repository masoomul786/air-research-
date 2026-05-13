@echo off
title AIR Benchmark Runner
color 0B

echo.
echo  AIR Benchmark Runner
echo  ════════════════════
echo.
echo  Make sure the AIR server is running (start.bat) before
echo  running this benchmark.
echo.

set /p MODE="  Run mode: [1] Unit tests only  [2] Full benchmark (all 24): "

if "%MODE%"=="2" (
    echo.
    echo  Running full benchmark suite (24 prompts)...
    echo  Results saved to benchmark\results\
    echo.
    python benchmark\run_benchmark.py --full --output benchmark\results
) else (
    echo.
    echo  Running unit tests...
    echo.
    python benchmark\run_benchmark.py --unit-only
)

echo.
pause
