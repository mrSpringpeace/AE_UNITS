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
    if not (-2000.0 <= h <= 84852.0):
        raise ValueError("Vyska mimo rozsah modelu (-2 az 86 km)")

    # najdi vrstvu (pod 0 m plati gradient prvni vrstvy)
    base = _BASES[0]
    for b in _BASES:
        if h >= b[0]:
            base = b
        else:
            break
    h_b, T_b, p_b, L = base

    if L == 0.0:
        T_std = T_b
        p = p_b * math.exp(-G0 * (h - h_b) / (R * T_b))
    else:
        T_std = T_b + L * (h - h_b)
        p = p_b * (T_b / T_std) ** (G0 / (R * L))

    T = T_std + dT
    rho = p / (R * T)
    a = math.sqrt(GAMMA * R * T)
    mu = 1.458e-6 * T ** 1.5 / (T + 110.4)   # Sutherland
    nu = mu / rho

    return IsaResult(z=z_m, h=h, T=T, T_isa=T_std, p=p, rho=rho, a=a,
                     mu=mu, nu=nu, sigma=rho / RHO0, delta=p / P0,
                     theta=T / T0)
