"""Perzistence uzivatelskych nastaveni."""

import json

from core import paths

_PATH = paths.writable_dir() / "settings.json"

_DEFAULTS = {
    "theme":      "dark",
    "fmt_mode":   "auto",
    "fmt_digits": 6,
    "lang":       "cs",
}

# Migrace starych cesky/anglicky psanych klicu na interni
_FMT_MIGRATE = {
    "Auto": "auto",
    "Vědecký (1.23e+05)": "sci",
    "Pevný (123456.79)":  "fixed",
}

_THEME_MIGRATE = {
    "Tmavý": "dark",
    "Světlý": "light",
    "Dark":  "dark",
    "Light": "light",
    "dark":  "dark",
    "light": "light",
}


def load() -> dict:
    try:
        data = json.loads(_PATH.read_text(encoding="utf-8"))
        merged = {**_DEFAULTS, **data}
        merged["fmt_mode"] = _FMT_MIGRATE.get(merged["fmt_mode"], merged["fmt_mode"])
        if merged["fmt_mode"] not in ("auto", "sci", "fixed"):
            merged["fmt_mode"] = _DEFAULTS["fmt_mode"]
        merged["theme"] = _THEME_MIGRATE.get(merged.get("theme", "dark"), "dark")
        if merged["theme"] not in ("dark", "light"):
            merged["theme"] = "dark"
        return merged
    except (FileNotFoundError, json.JSONDecodeError, TypeError, OSError):
        return dict(_DEFAULTS)


def save(data: dict):
    paths.atomic_write(
        _PATH,
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
    )
