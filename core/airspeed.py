"""Prevody rychlosti letu: CAS / EAS / TAS / Mach (subsonicke, stlacitelne).

Definice:
  TAS - skutecna vzdusna rychlost
  EAS - ekvivalentni: 1/2 rho0 EAS^2 = 1/2 rho TAS^2  =>  EAS = TAS*sqrt(sigma)
  CAS - kalibrovana: rychlost, ktera by na hladine more ve standardni
        atmosfere dala stejny impaktni tlak q_c (kompresibilni Bernoulli);
        IAS = CAS + pristrojova a polohova chyba (nelze obecne spocitat)
  M   - Machovo cislo TAS/a
  q   - dynamicky tlak 1/2 rho TAS^2 (= gamma/2 p M^2)
  q_c - impaktni tlak (celkovy minus staticky, to co meri pitot)

Vzorce (izentropicke, plati pro M <= 1):
  q_c = p*[(1 + (gamma-1)/2 M^2)^(gamma/(gamma-1)) - 1]
  CAS = a0*sqrt( 2/(gamma-1) * [(q_c/p0 + 1)^((gamma-1)/gamma) - 1] )

Pro M > 1 by bylo nutne pouzit Rayleighovu pitotovu formuli (razova
vlna pred snimacem) - mimo rozsah teto aplikace.
"""

import math
from dataclasses import dataclass

from core.isa import IsaResult, AtmosphereError, GAMMA, P0, RHO0, T0, R

A0 = math.sqrt(GAMMA * R * T0)     # rychlost zvuku na hladine more (340.294 m/s)

KINDS = ["TAS", "EAS", "CAS", "Mach"]


@dataclass(frozen=True)
class SpeedResult:
    tas: float     # [m/s]
    eas: float     # [m/s]
    cas: float     # [m/s]
    mach: float    # [-]
    q: float       # dynamicky tlak [Pa]
    qc: float      # impaktni tlak [Pa]


def _qc_from_mach(mach: float, p: float) -> float:
    return p * ((1 + (GAMMA - 1) / 2 * mach**2) ** (GAMMA / (GAMMA - 1)) - 1)


def _mach_from_qc(qc: float, p: float) -> float:
    return math.sqrt(2 / (GAMMA - 1)
                     * ((qc / p + 1) ** ((GAMMA - 1) / GAMMA) - 1))


def speeds(atm: IsaResult, value: float, kind: str) -> SpeedResult:
    """Prepocet rychlosti v dane atmosfere (vystup z isa()/isa_h()).

    value: rychlost [m/s], u kind="Mach" Machovo cislo [-]
    kind:  "TAS" | "EAS" | "CAS" | "Mach"
    """
    if value < 0:
        raise AtmosphereError("as_err_negative")
    sqrt_sigma = math.sqrt(atm.sigma)

    if kind == "TAS":
        mach = value / atm.a
    elif kind == "EAS":
        mach = value / sqrt_sigma / atm.a
    elif kind == "Mach":
        mach = value
    elif kind == "CAS":
        qc = _qc_from_mach(value / A0, P0)   # q_c z definice CAS
        mach = _mach_from_qc(qc, atm.p)
    else:
        raise AtmosphereError("as_err_kind", kind=kind)

    if mach > 1.0:
        raise AtmosphereError("as_supersonic")

    tas = mach * atm.a
    eas = tas * sqrt_sigma
    qc = _qc_from_mach(mach, atm.p)
    cas = A0 * math.sqrt(2 / (GAMMA - 1)
                         * ((qc / P0 + 1) ** ((GAMMA - 1) / GAMMA) - 1))
    q = 0.5 * atm.rho * tas**2
    return SpeedResult(tas=tas, eas=eas, cas=cas, mach=mach, q=q, qc=qc)
