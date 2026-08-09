"""Zjisteni cest podle rezimu spusteni: vyvoj / PyInstaller / Nuitka.

Kazdy build umistuje veci jinam, proto to resime na jednom miste:

  * resource_dir()  -- adresar s pribalenymi daty (icon.ico jen pro cteni)
  * writable_dir()  -- adresar pro zapisovatelne soubory (settings.json,
                       user_materials.json); musi prezit ukonceni programu
  * atomic_write()  -- bezpecny zapis (temp + replace)

PyInstaller onefile rozbaluje data do docasneho `sys._MEIPASS`, kdezto
zapisovatelne soubory patri do user data dir (APPDATA) nebo vedle .exe
pri portable rezimu. Nuitka onefile `sys._MEIPASS` ani `sys.frozen`
NEnastavuje: data i moduly ma v docasnem adresari (u `__file__`),
`sys.executable` take miri do teto docasne slozky, a skutecne .exe je
jen v `__compiled__.containing_dir`. Ve vyvoji je vse v korenu repa.

Portable rezim: soubor `portable` (bez pripony) vedle .exe -> zapis
vedle .exe misto do APPDATA.
"""

import os
import sys
import tempfile
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


def _exe_dir() -> Path:
    """Adresar se skutecnym .exe (frozen) nebo koren repa (vyvoj)."""
    if _IS_NUITKA:
        return Path(__compiled__.containing_dir).resolve()  # type: ignore[name-defined]  # noqa: F821
    if _IS_PYINSTALLER:
        return Path(sys.executable).resolve().parent
    return _BASE_DIR


def _user_data_dir() -> Path:
    """Per-user konfiguracni adresar (APPDATA / XDG)."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / "AE_UNITS"
        return Path.home() / "AppData" / "Roaming" / "AE_UNITS"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "AE_UNITS"
    return Path.home() / ".config" / "AE_UNITS"


def writable_dir() -> Path:
    """Adresar pro perzistentni uzivatelska data.

    * vyvoj: koren repa
    * frozen + soubor `portable` vedle .exe: vedle .exe
    * frozen jinak: %APPDATA%/AE_UNITS (resp. XDG)
    """
    if not (_IS_NUITKA or _IS_PYINSTALLER):
        return _BASE_DIR

    exe = _exe_dir()
    # portable: explicitni flag, nebo jiz existujici settings vedle exe
    if (exe / "portable").exists() or (exe / "settings.json").exists():
        return exe

    data = _user_data_dir()
    data.mkdir(parents=True, exist_ok=True)
    return data


def atomic_write(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Zapise text atomicky (temp soubor ve stejnem adresari + os.replace)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding, newline="\n") as f:
            f.write(text)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
