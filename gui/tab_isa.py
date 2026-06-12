"""Tab mezinarodni standardni atmosfery (ISA / US 1976, 0-86 km)."""

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from core.isa import isa
from core.formatting import fmt
from core.units import FT
from core import i18n
from gui import theme

ALT_UNITS = {"m": 1.0, "ft": FT, "km": 1000.0, "FL": 100 * FT}

# (klic, i18n klic popisku, jednotka)
ROWS = [
    ("h",      "isa_geopotential_h",  "m"),
    ("h_ft",   "isa_geopotential_h",  "ft"),
    ("T",      "isa_temperature",     "K"),
    ("T_C",    "isa_temperature",     "°C"),
    ("T_isa",  "isa_temperature_isa", "K"),
    ("p",      "isa_pressure",        "Pa"),
    ("p_hpa",  "isa_pressure",        "hPa"),
    ("p_psi",  "isa_pressure",        "psi"),
    ("p_inhg", "isa_pressure",        "inHg"),
    ("rho",    "isa_density",         "kg/m³"),
    ("rho_sl", "isa_density",         "slug/ft³"),
    ("rho_lb", "isa_density",         "lb/ft³"),
    ("sigma",  "isa_sigma",           "—"),
    ("rsigma", "isa_rsigma",          "—"),
    ("delta",  "isa_delta",           "—"),
    ("theta",  "isa_theta",           "—"),
    ("a",      "isa_sound_speed",     "m/s"),
    ("a_kt",   "isa_sound_speed",     "kt"),
    ("a_kmh",  "isa_sound_speed",     "km/h"),
    ("mu",     "isa_dyn_visc",        "Pa·s"),
    ("nu",     "isa_kin_visc",        "m²/s"),
]


class IsaTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._row_ids = {}

        inp = ctk.CTkFrame(self)
        inp.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.lbl_alt = ctk.CTkLabel(inp, font=("Segoe UI", 14))
        self.lbl_alt.grid(row=0, column=0, padx=(12, 6), pady=12)
        self.alt_entry = ctk.CTkEntry(inp, width=140, font=("Consolas", 18), justify="right")
        self.alt_entry.grid(row=0, column=1, padx=6, pady=12)
        self.alt_entry.insert(0, "0")
        self.alt_entry.bind("<KeyRelease>", lambda e: self.recalc())

        self.alt_unit = ctk.CTkOptionMenu(inp, width=80, values=list(ALT_UNITS),
                                          command=lambda _: self.recalc())
        self.alt_unit.grid(row=0, column=2, padx=6, pady=12)

        self.lbl_dt = ctk.CTkLabel(inp, font=("Segoe UI", 14))
        self.lbl_dt.grid(row=0, column=3, padx=(24, 6), pady=12)
        self.dt_entry = ctk.CTkEntry(inp, width=80, font=("Consolas", 18), justify="right")
        self.dt_entry.grid(row=0, column=4, padx=6, pady=12)
        self.dt_entry.insert(0, "0")
        self.dt_entry.bind("<KeyRelease>", lambda e: self.recalc())

        self.status = ctk.CTkLabel(inp, text="", text_color="gray60", anchor="w")
        self.status.grid(row=0, column=5, padx=(24, 12), pady=12, sticky="ew")
        inp.grid_columnconfigure(5, weight=1)

        self.note_label = ctk.CTkLabel(self, text_color="gray60", anchor="w")
        self.note_label.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))

        self.table = ttk.Treeview(
            self, columns=("qty", "val", "unit"), show="headings",
            style="AE.Treeview", selectmode="browse")
        self.table.column("qty",  width=340, stretch=False, anchor="w")
        self.table.column("val",  width=220, stretch=False, anchor="e")
        self.table.column("unit", width=140, stretch=True,  anchor="w")
        self.table.grid(row=2, column=0, sticky="nsew")
        self.table.bind("<Double-1>", self._copy_row)

        self._build_rows()
        self.apply_theme()
        self.refresh_lang()
        self.recalc()

    def _build_rows(self):
        for i, (key, lbl_key, unit) in enumerate(ROWS):
            tag = "odd" if i % 2 else "even"
            iid = self.table.insert("", "end",
                                    values=(i18n.t(lbl_key), "", unit),
                                    tags=(tag,))
            self._row_ids[key] = iid

    def refresh_lang(self):
        self.lbl_alt.configure(text=i18n.t("lbl_altitude"))
        self.lbl_dt.configure(text=i18n.t("lbl_delta_isa"))
        self.note_label.configure(text=i18n.t("isa_model_note"))
        self.table.heading("qty",  text=i18n.t("isa_col_qty"),  anchor="w")
        self.table.heading("val",  text=i18n.t("isa_col_val"),  anchor="e")
        self.table.heading("unit", text=i18n.t("isa_col_unit"), anchor="w")
        for key, lbl_key, _ in ROWS:
            self.table.set(self._row_ids[key], "qty", i18n.t(lbl_key))

    def apply_theme(self):
        theme.zebra(self.table)

    def _copy_row(self, event):
        iid = self.table.identify_row(event.y)
        if not iid:
            return
        val = self.table.set(iid, "val")
        if val:
            self.clipboard_clear()
            self.clipboard_append(val)
            self.status.configure(text=f"{i18n.t('copied')} {val}")
            self.after(1800, lambda: self.status.configure(text=""))

    def _parse(self, entry):
        txt = entry.get().strip().replace(",", ".").replace(" ", "")
        if txt in ("", "-", "+"):
            return None
        try:
            return float(txt)
        except ValueError:
            return None

    def recalc(self):
        alt = self._parse(self.alt_entry)
        dt = self._parse(self.dt_entry)
        if alt is None or dt is None:
            self._clear(i18n.t("isa_invalid"))
            return
        z = alt * ALT_UNITS[self.alt_unit.get()]
        try:
            r = isa(z, dT=dt)
        except ValueError as e:
            self._clear(str(e))
            return
        self.status.configure(text=i18n.t("isa_geom_alt", v=fmt(z)))
        vals = {
            "h": r.h, "h_ft": r.h / FT,
            "T": r.T, "T_C": r.T - 273.15, "T_isa": r.T_isa,
            "p": r.p, "p_hpa": r.p / 100,
            "p_psi":  r.p / 6894.757293168361,
            "p_inhg": r.p / 3386.388640341,
            "rho": r.rho, "rho_sl": r.rho / 515.3788183931961,
            "rho_lb": r.rho / 16.018463373960138,
            "sigma": r.sigma, "rsigma": r.sigma ** -0.5,
            "delta": r.delta, "theta": r.theta,
            "a": r.a, "a_kt": r.a / (1852 / 3600), "a_kmh": r.a * 3.6,
            "mu": r.mu, "nu": r.nu,
        }
        for key, v in vals.items():
            self.table.set(self._row_ids[key], "val", fmt(v))

    def _clear(self, msg):
        self.status.configure(text=msg)
        for iid in self._row_ids.values():
            self.table.set(iid, "val", "")
