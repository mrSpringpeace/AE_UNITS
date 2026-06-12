"""
AE_UNITS - definice jednotek a konverze.

Prevodni faktory jsou exaktni hodnoty dle SI brozury / NIST 2019.
Princip: kazda kategorie ma zakladni jednotku (SI). Faktor `factor`
splnuje: hodnota_v_zakladni = hodnota * factor.
Teplota je afinni - resi se dvojici funkci to_base / from_base.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
import math


@dataclass(frozen=True)
class Unit:
    symbol:  str
    name:    str            # cesky nazev
    name_en: str = ""       # anglicky nazev (prazdny = pouzit name)
    factor:  float = 1.0
    to_base:   Optional[Callable[[float], float]] = None
    from_base: Optional[Callable[[float], float]] = None


@dataclass(frozen=True)
class Category:
    name:    str            # cesky nazev
    name_en: str            # anglicky nazev
    base_symbol: str
    units:   tuple

    def unit(self, symbol: str) -> Unit:
        for u in self.units:
            if u.symbol == symbol:
                return u
        raise KeyError(f"Neznama jednotka '{symbol}' v kategorii '{self.name}'")


def convert(category: Category, value: float, from_sym: str, to_sym: str) -> float:
    fu = category.unit(from_sym)
    tu = category.unit(to_sym)
    if fu.to_base is not None or tu.from_base is not None:
        base = fu.to_base(value) if fu.to_base else value * fu.factor
        return tu.from_base(base) if tu.from_base else base / tu.factor
    return value * fu.factor / tu.factor


# ---------------------------------------------------------------------------
# Exaktni zakladni faktory (NIST / mezinarodni dohoda 1959)
# ---------------------------------------------------------------------------
IN = 0.0254
FT = 0.3048
LB = 0.45359237
G0 = 9.80665
LBF = LB * G0
SLUG = LBF / FT
PSI = LBF / IN**2
PSF = LBF / FT**2


CATEGORIES: list = []


def _cat(name: str, name_en: str, base_symbol: str, units: list) -> Category:
    c = Category(name=name, name_en=name_en,
                 base_symbol=base_symbol, units=tuple(units))
    CATEGORIES.append(c)
    return c


# --- Delka ------------------------------------------------------------------
DELKA = _cat("Délka", "Length", "m", [
    Unit("m",   "metr",                            "meter"),
    Unit("mm",  "milimetr",                        "millimeter",  1e-3),
    Unit("cm",  "centimetr",                       "centimeter",  1e-2),
    Unit("km",  "kilometr",                        "kilometer",   1e3),
    Unit("in",  "palec",                           "inch",        IN),
    Unit("mil", "mil / thou (0.001 in)",           "mil / thou (0.001 in)", IN / 1000),
    Unit("ft",  "stopa",                           "foot",        FT),
    Unit("yd",  "yard",                            "yard",        0.9144),
    Unit("mi",  "statute mile",                    "statute mile", 1609.344),
    Unit("NM",  "námořní míle",                    "nautical mile", 1852.0),
])

# --- Plocha -----------------------------------------------------------------
PLOCHA = _cat("Plocha", "Area", "m²", [
    Unit("m²",  "metr čtvereční",                  "square meter"),
    Unit("mm²", "milimetr čtvereční",              "square millimeter", 1e-6),
    Unit("cm²", "centimetr čtvereční",             "square centimeter", 1e-4),
    Unit("in²", "palec čtvereční",                 "square inch",  IN**2),
    Unit("ft²", "stopa čtvereční",                 "square foot",  FT**2),
])

# --- Objem ------------------------------------------------------------------
OBJEM = _cat("Objem", "Volume", "m³", [
    Unit("m³",     "metr krychlový",               "cubic meter"),
    Unit("mm³",    "milimetr krychlový",            "cubic millimeter",  1e-9),
    Unit("cm³",    "centimetr krychlový",           "cubic centimeter",  1e-6),
    Unit("L",      "litr",                          "liter",             1e-3),
    Unit("in³",    "palec krychlový",               "cubic inch",        IN**3),
    Unit("ft³",    "stopa krychlová",               "cubic foot",        FT**3),
    Unit("gal US", "galon americký",                "US gallon",         231 * IN**3),
    Unit("gal UK", "galon britský",                 "UK gallon",         4.54609e-3),
])

# --- Hmotnost ---------------------------------------------------------------
HMOTNOST = _cat("Hmotnost", "Mass", "kg", [
    Unit("kg",   "kilogram",                        "kilogram"),
    Unit("g",    "gram",                            "gram",              1e-3),
    Unit("t",    "tuna (metrická)",                 "metric ton (tonne)", 1e3),
    Unit("lb",   "libra (avoirdupois)",             "pound (avoirdupois)", LB),
    Unit("oz",   "unce",                            "ounce",             LB / 16),
    Unit("slug", "slug",                            "slug",              SLUG),
])

# --- Sila -------------------------------------------------------------------
SILA = _cat("Síla", "Force", "N", [
    Unit("N",   "newton",                           "newton"),
    Unit("kN",  "kilonewton",                       "kilonewton",        1e3),
    Unit("daN", "dekanewton",                       "decanewton",        10.0),
    Unit("kgf", "kilogram-síla (kp)",               "kilogram-force (kp)", G0),
    Unit("lbf", "libra-síla",                       "pound-force",       LBF),
    Unit("kip", "kip (1000 lbf)",                   "kip (1000 lbf)",    1000 * LBF),
])

# --- Tlak / Napeti ----------------------------------------------------------
TLAK = _cat("Tlak / Napětí", "Pressure / Stress", "Pa", [
    Unit("Pa",      "pascal",                       "pascal"),
    Unit("kPa",     "kilopascal",                   "kilopascal",        1e3),
    Unit("MPa",     "megapascal (N/mm²)",           "megapascal (N/mm²)", 1e6),
    Unit("GPa",     "gigapascal",                   "gigapascal",        1e9),
    Unit("bar",     "bar",                          "bar",               1e5),
    Unit("atm",     "atmosféra standardní",         "standard atmosphere", 101325.0),
    Unit("psi",     "libra na palec čtvereční",     "pound per square inch", PSI),
    Unit("ksi",     "kilolibra na palec čtvereční", "kilopound per square inch", 1000 * PSI),
    Unit("psf",     "libra na stopu čtvereční",     "pound per square foot", PSF),
    Unit("kgf/cm²", "kilogram-síla na cm²",         "kilogram-force per cm²", G0 / 1e-4),
    Unit("kgf/mm²", "kilogram-síla na mm²",         "kilogram-force per mm²", G0 / 1e-6),
    Unit("mmHg",    "milimetr rtuti (torr)",         "millimeter of mercury (torr)", 133.322387415),
    Unit("inHg",    "palec rtuti (0 °C)",            "inch of mercury (0 °C)", 3386.388640341),
])

# --- Rychlost ---------------------------------------------------------------
RYCHLOST = _cat("Rychlost", "Speed", "m/s", [
    Unit("m/s",    "metr za sekundu",               "meter per second"),
    Unit("km/h",   "kilometr za hodinu",            "kilometer per hour", 1 / 3.6),
    Unit("kt",     "uzel (NM/h) — KTAS/KIAS/KEAS", "knot (NM/h) — KTAS/KIAS/KEAS", 1852.0 / 3600),
    Unit("mph",    "míle za hodinu",                "mile per hour",     1609.344 / 3600),
    Unit("ft/s",   "stopa za sekundu",              "foot per second",   FT),
    Unit("ft/min", "stopa za minutu (stoupavost)",  "foot per minute (climb rate)", FT / 60),
])

# --- Zrychleni --------------------------------------------------------------
ZRYCHLENI = _cat("Zrychlení", "Acceleration", "m/s²", [
    Unit("m/s²",  "metr za sekundu na druhou",      "meter per second squared"),
    Unit("g",     "násobek g (9.80665 m/s²)",       "load factor (9.80665 m/s²)", G0),
    Unit("ft/s²", "stopa za sekundu na druhou",     "foot per second squared", FT),
    Unit("in/s²", "palec za sekundu na druhou",     "inch per second squared", IN),
])

# --- Hustota ----------------------------------------------------------------
HUSTOTA = _cat("Hustota", "Density", "kg/m³", [
    Unit("kg/m³",    "kilogram na metr krychlový",  "kilogram per cubic meter"),
    Unit("g/cm³",    "gram na cm³",                 "gram per cubic centimeter", 1e3),
    Unit("t/mm³",    "tuna na mm³ (Abaqus mm-t-s)", "tonne per cubic millimeter (Abaqus)", 1e3 / 1e-9),
    Unit("kg/mm³",   "kilogram na mm³",             "kilogram per cubic millimeter", 1 / 1e-9),
    Unit("lb/in³",   "libra na palec krychlový",    "pound per cubic inch",  LB / IN**3),
    Unit("lb/ft³",   "libra na stopu krychlovou",   "pound per cubic foot",  LB / FT**3),
    Unit("slug/ft³", "slug na stopu krychlovou",    "slug per cubic foot",   SLUG / FT**3),
])

# --- Moment sily ------------------------------------------------------------
MOMENT = _cat("Moment síly", "Moment", "N·m", [
    Unit("N·m",    "newtonmetr",                    "newton meter"),
    Unit("N·mm",   "newtonmilimetr",                "newton millimeter",  1e-3),
    Unit("kN·m",   "kilonewtonmetr",                "kilonewton meter",   1e3),
    Unit("kgf·m",  "kilogram-síla metr",            "kilogram-force meter", G0),
    Unit("lbf·in", "libra-síla palec",              "pound-force inch",   LBF * IN),
    Unit("lbf·ft", "libra-síla stopa",              "pound-force foot",   LBF * FT),
])

# --- Energie ----------------------------------------------------------------
ENERGIE = _cat("Energie / Práce", "Energy / Work", "J", [
    Unit("J",      "joule",                         "joule"),
    Unit("kJ",     "kilojoule",                     "kilojoule",          1e3),
    Unit("MJ",     "megajoule",                     "megajoule",          1e6),
    Unit("kWh",    "kilowatthodina",                "kilowatt hour",      3.6e6),
    Unit("ft·lbf", "stopa libra-síla",              "foot pound-force",   LBF * FT),
    Unit("BTU",    "British thermal unit (IT)",     "British thermal unit (IT)", 1055.05585262),
    Unit("cal",    "kalorie (IT)",                  "calorie (IT)",       4.1868),
    Unit("kcal",   "kilokalorie (IT)",              "kilocalorie (IT)",   4186.8),
])

# --- Vykon ------------------------------------------------------------------
VYKON = _cat("Výkon", "Power", "W", [
    Unit("W",        "watt",                        "watt"),
    Unit("kW",       "kilowatt",                    "kilowatt",           1e3),
    Unit("hp",       "horsepower (550 ft·lbf/s)",   "horsepower (550 ft·lbf/s)", 550 * LBF * FT),
    Unit("k (PS)",   "kůň metrický (75 kgf·m/s)",  "metric horsepower (75 kgf·m/s)", 75 * G0),
    Unit("ft·lbf/s", "stopa libra-síla za sekundu", "foot pound-force per second", LBF * FT),
    Unit("BTU/h",    "BTU za hodinu",               "BTU per hour",       1055.05585262 / 3600),
])

# --- Teplota (afinni) -------------------------------------------------------
TEPLOTA = _cat("Teplota", "Temperature", "K", [
    Unit("K",  "kelvin",                            "kelvin"),
    Unit("°C", "stupeň Celsia",                     "degree Celsius",
         to_base=lambda c: c + 273.15, from_base=lambda k: k - 273.15),
    Unit("°F", "stupeň Fahrenheita",                "degree Fahrenheit",
         to_base=lambda f: (f + 459.67) * 5 / 9,
         from_base=lambda k: k * 9 / 5 - 459.67),
    Unit("°R", "stupeň Rankina",                    "degree Rankine",
         to_base=lambda r: r * 5 / 9, from_base=lambda k: k * 9 / 5),
])

# --- Kvadraticky moment prurezu ---------------------------------------------
KVADR_MOMENT = _cat("Kvadr. moment průřezu (I)", "Second Moment of Area (I)", "m⁴", [
    Unit("m⁴",  "metr na čtvrtou",                 "meter to the fourth"),
    Unit("cm⁴", "centimetr na čtvrtou",            "centimeter to the fourth", 1e-8),
    Unit("mm⁴", "milimetr na čtvrtou",             "millimeter to the fourth", 1e-12),
    Unit("in⁴", "palec na čtvrtou",                "inch to the fourth",   IN**4),
    Unit("ft⁴", "stopa na čtvrtou",                "foot to the fourth",   FT**4),
])

# --- Modul prurezu ----------------------------------------------------------
MODUL_PRUREZU = _cat("Modul průřezu (W, S)", "Section Modulus (W, S)", "m³", [
    Unit("m³",  "metr krychlový",                  "cubic meter"),
    Unit("cm³", "centimetr krychlový",             "cubic centimeter",    1e-6),
    Unit("mm³", "milimetr krychlový",              "cubic millimeter",    1e-9),
    Unit("in³", "palec krychlový",                 "cubic inch",          IN**3),
])

# --- Lomova houzevnatost ----------------------------------------------------
LOMOVA = _cat("Lomová houževnatost (K)", "Fracture Toughness (K)", "MPa·√m", [
    Unit("MPa·√m",   "megapascal odmocnina metru",  "megapascal root meter"),
    Unit("ksi·√in",  "ksi odmocnina palce",         "ksi root inch",
         factor=(1000 * PSI / 1e6) * math.sqrt(IN)),
    Unit("N/mm^3/2", "newton na mm^(3/2)",          "newton per mm^(3/2)",
         factor=1 / math.sqrt(1000)),
])

# --- Plosna hmotnost --------------------------------------------------------
PLOSNA_HMOTNOST = _cat("Plošná hmotnost", "Areal Weight", "kg/m²", [
    Unit("kg/m²",  "kilogram na metr čtvereční",   "kilogram per square meter"),
    Unit("g/m²",   "gram na m² (gramáž tkaniny)",  "gram per square meter (fabric)", 1e-3),
    Unit("lb/ft²", "libra na stopu čtvereční",      "pound per square foot", LB / FT**2),
    Unit("oz/yd²", "unce na yard čtvereční",        "ounce per square yard", (LB / 16) / 0.9144**2),
])

# --- Tuhost pruziny ---------------------------------------------------------
TUHOST = _cat("Tuhost (lineární)", "Linear Stiffness", "N/m", [
    Unit("N/m",    "newton na metr",                "newton per meter"),
    Unit("N/mm",   "newton na milimetr",            "newton per millimeter", 1e3),
    Unit("kN/mm",  "kilonewton na milimetr",        "kilonewton per millimeter", 1e6),
    Unit("lbf/in", "libra-síla na palec",           "pound-force per inch",  LBF / IN),
    Unit("lbf/ft", "libra-síla na stopu",           "pound-force per foot",  LBF / FT),
])

# --- Hmotnostni moment setrvacnosti ----------------------------------------
HMOT_MOMENT = _cat("Hmotnostní moment setrvačnosti", "Mass Moment of Inertia", "kg·m²", [
    Unit("kg·m²",    "kilogram metr čtvereční",     "kilogram square meter"),
    Unit("kg·mm²",   "kilogram milimetr čtvereční", "kilogram square millimeter", 1e-6),
    Unit("t·mm²",    "tuna milimetr čtvereční (Abaqus)", "tonne square millimeter (Abaqus)", 1e-3),
    Unit("lb·in²",   "libra palec čtvereční",       "pound square inch",     LB * IN**2),
    Unit("lb·ft²",   "libra stopa čtvereční",       "pound square foot",     LB * FT**2),
    Unit("slug·ft²", "slug stopa čtvereční",        "slug square foot",      SLUG * FT**2),
])

# --- Uhel -------------------------------------------------------------------
UHEL = _cat("Úhel", "Angle", "rad", [
    Unit("rad",  "radián",                          "radian"),
    Unit("°",    "stupeň",                          "degree",              math.pi / 180),
    Unit("mrad", "miliradián",                      "milliradian",         1e-3),
    Unit("'",    "úhlová minuta",                   "arcminute",           math.pi / 180 / 60),
])

# --- Uhlova rychlost --------------------------------------------------------
UHLOVA_RYCHLOST = _cat("Úhlová rychlost", "Angular Velocity", "rad/s", [
    Unit("rad/s", "radián za sekundu",              "radian per second"),
    Unit("°/s",   "stupeň za sekundu",              "degree per second",   math.pi / 180),
    Unit("rpm",   "otáčky za minutu",               "revolutions per minute", 2 * math.pi / 60),
    Unit("Hz",    "otáčky za sekundu",              "revolutions per second", 2 * math.pi),
])

# --- Viskozita dynamicka ----------------------------------------------------
VISK_DYN = _cat("Viskozita dynamická (μ)", "Dynamic Viscosity (μ)", "Pa·s", [
    Unit("Pa·s",      "pascalsekunda",              "pascal second"),
    Unit("mPa·s",     "milipascalsekunda (= cP)",   "millipascal second (= cP)", 1e-3),
    Unit("P",         "poise",                      "poise",               0.1),
    Unit("cP",        "centipoise",                 "centipoise",          1e-3),
    Unit("lbf·s/ft²", "libra-síla sekunda na ft²",  "pound-force second per sq. ft", PSF),
])

# --- Viskozita kinematicka --------------------------------------------------
VISK_KIN = _cat("Viskozita kinematická (ν)", "Kinematic Viscosity (ν)", "m²/s", [
    Unit("m²/s",  "metr čtvereční za sekundu",      "square meter per second"),
    Unit("mm²/s", "milimetr čtvereční za s (= cSt)", "square millimeter per second (= cSt)", 1e-6),
    Unit("St",    "stokes",                         "stokes",              1e-4),
    Unit("cSt",   "centistokes",                    "centistokes",         1e-6),
    Unit("ft²/s", "stopa čtvereční za sekundu",     "square foot per second", FT**2),
])


def format_value(x: float, sig: int = 6) -> str:
    if x == 0:
        return "0"
    if not math.isfinite(x):
        return str(x)
    mag = abs(x)
    if mag >= 1e7 or mag < 1e-4:
        s = f"{x:.{sig - 1}e}"
        mant, exp = s.split("e")
        mant = mant.rstrip("0").rstrip(".")
        return f"{mant}e{int(exp)}"
    s = f"{x:.{sig}g}"
    if "e" in s or "E" in s:
        s = f"{x:.{sig + 4}f}".rstrip("0").rstrip(".")
    return s
