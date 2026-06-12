"""Kontrola prevodnich faktoru proti znamym hodnotam z literatury (Niu app. A, Bruhn)."""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core.units import (CATEGORIES, convert, DELKA, RYCHLOST, TLAK, SILA,
                        HUSTOTA, TEPLOTA, VYKON, LOMOVA, HMOTNOST,
                        PLOSNA_HMOTNOST, ZRYCHLENI)

CHECKS = [
    # (kategorie, hodnota, z, do, ocekavani, tolerance_rel)
    (DELKA, 1, "in", "mm", 25.4, 0),
    (DELKA, 1, "ft", "m", 0.3048, 0),
    (DELKA, 1, "NM", "km", 1.852, 0),
    (RYCHLOST, 100, "kt", "m/s", 51.4444, 1e-4),       # ten KTAS dotaz z rozhovoru
    (RYCHLOST, 1, "kt", "km/h", 1.852, 1e-12),
    (RYCHLOST, 1000, "ft/min", "m/s", 5.08, 1e-12),
    (TLAK, 1, "ksi", "MPa", 6.894757, 1e-6),
    (TLAK, 1, "MPa", "psi", 145.0377, 1e-6),
    (TLAK, 1, "atm", "psi", 14.69595, 1e-6),
    (TLAK, 1, "bar", "psi", 14.50377, 1e-6),
    (SILA, 1, "lbf", "N", 4.4482216152605, 0),
    (SILA, 1, "kip", "kN", 4.4482216152605, 1e-12),
    (HMOTNOST, 1, "slug", "kg", 14.5939, 1e-5),
    (HMOTNOST, 1, "lb", "kg", 0.45359237, 0),
    (HUSTOTA, 1, "lb/in³", "kg/m³", 27679.9, 1e-5),    # hlinik 0.101 lb/in3 = 2796 kg/m3
    (HUSTOTA, 0.101, "lb/in³", "g/cm³", 2.79567, 1e-4),
    (HUSTOTA, 1, "slug/ft³", "kg/m³", 515.3788, 1e-6),
    (TEPLOTA, 15, "°C", "K", 288.15, 0),
    (TEPLOTA, 15, "°C", "°F", 59.0, 1e-12),
    (TEPLOTA, 288.15, "K", "°R", 518.67, 1e-10),
    (VYKON, 1, "hp", "kW", 0.7456999, 1e-6),
    (VYKON, 1, "k (PS)", "W", 735.49875, 0),
    (LOMOVA, 1, "ksi·√in", "MPa·√m", 1.098843, 1e-5),
    (LOMOVA, 1, "MPa·√m", "N/mm^3/2", 31.6227766, 1e-9),
    (PLOSNA_HMOTNOST, 1, "oz/yd²", "g/m²", 33.9057, 1e-5),
    (ZRYCHLENI, 1, "g", "ft/s²", 32.17405, 1e-6),
]


def main():
    failed = 0
    for cat, val, f, t, expected, tol in CHECKS:
        got = convert(cat, val, f, t)
        rel = abs(got - expected) / abs(expected)
        ok = rel <= max(tol, 1e-15)
        status = "OK  " if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"{status} {val} {f} -> {t}: {got:.10g} (ocekavano {expected})")

    # kruhovy test: tam a zpet pres vsechny jednotky vsech kategorii
    for cat in CATEGORIES:
        base = cat.units[0].symbol
        for u in cat.units:
            x = convert(cat, 123.456, base, u.symbol)
            back = convert(cat, x, u.symbol, base)
            if abs(back - 123.456) / 123.456 > 1e-12:
                print(f"FAIL roundtrip {cat.name}: {base} <-> {u.symbol}")
                failed += 1

    print(f"\n{'VSE OK' if failed == 0 else f'{failed} CHYB'} "
          f"({len(CHECKS)} kontrol + roundtrip vsech jednotek)")
    return failed


if __name__ == "__main__":
    sys.exit(main())
