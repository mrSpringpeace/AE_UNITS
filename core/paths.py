"""Zjisteni cest podle rezimu spusteni: vyvoj / PyInstaller / Nuitka.

Kazdy build umistuje veci jinam, proto to resime na jednom miste:

  * resource_dir()  -- adresar s pribalenymi daty (icon.ico jen pro cteni)
  * writable_dir()  -- adresar pro zapisovatelne soubory (settings.json,
                       user_materials.json); musi prezit ukonceni programu

PyInstaller onefile rozbaluje data do docasneho `sys._MEIPASS`, kdezto
zapisovatelne soubory patri vedle .exe (`sys.executable`). Nuitka onefile
`sys._MEIPASS` ani `sys.frozen` NEnastavuje: data i moduly ma v docasnem
adresari (u `__file__`), `sys.executable` take miri do teto docasne slozky,
a skutecne .exe je jen v `__compiled__.containing_dir`. Ve vyvoji je vse
v korenu repa.
"""

import sys
from pathlib import Path

# Nuitka vklada `__compiled__` do globalu kazdeho zkompilovaneho modulu.
_IS_NUITKA = "__compiled__" in globals()
# PyInstaller pozname podle dvojice frozen + _MEIPASS.
_IS_PYINSTALLER = getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

# koren repa (vyvoj) resp. adresar rozbalenych dat (Nuitka onefile)
_BASE_DIR = Path(__file__).resolve().parent.parent


def resource_dir() -> Path:
    """Adresar, ze ktereho se ctou pribalena data (ikona apod.)."""
    if _IS_PYINSTALLER:
        return Path(sys._MEIPASS)
    return _BASE_DIR


def writable_dir() -> Path:
    """Adresar pro perzistentni uzivatelska data (vedle .exe, resp. koren repa)."""
    if _IS_NUITKA:
        # sys.executable miri do docasne onefile slozky; skutecne .exe
        # je jen v __compiled__.containing_dir.
        return Path(__compiled__.containing_dir).resolve()  # type: ignore[name-defined]  # noqa: F821
    if _IS_PYINSTALLER:
        return Path(sys.executable).resolve().parent
    return _BASE_DIR
