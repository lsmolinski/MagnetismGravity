@echo off
set "scripts=ewt_amm_extended.py ewt_amm_resonance_scanner.py ewt_amm_structural_resonance.py ewt_electroweak_bosons.py ewt_emergence_engine.py ewt_particle_masses.py ewt_robustness_plots.py ewt_cosmological_constant.py"

for %%f in (%scripts%) do (
    echo Run %%f ...
    python3 -X utf8 %%f > %%~nf.txt 2>&1
    echo saved to %%~nf.txt
)

echo All done.
