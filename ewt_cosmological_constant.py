#!/usr/bin/env python3
"""
M4.x - Lambda from EWT trinity + one anchor (T_cmb)
        + matter-correction test
        + Omega_Lambda = eta_BCC * C_gap  (working hypothesis)
        + tension analysis

Chain (all EWT-derived, one anchor):
    [1] BCC geometry                -> alpha_geom
    [2] BCC geometry + charge e     -> r_nu
    [3] BCC + anchors (r_e, m_e, c) -> hbar_geom, G_geom
    [4] Self-consistent closure     -> lambda_l
    [5] hbar_geom, G_geom           -> T_p
    [6] ANCHOR (measured)           -> T_cmb
    [7] Haug horizon relation       -> R_H
    [8] definition                  -> H_0 = c/R_H
    [9] definition                  -> Lambda = 3/R_H^2

Then:
    [A] try_matter_correction()      -> effective Omega_m correction
    [B] try_omega_lambda_hypothesis() -> Omega_L = eta_BCC * C_gap
                                         (working hypothesis, NOT derivation)
    [C] tension analysis              -> H_0 and Lambda vs Planck/DESI/SH0ES

Why Omega_L = eta_BCC * C_gap (physical and geometric motivation):

    eta_BCC = pi*sqrt(3)/8 = 0.68017 is the BCC packing fraction:
    the fraction of space occupied by EMC spheres in the ideal lattice.
    In EWT, the vacuum is the BCC lattice, and matter solitons are
    localized regions where the EMC density is depleted (N_eff << N_stat).

    C_gap = 1 + pi^6 * C_local is the volumetric gap operator for a
    neutral vertex (Z-Z, Z-H). It encodes the additional phase-space
    volume available to a neutral excitation in the BCC lattice.
    The global vacuum has no net charge, so its gap structure is
    the neutral one (C_gap), not the mixed charged-neutral one
    (C_gap_mixed). This is the geometric justification for using
    C_gap rather than C_gap_mixed.

    The dark-energy fraction is therefore the occupied-sphere fraction
    eta_BCC enhanced by the neutral volumetric gap C_gap:

        Omega_L = eta_BCC * C_gap = 0.689749

    This is 0.12% from Planck+BAO (Omega_L = 0.6889 +/- 0.0056)
    and 0.74% from Planck TT,TE,EE+lowE+lensing (0.6847 +/- 0.0073).

    Lambda_pred = Omega_L * 3 H_0,EWT^2 / c^2 = 1.0826e-52 m^-2,
    which is 0.59% below Planck Lambda = 1.089e-52 m^-2.

    STATUS: this is a geometric POSTULATE with physical motivation,
    not a first-principles derivation. A horizon-balance argument
    linking the BCC void fraction to the dark-energy energy density
    is the open objective.

Reference values (verified):
    Planck 2018: H0 = 67.36 +/- 0.54 km/s/Mpc
                 Omega_L = 0.6847 +/- 0.0073 (TT,TE,EE+lowE+lensing)
                 Omega_L = 0.6889 +/- 0.0056 (TT,TE,EE+lowE+lensing+BAO)
                 Lambda  = 1.089e-52 m^-2
    DESI 2024:   H0 = 68.52 +/- 0.62 km/s/Mpc
    SH0ES 2022:  H0 = 73.04 +/- 1.04 km/s/Mpc
"""

import math

try:
    from ewt_emergence_engine import (
        PI, C0, M_E, R_E, E_CHARGE_CODATA,
        BCC_IDEAL_PROJECTION_LP,
        compute_alpha_core,
        compute_alpha_geometric,
        derive_eps_M_from_BCC,
        derive_planck_charge_from_e,
        derive_neutrino_radius,
        derive_hbar,
        derive_lambda_l_geometric,
        gravity_sector,
        build_geometric_ladder,
    )
except ImportError as e:
    raise ImportError(
        "This script requires ewt_emergence_engine.py in the same directory."
    ) from e


