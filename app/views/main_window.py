"""Главное окно — список материалов."""

import os
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageTk

from .. import dal
from .material_form import MaterialForm

BG, ACCENT = "#FFFFFF", "#D32B39"
LOW_STOCK, HIGH_STOCK = "#f19292", "#ffba01"
FONT = "Verdana"
PAGE_SIZE = 15

RES = os.path.join(os.path.dirname(__file__), "..", "resources")
PLACEHOLDER = os.path.join(RES, "picture.png")
IMG_DIR = os.path.join(RES, "material_images")

SORT = {
    "Наименование (А-Я)": ("name", "asc"),
    "Наименование (Я-А)": ("name", "desc"),
    "Остаток (возр.)":    ("stock_quantity", "asc"),
    "Остаток (убыв.)":    ("stock_quantity", "desc"),
    "Стоимость (возр.)":  ("price", "asc"),
    "Стоимость (убыв.)":  ("price", "desc"),
}


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Большая пачка — Учёт материалов")
        self.geometry("1000x680")
        self.configure(bg=BG)

        self.materials = []
        self.page = 1
        self.edit_window = None
        self._build()
        self.after(50, self.reload)

    def _build(self):
        top = tk.Frame(self, bg=BG, padx=15, pady=10)
        top.pack(fill=tk.X)

        self.search = tk.StringVar()
        self.sort = tk.StringVar(value=list(SORT)[0])
        self.filt = tk.StringVar(value="Все типы")
        for v in (self.search, self.sort, self.filt):
            v.trace_add("write", lambda *_: self._reload(reset=True))

        tk.Entry(top, textvariable=self.search, font=(FONT, 11),
                 relief=tk.SOLID, bd=1).pack(
            side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        ttk.Combobox(top, textvariable=self.sort, values=list(SORT),
                     state="readonly", font=(FONT, 10), width=22).pack(
            side=tk.LEFT, padx=(10, 0))
        self.filt_cb = ttk.Combobox(top, textvariable=self.filt, state="readonly",
                                    font=(FONT, 10), width=18)
        self.filt_cb.pack(side=tk.LEFT, padx=(10, 0))
        tk.Button(top, text="+ Добавить", font=(FONT, 10, "bold"),
                  bg=ACCENT, fg="white", relief=tk.FLAT, padx=15, pady=4,
                  command=lambda: self._open_form(None)).pack(
            side=tk.LEFT, padx=(10, 0))

        self.counter = tk.StringVar(value="0 из 0")
        tk.Label(self, textvariable=self.counter, font=(FONT, 10),
                 fg="#555", bg=BG).pack(anchor="e", padx=15)

        # Скроллируемый список карточек
        wrap = tk.Frame(self, bg=BG, padx=15, pady=5)
        wrap.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(wrap, bg=BG, bd=0, highlightthickness=0)
        sb = ttk.Scrollbar(wrap, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.list_frame = tk.Frame(self.canvas, bg=BG)
        self.canvas.create_window((0, 0), window=self.list_frame,
                                  anchor="nw", tags="lf")
        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(
            "lf", width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(
            int(-e.delta / 120), "units"))

        self.pages = tk.Frame(self, bg=BG, padx=15, pady=10)
        self.pages.pack(fill=tk.X, side=tk.BOTTOM)

    def _reload(self, reset=False):
        if reset:
            self.page = 1
        self.reload()

    def reload(self):
        try:
            types = dal.fetch_material_types()
            self.types_idx = {t["name"]: t["id"] for t in types}
            self.filt_cb["values"] = ["Все типы"] + [t["name"] for t in types]
            sort_by, sort_dir = SORT.get(self.sort.get(), ("name", "asc"))
            self.materials = dal.fetch_materials(
                search=self.search.get().strip(),
                type_id=self.types_idx.get(self.filt.get()),
                sort_by=sort_by, sort_dir=sort_dir)
            total = dal.count_materials()
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось загрузить:\n{e}")
            self.materials, total = [], 0

        self.counter.set(f"{len(self.materials)} из {total}")
        max_page = max(1, (len(self.materials) + PAGE_SIZE - 1) // PAGE_SIZE)
        if self.page > max_page:
            self.page = max_page
        self._render()

    def _render(self):
        for w in self.list_frame.winfo_children() + self.pages.winfo_children():
            w.destroy()

        if not self.materials:
            tk.Label(self.list_frame, text="Материалов не найдено.",
                     font=(FONT, 11), fg="#777", bg=BG, pady=30).pack()
            return

        start = (self.page - 1) * PAGE_SIZE
        for mat in self.materials[start:start + PAGE_SIZE]:
            self._render_card(mat)

        max_page = (len(self.materials) + PAGE_SIZE - 1) // PAGE_SIZE
        if max_page <= 1:
            return
        # пагинация: < 1 2 3 ... >
        tk.Button(self.pages, text=">", width=3, font=(FONT, 10),
                  relief=tk.FLAT, bg=BG,
                  state=tk.DISABLED if self.page == max_page else tk.NORMAL,
                  command=lambda: self._goto(self.page + 1)).pack(
            side=tk.RIGHT, padx=2)
        for p in range(max_page, 0, -1):
            cur = p == self.page
            tk.Button(self.pages, text=str(p), width=3,
                      font=(FONT, 10, "bold" if cur else "normal"),
                      fg=ACCENT if cur else "#333", bg=BG, relief=tk.FLAT,
                      command=lambda p=p: self._goto(p)).pack(
                side=tk.RIGHT, padx=1)
        tk.Button(self.pages, text="<", width=3, font=(FONT, 10),
                  relief=tk.FLAT, bg=BG,
                  state=tk.DISABLED if self.page == 1 else tk.NORMAL,
                  command=lambda: self._goto(self.page - 1)).pack(
            side=tk.RIGHT, padx=2)

    def _render_card(self, mat):
        bg = BG
        s, mq = mat["stock_quantity"], mat["min_quantity"]
        if mq > 0 and s >= 3 * mq:
            bg = HIGH_STOCK
        elif s < mq:
            bg = LOW_STOCK

        card = tk.Frame(self.list_frame, bg=bg,
                        highlightbackground="#ddd", highlightthickness=1)
        card.pack(fill=tk.X, pady=4)

        thumb = self._thumb(mat["image_path"])
        img = tk.Label(card, image=thumb, bg=bg)
        img.image = thumb
        img.pack(side=tk.LEFT, padx=8, pady=8)

        c = tk.Frame(card, bg=bg)
        c.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=6)
        tk.Label(c, text=f"{mat['material_type_name']} | {mat['name']}",
                 font=(FONT, 11, "bold"), bg=bg, anchor="w").pack(fill=tk.X)
        tk.Label(c, text=f"Минимальное количество: {mq} {mat['unit']}",
                 font=(FONT, 9), bg=bg, anchor="w").pack(fill=tk.X)
        try:
            sup = ", ".join(x["name"] for x in dal.suppliers_of_material(mat["id"])) or "—"
        except Exception:
            sup = "—"
        tk.Label(c, text=f"Поставщики: {sup}", font=(FONT, 9), bg=bg, anchor="w",
                 wraplength=600, justify=tk.LEFT).pack(fill=tk.X)

        tk.Label(card, text=f"Остаток: {s} {mat['unit']}",
                 font=(FONT, 11), bg=bg).pack(side=tk.RIGHT, padx=12)

        for w in (card, c, img):
            w.bind("<Double-Button-1>", lambda e, mid=mat["id"]: self._open_form(mid))

    def _thumb(self, name):
        path = os.path.join(IMG_DIR, name) if name else None
        if not path or not os.path.exists(path):
            path = PLACEHOLDER
        try:
            return ImageTk.PhotoImage(Image.open(path).resize((80, 80), Image.LANCZOS))
        except Exception:
            return ImageTk.PhotoImage(Image.new("RGB", (80, 80), "#ccc"))

    def _goto(self, p):
        self.page = p
        self._render()
        self.canvas.yview_moveto(0)

    def _open_form(self, material_id):
        if self.edit_window is not None and self.edit_window.winfo_exists():
            messagebox.showwarning("Окно открыто",
                                   "Закройте текущее окно редактирования.")
            return
        self.edit_window = MaterialForm(self, material_id=material_id,
                                        on_close=self._on_form_closed)

    def _on_form_closed(self):
        self.edit_window = None
        self.reload()
