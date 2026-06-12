"""Perzistence uzivatelskych nastaveni."""

import json
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    _PATH = Path(sys.executable).parent / "settings.json"
else:
    _PATH = Path(__file__).parent.parent / "settings.json"

_DEFAULTS = {
    "theme":      "Tmavý",
    "fmt_mode":   "auto",
    "fmt_digits": 6,
    "lang":       "cs",
}

# Migrace starych cesky psanych klicu formatu na interni
_FMT_MIGRATE = {
    "Auto": "auto",
    "Vědecký (1.23e+05)": "sci",
    "Pevný (123456.79)":  "fixed",
}


def load() -> dict:
    try:
        data = json.loads(_PATH.read_text(encoding="utf-8"))
        merged = {**_DEFAULTS, **data}
        merged["fmt_mode"] = _FMT_MIGRATE.get(merged["fmt_mode"], merged["fmt_mode"])
        return merged
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(_DEFAULTS)


def save(data: dict):
    _PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                     encoding="utf-8")
