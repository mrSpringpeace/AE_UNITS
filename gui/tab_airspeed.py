"""Tab prevodu rychlosti letu (CAS / EAS / TAS / Mach + q)."""

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from core.isa import isa, isa_h
from core.airspeed import speeds, KINDS
from core.formatting import fmt
from core.units import FT, PSF
from core import i18n
from gui import theme

ALT_UNITS = {"m": 1.0, "ft": FT, "km": 1000.0, "FL": 100 * FT}
SPEED_UNITS = {"m/s": 1.0, "km/h": 1 / 3.6, "kt": 1852.0 / 3600.0,
               "mph": 1609.344 / 3600.0, "ft/s": FT}
_KT = SPEED_UNITS["kt"]

# (klic, i18n klic popisku, jednotka)
ROWS = [
    ("mach",    "as_mach", "—"),
    ("tas",     "as_tas",  "m/s"),
    ("tas_kmh", "as_tas",  "km/h"),
    ("tas_kt",  "as_tas",  "kt"),
    ("eas",     "as_eas",  "m/s"),
    ("eas_kmh", "as_eas",  "km/h"),
    ("eas_kt",  "as_eas",  "kt"),
    ("cas",     "as_cas",  "m/s"),
    ("cas_kmh", "as_cas",  "km/h"),
    ("cas_kt",  "as_cas",  "kt"),
    ("q",       "as_q",    "Pa"),
    ("q_psf",   "as_q",    "psf"),
    ("qc",      "as_qc",   "Pa"),
    ("qc_hpa",  "as_qc",   "hPa"),
    ("a",       "isa_sound_speed", "m/s"),
    ("a_kt",    "isa_sound_speed", "kt"),
    ("rsigma",  "isa_rsigma",      "—"),
]


class AirspeedTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._row_ids = {}

        inp = ctk.CTkFrame(self)
        inp.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # --- radek 0: vyska + dISA --------------------------------------
        self.lbl_alt = ctk.CTkLabel(inp, font=theme.ui_font(14))
        self.lbl_alt.grid(row=0, column=0, padx=(12, 6), pady=(12, 4))
        self.alt_entry = ctk.CTkEntry(inp, width=140, font=("Consolas", 18), justify="right")
        self.alt_entry.grid(row=0, column=1, padx=6, pady=(12, 4))
        self.alt_entry.insert(0, "0")
        self.alt_entry.bind("<KeyRelease>", lambda e: self.recalc())

        self.alt_unit = ctk.CTkOptionMenu(inp, width=80, values=list(ALT_UNITS),
                                          command=lambda _: self.recalc())
        self.alt_unit.grid(row=0, column=2, padx=6, pady=(12, 4))

        self._alt_mode = "press"   # letove vysky jsou obvykle tlakove
        self.alt_type = ctk.CTkSegmentedButton(inp, command=self._on_alt_type)
        self.alt_type.grid(row=0, column=3, padx=(12, 6), pady=(12, 4))

        self.lbl_dt = ctk.CTkLabel(inp, font=theme.ui_font(14))
        self.lbl_dt.grid(row=0, column=4, padx=(24, 6), pady=(12, 4))
        self.dt_entry = ctk.CTkEntry(inp, width=80, font=("Consolas", 18), justify="right")
        self.dt_entry.grid(row=0, column=5, padx=6, pady=(12, 4))
        self.dt_entry.insert(0, "0")
        self.dt_entry.bind("<KeyRelease>", lambda e: self.recalc())

        # --- radek 1: rychlost -------------------------------------------
        self.lbl_speed = ctk.CTkLabel(inp, font=theme.ui_font(14))
        self.lbl_speed.grid(row=1, column=0, padx=(12, 6), pady=(4, 12))
        self.speed_entry = ctk.CTkEntry(inp, width=140, font=("Consolas", 18), justify="right")
        self.speed_entry.grid(row=1, column=1, padx=6, pady=(4, 12))
        self.speed_entry.insert(0, "100")
        self.speed_entry.bind("<KeyRelease>", lambda e: self.recalc())

        self.speed_unit = ctk.CTkOptionMenu(inp, width=80, values=list(SPEED_UNITS),
                                            command=lambda _: self.recalc())
        self.speed_unit.set("kt")
        self.speed_unit.grid(row=1, column=2, padx=6, pady=(4, 12))

        self.kind_menu = ctk.CTkOptionMenu(inp, width=100, values=KINDS,
                                           command=self._on_kind_change)
        self.kind_menu.set("CAS")
        self.kind_menu.grid(row=1, column=3, padx=(12, 6), pady=(4, 12))

        self.status = ctk.CTkLabel(inp, text="", text_color="gray60", anchor="w")
        self.status.grid(row=1, column=4, columnspan=2, padx=(24, 12),
                         pady=(4, 12), sticky="ew")
        inp.grid_columnconfigure(5, weight=1)

        self.note_label = ctk.CTkLabel(self, text_color="gray60", anchor="w",
                                       justify="left")
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

    # ------------------------------------------------------------------
    def _build_rows(self):
        for i, (key, lbl_key, unit) in enumerate(ROWS):
            tag = "odd" if i % 2 else "even"
            iid = self.table.insert("", "end",
                                    values=(i18n.t(lbl_key), "", unit),
                                    tags=(tag,))
            self._row_ids[key] = iid

    def _on_alt_type(self, value):
        self._alt_mode = "geom" if value == i18n.t("alt_type_geom") else "press"
        self.recalc()

    def _on_kind_change(self, value):
        if value == "Mach":
            self.speed_unit.set("—")
            self.speed_unit.configure(values=["—"], state="disabled")
        else:
            self.speed_unit.configure(values=list(SPEED_UNITS), state="normal")
            if self.speed_unit.get() == "—":
                self.speed_unit.set("kt")
        self.recalc()

    def refresh_lang(self):
        self.lbl_alt.configure(text=i18n.t("lbl_altitude"))
        self.lbl_dt.configure(text=i18n.t("lbl_delta_isa"))
        self.lbl_speed.configure(text=i18n.t("lbl_speed"))
        geom_lbl, press_lbl = i18n.t("alt_type_geom"), i18n.t("alt_type_press")
        self.alt_type.configure(values=[geom_lbl, press_lbl])
        self.alt_type.set(geom_lbl if self._alt_mode == "geom" else press_lbl)
        self.note_label.configure(text=i18n.t("as_note"))
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
        spd = self._parse(self.speed_entry)
        if alt is None or dt is None or spd is None:
            self._clear(i18n.t("isa_invalid"))
            return
        x = alt * ALT_UNITS[self.alt_unit.get()]
        try:
            atm = isa(x, dT=dt) if self._alt_mode == "geom" else isa_h(x, dT=dt)
        except ValueError as e:
            self._clear(i18n.err(e))
            return
        kind = self.kind_menu.get()
        value = spd if kind == "Mach" else spd * SPEED_UNITS[self.speed_unit.get()]
        try:
            r = speeds(atm, value, kind)
        except ValueError as e:
            self._clear(i18n.err(e))
            return
        self.status.configure(text="")
        vals = {
            "mach": r.mach,
            "tas": r.tas, "tas_kmh": r.tas * 3.6, "tas_kt": r.tas / _KT,
            "eas": r.eas, "eas_kmh": r.eas * 3.6, "eas_kt": r.eas / _KT,
            "cas": r.cas, "cas_kmh": r.cas * 3.6, "cas_kt": r.cas / _KT,
            "q": r.q, "q_psf": r.q / PSF,
            "qc": r.qc, "qc_hpa": r.qc / 100,
            "a": atm.a, "a_kt": atm.a / _KT,
            "rsigma": atm.sigma ** -0.5,
        }
        for key, v in vals.items():
            self.table.set(self._row_ids[key], "val", fmt(v))

    def _clear(self, msg):
        self.status.configure(text=msg)
        for iid in self._row_ids.values():
            self.table.set(iid, "val", "")
