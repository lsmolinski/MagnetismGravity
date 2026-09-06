#!/usr/bin/env python3
"""
Enhanced EWT -- Robustness & Stability Plot Suite
==================================================
Python port of EWT_Robustness_G_AMM_check.sc (Modules 1-10),
adapted to the zero-calibration geometric version.

Uses the geometric eps_M derived from BCC packing impedance
instead of the old calibrated N_final and L_p.

Generates the same PDF figures as the Scilab original.
"""

import os
import math

import numpy as np
import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# Import shared functions from the main engine and other modules
try:
    from ewt_emergence_engine import (
        PI, SQRT2, SQRT3, EULER,
        C0, M_E, R_E, G_CODATA,
        ALPHA_INV_CODATA, A_E_CODATA,
        M_Z_CODATA, M_W_PDG, M_W_CDFII, M_H_CODATA,
        SIN2_THETA_W, SIN_THETA_C_PDG,
        M_D_PDG, M_S_PDG,
        Q_P_INPUT, LAMBDA_L, E_CHARGE_CODATA,
        compute_alpha_core,
        compute_alpha_geometric,
        derive_eps_M_from_BCC,
        lattice_impedance,
        build_geometric_ladder,
        derive_hbar,
        derive_planck_charge_from_e,
        derive_lambda_uncorr,
        derive_neutrino_radius,
        test_decadic_resonance,
        compute_C_unif,
        compute_X_eff,
        derive_lambda_l_geometric,
        gravity_sector,
        compute_lepton_amms,
        compute_atomic_scales,
        get_AMMi_K,
    )
    from ewt_particle_masses import mass_spherical, mass_orbital, mass_meson_style
    from ewt_electroweak_bosons import (
        weinberg_sector,
        compute_higgs_mixing_angles,
        cabibbo_sector,
        compute_boson_radii,
        test_weinberg_angle,
    )
except ImportError:
    raise ImportError(
        "This module requires ewt_emergence_engine.py, ewt_particle_masses.py "
        "and ewt_electroweak_bosons.py in the same directory."
    )


# ----------------------------------------------------------------------
# Helper: create output directory and return PDF path
# ----------------------------------------------------------------------
def pdf_path(filename: str) -> str:
    out_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(out_dir, filename)


# ----------------------------------------------------------------------
# MODULE 1: G-CONSTANT SURFACE TRANSITION ANALYSIS
# ----------------------------------------------------------------------
def module1_g_surface_transition():
    # Use geometric N_geom from BCC
    bcc = derive_eps_M_from_BCC(8.0 * PI**4)
    N_geom = bcc["N_geom"]
    A_pi = compute_alpha_core()
    G_Base = (C0**2 * R_E) / M_E
    K_WC = 10

    # Scan over N_nu (volume deficit)
    N_test_range = np.linspace(1.2e48, 1.0e49, 1000)
    G_results = (G_Base / A_pi) * (1.0 / (N_geom * A_pi)**3) * \
                (1.0 / (K_WC * np.sqrt(N_test_range)))

    # Get geometric N_nu_eff for the reference point
    alpha_geom = 1.0 / compute_alpha_geometric(bcc["eps_M"])
    r_nu = derive_neutrino_radius(
        alpha_geom, derive_planck_charge_from_e(alpha_geom, E_CHARGE_CODATA)
    )["r_nu"]
    lambda_l = derive_lambda_l_geometric(
        alpha_geom=alpha_geom,
        r_e=R_E,
        r_nu=r_nu,
        N_geom=N_geom,
        L_p_geom=2.0 / SQRT3,
        K_WC=10,
    )
    res = gravity_sector(
        alpha_geom=alpha_geom,
        r_nu=r_nu,
        N_geom=N_geom,
        L_p_geom=2.0 / SQRT3,
        K_WC=10,
        lambda_l=lambda_l,
        r_e=R_E,
        m_e=M_E,
        c0=C0,
    )
    N_nu_eff = res["N_nu_eff"]

    plt.figure()
    plt.plot(N_test_range, G_results, 'g-', linewidth=2)
    plt.plot(N_nu_eff, G_CODATA, 'ro', markersize=10)
    plt.axhline(G_CODATA, color='r', linestyle='--')
    plt.xlabel("N_nu (Volume Deficit)")
    plt.ylabel("G_eff (m^3 kg^-1 s^-2)")
    plt.title("G-Constant Surface Transition Analysis")
    plt.legend(["EWT Model Transition", "CODATA Target Point"], loc="upper right")
    plt.grid(True, which='both', ls='-', alpha=0.5)
    plt.savefig(pdf_path("EWT_Robustness_G_Surface_Transition.pdf"))
    plt.close()
    print("[EXPORT] EWT_Robustness_G_Surface_Transition.pdf")


