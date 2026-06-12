"""Orientacni tabulka leteckych materialu.

Hodnoty jsou typicke ucebnicove (plech/tyc, pokojova teplota).
PRO PRUKAZ PEVNOSTI POUZIJTE MMPDS / CMH-17 / materialovy list -
navrhove hodnoty zavisi na polotovaru, tloustce a basis (A/B).

Sloupce: nazev, rho [kg/m3], E [GPa], nu, Ftu [MPa], Fty [MPa], poznamka
Fty=None u kompozitu/dreva (nema smysl).
"""

MATERIALS = [
    # hlinikove slitiny
    ("Al 2024-T3 plech",      2780, 73.1, 0.33, 448, 324,
     "≈ dural ČSN 42 4203; potahy, žebra"),
    ("Al 6061-T6",            2700, 68.9, 0.33, 310, 276,
     "svařitelná; trubky, UL konstrukce"),
    ("Al 7075-T6 plech",      2810, 71.7, 0.33, 538, 469,
     "vysokopevnostní; pásnice, kování"),
    ("Al 7050-T7451 deska",   2830, 71.7, 0.33, 524, 469,
     "tlusté desky, obráběné integrály"),
    ("Al 5052-H32",           2680, 70.3, 0.33, 228, 193,
     "nádrže, svařitelná, mořské prostředí"),
    # horcik, titan
    ("Mg AZ31B",              1770, 45.0, 0.35, 260, 200,
     "hořčíková slitina; pozor na korozi"),
    ("Ti-6Al-4V (žíhaný)",    4430, 113.8, 0.342, 950, 880,
     "kování, šrouby, horké části"),
    ("Ti Grade 2 (CP)",       4510, 105.0, 0.37, 345, 275,
     "čistý titan; výfuky, požární přepážky"),
    # oceli
    ("Ocel 4130 (normaliz.)", 7850, 205.0, 0.29, 670, 435,
     "≈ ČSN 15 130; motorová lože, příhradoviny"),
    ("Ocel 4340 (zušlecht.)", 7850, 205.0, 0.29, 1080, 930,
     "podvozky, čepy, vysoce namáhané díly"),
    ("Nerez 17-4PH H900",     7750, 196.0, 0.27, 1310, 1170,
     "vytvrditelná nerez; kování, hřídele"),
    ("Nerez 304 (žíhaná)",    8000, 193.0, 0.29, 515, 205,
     "požární přepážky, výfukové díly"),
    ("Inconel 718",           8190, 200.0, 0.29, 1375, 1100,
     "horké části, výfukové systémy"),
    # kompozity (podelny smer vlaken)
    ("C/epoxy UD (Vf≈60 %)",  1600, 135.0, 0.30, 1500, None,
     "E₁ a Ftu podél vláken; CMH-17"),
    ("C/epoxy tkanina 0/90",  1600, 55.0, 0.06, 600, None,
     "orientační; závisí na tkanině a Vf"),
    ("E-sklo/epoxy UD",       2000, 39.0, 0.28, 1000, None,
     "podél vláken"),
    # drevo a jadra
    ("Smrk sitka (letecký)",  430, 10.8, None, 70, None,
     "podél vláken; ohyb ~65–75 MPa"),
    ("Překližka bříza (let.)", 680, 12.5, None, 70, None,
     "podél vláken vnější dýhy; orientační"),
    ("Rohacell 51 IG",        52, 0.07, None, 1.6, None,
     "PMI pěna, jádra sendvičů"),
]

DISCLAIMER = ("Orientační typické hodnoty (RT). Pro průkaz pevnosti použijte "
              "MMPDS / CMH-17 nebo materiálový list — návrhové hodnoty závisí "
              "na polotovaru, tloušťce a statistickém basis (A/B).")

# prevody do anglosaskych jednotek
KG_M3_TO_LB_IN3 = 1 / 27679.904710203125   # = 0.45359237 / 0.0254**3
GPA_TO_MSI = 1 / 6.894757293168361
MPA_TO_KSI = 1 / 6.894757293168361
