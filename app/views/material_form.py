"""Форма добавления / редактирования материала."""

import tkinter as tk
from tkinter import ttk, messagebox

import psycopg2

from .. import dal

BG, ACCENT, FONT = "#FFFFFF", "#D32B39", "Verdana"

# поля: ключ, подпись, начальное значение
FIELDS = [
    ("name",    "Наименование *",           ""),
    ("type",    "Тип материала *",          ""),
    ("stock",   "Количество на складе *",   "0"),
    ("min",     "Минимальное количество *", "0"),
    ("price",   "Цена за единицу *",        "0.00"),
    ("package", "Количество в упаковке *",  "1"),
    ("unit",    "Единица измерения *",      "шт"),
]


class MaterialForm(tk.Toplevel):
    def __init__(self, parent, material_id=None, on_close=None):
        super().__init__(parent)
        self.material_id = material_id
        self.on_close_cb = on_close
        self.title("Редактирование материала" if material_id else "Новый материал")
        self.geometry("550x600")
        self.configure(bg=BG)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._close)

        self.material_types = dal.fetch_material_types()
        self.all_suppliers = dal.fetch_all_suppliers()
        self.image_filename = None
        self.supplier_ids = []
        self.vars = {k: tk.StringVar(value=v) for k, _, v in FIELDS}

        self._build()
        if self.material_id:
            self._load()

    def _build(self):
        f = tk.Frame(self, bg=BG, padx=20, pady=15)
        f.pack(fill=tk.BOTH, expand=True)

        # Поля
        for i, (key, label, _) in enumerate(FIELDS):
            tk.Label(f, text=label, font=(FONT, 10), bg=BG).grid(
                row=i, column=0, sticky="w", pady=2)
            if key == "type":
                w = ttk.Combobox(f, textvariable=self.vars[key],
                                 values=[t["name"] for t in self.material_types],
                                 state="readonly", font=(FONT, 10), width=30)
            else:
                w = tk.Entry(f, textvariable=self.vars[key], font=(FONT, 10),
                             relief=tk.SOLID, bd=1, width=32)
            w.grid(row=i, column=1, sticky="we", pady=2, padx=(10, 0))

        # Описание
        tk.Label(f, text="Описание", font=(FONT, 10), bg=BG).grid(
            row=len(FIELDS), column=0, sticky="nw", pady=2)
        self.descr = tk.Text(f, height=4, font=(FONT, 10),
                             relief=tk.SOLID, bd=1, width=32)
        self.descr.grid(row=len(FIELDS), column=1, sticky="we",
                        pady=2, padx=(10, 0))

        # Поставщики
        r = len(FIELDS) + 1
        tk.Label(f, text="Поставщики", font=(FONT, 10, "bold"), bg=BG).grid(
            row=r, column=0, columnspan=2, sticky="w", pady=(15, 4))

        self.add_sup = tk.StringVar()
        sup_box = tk.Frame(f, bg=BG)
        sup_box.grid(row=r + 1, column=0, columnspan=2, sticky="we")
        ttk.Combobox(sup_box, textvariable=self.add_sup,
                     values=[s["name"] for s in self.all_suppliers],
                     font=(FONT, 9), width=30).pack(side=tk.LEFT)
        tk.Button(sup_box, text="+", width=3, bg=ACCENT, fg="white",
                  relief=tk.FLAT, command=self._add_sup).pack(
            side=tk.LEFT, padx=4)

        self.sup_lb = tk.Listbox(f, height=4, font=(FONT, 9),
                                 relief=tk.SOLID, bd=1)
        self.sup_lb.grid(row=r + 2, column=0, columnspan=2, sticky="we", pady=(4, 0))
        tk.Button(f, text="Удалить выбранного", font=(FONT, 9), relief=tk.FLAT,
                  command=self._remove_sup).grid(
            row=r + 3, column=0, columnspan=2, sticky="w", pady=4)

        f.grid_columnconfigure(1, weight=1)

        # Кнопки
        btns = tk.Frame(self, bg=BG, padx=20, pady=10)
        btns.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Button(btns, text="Сохранить", font=(FONT, 10, "bold"),
                  bg=ACCENT, fg="white", relief=tk.FLAT, padx=20, pady=5,
                  command=self._save).pack(side=tk.RIGHT)
        tk.Button(btns, text="Отмена", font=(FONT, 10), relief=tk.FLAT,
                  padx=20, pady=5, command=self._close).pack(
            side=tk.RIGHT, padx=(0, 8))
        if self.material_id:
            tk.Button(btns, text="Удалить", font=(FONT, 10), bg="#888",
                      fg="white", relief=tk.FLAT, padx=20, pady=5,
                      command=self._delete).pack(side=tk.LEFT)

    def _load(self):
        m = dal.get_material(self.material_id)
        if m is None:
            messagebox.showerror("Не найдено", "Материал не существует.", parent=self)
            self._close()
            return
        # ключ в self.vars -> ключ в m
        mp = {"name": "name", "type": "material_type_name",
              "stock": "stock_quantity", "min": "min_quantity",
              "price": "price", "package": "package_quantity", "unit": "unit"}
        for k, mk in mp.items():
            self.vars[k].set(str(m[mk]))
        if m.get("description"):
            self.descr.insert("1.0", m["description"])
        self.image_filename = m.get("image_path")
        self.supplier_ids = list(m.get("supplier_ids", []))
        self._refresh_sup()

    def _refresh_sup(self):
        self.sup_lb.delete(0, tk.END)
        names = {s["id"]: s["name"] for s in self.all_suppliers}
        for sid in self.supplier_ids:
            self.sup_lb.insert(tk.END, names.get(sid, "?"))

    def _add_sup(self):
        sup = next((s for s in self.all_suppliers
                    if s["name"] == self.add_sup.get().strip()), None)
        if sup is None:
            messagebox.showwarning("Не найден",
                                   "Выберите поставщика из списка.", parent=self)
            return
        if sup["id"] not in self.supplier_ids:
            self.supplier_ids.append(sup["id"])
            self._refresh_sup()
        self.add_sup.set("")

    def _remove_sup(self):
        sel = self.sup_lb.curselection()
        if sel:
            self.supplier_ids.pop(sel[0])
            self._refresh_sup()

    def _save(self):
        v = {k: self.vars[k].get().strip() for k in self.vars}
        if not v["name"]:
            return messagebox.showerror("Ошибка", "Введите наименование.", parent=self)
        if not v["type"]:
            return messagebox.showerror("Ошибка", "Выберите тип материала.", parent=self)
        try:
            stock, min_q = int(v["stock"] or 0), int(v["min"] or 0)
            pack, price = int(v["package"] or 1), float(v["price"] or 0)
        except ValueError:
            return messagebox.showerror("Ошибка",
                                        "Числовые поля заполнены некорректно.",
                                        parent=self)
        if min(stock, min_q, price) < 0 or pack <= 0:
            return messagebox.showerror("Ошибка",
                                        "Цена и количество не могут быть отрицательными, "
                                        "упаковка > 0.", parent=self)
        type_id = next((t["id"] for t in self.material_types
                        if t["name"] == v["type"]), None)
        data = {
            "name": v["name"], "material_type_id": type_id,
            "image_path": self.image_filename, "price": price,
            "stock_quantity": stock, "min_quantity": min_q,
            "package_quantity": pack, "unit": v["unit"] or "шт",
            "description": self.descr.get("1.0", tk.END).strip() or None,
        }
        try:
            dal.save_material(data, self.supplier_ids, self.material_id)
        except Exception as e:
            return messagebox.showerror("Ошибка БД", str(e), parent=self)
        self._close()

    def _delete(self):
        if not messagebox.askyesno("Подтверждение", "Удалить материал?", parent=self):
            return
        try:
            dal.delete_material(self.material_id)
        except psycopg2.errors.ForeignKeyViolation:
            return messagebox.showerror("Удаление невозможно",
                                        "Материал используется в продукции.",
                                        parent=self)
        except Exception as e:
            return messagebox.showerror("Ошибка БД", str(e), parent=self)
        self._close()

    def _close(self):
        if self.on_close_cb:
            self.on_close_cb()
        self.destroy()