# ----------------------------------------------------------------------
# MODULE 2: ALPHA-INVERSE SENSITIVITY VALIDATION
# ----------------------------------------------------------------------
def module2_alpha_sensitivity():
    bcc = derive_eps_M_from_BCC(8.0 * PI**4)
    N_geom = bcc["N_geom"]

    alpha_base = 4.0 * PI**3 + PI**2 + PI
    alpha_inv_final = alpha_base - (1.0 / (N_geom * PI**3))

    N_scan = np.linspace(778.5, 779.2, 1000)
    alpha_scan = alpha_base - (1.0 / (N_scan * PI**3))

    plt.figure()
    plt.plot(N_scan, alpha_scan, 'b-', linewidth=2)
    plt.plot(N_geom, alpha_inv_final, 'ro', markersize=10)
    plt.axhline(alpha_inv_final, color='r', linestyle='--')
    plt.xlabel("Dimensionless N")
    plt.ylabel("alpha^-1")
    plt.title("Validation of Alpha-Inverse vs N Coefficient")
    plt.legend(["EWT Model: Base - 1/(N*pi^3)", f"Target: {alpha_inv_final:.12f}"],
               loc="upper right")
    plt.grid(True, which='both', ls='-', alpha=0.5)
    plt.savefig(pdf_path("EWT_Robustness_Alpha_Sensitivity.pdf"))
    plt.close()
    print("[EXPORT] EWT_Robustness_Alpha_Sensitivity.pdf")


# ----------------------------------------------------------------------
# MODULE 3: CORRELATION PHASE PLOT (ALPHA^-1 vs AMM GEOMETRIC BASE)
# ----------------------------------------------------------------------
def module3_alpha_amm_phase():
    N_scan_range = np.linspace(500, 1500, 2000)
    A_pi_base_inv = 137.036040608

    alpha_inv_coords = []
    amm_base_coords = []

    for n_v in N_scan_range:
        eps_m_local = 1.0 / (n_v * PI**3)
        a_inv_local = A_pi_base_inv - eps_m_local
        alpha_local = 1.0 / a_inv_local
        a_base_val = (alpha_local / (2.0 * PI)) * (1.0 - (1.0 / n_v))
        alpha_inv_coords.append(a_inv_local)
        amm_base_coords.append(a_base_val * 1e10)

    alpha_inv_codata = 137.035999166
    amm_exp_codata = 11596521.82

    plt.figure()
    plt.plot(alpha_inv_coords, amm_base_coords, 'm-', linewidth=2)
    plt.plot(alpha_inv_codata, amm_exp_codata, 'ro', markersize=10, markeredgewidth=2)
    plt.xlabel("alpha^-1")
    plt.ylabel("a_e x 10^-10")
    plt.title("Phase Space: Electron AMM Base vs Alpha^-1")
    plt.xlim(alpha_inv_codata - 0.005, alpha_inv_codata + 0.005)
    plt.ylim(amm_exp_codata - 5000, amm_exp_codata + 5000)
    plt.legend(["EWT Theoretical Base Path", "CODATA 2022 (Experimental)"],
               loc="lower right")
    plt.grid(True, which='both', ls='-', alpha=0.5)
    plt.savefig(pdf_path("EWT_Alpha_vs_AMM_PhasePlot.pdf"))
    plt.close()
    print("[EXPORT] EWT_Alpha_vs_AMM_PhasePlot.pdf")


