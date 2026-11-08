REM 1. Stare wartości usunięte
findstr /N /C:"0.0055" MagnetismGravity.tex
findstr /N /C:"4.692" MagnetismGravity.tex
findstr /N /C:"94.954" MagnetismGravity.tex
REM Oczekiwane: pusto (0.0055 i 4.692/94.954 tylko w A6 jako "earlier versions")

REM 2. Nowe wartości obecne
findstr /N /C:"epsilon_{\text{flavor}}" MagnetismGravity.tex
REM Oczekiwane: Dimensional Budget (A1), Symmetry (A2), Section 3.2.2 (A3), Table (A4), Inventory (A5), Section 32 (A6)

findstr /N /C:"0.22430" MagnetismGravity.tex
REM Oczekiwane: Section 3.2.2 (Variant B), Table (Variant B + reference)

REM 3. C_fermion tylko jako deprecated
findstr /N /C:"C_{\text{fermion}}" MagnetismGravity.tex
REM Oczekiwane: A1 (historyczne "old quadratic form"), A5 (inventory deprecated), A6 (Section 32 deprecated)

