"""Tab orientacni tabulky leteckych materialu."""

from pathlib import Path
from tkinter import filedialog, messagebox
from tkinter import ttk

import customtkinter as ctk

from data.materials import (MATERIALS, KG_M3_TO_LB_IN3, GPA_TO_MSI, MPA_TO_KSI,
                            mat_name, mat_note)
from core import user_materials as um
from core import i18n
from gui import theme
from gui.dialog_material import MaterialDialog

# (key, cs_header, width, anchor)
_COLS = [
    ("name",    "Materiál",   260, "w"),
    ("rho",     "ρ [kg/m³]",   90, "e"),
    ("rho_us",  "ρ [lb/in³]",  90, "e"),
    ("E",       "E [GPa]",     80, "e"),
    ("E_us",    "E [Msi]",     80, "e"),
    ("nu",      "ν [—]",       60, "e"),
    ("ftu",     "Ftu [MPa]",   90, "e"),
    ("ftu_us",  "Ftu [ksi]",   80, "e"),
    ("fty",     "Fty [MPa]",   90, "e"),
    ("fty_us",  "Fty [ksi]",   80, "e"),
    ("note",    "Poznámka",   260, "w"),
]


def _row_values(name: str, rho, E, nu, ftu, fty, note: str):
    return (
        name,
        f"{rho:g}",
        f"{rho * KG_M3_TO_LB_IN3:.4f}",
        f"{E:g}",
        f"{E * GPA_TO_MSI:.2f}",
        f"{nu:g}" if nu is not None else "—",
        f"{ftu:g}",
        f"{ftu * MPA_TO_KSI:.1f}",
        f"{fty:g}" if fty is not None else "—",
        f"{fty * MPA_TO_KSI:.1f}" if fty is not None else "—",
        note,
    )


class MaterialsTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._user_mats: list[tuple] = self._load_default()
        # iid -> ("user", index) | ("builtin", index)
        self._iid_map: dict[str, tuple] = {}

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        self.lbl_search = ctk.CTkLabel(top, font=theme.ui_font(13))
        self.lbl_search.pack(side="left", padx=(4, 6))
        self.search = ctk.CTkEntry(top, width=220)
        self.search.pack(side="left")
        self.search.bind("<KeyRelease>", lambda e: self.refill())

        self.btn_add    = ctk.CTkButton(top, width=148, command=self._add)
        self.btn_edit   = ctk.CTkButton(top, width=90, fg_color="gray40", command=self._edit)
        self.btn_delete = ctk.CTkButton(top, width=90, fg_color="#8B2020",
                                        hover_color="#6B1010", command=self._delete)
        self.btn_load   = ctk.CTkButton(top, width=148, command=self._load_lib)
        self.btn_save   = ctk.CTkButton(top, width=148, fg_color="gray40",
                                        command=self._save_lib)
        for btn, pad in ((self.btn_add, (16, 4)), (self.btn_edit, (4, 4)),
                         (self.btn_delete, (4, 4)), (self.btn_load, (24, 4)),
                         (self.btn_save, (4, 4))):
            btn.pack(side="left", padx=pad)

        self.disclaimer_lbl = ctk.CTkLabel(
            self, text="", text_color="gray60", anchor="w",
            justify="left", wraplength=1000)
        self.disclaimer_lbl.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 6))

        self.table = ttk.Treeview(
            self, columns=[c[0] for c in _COLS], show="headings",
            style="AE.Treeview", selectmode="browse")
        for key, _, width, anchor in _COLS:
            self.table.column(key, width=width, anchor=anchor,
                              stretch=(key in ("name", "note")))
        self.table.grid(row=2, column=0, sticky="nsew")

        self.apply_theme()
        self.refresh_lang()
        self.refill()

    # ------------------------------------------------------------------
    def _load_default(self) -> list[tuple]:
        try:
            return um.load()
        except um.UserMaterialsError as e:
            # nespadnout pri startu; prazdna knihovna + upozorneni po UI
            err = str(e)
            self.after(200, lambda err=err: messagebox.showwarning(
                i18n.t("mat_load_error"),
                i18n.t("mat_load_corrupt", err=err)))
            return []

    def refresh_lang(self):
        self.lbl_search.configure(text=i18n.t("lbl_search"))
        self.btn_add.configure(text=i18n.t("btn_add_mat"))
        self.btn_edit.configure(text=i18n.t("btn_edit"))
        self.btn_delete.configure(text=i18n.t("btn_delete"))
        self.btn_load.configure(text=i18n.t("btn_load_lib"))
        self.btn_save.configure(text=i18n.t("btn_save_lib"))
        self.disclaimer_lbl.configure(text=i18n.t("mat_disclaimer"))
        for key, base_header, _, anchor in _COLS:
            if key == "name":
                self.table.heading(key, text=i18n.t("col_material"), anchor=anchor)
            elif key == "note":
                self.table.heading(key, text=i18n.t("col_note"), anchor=anchor)
            else:
                self.table.heading(key, text=base_header, anchor=anchor)
        self.refill()

    def apply_theme(self):
        theme.zebra(self.table)
        p = theme.palette()
        self.table.tag_configure("user", background=p["accent"], foreground="white")
        self.table.tag_configure("builtin", background=p["bg"])

    def _selected_user_idx(self):
        sel = self.table.selection()
        if not sel:
            return None
        iid = sel[0]
        info = self._iid_map.get(iid)
        if info is None or info[0] != "user":
            messagebox.showinfo("AE_UNITS", i18n.t("mat_only_user"))
            return None
        return info[1]

    def _name_taken(self, name: str, exclude_idx: int | None = None) -> bool:
        for i, m in enumerate(self._user_mats):
            if exclude_idx is not None and i == exclude_idx:
                continue
            if m[1] == name:
                return True
        return False

    def _persist(self) -> bool:
        try:
            um.save(self._user_mats)
            return True
        except OSError as e:
            messagebox.showerror(i18n.t("mat_save_error"), str(e))
            return False

    def _add(self):
        dlg = MaterialDialog(self.winfo_toplevel())
        self.wait_window(dlg)
        if not dlg.result:
            return
        name, rho, E, nu, ftu, fty, note = dlg.result
        if self._name_taken(name):
            messagebox.showwarning("AE_UNITS", i18n.t("mat_dup_name", name=name))
            return
        self._user_mats.append(um.make(name, rho, E, nu, ftu, fty, note))
        if self._persist():
            self.refill()

    def _edit(self):
        idx = self._selected_user_idx()
        if idx is None:
            return
        dlg = MaterialDialog(self.winfo_toplevel(), prefill=self._user_mats[idx])
        self.wait_window(dlg)
        if not dlg.result:
            return
        name, rho, E, nu, ftu, fty, note = dlg.result
        if self._name_taken(name, exclude_idx=idx):
            messagebox.showwarning("AE_UNITS", i18n.t("mat_dup_name", name=name))
            return
        mid = self._user_mats[idx][0]
        self._user_mats[idx] = um.make(name, rho, E, nu, ftu, fty, note, mid=mid)
        if self._persist():
            self.refill()

    def _delete(self):
        idx = self._selected_user_idx()
        if idx is None:
            return
        name = self._user_mats[idx][1]
        if not messagebox.askyesno(i18n.t("mat_delete_title"),
                                   i18n.t("mat_delete_confirm", name=name)):
            return
        self._user_mats.pop(idx)
        if self._persist():
            self.refill()

    def _load_lib(self):
        path = filedialog.askopenfilename(
            title=i18n.t("mat_load_title"),
            filetypes=[("JSON", "*.json"), ("*", "*.*")])
        if not path:
            return
        try:
            imported = um.load(Path(path))
        except um.UserMaterialsError as e:
            messagebox.showerror(i18n.t("mat_load_error"),
                                 i18n.t("mat_load_corrupt", err=e))
            return
        except OSError as e:
            messagebox.showerror(i18n.t("mat_load_error"), str(e))
            return
        if not imported:
            messagebox.showwarning(i18n.t("mat_load_empty"),
                                   i18n.t("mat_load_empty_msg"))
            return
        existing = {m[1] for m in self._user_mats}
        new = [m for m in imported if m[1] not in existing]
        self._user_mats.extend(new)
        if self._persist():
            self.refill()
            messagebox.showinfo(i18n.t("mat_loaded"),
                                i18n.t("mat_loaded_msg",
                                       added=len(new),
                                       skipped=len(imported) - len(new)))

    def _save_lib(self):
        if not self._user_mats:
            messagebox.showinfo(i18n.t("mat_empty_lib"),
                                i18n.t("mat_empty_lib_msg"))
            return
        path = filedialog.asksaveasfilename(
            title=i18n.t("mat_save_title"),
            defaultextension=".json",
            filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            um.save(self._user_mats, Path(path))
            messagebox.showinfo(i18n.t("mat_saved"),
                                i18n.t("mat_saved_msg", n=len(self._user_mats)))
        except OSError as e:
            messagebox.showerror(i18n.t("mat_save_error"), str(e))

    def refill(self):
        needle = self.search.get().strip().lower()
        lang = i18n.get_lang()
        self.table.delete(*self.table.get_children())
        self._iid_map.clear()
        p = theme.palette()

        for i, m in enumerate(self._user_mats):
            # (id, name, rho, E, nu, ftu, fty, note)
            mid, name, rho, E, nu, ftu, fty, note = m
            if needle and needle not in name.lower() and needle not in note.lower():
                continue
            iid = f"u{mid}"
            self.table.insert("", "end", iid=iid,
                              values=_row_values(name, rho, E, nu, ftu, fty, note),
                              tags=("user",))
            self._iid_map[iid] = ("user", i)

        bi = 0
        for i, m in enumerate(MATERIALS):
            name = mat_name(m, lang)
            note = mat_note(m, lang)
            rho, E, nu, ftu, fty = m[1], m[2], m[3], m[4], m[5]
            if needle and needle not in name.lower() and needle not in note.lower() \
                    and needle not in m[0].lower() and needle not in m[6].lower():
                continue
            tag = "odd" if bi % 2 else "even"
            iid = f"b{i}"
            self.table.insert("", "end", iid=iid,
                              values=_row_values(name, rho, E, nu, ftu, fty, note),
                              tags=(tag, "builtin"))
            self._iid_map[iid] = ("builtin", i)
            bi += 1

        theme.zebra(self.table)
        self.table.tag_configure("user", background=p["accent"], foreground="white")
