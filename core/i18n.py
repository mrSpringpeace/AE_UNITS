"""Minimalni lokalizacni engine (CS / EN)."""

_lang = "cs"
_strings: dict = {}


def set_lang(lang: str):
    global _lang, _strings
    _lang = lang
    if lang == "en":
        from lang import en
        _strings = en.STRINGS
    else:
        from lang import cs
        _strings = cs.STRINGS


def get_lang() -> str:
    return _lang


def t(key: str, **kwargs) -> str:
    """Prelozi UI klic; fallback = klic sam."""
    s = _strings.get(key, key)
    return s.format(**kwargs) if kwargs else s


def uname(unit) -> str:
    """Lokalizovany nazev jednotky."""
    if _lang == "en" and getattr(unit, "name_en", ""):
        return unit.name_en
    return unit.name


def cname(category) -> str:
    """Lokalizovany nazev kategorie."""
    if _lang == "en" and getattr(category, "name_en", ""):
        return category.name_en
    return category.name


def qty(czech_label: str) -> str:
    """Prelozi cesky popisek veliciny (solver tabulka)."""
    if _lang == "en":
        from lang import en
        return en.QUANTITY_MAP.get(czech_label, czech_label)
    return czech_label