# ----------------------------------------------------------------------
# MODULE 4: PARAMETRIC UNIFICATION PATH (G VS ALPHA^-1)
# ----------------------------------------------------------------------
def module4_unification_trajectory():
    bcc = derive_eps_M_from_BCC(8.0 * PI**4)
    N_geom = bcc["N_geom"]
    alpha_geom = 1.0 / compute_alpha_geometric(bcc["eps_M"])

    # Geometric N_nu_eff (from gravity_sector)
    r_nu = derive_neutrino_radius(
        alpha_geom, derive_planck_charge_from_e(alpha_geom, E_CHARGE_CODATA)
    )["r_nu"]
    lambda_l = derive_lambda_l_geometric(
        alpha_geom=alpha_geom,
        r_e=R_E,
        r_nu=r_nu,
        N_geom=N_geom,
        L_p_geom=2.0 / SQRT3,
        K_WC=10,
    )
    res_gravity = gravity_sector(
        alpha_geom=alpha_geom,
        r_nu=r_nu,
        N_geom=N_geom,
        L_p_geom=2.0 / SQRT3,
        K_WC=10,
        lambda_l=lambda_l,
        r_e=R_E,
        m_e=M_E,
        c0=C0,
    )
    N_nu_eff = res_gravity["N_nu_eff"]

    N_unify_range = np.linspace(500, 2000, 3000)
    G_Base = (C0**2 * R_E) / M_E
    A_pi = compute_alpha_core()
    A_pi_base_inv = 137.036040608

    alpha_path = []
    G_path = []

    for n_v in N_unify_range:
        eps_m_local = 1.0 / (n_v * PI**3)
        a_inv_local = A_pi_base_inv - eps_m_local
        alpha_path.append(a_inv_local)
        g_val = (G_Base / A_pi) * (1.0 / (n_v * A_pi)**3) * \
                (1.0 / (10 * math.sqrt(N_nu_eff)))
        G_path.append(g_val)

    alpha_inv_exp = ALPHA_INV_CODATA

    plt.figure()
    plt.plot(alpha_path, G_path, 'm-', linewidth=2)
    plt.xlim(alpha_inv_exp - 0.001, alpha_inv_exp + 0.001)
    plt.ylim(G_CODATA - 2.0e-11, G_CODATA + 2.0e-11)
    plt.xlabel("alpha^-1")
    plt.ylabel("G (m^3 kg^-1 s^-2)")
    plt.title("EWT Unification Trajectory: G vs Alpha^-1")
    plt.grid(True, which='both', ls='-', alpha=0.5)
    plt.savefig(pdf_path("EWT_Unification_Path_English.pdf"))
    plt.close()
    print("[EXPORT] EWT_Unification_Path_English.pdf")


# ----------------------------------------------------------------------
# MODULE 5: POINT-LOCKED UNIFICATION (G & AMM CONVERGENCE)
# ----------------------------------------------------------------------
def module5_point_locked():
    bcc = derive_eps_M_from_BCC(8.0 * PI**4)
    N_geom = bcc["N_geom"]

    N_vec = np.concatenate([np.linspace(N_geom - 0.01, N_geom + 0.01, 2000),
                            [N_geom]])
    N_vec = np.unique(N_vec)

    G_raw = []
    ae_raw = []

    for n_v in N_vec:
        eps_m = 1.0 / (n_v * PI**3)
        a_inv_lock = 137.036040608 - eps_m
        ae_raw.append(((1.0 / a_inv_lock) / (2.0 * PI)) * (1.0 - (1.0 / n_v)) * 1e10)
        G_raw.append(G_CODATA * ((N_geom / n_v) ** 3))

    G_raw = np.array(G_raw)
    ae_raw = np.array(ae_raw)

    # Normalize G to match AMM at the node
    idx_n = np.argmin(np.abs(N_vec - N_geom))
    G_locked = G_raw * (ae_raw[idx_n] / G_raw[idx_n])

    plt.figure()
    plt.plot(N_vec, ae_raw, "b-", linewidth=3)
    plt.plot(N_vec, G_locked, "r-", linewidth=3)
    plt.axvline(N_geom, color='k', linestyle='--', linewidth=1)
    plt.xlabel("N")
    plt.ylabel("Amplitude (ae units)")
    plt.title("EWT Unified Point-Lock: G anchored to Electron AMM at N_geom")
    plt.legend(["Electron AMM (Base)", "Gravitational Constant (Point-Locked)"],
               loc="lower left")
    plt.grid(True, which='both', ls='-', alpha=0.5)
    plt.tight_layout()
    plt.savefig(pdf_path("EWT_POINT_LOCKED.pdf"))
    plt.close()
    print("[EXPORT] EWT_POINT_LOCKED.pdf")


