"""Testy load/save nastaveni vcetne migrace theme/fmt klicu."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main():
    failed = 0

    def check(cond, msg):
        nonlocal failed
        if not cond:
            print(f"FAIL {msg}")
            failed += 1

    with tempfile.TemporaryDirectory() as td:
        sp = Path(td) / "settings.json"

        # patch writable path used by settings module
        import core.paths as paths
        import importlib
        import core.settings as settings

        with mock.patch.object(paths, "writable_dir", return_value=Path(td)):
            importlib.reload(settings)

            # default when missing
            d = settings.load()
            check(d["theme"] == "dark", "default theme dark")
            check(d["fmt_mode"] == "auto", "default fmt")

            # migrate old Czech theme labels
            sp.write_text(json.dumps({
                "theme": "Tmavý",
                "fmt_mode": "Vědecký (1.23e+05)",
                "fmt_digits": 8,
                "lang": "en",
            }), encoding="utf-8")
            d = settings.load()
            check(d["theme"] == "dark", f"migrate Tmavý -> dark (got {d['theme']})")
            check(d["fmt_mode"] == "sci", f"migrate fmt sci (got {d['fmt_mode']})")
            check(d["fmt_digits"] == 8, "digits")
            check(d["lang"] == "en", "lang")

            sp.write_text(json.dumps({"theme": "Light"}), encoding="utf-8")
            d = settings.load()
            check(d["theme"] == "light", "migrate Light -> light")

            # save writes canonical keys
            settings.save({"theme": "light", "fmt_mode": "fixed",
                           "fmt_digits": 4, "lang": "cs"})
            raw = json.loads(sp.read_text(encoding="utf-8"))
            check(raw["theme"] == "light", "saved theme light")
            check(raw["fmt_mode"] == "fixed", "saved fmt fixed")

        importlib.reload(settings)

    # OpenFOAM quantity map completeness (EN)
    from data.solver_systems import SOLVERS
    from lang.en import QUANTITY_MAP
    of = SOLVERS["OpenFOAM"]
    missing = []
    for row in of["rows"]:
        label = row[0]
        if label.startswith("—"):
            continue
        if label not in QUANTITY_MAP:
            missing.append(label)
    check(not missing, f"OpenFOAM QUANTITY_MAP missing: {missing}")

    # slinch in mass category
    from core.units import HMOTNOST, convert
    check(any(u.symbol == "slinch" for u in HMOTNOST.units), "slinch unit present")
    # 1 slinch = LBF/IN ≈ 175.1268 kg
    got = convert(HMOTNOST, 1, "slinch", "kg")
    check(abs(got - 175.1268) < 1e-3, f"slinch factor {got}")

    print("VSE OK (settings)" if failed == 0 else f"{failed} CHYB (settings)")
    return failed


if __name__ == "__main__":
    sys.exit(main())
