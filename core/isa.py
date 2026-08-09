"""Mezinarodni standardni atmosfera (ISA / US Standard Atmosphere 1976).

Platnost -2 az 86 km geometricke vysky.
Vstup isa() je geometricka vyska; interne se prevadi na geopotencialni.
isa_h() bere geopotencialni (= tlakovou) vysku primo.

Podpora odchylky od ISA (dT): teplota se posune, tlak zustava na
standardni hodnote (bezna konvence pro vykonove vypocty), hustota
se prepocte ze stavove rovnice.
"""

import math
from dataclasses import dataclass

# konstanty (US Standard Atmosphere 1976)
R = 287.05287          # J/(kg.K) merna plynova konstanta vzduchu
GAMMA = 1.4            # Poissonova konstanta
G0 = 9.80665           # m/s2
R_EARTH = 6356766.0    # m, polomer Zeme pro geopotencialni prevod

T0 = 288.15            # K   hladina more
P0 = 101325.0          # Pa
RHO0 = P0 / (R * T0)   # 1.225 kg/m3

# vrstvy: (geopotencialni vyska zakladny [m], gradient L [K/m])
# Horni okraj 84 852 m geopot. = 86 km geometrickych (US 1976).
_LAYERS = [
    (0.0,     -0.0065),
    (11000.0,  0.0),
    (20000.0,  0.001),
    (32000.0,  0.0028),
    (47000.0,  0.0),
    (51000.0, -0.0028),
    (71000.0, -0.002),
    (84852.0,  None),   # konec modelu (geopotencial)
]

# predpocet teplot a tlaku na zakladnach vrstev
_BASES = []  # (h_b, T_b, p_b, L)
_t, _p = T0, P0
for _i, (_hb, _L) in enumerate(_LAYERS[:-1]):
    _BASES.append((_hb, _t, _p, _L))
    _h_next = _LAYERS[_i + 1][0]
    _dh = _h_next - _hb
    if _L == 0.0:
        _p = _p * math.exp(-G0 * _dh / (R * _t))
    else:
        _p = _p * (_t / (_t + _L * _dh)) ** (G0 / (R * _L))
        _t = _t + _L * _dh

# Geometricke limity (ofic. US 1976: 0–86 km; aplikace umoznuje -2 km)
Z_MIN, Z_MAX = -2000.0, 86000.0
# Geopotencialni limity odpovidajici geometrickym koncum
H_MIN = R_EARTH * Z_MIN / (R_EARTH + Z_MIN)  # ~-2000.63 m
H_MAX = R_EARTH * Z_MAX / (R_EARTH + Z_MAX)  # ~84852.05 m
_H_TABLE_TOP = _LAYERS[-1][0]                # 84852.0 m geopot. (US-1976)


class AtmosphereError(ValueError):
    """Chyba atmosferickeho modelu s i18n klicem."""

    def __init__(self, key: str, **kwargs):
        self.key = key
        self.kwargs = kwargs
        super().__init__(key)


def _std_Tp(h: float) -> tuple:
    """Standardni (T, p) v geopotencialni vysce h [m]. Bez kontroly rozsahu."""
    # z=86000 m geometrickych da h o zlomek m nad 84852 — clamp na tabulku
    h_use = min(h, _H_TABLE_TOP)
    base = _BASES[0]
    for b in _BASES:
        if h_use >= b[0]:
            base = b
        else:
            break
    h_b, T_b, p_b, L = base
    if L == 0.0:
        return T_b, p_b * math.exp(-G0 * (h_use - h_b) / (R * T_b))
    T = T_b + L * (h_use - h_b)
    return T, p_b * (T_b / T) ** (G0 / (R * L))


P_MAX = _std_Tp(H_MIN)[1]          # tlak na dolnim okraji modelu
_P_TOP = _std_Tp(H_MAX)[1]         # tlak na hornim okraji (86 km geometrickych)


@dataclass(frozen=True)
class IsaResult:
    z: float        # geometricka vyska [m]
    h: float        # geopotencialni vyska [m]
    T: float        # teplota [K] (vcetne dT)
    T_isa: float    # standardni ISA teplota [K]
    p: float        # tlak [Pa]
    rho: float      # hustota [kg/m3]
    a: float        # rychlost zvuku [m/s]
    mu: float       # dynamicka viskozita [Pa.s]
    nu: float       # kinematicka viskozita [m2/s]
    sigma: float    # rho/rho0
    delta: float    # p/p0
    theta: float    # T/T0


def _from_geopot(h: float, dT: float = 0.0, z: float | None = None) -> IsaResult:
    """Sdilena cesta: geopotencialni h + dT -> IsaResult."""
    T_std, p = _std_Tp(h)
    T = T_std + dT
    if T <= 0.0:
        raise AtmosphereError("isa_err_temp")
    rho = p / (R * T)
    a = math.sqrt(GAMMA * R * T)
    mu = 1.458e-6 * T ** 1.5 / (T + 110.4)   # Sutherland
    nu = mu / rho
    if z is None:
        z = R_EARTH * h / (R_EARTH - h)
    return IsaResult(z=z, h=h, T=T, T_isa=T_std, p=p, rho=rho, a=a,
                     mu=mu, nu=nu, sigma=rho / RHO0, delta=p / P0,
                     theta=T / T0)


def isa(z_m: float, dT: float = 0.0) -> IsaResult:
    """Vypocet atmosfery v geometricke vysce z_m [m], dT = odchylka od ISA [K]."""
    if not (Z_MIN <= z_m <= Z_MAX):
        raise AtmosphereError("isa_err_alt")
    h = R_EARTH * z_m / (R_EARTH + z_m)
    return _from_geopot(h, dT, z=z_m)


def isa_h(h_m: float, dT: float = 0.0) -> IsaResult:
    """Vypocet ze zadane geopotencialni (= tlakove) vysky h_m [m].

    Tlakova vyska (altimetr na 1013.25 hPa, FL) je ve standardni
    atmosfere totozna s geopotencialni vyskou.
    """
    if not (H_MIN <= h_m <= H_MAX):
        raise AtmosphereError("isa_err_alt")
    return _from_geopot(h_m, dT)


def pressure_altitude(p: float) -> float:
    """Tlakova (geopotencialni) vyska [m] pro tlak p [Pa] — inverze std. atmosfery."""
    if not (_P_TOP <= p <= P_MAX):
        raise AtmosphereError("isa_err_pressure")
    base = _BASES[0]
    for b in _BASES:
        if p <= b[2]:
            base = b
        else:
            break
    h_b, T_b, p_b, L = base
    if L == 0.0:
        return h_b - R * T_b / G0 * math.log(p / p_b)
    T = T_b * (p_b / p) ** (R * L / G0)
    return h_b + (T - T_b) / L


def density_altitude(rho: float) -> float:
    """Hustotni vyska [m geopot.] — vyska std. atmosfery se stejnou hustotou.

    Hustota std. atmosfery monotonne klesa, staci bisekce.
    """
    def _std_rho(h):
        T, p = _std_Tp(h)
        return p / (R * T)

    if not (_std_rho(H_MAX) <= rho <= _std_rho(H_MIN)):
        raise AtmosphereError("isa_err_density")
    lo, hi = H_MIN, H_MAX
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if _std_rho(mid) > rho:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
