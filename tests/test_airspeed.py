"""Kontrola prevodu rychlosti letu (CAS/EAS/TAS/Mach)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core.isa import isa, isa_h
from core.airspeed import speeds, A0

KT = 1852.0 / 3600.0


def main():
    failed = 0

    def check(name, got, exp, tol):
        nonlocal failed
        rel = abs(got - exp) / max(abs(exp), 1e-12)
        if rel > tol:
            print(f"FAIL {name}: {got:.6g} vs {exp} (rel {rel:.2e})")
            failed += 1

    # hladina more, std: TAS = EAS = CAS, M = V/a0
    r = speeds(isa(0), 100.0, "TAS")
    check("SL tas", r.tas, 100.0, 1e-12)
    check("SL eas", r.eas, 100.0, 1e-9)
    check("SL cas", r.cas, 100.0, 1e-9)
    check("SL mach", r.mach, 100.0 / A0, 1e-12)
    check("SL q", r.q, 0.5 * 1.225 * 100**2, 1e-6)

    # klasicky referencni bod: M 0.80 ve FL350 (tlakova vyska 10668 m)
    atm = isa_h(10668)
    r = speeds(atm, 0.80, "Mach")
    check("FL350 tas [m/s]", r.tas, 237.23, 5e-4)     # ~461 KTAS
    check("FL350 eas [m/s]", r.eas, 132.05, 5e-4)
    check("FL350 cas [m/s]", r.cas, 139.89, 5e-4)     # ~272 KCAS
    check("FL350 qc [Pa]",   r.qc,  12501.0, 1e-3)
    # konzistence q = gamma/2 p M^2
    check("FL350 q konzist.", r.q, 0.7 * atm.p * 0.8**2, 1e-9)

    # roundtripy pres vsechny druhy rychlosti
    for h in (0, 2000, 8000, 12000):
        atm = isa_h(h)
        r0 = speeds(atm, 120.0, "CAS")
        check(f"h={h} CAS->TAS->CAS", speeds(atm, r0.tas, "TAS").cas, 120.0, 1e-9)
        check(f"h={h} CAS->EAS->CAS", speeds(atm, r0.eas, "EAS").cas, 120.0, 1e-9)
        check(f"h={h} CAS->M->CAS", speeds(atm, r0.mach, "Mach").cas, 120.0, 1e-9)
        # subsonicky vzdy CAS >= EAS (kompresibilita) a TAS >= EAS
        if not (r0.cas >= r0.eas - 1e-9 and r0.tas >= r0.eas - 1e-9):
            print(f"FAIL h={h}: poradi CAS/EAS/TAS")
            failed += 1

    # ΔISA: TAS pri stejne CAS roste s teplotou
    tas_std = speeds(isa_h(2000), 120.0, "CAS").tas
    tas_hot = speeds(isa_h(2000, dT=20), 120.0, "CAS").tas
    if not tas_hot > tas_std:
        print("FAIL dT: TAS nevzrostla s teplotou")
        failed += 1

    # nadzvuk musi vyhodit chybu
    try:
        speeds(isa(0), 400.0, "TAS")
        print("FAIL: M>1 nevyhodilo ValueError")
        failed += 1
    except ValueError:
        pass

    print("VSE OK (airspeed)" if failed == 0 else f"{failed} CHYB (airspeed)")
    return failed


if __name__ == "__main__":
    sys.exit(main())
