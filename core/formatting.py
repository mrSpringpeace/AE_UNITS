"""Globalni nastaveni formatovani cisel (sdilene vsemi taby).

mode (interni klic):
  "auto"  - obecny format, `digits` = pocet platnych cislic
  "sci"   - vedecky zapis, `digits` = pocet desetinnych mist mantisy
  "fixed" - pevny pocet desetinnych mist, `digits` = pocet mist
"""

from core.units import format_value

MODES = ["auto", "sci", "fixed"]   # interni klice

_state = {"mode": "auto", "digits": 6}


def set_format(mode: str = None, digits: int = None):
    if mode is not None and mode in MODES:
        _state["mode"] = mode
    if digits is not None:
        _state["digits"] = digits


def get_format():
    return _state["mode"], _state["digits"]


def fmt(x: float) -> str:
    mode, d = _state["mode"], _state["digits"]
    if mode == "sci":
        return f"{x:.{d}e}"
    if mode == "fixed":
        return f"{x:.{d}f}"
    return format_value(x, d)
