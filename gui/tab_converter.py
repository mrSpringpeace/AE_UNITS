"""Tab prevodniku jednotek."""

import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

from core.units import CATEGORIES, convert
from core.formatting import fmt
from core import i18n
from gui import theme


class ConverterTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.category = CATEGORIES[0]
        self._row_ids = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- leva lista kategorii ---------------------------------------
        self.cat_list = tk.Listbox(
            self, width=26, font=("Segoe UI", 12),
            activestyle="none", borderwidth=0, highlightthickness=0,
            exportselection=False)
        self.cat_list.grid(row=0, column=0, sticky="nsw", padx=(0, 12))
        self._fill_cat_list()
        self.cat_list.bind("<<ListboxSelect>>", self._on_category_click)

        # --- prava cast -----------------------------------------------
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(2, weight=1)

        conv = ctk.CTkFrame(right)
        conv.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        conv.grid_columnconfigure(0, weight=2)
        conv.grid_columnconfigure(4, weight=2)

        self.entry = ctk.CTkEntry(conv, font=("Consolas", 20), justify="right")
        self.entry.grid(row=0, column=0, sticky="ew", padx=(12, 6), pady=12)
        self.entry.insert(0, "1")
        self.entry.bind("<KeyRelease>", lambda e: self.recalc())

        self.from_menu = ctk.CTkOptionMenu(conv, width=130, command=lambda _: self.recalc())
        self.from_menu.grid(row=0, column=1, padx=6, pady=12)

        self.swap_btn = ctk.CTkButton(conv, text="⇄", width=44, command=self.swap)
        self.swap_btn.grid(row=0, column=2, padx=6, pady=12)

        self.result_var = tk.StringVar()
        self.result_entry = ctk.CTkEntry(
            conv, font=("Consolas", 20, "bold"), justify="right",
            textvariable=self.result_var, state="readonly")
        self.result_entry.grid(row=0, column=4, sticky="ew", padx=6, pady=12)

        self.to_menu = ctk.CTkOptionMenu(conv, width=130, command=lambda _: self.recalc())
        self.to_menu.grid(row=0, column=5, padx=(6, 12), pady=12)

        self.copy_btn = ctk.CTkButton(conv, width=88, command=self.copy_result)
        self.copy_btn.grid(row=0, column=6, padx=(0, 12), pady=12)

        self.desc_label = ctk.CTkLabel(right, text="", text_color="gray60", anchor="w")
        self.desc_label.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 8))

        self.table = ttk.Treeview(
            right, columns=("sym", "val", "name"), show="headings",
            style="AE.Treeview", selectmode="browse")
        self.table.column("sym",  width=120, stretch=False, anchor="w")
        self.table.column("val",  width=220, stretch=False, anchor="e")
        self.table.column("name", width=320, stretch=True,  anchor="w")
        self.table.grid(row=2, column=0, sticky="nsew")
        self.table.bind("<Double-1>", self._copy_row)

        self.apply_theme()
        self.cat_list.selection_set(0)
        self.select_category(self.category)
        self.refresh_lang()

    # ------------------------------------------------------------------
    def refresh_lang(self):
        self.copy_btn.configure(text=i18n.t("btn_copy"))
        self.table.heading("sym",  text=i18n.t("col_unit"),  anchor="w")
        self.table.heading("val",  text=i18n.t("col_value"), anchor="e")
        self.table.heading("name", text=i18n.t("col_desc"),  anchor="w")
        self._fill_cat_list()
        self._update_desc()
        self.refill_table()

    def _fill_cat_list(self):
        sel = self.cat_list.curselection()
        self.cat_list.delete(0, "end")
        for cat in CATEGORIES:
            self.cat_list.insert("end", f"  {i18n.cname(cat)}")
        if sel:
            self.cat_list.selection_set(sel[0])

    def apply_theme(self):
        theme.style_listbox(self.cat_list)
        theme.zebra(self.table)

    def _on_category_click(self, _event):
        sel = self.cat_list.curselection()
        if sel:
            self.select_category(CATEGORIES[sel[0]])

    def select_category(self, cat):
        self.category = cat
        symbols = [u.symbol for u in cat.units]
        self.from_menu.configure(values=symbols)
        self.to_menu.configure(values=symbols)
        self.from_menu.set(symbols[0])
        self.to_menu.set(symbols[1] if len(symbols) > 1 else symbols[0])
        self.table.delete(*self.table.get_children())
        self._row_ids = []
        for i, u in enumerate(cat.units):
            tag = "odd" if i % 2 else "even"
            iid = self.table.insert("", "end",
                                    values=(u.symbol, "", i18n.uname(u)),
                                    tags=(tag,))
            self._row_ids.append(iid)
        self.recalc()

    def refill_table(self):
        """Aktualizuje nazvy jednotek v tabulce (po zmene jazyka)."""
        for iid, u in zip(self._row_ids, self.category.units):
            self.table.set(iid, "name", i18n.uname(u))

    def swap(self):
        a, b = self.from_menu.get(), self.to_menu.get()
        self.from_menu.set(b)
        self.to_menu.set(a)
        self.recalc()

    def copy_result(self):
        txt = self.result_var.get()
        if txt and txt != "—":
            self.clipboard_clear()
            self.clipboard_append(txt)
            self._flash(f"{i18n.t('copied')} {txt}")

    def _copy_row(self, event):
        iid = self.table.identify_row(event.y)
        if not iid:
            return
        val = self.table.set(iid, "val")
        if val:
            self.clipboard_clear()
            self.clipboard_append(val)
            self._flash(f"{i18n.t('copied')} {val} {self.table.set(iid, 'sym')}")

    def _flash(self, msg):
        self.desc_label.configure(text=msg)
        self.after(1800, self._update_desc)

    def _update_desc(self):
        cat = self.category
        f_sym, t_sym = self.from_menu.get(), self.to_menu.get()
        fu, tu = cat.unit(f_sym), cat.unit(t_sym)
        self.desc_label.configure(
            text=f"{f_sym} = {i18n.uname(fu)}     →     {t_sym} = {i18n.uname(tu)}")

    def parse_input(self):
        txt = self.entry.get().strip().replace(",", ".").replace(" ", "")
        if not txt:
            return None
        try:
            return float(txt)
        except ValueError:
            return None

    def recalc(self):
        val = self.parse_input()
        f_sym = self.from_menu.get()
        self._update_desc()
        if val is None:
            self.result_var.set("—")
            for iid in self._row_ids:
                self.table.set(iid, "val", "")
            return
        res = convert(self.category, val, f_sym, self.to_menu.get())
        self.result_var.set(fmt(res))
        for iid, u in zip(self._row_ids, self.category.units):
            self.table.set(iid, "val", fmt(convert(self.category, val, f_sym, u.symbol)))
