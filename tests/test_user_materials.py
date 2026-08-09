"""Testy perzistence uzivatelskych materialu (load/save, legacy, chyby)."""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import user_materials as um


def main():
    failed = 0

    def check(cond, msg):
        nonlocal failed
        if not cond:
            print(f"FAIL {msg}")
            failed += 1

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "mats.json"

        # chybejici soubor
        check(um.load(p) == [], "missing file -> []")

        # save + load s id
        mats = [
            um.make("Test Al", 2700, 70, 0.33, 300, 250, "note"),
            um.make("Test Steel", 7850, 210, 0.29, 600, 400, ""),
        ]
        um.save(mats, p)
        loaded = um.load(p)
        check(len(loaded) == 2, "load count")
        check(loaded[0][0] == mats[0][0], "id preserved")
        check(loaded[0][1] == "Test Al", "name")
        check(abs(loaded[0][2] - 2700) < 1e-9, "rho")

        # legacy 7-prvkovy format
        legacy = Path(td) / "legacy.json"
        legacy.write_text(json.dumps([
            ["Legacy", 1000, 10, None, 50, None, "old"],
        ]), encoding="utf-8")
        leg = um.load(legacy)
        check(len(leg) == 1 and leg[0][1] == "Legacy", "legacy name")
        check(leg[0][0] and len(leg[0][0]) >= 8, "legacy got id")
        check(leg[0][4] is None, "legacy nu None")  # (id,name,rho,E,nu,...)

        # poskozeny JSON
        bad = Path(td) / "bad.json"
        bad.write_text("{not json", encoding="utf-8")
        try:
            um.load(bad)
            check(False, "corrupt should raise")
        except um.UserMaterialsError:
            pass

        # neplatna schema
        bad2 = Path(td) / "bad2.json"
        bad2.write_text(json.dumps({"no": "list"}), encoding="utf-8")
        try:
            um.load(bad2)
            check(False, "non-list should raise")
        except um.UserMaterialsError:
            pass

        # atomicky zapis - soubor existuje a je validni JSON
        check(p.exists() and p.read_text(encoding="utf-8").strip().startswith("["),
              "atomic write left valid file")

    print("VSE OK (user_materials)" if failed == 0 else f"{failed} CHYB (user_materials)")
    return failed


if __name__ == "__main__":
    sys.exit(main())
