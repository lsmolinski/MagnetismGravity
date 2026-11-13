@echo off
setlocal EnableDelayedExpansion

REM ---------------------------------------------------------------
REM Check that python3 is available
REM ---------------------------------------------------------------
where python3 >nul 2>&1
if errorlevel 1 (
    echo ERROR: python3 not found in PATH.
    echo Try: python --version
    exit /b 1
)

set "scripts=ewt_amm_extended.py ewt_amm_resonance_scanner.py ewt_amm_structural_resonance.py ewt_electroweak_bosons.py ewt_emergence_engine.py ewt_particle_masses.py ewt_robustness_plots.py ewt_cosmological_constant.py"

set "FAILED="
set "OK_COUNT=0"
set "FAIL_COUNT=0"

REM ---------------------------------------------------------------
REM Run each script and check its exit code
REM ---------------------------------------------------------------
for %%f in (%scripts%) do (
    echo.
    echo ============================================================
    echo Running %%f ...
    echo ============================================================

    python3 -X utf8 %%f > %%~nf.txt 2>&1

    if errorlevel 1 (
        set /a FAIL_COUNT+=1
        set "FAILED=!FAILED! %%~nf"
        echo   [FAIL] %%f  -- see %%~nf.txt
        echo.
        echo   Last 10 lines of %%~nf.txt:
        powershell -NoProfile -Command "Get-Content '%%~nf.txt' -Tail 10"
        echo.
    ) else (
        set /a OK_COUNT+=1
        echo   [ OK ] %%f  -- saved to %%~nf.txt
    )
)

REM ---------------------------------------------------------------
REM Summary
REM ---------------------------------------------------------------
echo.
echo ============================================================
echo Summary
echo ============================================================
echo   Succeeded: !OK_COUNT!
echo   Failed:    !FAIL_COUNT!

if defined FAILED (
    echo   Failed scripts:!FAILED!
    endlocal & exit /b 1
) else (
    echo   All scripts completed successfully.
    endlocal & exit /b 0
)