# ----------------------------------------------------------------------
# MODULE 6: LEPTON ERROR SPECTRUM (SM SYSTEMATIC BIAS)
# ----------------------------------------------------------------------
def module6_lepton_error_spectrum():
    lepton_errors = [0.0229, 0.031, 0.091]
    lepton_names = ["Electron", "Tau", "Muon"]

    plt.figure()
    x = np.arange(len(lepton_errors))
    plt.bar(x, lepton_errors, width=0.5, color='magenta')
    plt.xticks(x, lepton_names)
    plt.axhline(0.05, color='r', linestyle='--', linewidth=1)
    plt.xlabel("Lepton Generation")
    plt.ylabel("Deviation (%)")
    plt.title("Lepton Error Spectrum: EWT Geometry vs SM Interpretation")
    plt.legend(["EWT-to-SM Shift", "Systematic SM Bias Level"], loc="upper left")
    plt.grid(True, which='both', ls='-', alpha=0.5)
    plt.savefig(pdf_path("EWT_Lepton_Error_Spectrum.pdf"))
    plt.close()
    print("[EXPORT] EWT_Lepton_Error_Spectrum.pdf")


# ----------------------------------------------------------------------
# MODULE 7: STRUCTURAL ROBUSTNESS OF STATUTORY DENSITY (N_nu_stat)
# ----------------------------------------------------------------------
def module7_statutory_robustness():
    bcc = derive_eps_M_from_BCC(8.0 * PI**4)
    alpha_geom = 1.0 / compute_alpha_geometric(bcc["eps_M"])
    r_nu = derive_neutrino_radius(
        alpha_geom, derive_planck_charge_from_e(alpha_geom, E_CHARGE_CODATA)
    )["r_nu"]
    lambda_l = derive_lambda_l_geometric(
        alpha_geom=alpha_geom,
        r_e=R_E,
        r_nu=r_nu,
        N_geom=bcc["N_geom"],
        L_p_geom=2.0 / SQRT3,
        K_WC=10,
    )

    N_nu_stat_base = (r_nu / (2.0 * lambda_l * EULER)) ** 3

    dr_ratio = np.linspace(-0.3, 0.3, 200)

    compliance_r_nu = ((r_nu * (1 + dr_ratio)) / (2.0 * lambda_l * EULER)) ** 3
    compliance_r_nu /= N_nu_stat_base

    compliance_r_emc = (r_nu / (2.0 * (lambda_l * (1 + dr_ratio)) * EULER)) ** 3
    compliance_r_emc /= N_nu_stat_base

    plt.figure()
    plt.plot(dr_ratio, np.ones_like(dr_ratio) * 1.3, 'r:', linewidth=1)
    plt.plot(dr_ratio, np.ones_like(dr_ratio) * 0.7, 'r:', linewidth=1)
    plt.plot(dr_ratio, np.ones_like(dr_ratio), 'k--', linewidth=2)
    plt.plot(dr_ratio, compliance_r_nu, 'b-', linewidth=2)
    plt.plot(dr_ratio, compliance_r_emc, 'r-', linewidth=2)

    plt.xlim(-0.3, 0.3)
    plt.ylim(0.6, 1.5)
    plt.xticks([-0.3, -0.15, 0, 0.15, 0.3],
               ['-30%', '-15%', '0%', '15%', '30%'])
    plt.xlabel("Relative Lattice Fluctuation (dr/r)")
    plt.ylabel("Normalized N_stat Stability Response")
    plt.title("Structural Robustness of Statutory Density N_nu_stat")
    plt.legend(["Upper Bound (1.3)", "Lower Bound (0.7)", "Statutory Lock-in (1.0)",
                "Fluctuation by r_nu", "Fluctuation by lambda_l"],
               loc="upper left")
    plt.grid(True, which='both', ls='-', alpha=0.5)
    plt.tight_layout()
    plt.savefig(pdf_path("EWT_Robustness_Analysis_DataDriven.pdf"))
    plt.close()
    print("[EXPORT] EWT_Robustness_Analysis_DataDriven.pdf")


