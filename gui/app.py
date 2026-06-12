"""AE_UNITS - hlavni okno aplikace."""

import sys
from pathlib import Path

import customtkinter as ctk

from core import formatting, i18n
from core import settings as cfg
from gui import theme
from gui.tab_converter import ConverterTab
from gui.tab_solvers import SolversTab
from gui.tab_isa import IsaTab
from gui.tab_materials import MaterialsTab

APP_TITLE = "AE_UNITS"
VERSION = "0.31"

_FMT_KEYS = ["auto", "sci", "fixed"]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self._s = cfg.load()
        i18n.set_lang(self._s.get("lang", "cs"))
        ctk.set_appearance_mode("dark" if self._s["theme"] == i18n.t("theme_dark")
                                or self._s["theme"] == "Tmavý" else "light")
        ctk.set_default_color_theme("blue")
        formatting.set_format(mode=self._s["fmt_mode"],
                              digits=self._s["fmt_digits"])

        self.title(f"{APP_TITLE}  v{VERSION}")
        self._set_icon()
        self.geometry("1240x720")
        self.minsize(1000, 580)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        theme.apply_treeview_style(self)

        # --- toolbar -----------------------------------------------------
        bar = ctk.CTkFrame(self)
        bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 0))
        bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(bar, text="AE_UNITS",
                     font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, sticky="w", padx=12)

        self.fmt_label = ctk.CTkLabel(bar)
        self.fmt_label.grid(row=0, column=1, padx=(12, 4))
        self.fmt_menu = ctk.CTkOptionMenu(
            bar, width=190, command=self._on_format_change)
        self.fmt_menu.grid(row=0, column=2, padx=4, pady=8)

        self.digits_label = ctk.CTkLabel(bar)
        self.digits_label.grid(row=0, column=3, padx=(12, 4))
        self.digits_menu = ctk.CTkOptionMenu(
            bar, width=64, values=[str(i) for i in range(1, 13)],
            command=self._on_format_change)
        self.digits_menu.set(str(self._s["fmt_digits"]))
        self.digits_menu.grid(row=0, column=4, padx=4, pady=8)

        self.theme_switch = ctk.CTkSegmentedButton(
            bar, values=["Tmavý", "Světlý"], command=self._on_theme_change)
        self.theme_switch.grid(row=0, column=5, padx=(24, 8), pady=8)

        self.lang_switch = ctk.CTkSegmentedButton(
            bar, values=["EN", "CS"], command=self._on_lang_change, width=90)
        self.lang_switch.set(self._s.get("lang", "cs").upper())
        self.lang_switch.grid(row=0, column=6, padx=(8, 12), pady=8)

        # --- taby --------------------------------------------------------
        self.tabs = ctk.CTkTabview(self, anchor="nw")
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self._tab_names = ["tab_converter", "tab_solvers", "tab_isa", "tab_materials"]
        for key in self._tab_names:
            t = self.tabs.add(i18n.t(key))
            t.grid_columnconfigure(0, weight=1)
            t.grid_rowconfigure(0, weight=1)

        self.tab_converter = ConverterTab(self.tabs.tab(i18n.t("tab_converter")))
        self.tab_converter.grid(row=0, column=0, sticky="nsew")
        self.tab_solvers = SolversTab(self.tabs.tab(i18n.t("tab_solvers")))
        self.tab_solvers.grid(row=0, column=0, sticky="nsew")
        self.tab_isa = IsaTab(self.tabs.tab(i18n.t("tab_isa")))
        self.tab_isa.grid(row=0, column=0, sticky="nsew")
        self.tab_materials = MaterialsTab(self.tabs.tab(i18n.t("tab_materials")))
        self.tab_materials.grid(row=0, column=0, sticky="nsew")

        self._theme_aware  = [self.tab_converter, self.tab_solvers,
                               self.tab_isa, self.tab_materials]
        self._recalcable   = [self.tab_converter, self.tab_isa]
        self._lang_aware   = [self.tab_converter, self.tab_solvers,
                               self.tab_isa, self.tab_materials]

        self._refresh_toolbar_labels()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    def _refresh_toolbar_labels(self):
        lang = i18n.get_lang()
        self.fmt_label.configure(text=i18n.t("fmt_label"))
        self.digits_label.configure(text=i18n.t("digits_label"))
        # theme prepinac - hodnoty jsou lokalizovane labely
        dark_lbl  = i18n.t("theme_dark")
        light_lbl = i18n.t("theme_light")
        self.theme_switch.configure(values=[dark_lbl, light_lbl])
        saved_theme = self._s["theme"]
        # normalizace: "Tmavý"/"Dark" -> dark_lbl, "Světlý"/"Light" -> light_lbl
        is_dark = saved_theme in ("Tmavý", "Dark", dark_lbl)
        self.theme_switch.set(dark_lbl if is_dark else light_lbl)
        # format menu
        labels = [i18n.t(f"fmt_{k}") for k in _FMT_KEYS]
        self.fmt_menu.configure(values=labels)
        self.fmt_menu.set(i18n.t(f"fmt_{self._s['fmt_mode']}"))

    def _on_format_change(self, _value=None):
        label = self.fmt_menu.get()
        key = next((k for k in _FMT_KEYS if i18n.t(f"fmt_{k}") == label), "auto")
        digits = int(self.digits_menu.get())
        formatting.set_format(mode=key, digits=digits)
        self._s["fmt_mode"]   = key
        self._s["fmt_digits"] = digits
        for tab in self._recalcable:
            tab.recalc()

    def _on_theme_change(self, value):
        is_dark = value == i18n.t("theme_dark")
        ctk.set_appearance_mode("dark" if is_dark else "light")
        self._s["theme"] = "Tmavý" if is_dark else "Světlý"
        theme.apply_treeview_style(self)
        for tab in self._theme_aware:
            tab.apply_theme()

    def _on_lang_change(self, value):
        lang = value.lower()
        i18n.set_lang(lang)
        self._s["lang"] = lang
        # prejmenovani tabu
        for key in self._tab_names:
            old = self.tabs._tab_dict  # type: ignore[attr-defined]
            # CTkTabview nema verejne rename API; pouzijeme interni metodu
            try:
                self.tabs.rename(self._tab_key_to_current(key), i18n.t(key))
            except Exception:
                pass
        self._refresh_toolbar_labels()
        theme.apply_treeview_style(self)
        for tab in self._lang_aware:
            tab.refresh_lang()
        for tab in self._recalcable:
            tab.recalc()

    def _tab_key_to_current(self, key: str) -> str:
        """Vrati aktualni (pred prekladem) nazev tabu — zjisti ho z existujicich tabu."""
        for name in self.tabs._tab_dict:  # type: ignore[attr-defined]
            if name == i18n.t(key):
                return name
        # fallback: zkus oba jazyky
        from lang import cs, en
        for d in (cs.STRINGS, en.STRINGS):
            candidate = d.get(key, "")
            if candidate in self.tabs._tab_dict:  # type: ignore[attr-defined]
                return candidate
        return i18n.t(key)

    def _set_icon(self):
        if getattr(sys, "frozen", False):
            base = Path(sys._MEIPASS)
        else:
            base = Path(__file__).parent.parent
        ico = base / "icon.ico"
        if ico.exists():
            self.iconbitmap(str(ico))

    def _on_close(self):
        cfg.save(self._s)
        self.destroy()


def run():
    App().mainloop()
