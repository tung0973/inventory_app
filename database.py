import sqlite3

DB_NAME = "inventory.db"

def get_conn():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # Bảng users
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            is_logged_in INTEGER NOT NULL DEFAULT 0
        )
    """)
    # Bảng products
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT,
        name TEXT UNIQUE NOT NULL,
        unit TEXT DEFAULT 'pcs',
        price REAL DEFAULT 0,
        stock INTEGER NOT NULL DEFAULT 0,
        category TEXT
    )
""")

# Bảng lịch sử nhập kho
    c.execute("""
    CREATE TABLE IF NOT EXISTS stock_in_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        sku TEXT,
        qty INTEGER,
        price REAL,
        time TEXT
    )
""")
    
    # seed admin
    row = c.execute("SELECT COUNT(1) FROM users").fetchone()[0]
    if row == 0:
        c.execute("INSERT INTO users(username,password,role,is_logged_in) VALUES(?,?,?,0)", 
                  ("admin","admin","admin"))
    conn.commit()
    conn.close()

# ---------- Users ----------
def login(username, password):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    if row:
        conn.execute("UPDATE users SET is_logged_in=1 WHERE id=?", (row["id"],))
        conn.commit()
        conn.close()
        return dict(row)
    conn.close()
    return None

def current_user():
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE is_logged_in=1 LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None

def logout_user():
    conn = get_conn()
    conn.execute("UPDATE users SET is_logged_in=0 WHERE is_logged_in=1")
    conn.commit()
    conn.close()

def list_users():
    conn = get_conn()
    rows = conn.execute("SELECT id, username, role, is_logged_in FROM users ORDER BY id DESC").fetchall()
    conn.close()
    return rows

def add_user(username, password, role):
    conn = get_conn()
    conn.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)", (username, password, role))
    conn.commit()
    conn.close()

def delete_user(uid):
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit()
    conn.close()

# ---------- Products ----------
def add_or_update_product(name, price=0.0, stock=0, sku=None, unit="pcs", category=None):
    conn = get_conn()
    cur = conn.cursor()
    row = cur.execute("SELECT id FROM products WHERE name=?", (name,)).fetchone()
    if row:
        cur.execute("""
            UPDATE products 
            SET price=?, stock=stock+?, sku=?, unit=?, category=? 
            WHERE id=?
        """, (float(price), int(stock), sku, unit, category, row["id"]))
    else:
        cur.execute("""
            INSERT INTO products(name, price, stock, sku, unit, category) 
            VALUES(?,?,?,?,?,?)
        """, (name, float(price), int(stock), sku, unit, category))
    conn.commit()
    conn.close()

def list_products():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    conn.close()
    return rows

def log_stock_in(name, sku, qty, price, time):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO stock_in_history (name, sku, qty, price, time)
        VALUES (?, ?, ?, ?, ?)
    """, (name, sku, qty, price, time))
    conn.commit()
    conn.close()