# ----------------------------------------------------------------------
# MODULE 8: STIFFNESS-VOLUME STABILITY (FINAL PRECISION VERSION)
# ----------------------------------------------------------------------
def module8_stiffness_equilibrium():
    # Hierarchical gap
    N_nu_stat = 3.2986e52
    N_nu_eff = 6.2525176e48
    ratio_stat = N_nu_stat / N_nu_eff

    stiffness_exponent = -1.0 / 6.0

    dr_range = np.linspace(-0.25, 0.25, 200)
    N_nu_norm = (1 + dr_range) ** 3
    N_req_norm = (1 + dr_range) ** (3 * stiffness_exponent)

    plt.figure(figsize=(9, 7))
    plt.plot(dr_range, N_nu_norm, "b-", linewidth=3)
    plt.plot(dr_range, N_req_norm, "r-", linewidth=3)
    plt.plot(0, 1.0, "ko", markersize=12, markeredgewidth=2)

    plt.xlim(-0.25, 0.25)
    plt.ylim(0.4, 2.0)
    plt.xlabel("Relative Radius Fluctuation (dr/r)")
    plt.ylabel("Normalized Response (Value / N_eff)")
    plt.title("Gravity Stability: Nodal Stiffness vs. Soliton Volume")
    plt.legend(["Soliton Vol. Response (r^3)",
                "Nodal Stiffness (r^-0.5 from N_eff^-1/6)",
                "Effective Lock-in Point"], loc="upper center")
    plt.grid(True, which='both', ls='-', alpha=0.5)
    plt.tight_layout()
    plt.savefig(pdf_path("EWT_Stiffness_Equilibrium.pdf"))
    plt.close()
    print("[EXPORT] EWT_Stiffness_Equilibrium.pdf")
    print(f"       [HIERARCHY] Stat/Eff Density Gap: {ratio_stat:.2e}")


# ----------------------------------------------------------------------
# MODULE 9: LEPTODYNAMICS STABILITY & AMM ROBUSTNESS ANALYSIS
# ----------------------------------------------------------------------
def module9_amm_robustness():
    dr_range = np.linspace(-0.05, 0.05, 100)

    a_mu_ref = 116592061e-11
    a_tau_ref = 117721e-9

    a_mu_norm = 1.0 + dr_range * 0.1
    a_tau_norm = 1.0 + dr_range * 0.15

    plt.figure()
    plt.plot(dr_range * 100, a_mu_norm, "g-", linewidth=2)
    plt.plot(dr_range * 100, a_tau_norm, "m-", linewidth=2)
    plt.plot(0, 1.0, "ro", markersize=10)

    plt.xlabel("Radius Fluctuation dr/r (%)")
    plt.ylabel("Normalized AMM Response (a_i / a_target)")
    plt.title("Robustness: AMM Stability vs. Lattice Fluctuation")
    plt.legend(["Muon AMM (2D Planar Slope)",
                "Tau AMM (3D Volumetric Slope)",
                "Resonance Lock (N_geom)"], loc="lower right")
    plt.grid(True, which='both', ls='-', alpha=0.5)
    plt.savefig(pdf_path("EWT_AMM_Robustness_Leptons.pdf"))
    plt.close()
    print("[EXPORT] EWT_AMM_Robustness_Leptons.pdf")


