"""Orientacni tabulka leteckych materialu.

Hodnoty jsou typicke ucebnicove (plech/tyc, pokojova teplota).
PRO PRUKAZ PEVNOSTI POUZIJTE MMPDS / CMH-17 / materialovy list -
navrhove hodnoty zavisi na polotovaru, tloustce a basis (A/B).

Zaznam: (name, rho, E, nu, Ftu, Fty, note, name_en, note_en)
  rho [kg/m3], E [GPa], Ftu/Fty [MPa]
  Fty=None u kompozitu/dreva (nema smysl).
"""

MATERIALS = [
    ('Al 2024-T3 plech', 2780, 73.1, 0.33, 448, 324,
     '≈ dural ČSN 42 4203; potahy, žebra',
     'Al 2024-T3 sheet', '≈ dural ČSN 42 4203; skins, ribs'),
    ('Al 6061-T6', 2700, 68.9, 0.33, 310, 276,
     'svařitelná; trubky, UL konstrukce',
     'Al 6061-T6', 'weldable; tubes, UL structures'),
    ('Al 7075-T6 plech', 2810, 71.7, 0.33, 538, 469,
     'vysokopevnostní; pásnice, kování',
     'Al 7075-T6 sheet', 'high-strength; spar caps, forgings'),
    ('Al 7050-T7451 deska', 2830, 71.7, 0.33, 524, 469,
     'tlusté desky, obráběné integrály',
     'Al 7050-T7451 plate', 'thick plate, machined integral parts'),
    ('Al 5052-H32', 2680, 70.3, 0.33, 228, 193,
     'nádrže, svařitelná, mořské prostředí',
     'Al 5052-H32', 'tanks, weldable, marine environment'),
    ('Al 2014-T6', 2800, 72.4, 0.33, 483, 414,
     'kování, obráběné díly; starší slitina',
     'Al 2014-T6', 'forgings, machined parts; older alloy'),
    ('Al 6082-T6', 2700, 70.0, 0.33, 310, 260,
     'evropská konstrukční; profily, svařitelná',
     'Al 6082-T6', 'European structural; extrusions, weldable'),
    ('Al 7075-T73', 2810, 71.7, 0.33, 500, 430,
     'odolnost SCC; kování, tlusté průřezy',
     'Al 7075-T73', 'SCC resistance; forgings, thick sections'),
    ('Mg AZ31B', 1770, 45.0, 0.35, 260, 200,
     'hořčíková slitina; pozor na korozi',
     'Mg AZ31B', 'magnesium alloy; watch for corrosion'),
    ('Ti-6Al-4V (žíhaný)', 4430, 113.8, 0.342, 950, 880,
     'kování, šrouby, horké části',
     'Ti-6Al-4V (annealed)', 'forgings, fasteners, hot sections'),
    ('Ti Grade 2 (CP)', 4510, 105.0, 0.37, 345, 275,
     'čistý titan; výfuky, požární přepážky',
     'Ti Grade 2 (CP)', 'commercially pure Ti; exhausts, firewalls'),
    ('Ti-3Al-2.5V', 4480, 100.0, 0.3, 620, 500,
     'hydraulické trubky, tvárnější než 6-4',
     'Ti-3Al-2.5V', 'hydraulic tubing, more formable than 6-4'),
    ('Ocel 4130 (normaliz.)', 7850, 205.0, 0.29, 670, 435,
     '≈ ČSN 15 130; motorová lože, příhradoviny',
     'Steel 4130 (normalized)', '≈ AISI 4130; engine mounts, truss frames'),
    ('Ocel 4340 (zušlecht.)', 7850, 205.0, 0.29, 1080, 930,
     'podvozky, čepy, vysoce namáhané díly',
     'Steel 4340 (heat-treated)', 'landing gear, pins, highly loaded parts'),
    ('Ocel 300M (zušlecht.)', 7830, 205.0, 0.29, 1930, 1590,
     'podvozkové nohy; vysokopevnostní 4340M',
     'Steel 300M (heat-treated)', 'landing-gear legs; high-strength 4340M'),
    ('Nerez 17-4PH H900', 7750, 196.0, 0.27, 1310, 1170,
     'vytvrditelná nerez; kování, hřídele',
     'Stainless 17-4PH H900', 'precipitation-hardening SS; forgings, shafts'),
    ('Nerez 15-5PH H1025', 7800, 196.0, 0.27, 1070, 1000,
     'houževnatější než 17-4; kování, čepy',
     'Stainless 15-5PH H1025', 'tougher than 17-4; forgings, pins'),
    ('Nerez 304 (žíhaná)', 8000, 193.0, 0.29, 515, 205,
     'požární přepážky, výfukové díly',
     'Stainless 304 (annealed)', 'firewalls, exhaust parts'),
    ('Inconel 718', 8190, 200.0, 0.29, 1375, 1100,
     'horké části, výfukové systémy',
     'Inconel 718', 'hot sections, exhaust systems'),
    ('C/epoxy UD (Vf≈60 %)', 1600, 135.0, 0.3, 1500, None,
     'E₁ a Ftu podél vláken; CMH-17',
     'C/epoxy UD (Vf≈60 %)', 'E₁ and Ftu along fibres; CMH-17'),
    ('C/epoxy tkanina 0/90', 1600, 55.0, 0.06, 600, None,
     'orientační; závisí na tkanině a Vf',
     'C/epoxy fabric 0/90', 'indicative; depends on fabric and Vf'),
    ('C/epoxy kvaziizotropní', 1600, 50.0, 0.3, 550, None,
     '[0/±45/90]s laminát; orientační',
     'C/epoxy quasi-isotropic', '[0/±45/90]s laminate; indicative'),
    ('E-sklo/epoxy UD', 2000, 39.0, 0.28, 1000, None,
     'podél vláken',
     'E-glass/epoxy UD', 'along fibres'),
    ('Kevlar 49/epoxy UD', 1380, 75.0, 0.34, 1280, None,
     'tah podél vláken; v tlaku slabý (~230 MPa)!',
     'Kevlar 49/epoxy UD', 'tension along fibres; weak in compression (~230 MPa)!'),
    ('Smrk sitka (letecký)', 430, 10.8, None, 70, None,
     'podél vláken; ohyb ~65–75 MPa',
     'Sitka spruce (aircraft)', 'along grain; bending ~65–75 MPa'),
    ('Překližka bříza (let.)', 680, 12.5, None, 70, None,
     'podél vláken vnější dýhy; orientační',
     'Birch plywood (aircraft)', 'along outer veneer grain; indicative'),
    ('Rohacell 51 IG', 52, 0.07, None, 1.6, None,
     'PMI pěna, jádra sendvičů',
     'Rohacell 51 IG', 'PMI foam, sandwich cores'),
    ('Divinycell H80', 80, 0.09, None, 2.5, None,
     'PVC pěna, jádra sendvičů',
     'Divinycell H80', 'PVC foam, sandwich cores'),
    ('Balsa (podél vláken)', 155, 4.0, None, 20, None,
     'jádra sendvičů; vlastnosti silně kolísají',
     'Balsa (along grain)', 'sandwich cores; properties vary widely'),
]

