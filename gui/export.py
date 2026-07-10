"""Export ttk.Treeview tabulek do CSV souboru nebo schranky.

CSV: oddelovac ';' a UTF-8 s BOM, aby soubor rovnou otevrela
ceska Excel instalace. Schranka: TSV (vlozitelne do Excelu).
"""

import csv
from tkinter import filedialog


def _rows(tree) -> list:
    cols = list(tree["columns"])
    out = [[tree.heading(c)["text"] for c in cols]]
    for iid in tree.get_children():
        out.append([tree.set(iid, c) for c in cols])
    return out


def copy_to_clipboard(widget, tree) -> int:
    """Zkopiruje celou tabulku do schranky jako TSV. Vraci pocet radku."""
    rows = _rows(tree)
    widget.clipboard_clear()
    widget.clipboard_append("\r\n".join("\t".join(r) for r in rows))
    return len(rows) - 1


def save_csv(tree, title: str, default_name: str):
    """Dialog + zapis CSV. Vraci cestu, nebo None pri zruseni."""
    path = filedialog.asksaveasfilename(
        title=title, defaultextension=".csv", initialfile=default_name,
        filetypes=[("CSV", "*.csv"), ("*", "*.*")])
    if not path:
        return None
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f, delimiter=";").writerows(_rows(tree))
    return path
