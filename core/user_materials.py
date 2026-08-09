"""Perzistence uzivatelskych materialu.

Vlastni materialy se ukladaji do user_materials.json vedle settings.json.
Uzivatel muze take importovat/exportovat libovolnou JSON knihovnu.

Format zaznamu (JSON):
  legacy:  [nazev, rho, E, nu, Ftu, Fty, poznamka]
  aktualni: {"id": "...", "name": ..., "rho": ..., "E": ..., "nu": ...,
             "ftu": ..., "fty": ..., "note": ...}

Interni reprezentace je vzdy:
  (id, name, rho, E, nu, ftu, fty, note)
  nu, fty mohou byt None.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from core import paths

_DEFAULT_PATH = paths.writable_dir() / "user_materials.json"


class UserMaterialsError(ValueError):
    """Soubor existuje, ale nelze ho nacist/zparsovat."""


def _new_id() -> str:
    return uuid.uuid4().hex


def _parse_row(raw) -> tuple:
    """Prevede JSON radek na interni 8-tici (id, name, rho, E, nu, ftu, fty, note)."""
    if isinstance(raw, dict):
        name = raw["name"]
        rho, E = raw["rho"], raw["E"]
        nu = raw.get("nu")
        ftu = raw["ftu"]
        fty = raw.get("fty")
        note = raw.get("note", "")
        mid = raw.get("id") or _new_id()
    elif isinstance(raw, (list, tuple)):
        if len(raw) == 8:
            mid, name, rho, E, nu, ftu, fty, note = raw
            mid = mid or _new_id()
        elif len(raw) == 7:
            name, rho, E, nu, ftu, fty, note = raw
            mid = _new_id()
        else:
            raise ValueError(f"expected 7 or 8 fields, got {len(raw)}")
    else:
        raise TypeError(f"material row must be list or dict, got {type(raw)}")

    return (
        str(mid),
        str(name),
        float(rho),
        float(E),
        float(nu) if nu is not None else None,
        float(ftu),
        float(fty) if fty is not None else None,
        str(note) if note is not None else "",
    )


def load(path: Path | None = None) -> list[tuple]:
    """Nacte materialy. Chybejici soubor -> []. Vadny soubor -> UserMaterialsError."""
    p = Path(path) if path is not None else _DEFAULT_PATH
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise UserMaterialsError("root must be a JSON array")
        return [_parse_row(r) for r in data]
    except UserMaterialsError:
        raise
    except (json.JSONDecodeError, ValueError, TypeError, KeyError, OSError) as e:
        raise UserMaterialsError(str(e)) from e


def save(materials: list[tuple], path: Path | None = None) -> None:
    p = Path(path) if path is not None else _DEFAULT_PATH
    rows = []
    for m in materials:
        # (id, name, rho, E, nu, ftu, fty, note)
        mid, name, rho, E, nu, ftu, fty, note = m
        rows.append({
            "id": mid,
            "name": name,
            "rho": rho,
            "E": E,
            "nu": nu,
            "ftu": ftu,
            "fty": fty,
            "note": note,
        })
    paths.atomic_write(
        p,
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
    )


def make(name: str, rho: float, E: float, nu, ftu: float, fty, note: str = "",
         mid: str | None = None) -> tuple:
    """Vytvori interni zaznam s novym (nebo zadanym) id."""
    return (mid or _new_id(), name, float(rho), float(E),
            float(nu) if nu is not None else None,
            float(ftu),
            float(fty) if fty is not None else None,
            str(note or ""))
