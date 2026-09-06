#!/usr/bin/env python3
"""
From manuscript version: 5.0.0

Enhanced EWT -- Categorical Comparison with Standard Model
============================================================
Compares EWT with SM in two separate categories:

  A. Predictive Advantage:
       Quantities where SM has no standalone prediction.
       EWT gives a concrete geometric value; SM is assigned 100% error.

  B. Precision Benchmark:
       Quantities where SM has extremely precise values from measurement
       or QED calculations using experimental inputs.

This separation avoids category errors and gives a fair picture.
"""

import math

try:
    from ewt_emergence_engine import (
        PI, SQRT2, SQRT3, EULER,
        C0, M_E, R_E, G_CODATA,
        ALPHA_INV_CODATA,
        A_E_CODATA,
        A_MU_EXP,
        A_TAU_EXP,
        E_CHARGE_CODATA,
        compute_alpha_core,
        compute_alpha_geometric,
        derive_eps_M_from_BCC,
        derive_planck_charge_from_e,
        derive_neutrino_radius,
        derive_lambda_l_geometric,
        gravity_sector,
        compute_lepton_amms,
    )
except ImportError:
    raise ImportError("This module requires ewt_emergence_engine.py in the same directory.")


def main():
    print("=" * 78)
    print("   EWT vs STANDARD MODEL: CATEGORICAL COMPARISON (GEOMETRIC)")
    print("=" * 78)

    # -------------------------------------------------------------------------
    # Prepare EWT geometry
    # -------------------------------------------------------------------------
    bcc = derive_eps_M_from_BCC(8.0 * PI**4)
    eps_M = bcc["eps_M"]
    N_geom = bcc["N_geom"]
    alpha_geom = 1.0 / compute_alpha_geometric(eps_M)

    q_P = derive_planck_charge_from_e(alpha_geom, E_CHARGE_CODATA)
    r_nu = derive_neutrino_radius(alpha_geom, q_P)["r_nu"]

    lambda_l = derive_lambda_l_geometric(
        alpha_geom=alpha_geom,
        r_e=R_E,
        r_nu=r_nu,
        N_geom=N_geom,
        L_p_geom=2.0 / SQRT3,
        K_WC=10,
    )

    gravity_res = gravity_sector(
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
    G_EWT = gravity_res["G_EWT"]

    amm = compute_lepton_amms(alpha_geom, eps_M)
    a_e_EWT = amm["a_e_ppm"] * 1e-6
    a_mu_EWT = amm["a_mu_ppm"] * 1e-6
    a_tau_EWT = amm["a_tau_ppm"] * 1e-6

    # -------------------------------------------------------------------------
    # EWT errors
    # -------------------------------------------------------------------------
    err_G_EWT = abs(G_EWT - G_CODATA) / G_CODATA
    err_alpha_EWT = abs((1.0 / alpha_geom) - ALPHA_INV_CODATA) / ALPHA_INV_CODATA
    err_a_e_EWT = abs(a_e_EWT - A_E_CODATA) / A_E_CODATA
    err_a_mu_EWT = abs(a_mu_EWT - A_MU_EXP) / A_MU_EXP
    err_a_tau_EWT = abs(a_tau_EWT - A_TAU_EXP) / A_TAU_EXP

    # =========================================================================
    # CATEGORY A: PREDICTIVE ADVANTAGE
    # =========================================================================
    print()
    print("CATEGORY A: PREDICTIVE ADVANTAGE")
    print("(Quantities for which SM has no standalone prediction)")
    print("-" * 78)
    print(f"{'Quantity':<20} {'EWT rel. err':>15} {'SM status':>20} {'Ratio (SM/EWT)':>15}")
    print("-" * 78)

    ratio_G = 1.0 / err_G_EWT
    ratio_alpha = 1.0 / err_alpha_EWT
    ratio_ae = 1.0 / err_a_e_EWT
    ratio_atau = 1.0 / err_a_tau_EWT

    print(f"{'G (Gravitation)':<20} {err_G_EWT:15.6e} {'no prediction':>20} {ratio_G:15.2e}")
    print(f"{'alpha^-1 (FSC)':<20} {err_alpha_EWT:15.6e} {'input only':>20} {ratio_alpha:15.2e}")
    print(f"{'a_e (Electron g-2)':<20} {err_a_e_EWT:15.6e} {'consistency test':>20} {ratio_ae:15.2e}")
    print(f"{'a_tau (Tau g-2)':<20} {err_a_tau_EWT:15.6e} {'no prediction':>20} {ratio_atau:15.2e}")
    print("-" * 78)

    pred_advantage_log = (
        math.log10(ratio_G)
        + math.log10(ratio_alpha)
        + math.log10(ratio_ae)
        + math.log10(ratio_atau)
    )
    pred_advantage = 10 ** pred_advantage_log

    print(f"  Aggregate predictive advantage: {pred_advantage:.4e} times")
    print()

    # =========================================================================
    # CATEGORY B: PRECISION BENCHMARK
    # =========================================================================
    print("CATEGORY B: PRECISION BENCHMARK")
    print("(Quantities where SM has extremely precise values from measurement/QED)")
    print("-" * 78)
    print(f"{'Quantity':<20} {'EWT rel. err':>15} {'SM precision':>20} {'Ratio (SM/EWT)':>15}")
    print("-" * 78)

    sm_a_mu_precision = 2.152805e-6   # relative uncertainty in a_mu (SM QED + inputs)

    ratio_amu = sm_a_mu_precision / err_a_mu_EWT

    print(f"{'a_mu (Muon g-2)':<20} {err_a_mu_EWT:15.6e} {sm_a_mu_precision:20.6e} {ratio_amu:15.2e}")
    print("-" * 78)

    precision_log = math.log10(ratio_amu)
    precision_factor = 10 ** precision_log

    print(f"  Aggregate precision benchmark factor: {precision_factor:.4e} times")
    print()

    print("=" * 78)
    print("""INTERPRETATION:
  Category A shows that EWT provides concrete geometric predictions for
  G, alpha, a_e, and a_tau, while SM either has no prediction or treats
  these quantities as external inputs.

  Category B shows that SM remains more precise for a_mu, because it
  uses experimental inputs and perturbative QED. EWT achieves its
  accuracy without any free parameters or experimental inputs beyond
  the four fundamental anchors (e, r_e, m_e, c).
""")
    print("=" * 78)


if __name__ == "__main__":
    main()