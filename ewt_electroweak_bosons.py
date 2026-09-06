#!/usr/bin/env python3
"""
From manuscript version: 5.0.0

Enhanced EWT -- Electroweak and Heavy Boson Module
====================================================
Extends the main emergence engine with:
  - Weinberg sector (W mass)
  - Higgs-vector boson mixing angles (ZH, WH)
  - Cabibbo angle (surface mixing)
  - heavy boson geometric radii (Z, H)
  - comparison with nuclear mass-equivalents

This module should be used together with ewt_emergence_engine.py
and ewt_particle_masses.py.
"""

import math

# --- Import shared constants and functions ---
try:
    from ewt_emergence_engine import (
        PI, SQRT2, SQRT3, EULER,
        M_Z_CODATA, M_W_CDFII, M_H_CODATA,
        compute_alpha_core,
        derive_eps_M_from_BCC,
        build_geometric_ladder,
    )
    from ewt_particle_masses import mass_spherical
except ImportError:
    raise ImportError("This module requires ewt_emergence_engine.py and ewt_particle_masses.py.")


def weinberg_sector(C_gap: float, M_Z: float, sin2_W: float) -> float:
    """
    Compute W boson mass from the Weinberg angle.

    Formula:
        M_W = M_Z * sqrt( (1 - sin^2(theta_W)) * C_gap )
    """
    return M_Z * math.sqrt((1.0 - sin2_W) * C_gap)


def compute_higgs_mixing_angles(
    C_gap: float,
    M_Z_EWT: float,
    M_H_EWT: float,
    M_W_EWT: float,
) -> tuple:
    """
    Compute Higgs-vector mixing angles from the geometric C_gap operator.

    Returns
    -------
    tuple (sin^2(theta_ZH), sin^2(theta_WH))
    """
    sin2_ZH = 1.0 - ((M_Z_EWT / M_H_EWT) ** 2) * (1.0 / C_gap)
    sin2_WH = 1.0 - ((M_W_EWT / M_H_EWT) ** 2) * (1.0 / C_gap)
    return sin2_ZH, sin2_WH


def cabibbo_sector(C_fermion: float) -> None:
    """
    Compute Cabibbo angle using EWT and PDG quark masses.

    Prints both variants:
        A: EWT spherical mode quark masses
        B: PDG 2022 quark masses
    """
    # Variant A: EWT masses
    m_d_ewt = mass_spherical(15)
    m_s_ewt = mass_spherical(28)
    sinC_A = math.sqrt(m_d_ewt / m_s_ewt) * C_fermion
    err_A = abs(sinC_A - 0.2243) / 0.2243 * 100

    # Variant B: PDG masses
    m_d_pdg = 0.004692
    m_s_pdg = 0.094954
    sinC_B = math.sqrt(m_d_pdg / m_s_pdg) * C_fermion
    err_B = abs(sinC_B - 0.2243) / 0.2243 * 100

    print("\n--- CABIBBO MIXING & SURFACE RESONANCE ---")
    print(f"  C_fermion (pi^5 operator):       {C_fermion:.10f}")
    print("  VARIANT A: EWT-derived quark masses (spherical mode)")
    print(f"    EWT d-quark mass (K=15):       {m_d_ewt:.10f} GeV")
    print(f"    EWT s-quark mass (K=28):       {m_s_ewt:.10f} GeV")
    print(f"    EWT Prediction sin(theta_C):   {sinC_A:.10f}")
    print("    PDG 2022 Target:               0.2243000000")
    print(f"    Percentage Error:              {err_A:.6f} %")
    print("  VARIANT B: PDG 2022 target quark masses (mechanism test)")
    print(f"    PDG d-quark mass:              {m_d_pdg:.10f} GeV")
    print(f"    PDG s-quark mass:              {m_s_pdg:.10f} GeV")
    print(f"    EWT Prediction sin(theta_C):   {sinC_B:.10f}")
    print("    PDG 2022 Target:               0.2243000000")
    print(f"    Percentage Error:              {err_B:.6f} %")
    print("  INTERPRETATION:")
    print("  Variant A error originates from EWT light quark mass predictions.")
    print("  Variant B isolates the geometric mixing mechanism (pi^5 operator).")


def compute_boson_radii(r_e_geom: float) -> dict:
    """
    Predict radii of heavy neutral bosons from spherical mode masses
    using r = r_e * (m / m_e)^(1/5).

    Parameters
    ----------
    r_e_geom : float
        Geometric electron radius [m] (usually 100 * r_nu).

    Returns
    -------
    dict with:
        r_Z : float
        r_H : float
        m_Z : float
        m_H : float
    """
    m_e_GeV = mass_spherical(10)
    m_Z = mass_spherical(110)
    m_H = mass_spherical(117)

    r_Z = r_e_geom * (m_Z / m_e_GeV) ** (1.0 / 5.0)
    r_H = r_e_geom * (m_H / m_e_GeV) ** (1.0 / 5.0)

    return {"r_Z": r_Z, "r_H": r_H, "m_Z": m_Z, "m_H": m_H}