# ----------------------------------------------------------------------
# Unit-definition constants (SI 2019) and one measured anchor
# ----------------------------------------------------------------------
K_B          = 1.380649e-23    # Boltzmann constant [J/K] -- exact by definition
T_CMB_CODATA = 2.7255          # CMB temperature [K]       -- MEASURED ANCHOR
T_CMB_SIGMA  = 0.0006          # uncertainty [K]
MPC_M        = 3.0856775814913673e22   # 1 Mpc [m]

K_WC = 10  # electron wave-centre count (geometric integer)


# ----------------------------------------------------------------------
# Reference values for tension analysis (verified)
# ----------------------------------------------------------------------
H0_PLANCK          = 67.36
H0_PLANCK_SIGMA    = 0.54
OMEGA_L_PLANCK_TT  = 0.6847      # TT,TE,EE+lowE+lensing
OMEGA_L_PLANCK_ALL = 0.6889      # TT,TE,EE+lowE+lensing+BAO
OMEGA_L_PLANCK_TT_SIGMA  = 0.0073
OMEGA_L_PLANCK_ALL_SIGMA = 0.0056
LAMBDA_PLANCK      = 1.089e-52   # m^-2

H0_DESI         = 68.52
H0_DESI_SIGMA   = 0.62

H0_SHOES        = 73.04
H0_SHOES_SIGMA  = 1.04


# ----------------------------------------------------------------------
# [1] EWT trinity
# ----------------------------------------------------------------------
def derive_trinity():
    bcc = derive_eps_M_from_BCC(8.0 * PI**4)
    N_geom = bcc["N_geom"]
    eps_M  = bcc["eps_M"]
    zeta   = bcc["zeta"]

    alpha_inv  = compute_alpha_geometric(eps_M)
    alpha_geom = 1.0 / alpha_inv

    q_P    = derive_planck_charge_from_e(alpha_geom, E_CHARGE_CODATA)
    nu_res = derive_neutrino_radius(alpha_geom, q_P)
    r_nu   = nu_res["r_nu"]

    lambda_l = derive_lambda_l_geometric(
        alpha_geom=alpha_geom, r_e=R_E, r_nu=r_nu,
        N_geom=N_geom, L_p_geom=BCC_IDEAL_PROJECTION_LP, K_WC=K_WC,
    )

    res = gravity_sector(
        alpha_geom=alpha_geom, r_nu=r_nu, N_geom=N_geom,
        L_p_geom=BCC_IDEAL_PROJECTION_LP, K_WC=K_WC,
        lambda_l=lambda_l, r_e=R_E, m_e=M_E, c0=C0,
    )

    hbar_geom = derive_hbar(alpha_geom, R_E, M_E, C0)

    # Geometric ladder from the engine (single source of truth for C_gap)
    ladder = build_geometric_ladder(eps_M, "BCC packing derived", zeta=zeta)

    return {
        "alpha_geom": alpha_geom, "alpha_inv": alpha_inv,
        "eps_M": eps_M, "N_geom": N_geom, "zeta": zeta,
        "r_nu": r_nu, "lambda_l": lambda_l, "hbar_geom": hbar_geom,
        "G_geom": res["G_EWT"],
        "N_nu_stat": res["N_nu_statutory"],
        "N_nu_eff": res["N_nu_eff"],
        "X_eff": res["X_eff"],
        "eta_BCC": (math.pi * math.sqrt(3.0)) / 8.0,
        "C_local": ladder["C_local"],
        "C_gap": ladder["C_gap"],
        "C_gap_mixed": ladder["C_gap_mixed"],
        "O_mixed": ladder["O_mixed"],
    }


# ----------------------------------------------------------------------
# [5] Planck temperature
# ----------------------------------------------------------------------
def planck_temperature(hbar, G, c, k_B):
    return (1.0 / k_B) * math.sqrt(hbar * c**5 / G)


# ----------------------------------------------------------------------
# [7] Haug horizon relation
# ----------------------------------------------------------------------
def horizon_from_Tcmb(T_cmb, T_p, lambda_l):
    factor = T_p / (8.0 * math.pi * T_cmb)
    return 2.0 * lambda_l * factor**2


