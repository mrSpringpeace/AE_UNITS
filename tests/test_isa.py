"""Kontrola ISA modelu proti tabulkam US Standard Atmosphere 1976
(geometricke vysky)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core.isa import isa

# (z [m], T [K], p [Pa], rho [kg/m3]) - tabulkove hodnoty US 1976
TABLE = [
    (0,     288.150, 101325.0, 1.22500),
    (1000,  281.651,  89876.3, 1.11166),
    (5000,  255.676,  54048.3, 0.73643),
    (10000, 223.252,  26499.9, 0.41351),
    (11000, 216.774,  22699.9, 0.36480),
    (15000, 216.650,  12111.8, 0.19476),
    (20000, 216.650,   5529.3, 0.08891),
    (30000, 226.509,   1197.0, 0.01841),
    (50000, 270.650,    79.78, 1.027e-3),
]

TOL = 2e-3  # 0.2 % (tabulky jsou zaokrouhlene)


def main():
    failed = 0
    for z, T_exp, p_exp, rho_exp in TABLE:
        r = isa(z)
        for name, got, exp in (("T", r.T, T_exp), ("p", r.p, p_exp),
                               ("rho", r.rho, rho_exp)):
            rel = abs(got - exp) / abs(exp)
            if rel > TOL:
                print(f"FAIL z={z} m  {name}: {got:.6g} vs {exp} (rel {rel:.2e})")
                failed += 1

    # rychlost zvuku a viskozita na hladine more
    r0 = isa(0)
    checks = [("a0", r0.a, 340.294, 1e-4), ("mu0", r0.mu, 1.7894e-5, 1e-3),
              ("nu0", r0.nu, 1.4607e-5, 1e-3), ("sigma0", r0.sigma, 1.0, 1e-12)]
    for name, got, exp, tol in checks:
        if abs(got - exp) / exp > tol:
            print(f"FAIL {name}: {got:.6g} vs {exp}")
            failed += 1

    # dT konvence: tlak se nemeni, hustota klesa s teplotou
    rh = isa(0, dT=15)
    if abs(rh.p - r0.p) > 1e-9:
        print("FAIL dT: tlak se zmenil")
        failed += 1
    if not rh.rho < r0.rho:
        print("FAIL dT: hustota neklesla")
        failed += 1

    # tropopauza ~36 089 ft
    rt = isa(11019)  # 11 km geopotencialni ~ 11019 m geometricke
    if abs(rt.T_isa - 216.65) > 0.01:
        print(f"FAIL tropopauza: T={rt.T_isa}")
        failed += 1

    print("VSE OK (ISA)" if failed == 0 else f"{failed} CHYB (ISA)")
    return failed


if __name__ == "__main__":
    sys.exit(main())
