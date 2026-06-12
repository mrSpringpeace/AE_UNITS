"""Konzistentni jednotkove systemy pro FEM/CFD resice.

Kazdy solver ma seznam sloupcu (nazvy systemu) a radky
(velicina + jednotka/hodnota v kazdem systemu). Soucasti tabulky
jsou kontrolni hodnoty (g, ocel, hlinik), kterymi si clovek rychle
overi, ze ma model v konzistentnich jednotkach.
"""

SOLVERS = {
    "Abaqus": {
        "note": ("Abaqus jednotky nekontroluje — odpovědnost je na vás. "
                 "Nejběžnější volba pro konstrukce je SI (mm): délky mm, síly N, "
                 "napětí a moduly MPa, hustota v t/mm³ (ocel 7.85e-9!). "
                 "Energie pak vychází v mJ."),
        "note_en": ("Abaqus does not check units — the responsibility is yours. "
                    "The most common choice for structures is SI (mm): lengths in mm, forces in N, "
                    "stress and moduli in MPa, density in t/mm³ (steel 7.85e-9!). "
                    "Energy then comes out in mJ."),
        "systems": ["SI (m, kg, s)", "SI (mm, t, s)", "US (in, lbf·s²/in, s)", "US (ft, slug, s)"],
        "rows": [
            ("Délka",            "m",        "mm",        "in",            "ft"),
            ("Hmotnost",         "kg",       "t (10³ kg)", "lbf·s²/in (slinch)", "slug"),
            ("Čas",              "s",        "s",         "s",             "s"),
            ("Síla",             "N",        "N",         "lbf",           "lbf"),
            ("Napětí, tlak, E",  "Pa",       "MPa",       "psi",           "psf"),
            ("Hustota",          "kg/m³",    "t/mm³",     "lbf·s²/in⁴",    "slug/ft³"),
            ("Energie",          "J",        "mJ",        "in·lbf",        "ft·lbf"),
            ("Rychlost",         "m/s",      "mm/s",      "in/s",          "ft/s"),
            ("Zrychlení",        "m/s²",     "mm/s²",     "in/s²",         "ft/s²"),
            ("Moment",           "N·m",      "N·mm",      "in·lbf",        "ft·lbf"),
            ("—  kontrolní hodnoty  —", "", "", "", ""),
            ("g (tíhové zrychl.)", "9.80665", "9806.65",  "386.089",       "32.174"),
            ("ρ ocel (7850 kg/m³)", "7850",   "7.85e-9",  "7.345e-4",      "15.23"),
            ("E ocel (210 GPa)",  "2.10e11",  "210 000",  "3.046e7",       "4.386e9"),
            ("ρ hliník (2700 kg/m³)", "2700", "2.70e-9",  "2.526e-4",      "5.239"),
            ("E hliník (70 GPa)", "7.0e10",   "70 000",   "1.015e7",       "1.462e9"),
        ],
    },

    "Nastran": {
        "note": ("Nastran jednotky nekontroluje. Pozor na anglosaské modely: "
                 "hustota bývá zadána jako tíhová (lb/in³) v kombinaci s "
                 "PARAM,WTMASS,0.00259 (= 1/386.089) — zkontrolujte, zda model "
                 "WTMASS používá, jinak vyjde hmotnostní matice 386× špatně!"),
        "note_en": ("Nastran does not check units. Watch out for US models: "
                    "density is often entered as weight density (lb/in³) together with "
                    "PARAM,WTMASS,0.00259 (= 1/386.089) — check whether the model uses "
                    "WTMASS, otherwise the mass matrix will be off by a factor of 386!"),
        "systems": ["SI (m, kg, s)", "SI (mm, t, s)", "US (in, slinch, s)", "US (ft, slug, s)"],
        "rows": [
            ("Délka",            "m",        "mm",        "in",            "ft"),
            ("Hmotnost",         "kg",       "t (10³ kg)", "lbf·s²/in (slinch)", "slug"),
            ("Čas",              "s",        "s",         "s",             "s"),
            ("Síla",             "N",        "N",         "lbf",           "lbf"),
            ("Napětí, tlak, E",  "Pa",       "MPa",       "psi",           "psf"),
            ("Hustota (RHO)",    "kg/m³",    "t/mm³",     "lbf·s²/in⁴",    "slug/ft³"),
            ("Energie",          "J",        "mJ",        "in·lbf",        "ft·lbf"),
            ("Frekvence",        "Hz",       "Hz",        "Hz",            "Hz"),
            ("Moment",           "N·m",      "N·mm",      "in·lbf",        "ft·lbf"),
            ("—  kontrolní hodnoty  —", "", "", "", ""),
            ("g (tíhové zrychl.)", "9.80665", "9806.65",  "386.089",       "32.174"),
            ("ρ ocel (7850 kg/m³)", "7850",   "7.85e-9",  "7.345e-4",      "15.23"),
            ("E ocel (210 GPa)",  "2.10e11",  "210 000",  "3.046e7",       "4.386e9"),
            ("ρ hliník (2700 kg/m³)", "2700", "2.70e-9",  "2.526e-4",      "5.239"),
            ("E hliník (70 GPa)", "7.0e10",   "70 000",   "1.015e7",       "1.462e9"),
            ("WTMASS (při lb/in³)", "—",      "—",        "0.002590",      "—"),
        ],
    },

    "OpenFOAM": {
        "note": ("OpenFOAM pracuje výhradně v SI — jednotky jsou součástí "
                 "definice polí (dimensions). Pozor: nestlačitelné řešiče "
                 "(simpleFoam, pisoFoam, pimpleFoam) počítají s kinematickým "
                 "tlakem p* = p/ρ [m²/s²]; skutečný tlak v Pa dostanete "
                 "vynásobením hustotou."),
        "note_en": ("OpenFOAM always uses SI — units are part of the field definition "
                    "(dimensions). Note: incompressible solvers (simpleFoam, pisoFoam, "
                    "pimpleFoam) work with kinematic pressure p* = p/ρ [m²/s²]; "
                    "multiply by density to get the actual pressure in Pa."),
        "systems": ["SI (always!)"],
        "rows": [
            ("Délka",                        "m"),
            ("Čas",                          "s"),
            ("Rychlost (U)",                 "m/s"),
            ("Tlak — stlačitelné řešiče",    "Pa"),
            ("Tlak — nestlačitelné (p/ρ)",   "m²/s²"),
            ("Hustota (rho)",                "kg/m³"),
            ("Kinematická viskozita (nu)",   "m²/s"),
            ("Dynamická viskozita (mu)",     "Pa·s"),
            ("Turb. kin. energie (k)",       "m²/s²"),
            ("Disipace (epsilon)",           "m²/s³"),
            ("Specif. disipace (omega)",     "1/s"),
            ("Teplota (T)",                  "K"),
            ("—  kontrolní hodnoty (vzduch, ISA 0 m)  —", ""),
            ("ρ vzduch",                     "1.225 kg/m³"),
            ("ν vzduch",                     "1.461e-5 m²/s"),
            ("μ vzduch",                     "1.789e-5 Pa·s"),
        ],
    },

    "PAM-CRASH": {
        "note": ("Explicitní crash kódy běžně používají milisekundy. "
                 "Systém (mm, g, ms) má příjemnou vlastnost: síla vychází v N, "
                 "napětí v MPa a rychlost mm/ms je číselně rovna m/s. "
                 "Systém (mm, kg, ms) dává napětí v GPa."),
        "note_en": ("Explicit crash codes commonly use milliseconds. "
                    "The (mm, g, ms) system has a convenient property: force comes out in N, "
                    "stress in MPa, and mm/ms is numerically equal to m/s. "
                    "The (mm, kg, ms) system gives stress in GPa."),
        "systems": ["SI (m, kg, s)", "(mm, g, ms) → MPa", "(mm, kg, ms) → GPa"],
        "rows": [
            ("Délka",            "m",        "mm",        "mm"),
            ("Hmotnost",         "kg",       "g",         "kg"),
            ("Čas",              "s",        "ms",        "ms"),
            ("Síla",             "N",        "N",         "kN"),
            ("Napětí, tlak, E",  "Pa",       "MPa",       "GPa"),
            ("Hustota",          "kg/m³",    "g/mm³",     "kg/mm³"),
            ("Energie",          "J",        "mJ",        "J"),
            ("Rychlost",         "m/s",      "mm/ms (= m/s)", "mm/ms (= m/s)"),
            ("Zrychlení",        "m/s²",     "mm/ms²",    "mm/ms²"),
            ("—  kontrolní hodnoty  —", "", "", ""),
            ("g (tíhové zrychl.)", "9.80665", "9.80665e-3", "9.80665e-3"),
            ("ρ ocel (7850 kg/m³)", "7850",   "7.85e-3",   "7.85e-6"),
            ("E ocel (210 GPa)",  "2.10e11",  "210 000",   "210"),
            ("ρ hliník (2700 kg/m³)", "2700", "2.70e-3",   "2.70e-6"),
            ("E hliník (70 GPa)", "7.0e10",   "70 000",    "70"),
        ],
    },
}
