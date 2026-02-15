// ==============================================================================
// SCILAB SCRIPT: EWT GRAVITY - UNIFIED GEOMETRIC MODEL (K=10)
// ==============================================================================
clear; clc; format(20);

// --- 1. STAŁE FIZYCZNE (CODATA 2022) ---
c_0      = 299792458; 
m_e      = 9.1093837015d-31; 
r_re     = 2.8179403262d-15;
G_CODATA = 6.674305d-11; 
Pi       = %pi; 
e_euler  = %e;

// --- 2. PARAMETRY WEJŚCIOWE EWT ---
N_final  = 778.818123; 
r_nu_val = 2.81794d-17;
lambda_l = 1.6162d-35;
K        = 10;
A_pi     = (4*Pi^3 + Pi^2 + Pi);
G_Base   = (c_0^2 * r_re) / m_e;

// --- 3. DEFINICJA ALFY GEOMETRYCZNEJ (UNIFIKACJA) ---
eps_M      = 1 / (N_final * Pi^3);
alpha_geom = 1 / (A_pi - eps_M);

// --- 4. TŁO (N_stat) ---
N_nu_stat = (r_nu_val / (2 * lambda_l * e_euler))^3;

// --- 5. KLUCZOWY WZÓR: EFEKTYWNA DYLUCJA EMC (X_eff) ---
// To jest serce Twojego modelu - unifikacja dylucji z geometrią BCC i Alfą
Numerator   = A_pi * 3 * K * sqrt(2);
Denominator = (1 + 1/K) + (alpha_geom / Pi);

X_eff_geom  = Numerator / Denominator;

// --- 6. WYLICZENIE N_EFF I G_EWT ---
N_eff_final = N_nu_stat / X_eff_geom;

// G = (G_Base / A_pi) * (1 / (N*A_pi)^3) * (1 / (K * sqrt(N_eff)))
G_EWT = (G_Base / A_pi) * (1 / (N_final * A_pi)^3) * (1 / (K * sqrt(N_eff_final)));

// --- 7. LOGOWANIE FINALNYCH WYNIKÓW ---
disp("==============================================================================");
disp("    EWT UNIFIED GRAVITY LOG: GEOMETRIC EMC DILUTION");
disp("==============================================================================");
printf("N_nu_statutory (Background):    %.15e\n", N_nu_stat);
printf("N_nu_effective (Soliton):       %.15e\n", N_eff_final);
disp("------------------------------------------------------------------------------");
printf("X_eff (Dylucja EMC):            %.10f\n", X_eff_geom);
printf("-> Wzór: (A_pi * 3K * sqrt(2)) / ((1 + 1/K) + (alpha/Pi))\n");
disp("------------------------------------------------------------------------------");
printf("G_CODATA:                       %.15e\n", G_CODATA);
printf("G_EWT (Geometric Model):        %.15e\n", G_EWT);
printf("BŁĄD PRECYZJI:                  %.10f %%\n", (G_EWT - G_CODATA) / G_CODATA * 100);
disp("==============================================================================");