DISCLAIMER = 'Orientační typické hodnoty (RT). Pro průkaz pevnosti použijte MMPDS / CMH-17 nebo materiálový list — návrhové hodnoty závisí na polotovaru, tloušťce a statistickém basis (A/B).'

DISCLAIMER_EN = 'Indicative typical values (RT). For structural substantiation use MMPDS / CMH-17 or the material data sheet — design values depend on product form, thickness, and statistical basis (A/B).'

# prevody do anglosaskych jednotek
KG_M3_TO_LB_IN3 = 3.612729200008368e-05   # = 0.45359237 / 0.0254**3
GPA_TO_MSI = 0.14503773773020923
MPA_TO_KSI = 0.14503773773020923


def mat_name(m, lang: str = "cs") -> str:
    """Lokalizovany nazev materialu."""
    if lang == "en" and len(m) >= 9 and m[7]:
        return m[7]
    return m[0]


def mat_note(m, lang: str = "cs") -> str:
    """Lokalizovana poznamka materialu."""
    if lang == "en" and len(m) >= 9 and m[8]:
        return m[8]
    return m[6]


def mat_fields(m):
    """Vrati (name_key, rho, E, nu, ftu, fty, note_key) pro spocitani radku.
    name_key/note se berou z mat_name/mat_note; cisla z indexu 1-5.
    """
    return m[1], m[2], m[3], m[4], m[5]
