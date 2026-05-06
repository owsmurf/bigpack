"""Слой доступа к БД."""

import psycopg2
from psycopg2.extras import RealDictCursor

from .config import DB_CONFIG


def _conn():
    return psycopg2.connect(**DB_CONFIG)


def fetch_all(sql, params=()):
    with _conn() as c, c.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def fetch_one(sql, params=()):
    with _conn() as c, c.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def fetch_materials(search="", type_id=None, sort_by="name", sort_dir="asc"):
    cols = {"name": "m.name", "stock_quantity": "m.stock_quantity", "price": "m.price"}
    sort_col = cols.get(sort_by, "m.name")
    direction = "DESC" if sort_dir == "desc" else "ASC"
    sql = ("SELECT m.*, mt.name AS material_type_name FROM material m "
           "JOIN material_type mt ON mt.id = m.material_type_id WHERE 1=1")
    params = []
    if search:
        sql += " AND (m.name ILIKE %s OR COALESCE(m.description,'') ILIKE %s)"
        params += [f"%{search}%", f"%{search}%"]
    if type_id:
        sql += " AND m.material_type_id = %s"
        params.append(type_id)
    sql += f" ORDER BY {sort_col} {direction}, m.id"
    return fetch_all(sql, params)


def count_materials():
    with _conn() as c, c.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM material")
        return cur.fetchone()[0]


def get_material(material_id):
    mat = fetch_one(
        "SELECT m.*, mt.name AS material_type_name FROM material m "
        "JOIN material_type mt ON mt.id = m.material_type_id WHERE m.id=%s",
        (material_id,))
    if mat:
        rows = fetch_all(
            "SELECT supplier_id FROM material_supplier WHERE material_id=%s",
            (material_id,))
        mat["supplier_ids"] = [r["supplier_id"] for r in rows]
    return mat


def suppliers_of_material(material_id):
    return fetch_all(
        "SELECT s.id, s.name FROM supplier s "
        "JOIN material_supplier ms ON ms.supplier_id=s.id "
        "WHERE ms.material_id=%s ORDER BY s.name", (material_id,))


def save_material(data, supplier_ids, material_id=None):
    """Создаёт или обновляет материал и его поставщиков."""
    cols = ("name material_type_id image_path price stock_quantity "
            "min_quantity package_quantity unit description").split()
    with _conn() as c, c.cursor() as cur:
        if material_id is None:
            cur.execute(
                f"INSERT INTO material ({','.join(cols)}) "
                f"VALUES ({','.join('%(' + k + ')s' for k in cols)}) RETURNING id",
                data)
            material_id = cur.fetchone()[0]
        else:
            cur.execute(
                f"UPDATE material SET {','.join(k + '=%(' + k + ')s' for k in cols)} "
                f"WHERE id=%(id)s", {**data, "id": material_id})
            cur.execute("DELETE FROM material_supplier WHERE material_id=%s",
                        (material_id,))
        for sid in supplier_ids:
            cur.execute("INSERT INTO material_supplier VALUES (%s,%s)",
                        (material_id, sid))
        c.commit()
    return material_id


def delete_material(material_id):
    """FK с RESTRICT не даст удалить материал, используемый в продукции."""
    with _conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM material WHERE id=%s", (material_id,))
        c.commit()


def fetch_material_types():
    return fetch_all("SELECT id, name FROM material_type ORDER BY name")


def fetch_all_suppliers():
    return fetch_all("SELECT id, name FROM supplier ORDER BY name")
