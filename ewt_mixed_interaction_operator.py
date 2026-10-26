#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mixed interaction operator for the W-Z vertex.

Defines the harmonic mixed operator between the neutral (pi^6) and
charged (pi^7) rungs of the EWT geometric ladder, computes the
resulting W-boson mass prediction, and compares it with current
experimental benchmarks.

The operator is:
    O_mixed = pi^6 * pi^7 / (pi^6 + pi^7)         (harmonic mean)
    C_gap   = 1 + O_mixed * C_local
    M_W     = M_Z * sqrt((1 - sin^2 theta_W) * C_gap)

The harmonic form is the unique simple parameter-free combination
of the two rungs that reduces to the correct single-rung limit
when one channel decouples. It is a methodologically motivated
ansatz, not a first-principles derivation from the BCC lattice.

For comparison, the script also reports:
  - the pure pi^6 prediction (weinberg_sector from engine),
  - the spherical mode mass (K = 109),
  - the meson mode mass (K = 109).

Output:
  - console summary of all variants and their sigma deviations,
  - LaTeX table tab:mw_comparison for Section 3.1.2 of the manuscript.

Imports EWT primitives from ewt_emergence_engine and
ewt_particle_masses when available; falls back to manuscript
values otherwise.
"""

import math

# ============================================================
# Physical constants (CODATA / PDG)
# ============================================================

M_Z = 91.1876                 # GeV, CODATA
SIN2_THETA_W_MSBAR = 0.23122  # MS-bar at M_Z (CODATA)

# Standard Model reference values
M_W_SM_TREE = M_Z * math.sqrt(1.0 - SIN2_THETA_W_MSBAR)
M_W_SM_FULL = 80.360          # radiative-corrected SM reference

# ============================================================
# Experimental benchmarks
# ============================================================

EXP_BENCHMARKS = {
    "CDF II 2022":      (80.4335, 0.0094),
    "PDG 2022 average": (80.377,  0.012),
    "ATLAS 2024":       (80.360,  0.016),
    "CMS 2024":         (80.3602, 0.0099),
    "PDG 2024 average": (80.3692, 0.0133),
}


# ============================================================
# Load EWT primitives and predictions from engine
# ============================================================

def load_ewt_values():
    """
    Return a dict with EWT geometric primitives and predictions.

    Keys
    ----
    C_local       : local coupling constant
    pi6           : pi^6 (neutral weak rung)
    pi7           : pi^7 (charged weak rung)
    C_gap_old     : C_gap from the pure pi^6 rung (engine value)
    M_W_weinberg  : W mass via weinberg_sector (pure pi^6)
    M_W_spherical : W mass via spherical mode (K = 109)
    M_W_meson     : W mass via meson mode (K = 109)
    engine_ok     : True if imported from engine, False if fallback
    """
    try:
        from ewt_emergence_engine import (
            PI,
            M_Z_CODATA,
            SIN2_THETA_W,
            derive_eps_M_from_BCC,
            build_geometric_ladder,
            weinberg_sector,
        )
        from ewt_particle_masses import mass_spherical, mass_meson_style

        bcc = derive_eps_M_from_BCC(8.0 * PI**4)
        ladder = build_geometric_ladder(bcc["eps_M"], "BCC packing derived")
        C_local = ladder["C_local"]
        C_gap_old = ladder["C_gap"]

        weinberg_result = weinberg_sector(C_gap_old, M_Z_CODATA, SIN2_THETA_W)
        M_W_weinberg = weinberg_result["M_W_pred"]

        return {
            "C_local":       C_local,
            "pi6":           PI**6,
            "pi7":           PI**7,
            "C_gap_old":     C_gap_old,
            "M_W_weinberg":  M_W_weinberg,
            "M_W_spherical": mass_spherical(109),
            "M_W_meson":     mass_meson_style(109),
            "engine_ok":     True,
        }

    except ImportError:
        # Fallback: values from manuscript outputs
        C_local = 1.4641246e-5
        pi6 = math.pi**6
        pi7 = math.pi**7
        C_gap_old = 1.0 + pi6 * C_local
        return {
            "C_local":       C_local,
            "pi6":           pi6,
            "pi7":           pi7,
            "C_gap_old":     C_gap_old,
            "M_W_weinberg":  M_Z * math.sqrt((1.0 - SIN2_THETA_W_MSBAR) * C_gap_old),
            "M_W_spherical": 87.627848552791,
            "M_W_meson":     78.623523,
            "engine_ok":     False,
        }


# ============================================================
# Mixed operator (harmonic mean)
# ============================================================

def mixed_operator(pi6, pi7):
    """
    Harmonic combination of the neutral and charged weak rungs.

    O_mixed = pi^6 * pi^7 / (pi^6 + pi^7)

    Limiting behavior:
      - pi^7 -> infinity : O_mixed -> pi^6  (neutral channel dominant)
      - pi^6 -> infinity : O_mixed -> pi^7  (charged channel dominant)

    This is the unique simple parameter-free combination that
    reduces to the correct single-rung limit in either decoupling
    case. Arithmetic and geometric means both diverge in these
    limits and are therefore not admissible interpolations.
    """
    return (pi6 * pi7) / (pi6 + pi7)


def c_gap_mixed(c_local, pi6, pi7):
    """Return (C_gap, O_mixed) for the mixed operator."""
    o_mixed = mixed_operator(pi6, pi7)
    return 1.0 + o_mixed * c_local, o_mixed


def mw_from_cgap(m_z, sin2_theta_w, c_gap):
    """M_W = M_Z * sqrt((1 - sin^2 theta_W) * C_gap)."""
    return m_z * math.sqrt((1.0 - sin2_theta_w) * c_gap)


# ============================================================
# Helpers
# ============================================================

def delta_mev(mw, reference):
    """Signed deviation in MeV."""
    return (mw - reference) * 1000.0


def sigma_dev(mw, reference, sigma_ref):
    """Signed deviation in units of the experimental uncertainty."""
    return (mw - reference) / sigma_ref


# ============================================================
# Main
# ============================================================

def main():
    ewt = load_ewt_values()
    c_gap_mix, o_mixed = c_gap_mixed(ewt["C_local"], ewt["pi6"], ewt["pi7"])
    mw_mixed = mw_from_cgap(M_Z, SIN2_THETA_W_MSBAR, c_gap_mix)

    # ---- Geometry summary ----
    print("=" * 84)
    print("MIXED INTERACTION OPERATOR: W-Z VERTEX")
    print("=" * 84)
    if ewt["engine_ok"]:
        print("  [OK]   Engine imported: ewt_emergence_engine + ewt_particle_masses")
    else:
        print("  [WARN] Engine not found -- using manuscript fallback values")
    print()
    print("  Geometry:")
    print(f"    M_Z                = {M_Z:.6f} GeV  (CODATA)")
    print(f"    sin^2 theta_W      = {SIN2_THETA_W_MSBAR:.5f}  (MS-bar)")
    print(f"    sqrt(1 - sin^2)    = {math.sqrt(1.0 - SIN2_THETA_W_MSBAR):.8f}")
    print(f"    C_local            = {ewt['C_local']:.6e}")
    print(f"    pi^6               = {ewt['pi6']:.6f}")
    print(f"    pi^7               = {ewt['pi7']:.6f}")
    print()
    print("  Operators:")
    print(f"    C_gap (pure pi^6)  = {ewt['C_gap_old']:.10f}")
    print(f"    O_mixed            = pi^6*pi^7/(pi^6+pi^7) = {o_mixed:.4f}")
    print(f"    C_gap (mixed)      = {c_gap_mix:.10f}")
    print(f"    sqrt(C_gap_mixed)  = {math.sqrt(c_gap_mix):.8f}")
    print()

    # ---- EWT predictions ----
    print("  EWT predictions:")
    print(f"    M_W (mixed, main)       = {mw_mixed:.4f} GeV")
    print(f"    M_W (pure pi^6, old)    = {ewt['M_W_weinberg']:.4f} GeV")
    print(f"    M_W (spherical, K=109)  = {ewt['M_W_spherical']:.4f} GeV")
    print(f"    M_W (meson, K=109)      = {ewt['M_W_meson']:.4f} GeV")
    print()
    print(f"    M_W (SM tree)           = {M_W_SM_TREE:.4f} GeV")
    print(f"    M_W (SM full)           = {M_W_SM_FULL:.4f} GeV")
    print()

    # ---- Comparison table ----
    ref_name = "PDG 2024 average"
    mw_ref, sigma_ref = EXP_BENCHMARKS[ref_name]

    print("=" * 84)
    print(f"COMPARISON vs EXPERIMENTAL BENCHMARKS  (reference: {ref_name})")
    print("=" * 84)
    header = (
        f"{'Source':<30} {'M_W [GeV]':<22} "
        f"{'Delta vs PDG24 [MeV]':>20} {'sigma':>8}"
    )
    print(header)
    print("-" * len(header))

    # Experimental benchmarks
    print("  [Experimental]")
    for name, (mw, sigma) in EXP_BENCHMARKS.items():
        d = delta_mev(mw, mw_ref)
        s = sigma_dev(mw_mixed, mw, sigma)
        print(f"    {name:<28} {mw:.4f} +/- {sigma:.4f}   "
              f"{d:>+10.1f}            {s:>+6.1f} sigma")
    print()

    # SM reference
    print("  [Standard Model reference]")
    print(f"    {'SM tree (MS-bar)':<28} {M_W_SM_TREE:.4f}                "
          f"{delta_mev(M_W_SM_TREE, mw_ref):>+10.1f}")
    print(f"    {'SM full (radiative)':<28} {M_W_SM_FULL:.4f}                "
          f"{delta_mev(M_W_SM_FULL, mw_ref):>+10.1f}")
    print()

    # EWT predictions
    print("  [EWT predictions]")
    ewt_rows = [
        ("EWT mixed (main)",         mw_mixed),
        ("EWT pure pi^6 (old)",      ewt["M_W_weinberg"]),
        ("EWT spherical (K=109)",    ewt["M_W_spherical"]),
        ("EWT meson (K=109)",        ewt["M_W_meson"]),
    ]
    for name, mw in ewt_rows:
        print(f"    {name:<28} {mw:.4f}                "
              f"{delta_mev(mw, mw_ref):>+10.1f}")
    print()

    # Sigma of main prediction vs each benchmark
    print("  sigma of main (mixed) prediction vs benchmarks:")
    for name, (mw, sigma) in EXP_BENCHMARKS.items():
        s = sigma_dev(mw_mixed, mw, sigma)
        print(f"    {name:<28} {s:>+6.1f} sigma")
    print()

    # ---- LaTeX table ----
    print("=" * 84)
    print("LATEX TABLE (tab:mw_comparison)")
    print("=" * 84)
    print()
    print(generate_latex_table(ewt, mw_mixed, mw_ref))

    return 0


def generate_latex_table(ewt, mw_mixed, mw_ref):
    """
    Generate the LaTeX table for Section 3.1.2 of the manuscript.

    Standard reference framing: PDG 2024 average is the reference,
    Delta is in MeV, sigma is only shown for the EWT prediction
    (the deviation of a prediction from a measurement).
    """
    L = []
    L.append(r"\begin{table}[ht]")
    L.append(r"\centering")
    L.append(r"\small")
    L.append(r"\caption{Comparison of the EWT $W$-boson mass prediction with")
    L.append(r"current experimental benchmarks. The prediction uses the mixed")
    L.append(r"$W$--$Z$ operator of Eq.~\eqref{eq:mixed_operator}, with $M_Z$")
    L.append(r"and $\sin^2\theta_W$ (MS-bar) fixed to their CODATA values.")
    L.append(r"$\Delta$ is in MeV relative to the PDG~2024 average. The last")
    L.append(r"column gives the deviation of the EWT prediction from each")
    L.append(r"benchmark in units of the experimental uncertainty.}")
    L.append(r"\label{tab:mw_comparison}")
    L.append(r"\begin{tabular}{lccc}")
    L.append(r"\toprule")
    L.append(r"\textbf{Source} & \textbf{$M_W$ [GeV]} "
             r"& \textbf{$\Delta$ vs PDG 2024 [MeV]} "
             r"& \textbf{$\sigma$ vs PDG 2024} \\")
    L.append(r"\midrule")

    # Experimental benchmarks
    L.append(r"\multicolumn{4}{l}{\textit{Experimental benchmarks}} \\")
    L.append(r"\midrule")
    for name, (mw, sigma) in EXP_BENCHMARKS.items():
        d = delta_mev(mw, mw_ref)
        L.append(f"{name} & ${mw:.4f} \\pm {sigma:.4f}$ & ${d:+.1f}$ & --- \\\\")
    L.append(r"\midrule")

    # Standard Model reference
    L.append(r"\multicolumn{4}{l}{\textit{Standard Model reference}} \\")
    L.append(r"\midrule")
    for name, mw in [
        (r"SM tree (MS-bar, no rad.\ corr.)", M_W_SM_TREE),
        (r"SM full (radiative-corrected)", M_W_SM_FULL),
    ]:
        d = delta_mev(mw, mw_ref)
        L.append(f"{name} & ${mw:.4f}$ & ${d:+.1f}$ & --- \\\\")
    L.append(r"\midrule")

    # EWT main prediction
    L.append(r"\multicolumn{4}{l}{\textit{EWT prediction (this work)}} \\")
    L.append(r"\midrule")
    d_main = delta_mev(mw_mixed, mw_ref)
    s_pdg = sigma_dev(mw_mixed, mw_ref, EXP_BENCHMARKS["PDG 2024 average"][1])
    L.append(f"EWT via mixed operator & ${mw_mixed:.4f}$ "
             f"& ${d_main:+.1f}$ & ${s_pdg:+.1f}\\sigma$ \\\\")
    L.append(r"\midrule")

    # EWT alternative modes
    L.append(r"\multicolumn{4}{l}{\textit{EWT alternative modes (for comparison)}} \\")
    L.append(r"\midrule")
    for name, mw in [
        (r"EWT pure $\pi^6$ (earlier version)", ewt["M_W_weinberg"]),
        (r"EWT spherical ($K_{WC}=109$)",        ewt["M_W_spherical"]),
        (r"EWT meson ($K_{WC}=109$)",            ewt["M_W_meson"]),
    ]:
        d = delta_mev(mw, mw_ref)
        L.append(f"{name} & ${mw:.4f}$ & ${d:+.1f}$ & --- \\\\")

    L.append(r"\bottomrule")
    L.append(r"\end{tabular}")
    L.append(r"\end{table}")
    return "\n".join(L)


if __name__ == "__main__":
    main()