def Tcmb_from_horizon(R_H, T_p, lambda_l):
    return (T_p / (8.0 * math.pi)) * math.sqrt(2.0 * lambda_l / R_H)


# ----------------------------------------------------------------------
# [8], [9]
# ----------------------------------------------------------------------
def H0_from_RH(R_H, c):
    return c / R_H


def cosmological_constant(R_H):
    return 3.0 / (R_H * R_H)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def fmt(x, unit="", prec=6):
    s = f"{x:.{prec}e}"
    return f"{s} {unit}" if unit else s


def H0_in_km_s_Mpc(H_0):
    return H_0 * MPC_M / 1000.0


def tension_sigma(value, reference, sigma):
    return (value - reference) / sigma


# ----------------------------------------------------------------------
# [A] Matter correction test
# ----------------------------------------------------------------------
def try_matter_correction(trinity, T_p, T_cmb, Omega_m_target=0.31):
    print("\n[A] Matter correction test")
    print("-" * 78)
    print("    Haug relation assumes pure de Sitter (Omega_Lambda = 1).")
    print("    Test: R_H(Omega_m) = R_H(0) * (1 - Omega_m)^p")
    print("    Find p such that H_0(Omega_m=0.31) = Planck H_0 = 67.36 km/s/Mpc.")

    R_H_0 = horizon_from_Tcmb(T_cmb, T_p, trinity["lambda_l"])
    H_0_0 = H0_in_km_s_Mpc(H0_from_RH(R_H_0, C0))

    ratio = H_0_0 / H0_PLANCK
    p = math.log(ratio) / math.log(1.0 - Omega_m_target)
    f = (1.0 - Omega_m_target)**p

    print(f"    H_0(Omega_m=0)   = {H_0_0:.6f} km/s/Mpc")
    print(f"    target H_0       = {H0_PLANCK:.4f} km/s/Mpc")
    print(f"    required ratio   = {ratio:.6f}")
    print(f"    best-fit p       = {p:.6f}")
    print(f"    f(0.31)          = {f:.6f}")

    R_H_corr    = R_H_0 * f
    H_0_corr    = H0_in_km_s_Mpc(H0_from_RH(R_H_corr, C0))
    Lambda_corr = cosmological_constant(R_H_corr)

    print(f"    H_0(corrected)   = {H_0_corr:.6f} km/s/Mpc")
    print(f"    Lambda(corrected)= {Lambda_corr:.6e} m^-2")
    print(f"    ratio to Planck  = {Lambda_corr / LAMBDA_PLANCK:.6f}")
    print("    NOTE: p is a phenomenological fit; its small value (0.018)")
    print("    shows that de Sitter already dominates and matter is a")
    print("    ~0.6% perturbation. This corrects H_0, not Lambda.")

    return {"p": p, "f": f, "H_0_corr": H_0_corr, "Lambda_corr": Lambda_corr}


