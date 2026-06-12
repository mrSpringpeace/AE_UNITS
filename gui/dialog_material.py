"""Dialog pro pridani / editaci materialu."""

import customtkinter as ctk
from core import i18n

# (i18n klic, interni klic, typ, optional)
_FIELDS = [
    ("dlg_f_name", "name", str,   False),
    ("dlg_f_rho",  "rho",  float, False),
    ("dlg_f_E",    "E",    float, False),
    ("dlg_f_nu",   "nu",   float, True),
    ("dlg_f_ftu",  "ftu",  float, False),
    ("dlg_f_fty",  "fty",  float, True),
    ("dlg_f_note", "note", str,   True),
]


class MaterialDialog(ctk.CTkToplevel):
    def __init__(self, master, prefill: tuple = None):
        super().__init__(master)
        self.title(i18n.t("dlg_add_title") if prefill is None
                   else i18n.t("dlg_edit_title"))
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        self._entries = {}
        for i, (lbl_key, key, typ, optional) in enumerate(_FIELDS):
            ctk.CTkLabel(self, text=i18n.t(lbl_key), anchor="e", width=140).grid(
                row=i, column=0, padx=(16, 8), pady=6, sticky="e")
            e = ctk.CTkEntry(self, width=240)
            e.grid(row=i, column=1, padx=(0, 16), pady=6)
            self._entries[key] = (e, typ, optional)

        if prefill:
            vals = {"name": prefill[0], "rho": prefill[1], "E": prefill[2],
                    "nu": prefill[3], "ftu": prefill[4], "fty": prefill[5],
                    "note": prefill[6]}
            for key, (e, typ, _) in self._entries.items():
                v = vals.get(key)
                if v is not None:
                    e.insert(0, str(v))

        self._err = ctk.CTkLabel(self, text="", text_color="red", anchor="w")
        self._err.grid(row=len(_FIELDS), column=0, columnspan=2,
                       padx=16, pady=(4, 0), sticky="w")

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.grid(row=len(_FIELDS) + 1, column=0, columnspan=2, pady=(8, 14))
        ctk.CTkButton(btns, text=i18n.t("dlg_btn_save"), width=100,
                      command=self._submit).pack(side="left", padx=8)
        ctk.CTkButton(btns, text=i18n.t("dlg_btn_cancel"), width=100,
                      fg_color="gray40",
                      command=self.destroy).pack(side="left", padx=8)

        self.bind("<Return>", lambda e: self._submit())
        self.bind("<Escape>", lambda e: self.destroy())
        self._entries["name"][0].focus_set()
        self.after(50, self._center)

    def _center(self):
        self.update_idletasks()
        master = self.master
        x = master.winfo_x() + (master.winfo_width()  - self.winfo_width())  // 2
        y = master.winfo_y() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _submit(self):
        values = {}
        for key, (e, typ, optional) in self._entries.items():
            raw = e.get().strip().replace(",", ".")
            if not raw:
                if not optional:
                    self._err.configure(text=i18n.t("dlg_err_required", key=key))
                    return
                values[key] = None
            else:
                try:
                    values[key] = typ(raw)
                except ValueError:
                    self._err.configure(text=i18n.t("dlg_err_invalid", key=key))
                    return
        self.result = (values["name"], values["rho"], values["E"], values["nu"],
                       values["ftu"], values["fty"], values["note"] or "")
        self.destroy()
