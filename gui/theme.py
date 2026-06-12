"""Barevne palety pro nativni Tk widgety (Listbox, Treeview) sladene
s CustomTkinter temateme "blue" - vcetne prepinani tmavy/svetly rezim."""

from tkinter import ttk

import customtkinter as ctk

PALETTES = {
    "dark": {
        "bg": "#2b2b2b",
        "bg_odd": "#313131",
        "bg_head": "#333333",
        "fg": "#dce4ee",
        "fg_dim": "#9a9a9a",
        "accent": "#1f6aa5",
    },
    "light": {
        "bg": "#f4f4f4",
        "bg_odd": "#e9e9e9",
        "bg_head": "#dcdcdc",
        "fg": "#1a1a1a",
        "fg_dim": "#666666",
        "accent": "#3a7ebf",
    },
}


def palette() -> dict:
    mode = "dark" if ctk.get_appearance_mode() == "Dark" else "light"
    return PALETTES[mode]


def apply_treeview_style(root):
    """Nastavi/aktualizuje sdileny styl AE.Treeview podle aktualniho rezimu."""
    p = palette()
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("AE.Treeview", background=p["bg"], fieldbackground=p["bg"],
                    foreground=p["fg"], rowheight=30, borderwidth=0,
                    font=("Segoe UI", 12))
    style.configure("AE.Treeview.Heading", background=p["bg_head"],
                    foreground=p["fg"], borderwidth=0,
                    font=("Segoe UI", 11, "bold"))
    style.map("AE.Treeview.Heading", background=[("active", p["bg_head"])])
    style.map("AE.Treeview",
              background=[("selected", p["accent"])],
              foreground=[("selected", "white")])


def style_listbox(lb):
    """Prebarvi tk.Listbox podle aktualniho rezimu."""
    p = palette()
    lb.configure(bg=p["bg"], fg=p["fg"], selectbackground=p["accent"],
                 selectforeground="white")


def zebra(tree):
    """Aktualizuje zebrovani radku Treeview podle aktualniho rezimu."""
    p = palette()
    tree.tag_configure("even", background=p["bg"])
    tree.tag_configure("odd", background=p["bg_odd"])
