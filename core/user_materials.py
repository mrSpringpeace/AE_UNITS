"""Perzistence uzivatelskych materialu.

Vlastni materialy se ukladaji do user_materials.json vedle settings.json.
Uzivatel muze take importovat/exportovat libovolnou JSON knihovnu.

Format zaznamu je shodny s data/materials.py:
  [nazev, rho, E, nu, Ftu, Fty, poznamka]
  nu, Fty mohou byt null.
"""

import json
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    _DIR = Path(sys.executable).parent
else:
    _DIR = Path(__file__).parent.parent

_DEFAULT_PATH = _DIR / "user_materials.json"


def _parse(raw: list) -> tuple:
    name, rho, E, nu, ftu, fty, note = raw
    return (name, float(rho), float(E),
            float(nu) if nu is not None else None,
            float(ftu),
            float(fty) if fty is not None else None,
            str(note))


def load(path: Path = None) -> list[tuple]:
    p = path or _DEFAULT_PATH
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return [_parse(r) for r in data]
    except (FileNotFoundError, json.JSONDecodeError, ValueError, TypeError):
        return []


def save(materials: list[tuple], path: Path = None):
    p = path or _DEFAULT_PATH
    rows = [[m[0], m[1], m[2], m[3], m[4], m[5], m[6]] for m in materials]
    p.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
