//VERSION: 4.1.10
clear; clearglobal; clc;
format(20);
// Detect script directory for local export
try script_path = get_absolute_file_path("AMM_find.sc"); catch script_path = ""; end
// --- 1. CORE EWT CALCULATION ---
function [am_ppm, at_ppm, e_m, e_t] = calculate_EWT(Kn_m_in, Kn_t_in)
    alpha_inv = 137.035999084; alpha = 1 / alpha_inv; Pi = %pi;
    N_final = 778.818123000000014; eps_M = 1 / (N_final * (Pi^3));
    A_pi = 4*Pi^3 + Pi^2 + Pi; Kn_e = 10;
    
    // Experimental Targets (CODATA)
    target_amu = 248.8 / 1e6; target_atau = 1177.21 / 1e6;
    
    // Invariants from Onion Model (Sec 3.2)
    L_mu = 5;   
    L_tau = 34; // Fibonacci latch
    
    // Core: Electron Ground State
    ae_pred = (alpha / (2 * Pi)) * (1 - eps_M * (Pi^3));
    
    // Shell 1: Muon Resonance
    M_mu_shell = (Kn_m_in - Kn_e) / Kn_e;     
    B_mu_scale = (3 * A_pi * Pi^3) / (2 * L_mu^2);
    amu_shell = B_mu_scale * (1 - eps_M)^(M_mu_shell * Pi^3);
    am_ppm = (ae_pred + amu_shell); 
    e_m = abs(am_ppm/1e6 - target_amu) / target_amu * 100;

    // Shell 2: Tau Resonance (Recursive addition)
    M_tau_rel = Kn_t_in / Kn_e;       
    // B_tau_base incorporates the 8*sqrt(2) lattice factor
    B_tau_base = ((3 * A_pi * Pi^3) / (8 * sqrt(2))) + (A_pi / 2);
    at_shell = B_tau_base * (1 - eps_M)^(M_tau_rel * Pi^3);
    at_ppm = am_ppm + at_shell + L_mu^2; // L_mu^2 = 25 (interface tension)
    e_t = abs(at_ppm/1e6 - target_atau) / target_atau * 100;
endfunction

// Scan range aligned with LaTeX Table 1 (207, 2181)
Km_scan = 195:215; 
Kt_scan = 2170:2190; 
[KM, KT] = meshgrid(Km_scan, Kt_scan);
Z_err = zeros(KM);

printf("=== EWT RECURSIVE HIERARCHY ANALYSIS ===\n");
printf("Reference: Onion Model\n\n");


for i = 1:size(KM, 1)
    for j = 1:size(KM, 2)
        [am, at, em, et] = calculate_EWT(KM(i,j), KT(i,j));
        Z_err(i,j) = (em + et) / 2;
        
        if (KM(i,j) == 207 | KM(i,j) == 200) & (KT(i,j) == 2181 | KT(i,j) == 2180) then
            printf("POINT: Km=%d, Kt=%d | Err_mu: %.6f%% | Err_tau: %.6f%% | Mean: %.6f%% | amu: %.4f | atau: %.4f\n", ..
            KM(i,j), KT(i,j), em, et, Z_err(i,j), am, at);
        end
    end
end
Z_plot = (1 ./ (Z_err + 0.0001)).';

// --- 2. MULTI-WINDOW VISUALIZATION & PDF EXPORT ---

// FIG 1: Muon Profile
scf(1); clf();
m_idx = find(Kt_scan == 2181);
plot(Km_scan, Z_err(m_idx,:), "r-o"); xgrid();
xtitle("Muon 2D Resonance Profile", "Nodes Km", "Total Error %");
xs2pdf(1, script_path + "Fig1_Muon_Profile.pdf");
printf("EXPORTED: Fig1_Muon_Profile.pdf\n");

// FIG 2: Tau Profile
scf(2); clf();
t_idx = find(Km_scan == 207);
plot(Kt_scan, Z_err(:, t_idx), "b-s"); xgrid();
xtitle("Tau 2D Resonance Profile", "Nodes Kt", "Total Error %");
xs2pdf(2, script_path + "Fig2_Tau_Profile.pdf");
printf("EXPORTED: Fig2_Tau_Profile.pdf\n");

// FIG 3: 3D Stability Peak (For verification)
scf(3); clf();
plot3d1(Km_scan, Kt_scan, Z_plot, theta=45, alpha=65); 
xtitle("Recursive Stability Surface (Onion Model)");
xs2pdf(3, script_path + "Fig3_3D_Peak.pdf");
printf("EXPORTED: Fig3_3D_Peak.pdf\n");

// FIG 4: Topographic Map
scf(4); clf();
contour2d(Km_scan, Kt_scan, Z_plot, 15); xgrid();
xtitle("Topographic Lattice Latches (Km vs Kt)", "Km", "Kt");
xs2pdf(4, script_path + "Fig4_Topography.pdf");
printf("EXPORTED: Fig4_Topography.pdf\n");

printf("\n--- ALL DATA SYNCHRONIZED WITH LATEX DOCUMENT ---\n");