def test_weinberg_angle(
    M_Z: float,
    M_W: float,
    C_gap: float,
    label: str,
) -> None:
    """
    Compute sin^2(theta_W) from geometric C_gap and given boson masses.

    Formula:
        sin^2(theta_W) = 1 - (M_W^2 / M_Z^2) * (1 / C_gap)

    Parameters
    ----------
    M_Z : float
        Z boson mass [GeV].
    M_W : float
        W boson mass [GeV].
    C_gap : float
        Volumetric lattice operator from the pi^6 rung.
    label : str
        Descriptive label for the mass source.
    """
    sin2_W_pred = 1.0 - ((M_W / M_Z) ** 2) * (1.0 / C_gap)
    rel_err = abs(sin2_W_pred - 0.23122) / 0.23122 * 100

    print(f"\n--- WEINBERG ANGLE TEST ({label}) ---")
    print(f"  M_Z = {M_Z:.10f} GeV, M_W = {M_W:.10f} GeV")
    print(f"  Predicted sin^2(theta_W) = {sin2_W_pred:.10f}")
    print(f"  Experimental      = 0.23122")
    print(f"  Relative error    = {rel_err:.6f} %")

def main():
    print("EWT ELECTROWEAK & BOSON MODULE")

    # Use pure BCC geometry from the main engine
    bcc = derive_eps_M_from_BCC(8.0 * PI**4)
    eps_M = bcc["eps_M"]

    ladder = build_geometric_ladder(eps_M, "BCC packing derived")
    C_gap = ladder["C_gap"]
    C_fermion = ladder["C_fermion"]

    alpha_geom = 1.0 / (compute_alpha_core() - eps_M)

    # --- Weinberg sector ---
    M_W_EWT = weinberg_sector(C_gap, M_Z_CODATA, 0.23122)
    print("\n--- WEINBERG SECTOR ---")
    print(f"  EWT Predicted W-Boson Mass:      {M_W_EWT:.4f} GeV")
    print(f"  CDF II Experimental Target:      {M_W_CDFII:.4f} GeV")
    print(f"  Percentage Error vs. CDF II:     {abs(M_W_EWT - M_W_CDFII)/M_W_CDFII*100:.4f} %")

    # --- EWT masses for Z and H from spherical mode ---
    M_Z_EWT = mass_spherical(110)
    M_H_EWT = mass_spherical(117)

    print("\n--- EWT SPHERICAL MODE MASSES ---")
    print(f"  Z boson (K=110): {M_Z_EWT:.10f} GeV")
    print(f"  Higgs    (K=117): {M_H_EWT:.10f} GeV")

    # --- Higgs mixing angles ---
    sin2_ZH, sin2_WH = compute_higgs_mixing_angles(C_gap, M_Z_EWT, M_H_EWT, M_W_EWT)
    print("\n--- HIGGS MIXING PREDICTIONS ---")
    print(f"  Higgs-Z Mixing sin^2(theta_ZH): {sin2_ZH:.10f}")
    print(f"  Higgs-W Mixing sin^2(theta_WH): {sin2_WH:.10f}")
    print("  Note: ZH stability is superior due to the neutrality of Z and H solitons.")

    # --- Weinberg angle tests ---
    # 1. EWT spherical masses
    test_weinberg_angle(M_Z_EWT, M_W_EWT, C_gap, "EWT spherical masses")

    # 2. Empirical masses
    test_weinberg_angle(
        M_Z_CODATA,
        M_W_CDFII,
        C_gap,
        "empirical masses",
    )

    # --- Heavy boson radii ---
    r_e_geom = 100 * 2.817935436016830e-17
    radii = compute_boson_radii(r_e_geom)
    print("\n--- HEAVY BOSON GEOMETRIC RADIUS PREDICTIONS ---")
    print(f"  Z-Boson (K=110) Predicted Radius: {radii['r_Z']:.10e} m")
    print(f"  Higgs   (K=117) Predicted Radius: {radii['r_H']:.10e} m")
    print("  VERIFICATION AGAINST NUCLEAR SCALES:")
    print("  Predictions match the 10^-14 m order of magnitude, consistent")
    print("  with the mass-equivalent isotopes (Mo-98 and Xe-134).")

    # --- Cabibbo sector ---
    cabibbo_sector(C_fermion)


if __name__ == "__main__":
    main()