from database import get_conn

def fetch_invoices():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, code, date, total FROM invoices ORDER BY date DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def fetch_invoice_items(invoice_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.name, ii.quantity, ii.price
        FROM invoice_items ii
        JOIN products p ON p.id = ii.product_id
        WHERE ii.invoice_id=?
    """, (invoice_id,))
    items = cur.fetchall()
    conn.close()
    return items

def add_invoice(code, date, total, items):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO invoices (code, date, total) VALUES (?, ?, ?)", (code, date, total))
    inv_id = cur.lastrowid
    for prod_id, qty, price in items:
        cur.execute("""
            INSERT INTO invoice_items (invoice_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (inv_id, prod_id, qty, price))
    conn.commit()
    conn.close()