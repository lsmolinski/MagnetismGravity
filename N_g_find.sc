// ==============================================================================
// EWT MAIN SCRIPT: FULL LOGGING & GEOMETRIC CALIBRATION (L_p = 1.1486)
// ==============================================================================
clear; clc; format(20);

// --- 1. PHYSICAL CONSTANTS (CODATA 2022) ---
c_0      = 299792458; 
m_e      = 9.1093837015d-31; 
r_re     = 2.8179403262d-15;
G_CODATA = 6.674305d-11; 
Pi       = %pi; 
e_euler  = %e;

// --- 2. EWT CORE PARAMETERS ---
N_final  = 778.818123; 
r_nu_val = 2.81794d-17;
lambda_l = 1.6162d-35;
K        = 10;
A_pi     = (4*Pi^3 + Pi^2 + Pi);
G_Base   = (c_0^2 * r_re) / m_e;

// --- 3. GEOMETRIC BRIDGE & PROJECTION ---
eps_M      = 1 / (N_final * Pi^3);
alpha_geom = 1 / (A_pi - eps_M);
L_p        = 1.1486801482; // Lattice Projection Factor
C_Unif     = (1 + 1/K) + (alpha_geom / (Pi * L_p)); 

// --- 4. NODAL DENSITY LEVELS (The core logging data) ---

// A. N_nu MAX (Absolute Packing)
N_nu_max  = (r_nu_val / lambda_l)^3;

// B. N_nu STAT (Background Density)
N_nu_stat = (r_nu_val / (2 * lambda_l * e_euler))^3;

// C. N_nu GEOM (Effective EMC Density after 99.98% push-out)
X_eff_geom  = (A_pi * 3 * K * sqrt(2)) / C_Unif;
N_eff_geom  = N_nu_stat / X_eff_geom;

// D. N_nu CALIB (The value required by CODATA G)
Term_Base   = G_Base / A_pi;
Term_Volume = 1 / (N_final * A_pi)^3;
N_eff_calib = ( (Term_Base * Term_Volume) / (K * G_CODATA) )^2;

// --- 5. FINAL G CALCULATION ---
G_EWT = (Term_Base) * (Term_Volume) * (1 / (K * sqrt(N_eff_geom)));

// --- 6. FULL LOGGING (ENGLISH) ---
disp("==============================================================================");
disp("    EWT UNIFIED GRAVITY LOG: FULL DENSITY & GEOMETRIC CALIBRATION");
disp("==============================================================================");
printf("N_nu_max (Absolute Max):    %.15e\n", N_nu_max);
printf("N_nu_stat (Background):     %.15e\n", N_nu_stat);
printf("N_nu_geom (Effective EMC):  %.15e\n", N_eff_geom);
printf("N_nu_calib (Target G):      %.15e\n", N_eff_calib);
disp("------------------------------------------------------------------------------");
printf("LATTICE DYNAMICS (Dilution Frames):\n");
printf("- Eulerian Dilution (Max -> Stat):  %.10f %%\n", (1 - N_nu_stat/N_nu_max)*100);
printf("- Soliton Push-out (Stat -> Geom):  %.10f %%\n", (1 - N_eff_geom/N_nu_stat)*100);
disp("------------------------------------------------------------------------------");
printf("EMC DILUTION PARAMETERS:\n");
printf("- X_eff factor:                     %.10f\n", X_eff_geom);
printf("- Lattice Projection L_p:           %.10f\n", L_p);
printf("- Geometric Correction C_Unif:      %.10f\n", C_Unif);
disp("------------------------------------------------------------------------------");
printf("QUANTITATIVE COMPARISON:\n");
printf("- N_eff Density Error:              %.12f %%\n", (N_eff_geom - N_eff_calib)/N_eff_calib * 100);
printf("- G_CODATA:                         %.15e\n", G_CODATA);
printf("- G_EWT (Projected):                %.15e\n", G_EWT);
printf("- FINAL ACCURACY ERROR G:           %.15f %%\n", (G_EWT - G_CODATA)/G_CODATA * 100);
disp("==============================================================================");