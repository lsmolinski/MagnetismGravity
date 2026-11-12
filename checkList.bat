@echo off
setlocal
cd /d "%~dp0"

set TEX=MagnetismGravity.tex

echo ============================================
echo  Check 5.2.3 - comprehensive verification
echo ============================================
echo.

echo ----- SECTION A: PYTHON -----
echo.

echo [A1] C_fermion in Python (should be GONE)
findstr /N /C:"C_fermion" ewt_emergence_engine.py || echo     OK - pusto
findstr /N /C:"C_fermion" ewt_electroweak_bosons.py || echo     OK - pusto
findstr /N /C:"C_fermion" ewt_robustness_plots.py || echo     OK - pusto
echo.

echo [A2] old hardcoded A_pi (137.036040608) in Python (should be GONE)
findstr /N /C:"137.036040608" ewt_robustness_plots.py || echo     OK - pusto

echo [A2b] A_PI = compute_alpha_core() (should be PRESENT)
findstr /N /C:"A_PI = compute_alpha_core" ewt_robustness_plots.py
echo.

echo [A3] old hardcoded quark masses in Python (should be GONE)
findstr /N /C:"0.0046597252" ewt_robustness_plots.py || echo     OK - pusto
findstr /N /C:"0.0931160638" ewt_robustness_plots.py || echo     OK - pusto
findstr /N /C:"0.004692" ewt_emergence_engine.py || echo     OK - pusto
findstr /N /C:"0.094954" ewt_emergence_engine.py || echo     OK - pusto
findstr /N /C:"0.004692" ewt_electroweak_bosons.py || echo     OK - pusto
findstr /N /C:"0.094954" ewt_electroweak_bosons.py || echo     OK - pusto
echo.

echo [A4] old hardcoded N_nu in module 8 (should be GONE)
findstr /N /C:"3.2986e52" ewt_robustness_plots.py || echo     OK - pusto
findstr /N /C:"6.2525176e48" ewt_robustness_plots.py || echo     OK - pusto
echo.

echo [A5] synthetic placeholders in module 9 (should be GONE)
findstr /N /C:"a_mu_norm = 1.0 +" ewt_robustness_plots.py || echo     OK - pusto
findstr /N /C:"a_tau_norm = 1.0 +" ewt_robustness_plots.py || echo     OK - pusto
echo.

echo [A6] eps_flavor in robustness_plots.py (should be PRESENT, 2x)
findstr /N /C:"eps_flavor" ewt_robustness_plots.py
echo.

echo [A7] mass_spherical(15) and (28) in module 10 (should be PRESENT)
findstr /N /C:"mass_spherical(15)" ewt_robustness_plots.py
findstr /N /C:"mass_spherical(28)" ewt_robustness_plots.py
echo.

echo ----- SECTION B: LATEX -----
echo.

echo [B1] C_fermion in LaTeX (should be GONE or only historical)
findstr /N /C:"C_{\text{fermion}}" %TEX% || echo     OK - pusto
echo.

echo [B2] old 0.0055 value (should be GONE)
findstr /N /C:"0.0055" %TEX% || echo     OK - pusto
echo.

echo [B3] old tuned quark masses (should be GONE or historical)
findstr /N /C:"4.692" %TEX% || echo     OK - pusto
findstr /N /C:"94.954" %TEX% || echo     OK - pusto
echo.

echo [B4] pi-to-infinity argument (should be GONE)
findstr /N /C:"\pi^7 \to \infty" %TEX% || echo     OK - pusto
findstr /N /C:"\pi^6 \to \infty" %TEX% || echo     OK - pusto
echo.

echo [B5] parallel-impedance (should be PRESENT, min 10)
findstr /N /C:"parallel-impedance" %TEX%
echo.

echo [B6] epsilon_flavor (should be PRESENT, min 15)
findstr /N /C:"epsilon_{\text{flavor}}" %TEX%
echo.

echo [B7] eps_flavor with (1-zeta) full form (should be PRESENT, min 4)
findstr /N /C:"8\pi^5(1-\zeta)" %TEX%
echo.

echo [B8] F(Psi) = +gamma Psi^3 defocusing sign (should be GONE)
findstr /N /C:"+\gamma\Psi^{3}" %TEX% || echo     OK - pusto
findstr /N /C:"+\gamma\,\Psi^{3}" %TEX% || echo     OK - pusto
echo.

