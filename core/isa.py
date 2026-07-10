"""Mezinarodni standardni atmosfera (ISA / US Standard Atmosphere 1976).

Platnost 0 az 86 km geometricke vysky (resp. -2 km pod urovni more).
Vstup je geometricka vyska; interne se prevadi na geopotencialni.

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
_LAYERS = [
    (0.0,     -0.0065),
    (11000.0,  0.0),
    (20000.0,  0.001),
    (32000.0,  0.0028),
    (47000.0,  0.0),
    (51000.0, -0.0028),
    (71000.0, -0.002),
    (84852.0,  None),   # konec modelu
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

H_MIN, H_MAX = -2000.0, 84852.0   # platnost modelu [m geopotencialne]
_P_TOP = _p                        # tlak na hornim okraji modelu


def _std_Tp(h: float) -> tuple:
    """Standardni (T, p) v geopotencialni vysce h [m]. Bez kontroly rozsahu."""
    base = _BASES[0]
    for b in _BASES:
        if h >= b[0]:
            base = b
        else:
            break
    h_b, T_b, p_b, L = base
    if L == 0.0:
        return T_b, p_b * math.exp(-G0 * (h - h_b) / (R * T_b))
    T = T_b + L * (h - h_b)
    return T, p_b * (T_b / T) ** (G0 / (R * L))


P_MAX = _std_Tp(H_MIN)[1]          # tlak na dolnim okraji modelu (-2 km)


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


def isa(z_m: float, dT: float = 0.0) -> IsaResult:
    """Vypocet atmosfery v geometricke vysce z_m [m], dT = odchylka od ISA [K]."""
    h = R_EARTH * z_m / (R_EARTH + z_m)
    if not (H_MIN <= h <= H_MAX):
        raise ValueError("Vyska mimo rozsah modelu (-2 az 86 km)")

    T_std, p = _std_Tp(h)
    T = T_std + dT
    rho = p / (R * T)
    a = math.sqrt(GAMMA * R * T)
    mu = 1.458e-6 * T ** 1.5 / (T + 110.4)   # Sutherland
    nu = mu / rho

    return IsaResult(z=z_m, h=h, T=T, T_isa=T_std, p=p, rho=rho, a=a,
                     mu=mu, nu=nu, sigma=rho / RHO0, delta=p / P0,
                     theta=T / T0)


def isa_h(h_m: float, dT: float = 0.0) -> IsaResult:
    """Vypocet ze zadane geopotencialni (= tlakove) vysky h_m [m].

    Tlakova vyska (altimetr na 1013.25 hPa, FL) je ve standardni
    atmosfere totozna s geopotencialni vyskou.
    """
    if not (H_MIN <= h_m <= H_MAX):
        raise ValueError("Vyska mimo rozsah modelu (-2 az 86 km)")
    return isa(R_EARTH * h_m / (R_EARTH - h_m), dT)


def pressure_altitude(p: float) -> float:
    """Tlakova (geopotencialni) vyska [m] pro tlak p [Pa] — inverze std. atmosfery."""
    if not (_P_TOP <= p <= P_MAX):
        raise ValueError("Tlak mimo rozsah modelu")
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
        raise ValueError("Hustota mimo rozsah modelu")
    lo, hi = H_MIN, H_MAX
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if _std_rho(mid) > rho:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
