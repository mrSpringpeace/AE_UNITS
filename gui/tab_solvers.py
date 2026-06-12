"""Tab konzistentnich jednotkovych systemu pro FEM/CFD resice."""

from tkinter import ttk

import customtkinter as ctk

from data.solver_systems import SOLVERS
from core import i18n
from gui import theme


class SolversTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._current_solver = list(SOLVERS.keys())[0]

        self.selector = ctk.CTkSegmentedButton(
            self, values=list(SOLVERS.keys()), command=self.select_solver,
            font=("Segoe UI", 14))
        self.selector.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.note_label = ctk.CTkLabel(
            self, text="", anchor="w", justify="left", wraplength=950,
            text_color=("gray25", "gray75"), font=("Segoe UI", 13))
        self.note_label.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 10))

        self.table = ttk.Treeview(self, style="AE.Treeview", show="headings",
                                  selectmode="browse")
        self.table.grid(row=2, column=0, sticky="nsew")

        self.selector.set(self._current_solver)
        self.select_solver(self._current_solver)

    def apply_theme(self):
        theme.zebra(self.table)
        self._repaint_sep()

    def refresh_lang(self):
        self.select_solver(self._current_solver)

    def select_solver(self, name):
        self._current_solver = name
        data = SOLVERS[name]
        lang = i18n.get_lang()
        note = data.get("note_en", data["note"]) if lang == "en" else data["note"]
        self.note_label.configure(text=note)

        systems = data["systems"]
        rows = data.get("rows_en", data["rows"]) if lang == "en" else data["rows"]

        cols = ["quantity"] + [f"sys{i}" for i in range(len(systems))]
        self.table.delete(*self.table.get_children())
        self.table["columns"] = cols
        self.table.heading("quantity", text=i18n.t("solver_col_qty"), anchor="w")
        self.table.column("quantity", width=240, stretch=False, anchor="w")
        for i, sys_name in enumerate(systems):
            self.table.heading(f"sys{i}", text=sys_name, anchor="w")
            self.table.column(f"sys{i}", width=210, stretch=True, anchor="w")

        for i, row in enumerate(rows):
            is_sep = row[0].startswith("—")
            tag = "sep" if is_sep else ("odd" if i % 2 else "even")
            # Pokud neni rows_en, preloz prvni sloupec pres QUANTITY_MAP
            if lang == "en" and "rows_en" not in data:
                row = (i18n.qty(row[0]),) + row[1:]
            self.table.insert("", "end", values=row, tags=(tag,))

        theme.zebra(self.table)
        self._repaint_sep()

    def _repaint_sep(self):
        p = theme.palette()
        self.table.tag_configure("sep", background=p["bg_head"],
                                 foreground=p["fg_dim"])