echo [B9] F(Psi) = -gamma Psi^3 self-focusing sign (should be PRESENT, min 1)
findstr /N /C:"-\gamma\Psi^{3}" %TEX%
findstr /N /C:"-\gamma\,\Psi^{3}" %TEX%
echo.

echo [B10] winding number mathbf{n} vector field (should be PRESENT, min 8)
findstr /N /C:"mathbf{n}" %TEX%
echo.

echo [B11] old scalar winding Psi^* omega (should be GONE)
findstr /N /C:"\Psi^* \omega" %TEX% || echo     OK - pusto
findstr /N /C:"\Psi^{*}\,\omega" %TEX% || echo     OK - pusto
echo.

echo [B12] Manton-Sutcliffe citation (should be PRESENT, 2x)
findstr /N /C:"MantonSutcliffe2004" %TEX%
echo.

echo [B13] inventory class VI legacy EWT (should be PRESENT, 1x)
findstr /N /C:"VI. Legacy baseline-EWT" %TEX%
echo.

echo [B14] class VI references (should be PRESENT, min 2)
findstr /N /C:"class~VI" %TEX%
echo.

echo [B15] r_nu Derived quantity (should be PRESENT, 1x)
findstr /N /C:"Derived quantity" %TEX%
echo.

echo [B16] e notation warning (should be PRESENT, 1x)
findstr /N /C:"Notation warning" %TEX%
echo.

echo [B17] Q=10 structural assignment (should be PRESENT, 1x)
findstr /N /C:"structural assignment" %TEX%
echo.

echo [B18] key labels (should be PRESENT)
findstr /N /C:"label{eq:winding_number}" %TEX% || echo     MISSING eq:winding_number
findstr /N /C:"label{eq:eps_flavor" %TEX%
echo.

echo ----- SECTION C: RUN PYTHON -----
echo.

echo [C1] ewt_emergence_engine.py
python ewt_emergence_engine.py > temp_engine_out.txt 2>&1
if errorlevel 1 (
    echo     FAILED - see temp_engine_out.txt
    type temp_engine_out.txt
) else (
    echo     OK
)
echo.

echo [C2] ewt_electroweak_bosons.py
python ewt_electroweak_bosons.py > temp_ewb_out.txt 2>&1
if errorlevel 1 (
    echo     FAILED - see temp_ewb_out.txt
    type temp_ewb_out.txt
) else (
    echo     OK
)
echo.

echo [C3] ewt_robustness_plots.py
python ewt_robustness_plots.py > temp_robust_out.txt 2>&1
if errorlevel 1 (
    echo     FAILED - see temp_robust_out.txt
    type temp_robust_out.txt
) else (
    echo     OK
)
echo.

echo ----- SECTION D: KEY OUTPUT VALUES -----
echo.

echo [D1] sin theta_C in engine output (should be ~0.22429)
findstr /C:"sin theta_C" ewt_emergence_engine.txt
echo.

echo [D2] eps_flavor in engine output (should be ~4.087e-04)
findstr /C:"eps_flavor" ewt_emergence_engine.txt
echo.

echo [D3] zeta in engine output (should be ~6.03e-04)
findstr /C:"zeta" ewt_emergence_engine.txt
echo.

echo [D4] Cabibbo Variants in electroweak output
findstr /C:"Variant B" ewt_electroweak_bosons.txt
findstr /C:"Variant C" ewt_electroweak_bosons.txt
findstr /C:"Bare GST" ewt_electroweak_bosons.txt
echo.

echo ============================================
echo  Check complete
echo ============================================
echo.
echo Interpretacja:
echo   A1-A5, B1-B4, B8, B11: pusto = OK (bylo = zle)
echo   A2b, A6-A7, B5-B7, B9-B10, B12-B18: powinny byc wartosci (0 = zle)
echo   C1-C3: wszystkie powinny byc OK
echo   D1-D4: wartosci zgodne z oczekiwanymi
echo.
echo Jesli A6 ma mniej niz 2 lub B6 mniej niz 15 - sprawdz czy
echo wszystkie fixy z 5.2.2 i 5.2.3 zostaly wklejone.
echo.
pause