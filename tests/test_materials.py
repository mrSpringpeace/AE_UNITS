"""Sanity kontrola materialove databaze (struktura a fyzikalni rozsahy)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from data.materials import MATERIALS


def main():
    failed = 0
    names = set()
    for m in MATERIALS:
        name = m[0]
        if len(m) != 7:
            print(f"FAIL {name}: ocekavano 7 poli, je {len(m)}")
            failed += 1
            continue
        _, rho, E, nu, ftu, fty, note = m
        if name in names:
            print(f"FAIL duplicitni nazev: {name}")
            failed += 1
        names.add(name)
        if not (10 <= rho <= 25000):
            print(f"FAIL {name}: rho {rho} mimo rozsah")
            failed += 1
        if not (0.01 <= E <= 500):
            print(f"FAIL {name}: E {E} GPa mimo rozsah")
            failed += 1
        if nu is not None and not (0.0 <= nu <= 0.5):
            print(f"FAIL {name}: nu {nu} mimo rozsah")
            failed += 1
        if not (0.5 <= ftu <= 3000):
            print(f"FAIL {name}: Ftu {ftu} mimo rozsah")
            failed += 1
        if fty is not None:
            if not (0.5 <= fty <= 3000):
                print(f"FAIL {name}: Fty {fty} mimo rozsah")
                failed += 1
            if fty > ftu:
                print(f"FAIL {name}: Fty {fty} > Ftu {ftu}")
                failed += 1
        if not note:
            print(f"FAIL {name}: chybi poznamka")
            failed += 1

    print(f"{'VSE OK' if failed == 0 else f'{failed} CHYB'} "
          f"(materialy: {len(MATERIALS)} zaznamu)")
    return failed


if __name__ == "__main__":
    sys.exit(main())
