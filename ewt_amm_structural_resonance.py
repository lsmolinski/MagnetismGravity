#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nodal shell hierarchy and Fibonacci latch generator for the EWT lepton model.

Generates:
    K_n        total nodal count for generation n
    Delta K_n  nodal increment for generation n
    L_n        Fibonacci latch for generation n

The operator is:
    Delta K_k = round(10^k * pi^2)       for k = 0 (electron core)
    Delta K_k = round(10^k * 2*pi^2)     for k >= 1 (shells)

The Fibonacci latch is F_{4n-3}, advancing by 2^2 = 4 per generation.
"""

import math

PI = math.pi


# ----------------------------------------------------------------------
# Fibonacci and latch
# ----------------------------------------------------------------------

def _fib(n: int) -> int:
    """Standard Fibonacci number F_n, with F_1 = F_2 = 1."""
    if n < 1:
        raise ValueError("Fibonacci index must be >= 1")
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return a


def get_L_invariant(generation: int) -> int:
    """Fibonacci latch for generation n: F_{4n-3}."""
    if generation < 1:
        raise ValueError("Generation number must be >= 1")
    return _fib(4 * generation - 3)


# ----------------------------------------------------------------------
# Nodal increments and total
# ----------------------------------------------------------------------

def get_delta_K(k: int) -> int:
    """Nodal increment for shell index k."""
    if k < 0:
        raise ValueError("Shell index must be >= 0")
    if k == 0:
        return round(10 ** k * PI ** 2)
    return round(10 ** k * 2.0 * PI ** 2)


def get_AMMi_K(n: int) -> int:
    """Total nodal count for generation n (sum of increments up to n-1)."""
    if n < 1:
        raise ValueError("Generation number must be >= 1")
    return sum(get_delta_K(k) for k in range(n))


# ----------------------------------------------------------------------
# Main: print the hierarchy
# ----------------------------------------------------------------------

GENERATIONS = {
    1: "Electron (core)",
    2: "Muon (shell 1)",
    3: "Tau (shell 2)",
    4: "4th gen. (hypothetical)",
}


def main():
    print()
    print(f"{'Lepton Shell':<24} {'Operator':<20} "
          f"{'Delta K':>8} {'Total K_n':>10} {'L_dim':>6}")
    print("-" * 76)

    rows = [
        (1, "Core (Electron)",     "10^0 * pi^2"),
        (2, "Shell 1 (Muon)",      "10^1 * 2pi^2"),
        (3, "Shell 2 (Tau)",       "10^2 * 2pi^2"),
        (4, "Shell 3 (4th gen.)*", "10^3 * 2pi^2"),
    ]

    for n, label, op in rows:
        k = n - 1
        dK = get_delta_K(k)
        K = get_AMMi_K(n)
        L = get_L_invariant(n)
        print(f"{label:<24} {op:<20} {dK:>8} {K:>10} {L:>6}")

    print()
    print("* Hypothetical.")
    print()


if __name__ == "__main__":
    main()