# ----------------------------------------------------------------------
# [B] Omega_Lambda hypothesis: eta_BCC * C_gap
# ----------------------------------------------------------------------
def try_omega_lambda_hypothesis(trinity, H0_EWT_km, Lambda_EWT):
    """
    WORKING HYPOTHESIS -- NOT A DERIVATION.

    Omega_L = eta_BCC * C_gap

    Physical and geometric motivation:
      eta_BCC = pi*sqrt(3)/8 is the BCC packing fraction (occupied
      sphere volume in the ideal lattice).

      C_gap = 1 + pi^6 * C_local is the neutral volumetric gap operator
      from the geometric ladder (Z-Z, Z-H vertices). The global vacuum
      is neutral, so its gap structure is the neutral one. The choice
      C_gap over C_gap_mixed is therefore dictated by the charge-
      neutrality of the vacuum, not by numerical convenience.

      The product eta_BCC * C_gap gives the effective dark-energy
      fraction as the occupied lattice volume enhanced by the
      neutral volumetric gap.

    Status: geometric postulate with physical motivation. A horizon-
    balance argument linking the BCC void fraction to the dark-energy
    energy density is the open objective.
    """
    print("\n[B] Omega_Lambda WORKING HYPOTHESIS: Omega_L = eta_BCC * C_gap")
    print("-" * 78)
    print("    THIS IS A HYPOTHESIS, NOT A DERIVATION.")
    print("    A first-principles horizon-balance argument is NOT available.")
    print()

    eta   = trinity["eta_BCC"]
    C_gap = trinity["C_gap"]

    print(f"    eta_BCC         = {eta:.10f}")
    print(f"    C_gap           = {C_gap:.10f}")
    print(f"    Omega_L         = {eta * C_gap:.10f}")
    print()

    omega_pred = eta * C_gap

    # Compare to Planck TT and Planck+BAO
    rel_TT  = (omega_pred - OMEGA_L_PLANCK_TT)  / OMEGA_L_PLANCK_TT  * 100.0
    rel_ALL = (omega_pred - OMEGA_L_PLANCK_ALL) / OMEGA_L_PLANCK_ALL * 100.0

    t_TT  = (omega_pred - OMEGA_L_PLANCK_TT)  / OMEGA_L_PLANCK_TT_SIGMA
    t_ALL = (omega_pred - OMEGA_L_PLANCK_ALL) / OMEGA_L_PLANCK_ALL_SIGMA

    print("    Omega_L comparison:")
    print(f"    {'Reference':<32} {'Omega_L':>10} {'sigma':>9} {'rel':>9} {'tension':>12}")
    print(f"    {'-'*32} {'-'*10} {'-'*9} {'-'*9} {'-'*12}")
    print(f"    {'Planck TT,TE,EE+lowE+lensing':<32} {OMEGA_L_PLANCK_TT:>10.4f} {OMEGA_L_PLANCK_TT_SIGMA:>9.4f} {rel_TT:>+8.3f}% {t_TT:>+11.2f} sigma")
    print(f"    {'Planck + BAO':<32} {OMEGA_L_PLANCK_ALL:>10.4f} {OMEGA_L_PLANCK_ALL_SIGMA:>9.4f} {rel_ALL:>+8.3f}% {t_ALL:>+11.2f} sigma")
    print()

    # Implied Omega_m
    omega_m_pred = 1.0 - omega_pred
    omega_m_planck_TT  = 1.0 - OMEGA_L_PLANCK_TT
    omega_m_planck_ALL = 1.0 - OMEGA_L_PLANCK_ALL
    print("    Implied Omega_m = 1 - Omega_L:")
    print(f"    Omega_m (pred)            = {omega_m_pred:.4f}")
    print(f"    Omega_m (Planck TT)       = {omega_m_planck_TT:.4f}")
    print(f"    Omega_m (Planck + BAO)    = {omega_m_planck_ALL:.4f}")
    print()

    # Lambda prediction
    H_0_si = H0_EWT_km * 1000.0 / MPC_M
    Lambda_deSitter = 3.0 * H_0_si**2 / C0**2
    Lambda_pred = omega_pred * Lambda_deSitter
    rel_L = (Lambda_pred - LAMBDA_PLANCK) / LAMBDA_PLANCK * 100.0

    print("    Lambda prediction:")
    print(f"    Lambda (de Sitter, Omega_L=1) = {Lambda_deSitter:.6e} m^-2")
    print(f"    Lambda (pred, Omega_L*3H0^2/c^2) = {Lambda_pred:.6e} m^-2")
    print(f"    Lambda (Planck)               = {LAMBDA_PLANCK:.6e} m^-2")
    print(f"    ratio pred / Planck           = {Lambda_pred / LAMBDA_PLANCK:.6f}")
    print(f"    discrepancy                   = {rel_L:+.3f}%")
    print()

    print("    Interpretation:")
    print("    - The choice C_gap (neutral) over C_gap_mixed (charged-neutral)")
    print("      is dictated by the charge neutrality of the global vacuum.")
    print("    - The product eta_BCC * C_gap reduces the 1.44x de Sitter")
    print("      discrepancy to 0.59% for Lambda, and matches Planck+BAO")
    print("      Omega_L to 0.12%.")
    print("    - This is a POSTULATE: a first-principles horizon-balance")
    print("      derivation of Omega_L = eta_BCC * C_gap is the open")
    print("      objective.")

    return {
        "eta": eta,
        "C_gap": C_gap,
        "Omega_L": omega_pred,
        "Omega_m": omega_m_pred,
        "rel_TT": rel_TT,
        "rel_ALL": rel_ALL,
        "tension_TT": t_TT,
        "tension_ALL": t_ALL,
        "Lambda_deSitter": Lambda_deSitter,
        "Lambda_pred": Lambda_pred,
        "rel_L": rel_L,
    }


