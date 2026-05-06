"""
Импорт исходных данных заказчика в БД.
Запуск: python 03_import_data.py
"""

import csv
import os
import re
from pathlib import Path

import openpyxl
import psycopg2

DB_CONFIG = {
    "host":     os.getenv("PGHOST",     "localhost"),
    "port":     os.getenv("PGPORT",     "5432"),
    "dbname":   os.getenv("PGDATABASE", "bigpack"),
    "user":     os.getenv("PGUSER",     "postgres"),
    "password": os.getenv("PGPASSWORD", "postgres"),
}
SRC = Path(__file__).resolve().parent / "source_data"


def num(s):
    """Извлечь число из строки: '2191 руб.', 'На складе: 978' и т.п."""
    m = re.search(r"\d+(\.\d+)?", str(s or ""))
    return float(m.group()) if m else 0


def img(s):
    """Имя файла изображения или None."""
    t = str(s or "").strip().lower()
    if t in ("не указано", "отсутствует", "нет", ""):
        return None
    return str(s).replace("\\", "/").rsplit("/", 1)[-1] or None


def get_or_create(cur, table, name):
    cur.execute(f"SELECT id FROM {table} WHERE name=%s", (name,))
    r = cur.fetchone()
    if r:
        return r[0]
    cur.execute(f"INSERT INTO {table} (name) VALUES (%s) RETURNING id", (name,))
    return cur.fetchone()[0]


def import_materials(cur):
    with open(SRC / "materials_k_import.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f, delimiter=";"):
            tid = get_or_create(cur, "material_type", row["Тип материала"])
            cur.execute(
                "INSERT INTO material (name, material_type_id, image_path, price, "
                "stock_quantity, min_quantity, package_quantity, unit) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (row["Наименование материала"], tid, img(row["Изображение"]),
                 num(row["Цена"]), int(num(row["Количество на складе"])),
                 int(num(row["Минимальное количество"])),
                 max(int(num(row["Количество в упаковке"])), 1),
                 (row["Единица измерения"] or "шт").strip()))
    print("[materials] OK")


def import_suppliers(cur):
    with open(SRC / "supplier_k_import.txt", encoding="utf-8") as f:
        next(f)
        for line in f:
            p = [x.strip() for x in line.split(",")]
            if len(p) < 4 or not p[0]:
                continue
            tid = get_or_create(cur, "supplier_type", p[1])
            cur.execute(
                "INSERT INTO supplier (name, supplier_type_id, inn, quality_rating) "
                "VALUES (%s,%s,%s,%s) ON CONFLICT (inn) DO NOTHING",
                (p[0], tid, p[2], int(num(p[3]))))
    print("[suppliers] OK")


def import_links(cur):
    wb = openpyxl.load_workbook(SRC / "materialsupplier_k_import.xlsx", read_only=True)
    cur.execute("SELECT id, name FROM material")
    mats = {n: i for i, n in cur.fetchall()}
    cur.execute("SELECT id, name FROM supplier")
    sups = {n: i for i, n in cur.fetchall()}
    for i, row in enumerate(wb.active.iter_rows(values_only=True)):
        if i == 0 or not row[0] or not row[1]:
            continue
        mid, sid = mats.get(str(row[0]).strip()), sups.get(str(row[1]).strip())
        if mid and sid:
            cur.execute("INSERT INTO material_supplier (material_id, supplier_id) "
                        "VALUES (%s,%s) ON CONFLICT DO NOTHING", (mid, sid))
    print("[material_supplier] OK")


if __name__ == "__main__":
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            import_materials(cur)
            import_suppliers(cur)
            import_links(cur)
        conn.commit()
    finally:
        conn.close()
