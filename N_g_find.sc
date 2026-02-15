// ==============================================================================
// SCILAB SCRIPT: EWT GRAVITY - K=10 GEOMETRIC RECONCILIATION
// ==============================================================================
clear; clc; format(20);

// --- 1. STAŁE FIZYCZNE (CODATA 2022) ---
c_0      = 299792458; 
m_e      = 9.1093837015d-31; 
r_e      = 2.8179403262d-15;
G_CODATA = 6.674305d-11; 
Pi       = %pi; 
e_euler  = %e;

// --- 2. PARAMETRY WEJŚCIOWE EWT ---
N_final  = 778.818123; 
r_nu_val = 2.81794d-17;
lambda_l = 1.6162d-35;
K        = 10;         // Liczba centrów falowych (Wave Centers)
A_pi     = (4*Pi^3 + Pi^2 + Pi);
G_Base   = (c_0^2 * r_e) / m_e;

// --- 3. TŁO ODNIESIENIA (N_stat) ---
N_nu_stat = (r_nu_val / (2 * lambda_l * e_euler))^3;

// --- 4. WYZNACZANIE N_EFF KALIBROWANEGO (Wymóg matematyczny) ---
// G = (G_Base / A_pi) * (1 / (N*A_pi)^3) * (1 / (K * sqrt(N_eff)))
Term_Base   = G_Base / A_pi;
Term_Volume = 1 / (N_final * A_pi)^3;
N_eff_calibrated = ( (Term_Base * Term_Volume) / (K * G_CODATA) )^2;

// --- 5. WYZNACZANIE N_EFF GEOMETRYCZNEGO (Nasza nowa hipoteza) ---
// Hipoteza: X = A_pi * 3 * K * sqrt(2)
X_geom = A_pi * 3 * K * sqrt(2); 
N_eff_geom = N_nu_stat / X_geom;

// --- 6. OBLICZENIE FINALNEGO G Z GEOMETRII ---
G_model_geom = (G_Base / A_pi) * (1 / (N_final * A_pi)^3) * (1 / (K * sqrt(N_eff_geom)));

// --- 7. LOGOWANIE WARTOŚCI ---
disp("==============================================================================");
disp("   EWT GRAVITY: GEOMETRIC VS CALIBRATED ANALYSIS (K=10)");
disp("==============================================================================");
disp(['N_nu_statutory (Background):    ', string(N_nu_stat)]);
disp(['N_nu_effective_geom (Dilution): ', string(N_eff_geom)]);
disp(['N_nu_calibrated (Required):     ', string(N_eff_calibrated)]);
disp("------------------------------------------------------------------------------");
printf("Wymagana stała dylucji X (Calib): %.10f\n", N_nu_stat / N_eff_calibrated);
printf("Proponowana stała X (Geometric):  %.10f\n", X_geom);
disp("------------------------------------------------------------------------------");
printf("G_CODATA:  %.15e\n", G_CODATA);
printf("G_Model:   %.15e\n", G_model_geom);
printf("BŁĄD MODELU: %.10f %%\n", (G_model_geom - G_CODATA) / G_CODATA * 100);
disp("==============================================================================");

// --- 8. ANALIZA STRUKTURY X ---
// Sprawdzamy czy X_geom można jeszcze "dopieścić" o korektę (1 - 1/2N)
X_refined = X_geom / (1 - 1/(2*N_final));
N_eff_refined = N_nu_stat / X_refined;
G_refined = (G_Base / A_pi) * (1 / (N_final * A_pi)^3) * (1 / (K * sqrt(N_eff_refined)));
printf("BŁĄD Z POPRAWKĄ (1-1/2N): %.10f %%\n", (G_refined - G_CODATA) / G_CODATA * 100);