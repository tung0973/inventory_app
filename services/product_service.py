import sqlite3
from database import get_conn
from datetime import datetime

def fetch_products(search="", category_filter=None):
    conn = get_conn()
    cur = conn.cursor()

    query = """
        SELECT id, name, sku, unit, category, price, stock,attributes

        FROM products
    """
    params, conditions = [], []

    if search:
        conditions.append("(name LIKE ? OR sku LIKE ?)")
        params += [f"%{search}%", f"%{search}%"]

    if category_filter and category_filter != "Tất cả":
        conditions.append("category = ?")
        params.append(category_filter)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY name"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_categories():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT category FROM products ORDER BY category")
    cats = [r[0] for r in cur.fetchall()]
    conn.close()
    return cats

def add_product(name, sku, unit, category, price, stock, attributes=""):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO products (name, sku, unit, category, price, stock, attributes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, sku, unit, category, price, stock, attributes))
    conn.commit()
    conn.close()

def update_product(pid, name, sku, unit, category, price, stock):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE products
        SET name=?, sku=?, unit=?, category=?, price=?, stock=?
        WHERE id=?
    """, (name, sku, unit, category, price, stock, pid))
    conn.commit()
    conn.close()

def delete_product(pid):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit()
    conn.close()

def record_stock_in_receipt(entries, timestamp, note=""):
    """
    entries: List of tuples (product_id, quantity)
    timestamp: string "YYYY-MM-DD HH:MM:SS"
    note: ghi chú cho phiếu nhập
    """
    conn = get_conn()
    cur = conn.cursor()

    # Tạo mã phiếu nhập theo ngày, ví dụ: PN20250825-001
    cur.execute("SELECT COUNT(*) FROM stock_in_receipts WHERE date(timestamp) = date(?)", (timestamp,))
    count_today = cur.fetchone()[0] + 1
    code = f"PN{timestamp[:10].replace('-', '')}-{count_today:03d}"

    # Tạo phiếu nhập
    cur.execute("""
        INSERT INTO stock_in_receipts (code, timestamp, note)
        VALUES (?, ?, ?)
    """, (code, timestamp, note))
    receipt_id = cur.lastrowid

    # Ghi từng dòng nhập kho
    stock_entries = [(receipt_id, pid, qty, timestamp) for pid, qty in entries]
    cur.executemany("""
        INSERT INTO stock_in (receipt_id, product_id, quantity, timestamp)
        VALUES (?, ?, ?, ?)
    """, stock_entries)

    conn.commit()
    conn.close()
    return code

def record_stock_in(entries):
    """
    entries: List of tuples (product_id, quantity, timestamp)
    """
    conn = get_conn()
    cur = conn.cursor()

    # Gắn timestamp mặc định nếu thiếu
    entries = [
        (pid, qty, ts if ts else datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        for pid, qty, ts in entries
    ]

    cur.executemany("""
        INSERT INTO stock_in (product_id, quantity, timestamp)
        VALUES (?, ?, ?)
    """, entries)

    conn.commit()
    conn.close()


def record_stock_out(pid, qty):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE products SET stock = stock - ? WHERE id=?", (qty, pid))
    cur.execute("INSERT INTO stock_out (product_id, quantity) VALUES (?, ?)", (pid, qty))
    conn.commit()
    conn.close()

def create_stock_out_receipt(items, note=""):
    conn = get_conn()
    cur = conn.cursor()

    import uuid
    code = f"PX-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.now().isoformat(timespec="seconds")

    # Tạo phiếu xuất
    cur.execute("""
        INSERT INTO stock_out_receipts (code, timestamp, note)
        VALUES (?, ?, ?)
    """, (code, timestamp, note))
    receipt_id = cur.lastrowid

    for item in items:
        pid = item["product_id"]
        qty = item["quantity"]
        price = item["price"]

        # Ghi dòng xuất kho
        cur.execute("""
            INSERT INTO stock_out (receipt_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (receipt_id, pid, qty, price))

        # Trừ tồn kho
        cur.execute("""
            UPDATE products SET stock = stock - ?
            WHERE id = ? AND stock >= ?
        """, (qty, pid, qty))

    conn.commit()
    conn.close()


def record_stock_out_receipt(entries, timestamp, note=""):
    """
    entries: List of tuples (product_id, quantity, price)
    """
    conn = get_conn()
    cur = conn.cursor()

    # Tạo mã phiếu xuất, ví dụ: PX20250825-001
    cur.execute("SELECT COUNT(*) FROM stock_out_receipts WHERE date(timestamp) = date(?)", (timestamp,))
    count_today = cur.fetchone()[0] + 1
    code = f"PX{timestamp[:10].replace('-', '')}-{count_today:03d}"

    # Tạo phiếu xuất
    cur.execute("""
        INSERT INTO stock_out_receipts (code, timestamp, note)
        VALUES (?, ?, ?)
    """, (code, timestamp, note))
    receipt_id = cur.lastrowid

    # Ghi từng dòng xuất kho
    for pid, qty, price in entries:
        cur.execute("""
            INSERT INTO stock_out (receipt_id, product_id, quantity, price, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (receipt_id, pid, qty, price, timestamp))

        # Trừ tồn kho
        cur.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, pid))

    conn.commit()
    conn.close()
    return code

def fetch_stock_in():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT si.id, p.name, si.quantity, si.timestamp
        FROM stock_in si
        JOIN products p ON si.product_id = p.id
        ORDER BY si.timestamp DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_stock_in_receipts():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.code, r.timestamp, r.note, p.name, si.quantity
        FROM stock_in_receipts r
        JOIN stock_in si ON si.receipt_id = r.id
        JOIN products p ON si.product_id = p.id
        ORDER BY r.timestamp DESC, r.id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_stock_out():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT so.id, p.name, so.quantity, so.timestamp
        FROM stock_out so
        JOIN products p ON p.id = so.product_id
        ORDER BY so.timestamp DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_stock_out_receipts():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.code, r.timestamp, r.note, p.name, so.quantity, so.price
        FROM stock_out_receipts r
        JOIN stock_out so ON so.receipt_id = r.id
        JOIN products p ON so.product_id = p.id
        ORDER BY r.timestamp DESC, r.id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def update_stock_from_excel(df):
    """
    df: DataFrame có các cột ['sku', 'name', 'stock', 'attributes']
    """
    conn = get_conn()
    cur = conn.cursor()

    for _, row in df.iterrows():
        sku = str(row['sku']).strip()
        name = str(row['name']).strip()
        stock = int(row['stock'])
        attributes = str(row.get('attributes', '')).strip()

        cur.execute("SELECT id FROM products WHERE sku = ?", (sku,))
        result = cur.fetchone()

        if result:
            cur.execute("""
                UPDATE products SET stock = ?, attributes = ? WHERE sku = ?
            """, (stock, attributes, sku))
        else:
            cur.execute("""
                INSERT INTO products (name, sku, stock, attributes)
                VALUES (?, ?, ?, ?)
            """, (name, sku, stock, attributes))

    conn.commit()
    conn.close()