# ----------------------------------------------------------------------
# MODULE 10: WEINBERG & CABIBBO (Shift-Normalized)
# ----------------------------------------------------------------------
def module10_weinberg_cabibbo():
    bcc = derive_eps_M_from_BCC(8.0 * PI**4)
    N_geom = bcc["N_geom"]

    # Physical constants
    M_Z_exp = 91.1876
    sin2W_target = 0.23122

    eps_M_final = 1.0 / (N_geom * PI**3)
    C_local_final = eps_M_final / (2.0 * math.sqrt(2.0))
    C_gap_final = 1.0 + (PI**6) * C_local_final

    M_W_Ideal = M_Z_exp * math.sqrt((1.0 - sin2W_target) * C_gap_final)
    sin2W_at_Nfinal = 1.0 - ((M_W_Ideal / M_Z_exp) ** 2) * (1.0 / C_gap_final)

    N_scan_W = np.linspace(778.5, 779.2, 1000)
    N_scan_W = np.unique(np.concatenate([N_scan_W, [N_geom]]))

    sin2W_results = []
    for n_v in N_scan_W:
        eps_m_local = 1.0 / (n_v * PI**3)
        C_local = eps_m_local / (2.0 * math.sqrt(2.0))
        C_gap = 1.0 + (PI**6) * C_local
        sin2W_results.append(1.0 - ((M_W_Ideal / M_Z_exp) ** 2) * (1.0 / C_gap))

    # Cabibbo using EWT quark masses
    m_d_ewt = 0.0046597252
    m_s_ewt = 0.0931160638

    sinC_results = []
    for n_v in N_scan_W:
        eps_m_local = 1.0 / (n_v * PI**3)
        C_local = eps_m_local / (2.0 * math.sqrt(2.0))
        C_fermion_local = (1.0 + (PI**5) * C_local) ** 2
        sinC_results.append(math.sqrt(m_d_ewt / m_s_ewt) * C_fermion_local)

    C_fermion_final = (1.0 + (PI**5) * C_local_final) ** 2
    sinC_final = math.sqrt(m_d_ewt / m_s_ewt) * C_fermion_final

    shift_C = sin2W_at_Nfinal - sinC_final
    sinC_shifted = np.array(sinC_results) + shift_C

    plt.figure(figsize=(9, 7))
    plt.plot(N_scan_W, sin2W_results, 'c-', linewidth=3)
    plt.plot(N_geom, sin2W_at_Nfinal, 'ro', markersize=10)
    plt.plot(N_scan_W, sinC_shifted, 'g-', linewidth=3)

    shift_label = f"sin(theta_C) + shift (shift = {shift_C:.10f})"
    plt.xlabel("N Coefficient")
    plt.ylabel("Angle Value (Shifted)")
    plt.title("Shift-Normalized Robustness: Weinberg & Cabibbo Angles")
    plt.legend(["sin^2(theta_W)", "N_geom Lock-in", shift_label,
                "Cabibbo Lock-in (shifted)"], loc="lower right")

    y_min = min(min(sin2W_results), min(sinC_shifted))
    y_max = max(max(sin2W_results), max(sinC_shifted))
    padding = (y_max - y_min) * 0.15
    plt.ylim(y_min - padding, y_max + padding)

    plt.grid(True, which='both', ls='-', alpha=0.5)
    plt.tight_layout()
    plt.savefig(pdf_path("EWT_Weinberg_Cabibbo_Robustness.pdf"))
    plt.close()
    print("[EXPORT] EWT_Weinberg_Cabibbo_Robustness.pdf")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    print("Enhanced EWT -- Robustness Plot Suite (Geometric)")

    module1_g_surface_transition()
    module2_alpha_sensitivity()
    module3_alpha_amm_phase()
    module4_unification_trajectory()
    module5_point_locked()
    module6_lepton_error_spectrum()
    module7_statutory_robustness()
    module8_stiffness_equilibrium()
    module9_amm_robustness()
    module10_weinberg_cabibbo()

    print("All figures exported.")


if __name__ == "__main__":
    main()