# ----------------------------------------------------------------------
# [C] Tension analysis
# ----------------------------------------------------------------------
def tension_analysis(H_0_EWT_km, Lambda_EWT):
    print("\n[C] Tension analysis")
    print("-" * 78)
    print("    H_0 tensions (EWT vs reference):")
    print(f"    {'Reference':<20} {'H_0':>10} {'sigma':>8} {'tension':>12}")
    print(f"    {'-'*20} {'-'*10} {'-'*8} {'-'*12}")

    refs = [
        ("Planck 2018", H0_PLANCK, H0_PLANCK_SIGMA),
        ("DESI 2024",   H0_DESI,   H0_DESI_SIGMA),
        ("SH0ES 2022",  H0_SHOES,  H0_SHOES_SIGMA),
    ]
    for name, H0_ref, H0_sig in refs:
        t = tension_sigma(H_0_EWT_km, H0_ref, H0_sig)
        print(f"    {name:<20} {H0_ref:>10.2f} {H0_sig:>8.2f} {t:>+11.2f} sigma")

    print("\n    Lambda tension (EWT de Sitter limit vs Planck):")
    print(f"    Lambda(EWT de Sitter) = {Lambda_EWT:.6e} m^-2")
    print(f"    Lambda(Planck)        = {LAMBDA_PLANCK:.6e} m^-2")
    print(f"    ratio                 = {Lambda_EWT / LAMBDA_PLANCK:.6f}")
    print("    (Haug relation gives Omega_L = 1 by construction;")
    print("     Planck gives 0.6847. The 1.44x ratio is structural.)")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    print("=" * 78)
    print("M4.x - Lambda from EWT trinity + one anchor (T_cmb)")
    print("=" * 78)

    # [1]-[4] EWT trinity
    print("\n[1/5] Computing EWT trinity...")
    tri = derive_trinity()
    print(f"    alpha_geom      = {tri['alpha_geom']:.15f}")
    print(f"    alpha_inv       = {tri['alpha_inv']:.15f}")
    print(f"    eps_M           = {tri['eps_M']:.15e}")
    print(f"    zeta            = {tri['zeta']:.10e}")
    print(f"    N_geom          = {tri['N_geom']:.10f}")
    print(f"    r_nu            = {fmt(tri['r_nu'], 'm')}")
    print(f"    lambda_l        = {fmt(tri['lambda_l'], 'm')}")
    print(f"    hbar_geom       = {fmt(tri['hbar_geom'], 'J*s')}")
    print(f"    G_geom          = {fmt(tri['G_geom'], 'm^3/kg/s^2')}")
    print(f"    N_nu_stat       = {tri['N_nu_stat']:.6e}")
    print(f"    N_nu_eff        = {tri['N_nu_eff']:.6e}")
    print(f"    X_eff           = {tri['X_eff']:.6f}")
    print(f"    eta_BCC         = {tri['eta_BCC']:.10f}")
    print(f"    C_local         = {tri['C_local']:.10e}")
    print(f"    C_gap           = {tri['C_gap']:.10f}")
    print(f"    C_gap_mixed     = {tri['C_gap_mixed']:.10f}")
    print(f"    O_mixed         = {tri['O_mixed']:.6f}")

    # [5] T_p
    print("\n[2/5] Deriving T_p from EWT hbar_geom and G_geom...")
    T_p_EWT = planck_temperature(tri["hbar_geom"], tri["G_geom"], C0, K_B)
    print(f"    T_p (EWT)       = {T_p_EWT:.6e} K")

    # [6] Anchor
    print("\n[3/5] Anchor: T_cmb (measured by COBE/FIRAS)...")
    print(f"    T_cmb           = {T_CMB_CODATA:.4f} +/- {T_CMB_SIGMA:.4f} K")

    # [7] R_H
    print("\n[4/5] Solving Haug's horizon relation for R_H...")
    R_H = horizon_from_Tcmb(T_CMB_CODATA, T_p_EWT, tri["lambda_l"])
    H_0 = H0_from_RH(R_H, C0)
    print(f"    R_H (EWT)       = {fmt(R_H, 'm')}")
    print(f"    H_0 (EWT)       = {H0_in_km_s_Mpc(H_0):.6f} km/s/Mpc")

    T_check = Tcmb_from_horizon(R_H, T_p_EWT, tri["lambda_l"])
    print(f"    forward check   = {T_check:.10f} K  (must equal T_cmb input)")

    # [8]-[9] Lambda
    print("\n[5/5] Computing Lambda = 3 / R_H^2 ...")
    Lambda_EWT = cosmological_constant(R_H)
    print(f"    Lambda (EWT)    = {fmt(Lambda_EWT, 'm^-2')}")

    H_0_km = H0_in_km_s_Mpc(H_0)

    # [A]
    corr = try_matter_correction(tri, T_p_EWT, T_CMB_CODATA, Omega_m_target=0.31)

    # [B]
    omega_hyp = try_omega_lambda_hypothesis(tri, H_0_km, Lambda_EWT)

    # [C]
    tension_analysis(H_0_km, Lambda_EWT)

    # Full chain
    print("\n" + "=" * 78)
    print("FULL CHAIN (all values from EWT + one anchor)")
    print("=" * 78)
    print(f"    BCC geometry          -> alpha_geom   = {tri['alpha_geom']:.15f}")
    print(f"    BCC + charge e        -> r_nu         = {fmt(tri['r_nu'], 'm')}")
    print(f"    BCC + anchors         -> hbar_geom    = {fmt(tri['hbar_geom'], 'J*s')}")
    print(f"    BCC + anchors         -> G_geom       = {fmt(tri['G_geom'], 'm^3/kg/s^2')}")
    print(f"    Planck closure        -> lambda_l     = {fmt(tri['lambda_l'], 'm')}")
    print(f"    EWT hbar_geom,G_geom  -> T_p          = {T_p_EWT:.6e} K")
    print(f"    ANCHOR (measured)     -> T_cmb        = {T_CMB_CODATA:.4f} K")
    print(f"    Haug relation         -> R_H          = {fmt(R_H, 'm')}")
    print(f"    definition            -> H_0          = {H_0_km:.4f} km/s/Mpc")
    print(f"    definition            -> Lambda       = {Lambda_EWT:.6e} m^-2")
    print()
    print("    The only empirical inputs are r_e, m_e, c, e (dimensional")
    print("    anchors) and T_cmb (cosmological anchor).")
    print()
    print("    WORKING HYPOTHESIS (not derived):")
    print(f"      Omega_L = eta_BCC * C_gap = {omega_hyp['Omega_L']:.6f}")
    print(f"      => Lambda_pred            = {omega_hyp['Lambda_pred']:.6e} m^-2")
    print(f"      vs Planck                 = {LAMBDA_PLANCK:.6e} m^-2")
    print(f"      discrepancy               = {omega_hyp['rel_L']:+.2f}%")
    print(f"      vs Planck+BAO Omega_L     = {omega_hyp['rel_ALL']:+.2f}%")
    print("      A first-principles horizon-balance derivation is OPEN.")

    print("\n" + "-" * 78)
    print("NOTE: reference values (Planck, DESI, SH0ES) are used ONLY in")
    print("tension analysis. For EWT internal accuracy checks, see the")
    print("test functions in ewt_emergence_engine.py.")
    print("-" * 78)

    return {
        "trinity": tri, "T_p": T_p_EWT, "T_cmb": T_CMB_CODATA,
        "R_H": R_H, "H_0": H_0, "Lambda": Lambda_EWT,
        "correction": corr, "omega_hypothesis": omega_hyp,
    }


if __name__ == "__main__":
    main()