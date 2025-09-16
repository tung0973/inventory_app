import sqlite3
import os

DB_PATH = "inventory.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def ensure_price_column(cur):
    cur.execute("PRAGMA table_info(stock_out)")
    columns = [row[1] for row in cur.fetchall()]
    if "price" not in columns:
        cur.execute("ALTER TABLE stock_out ADD COLUMN price REAL DEFAULT 0")

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("PRAGMA foreign_keys = ON")
    

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_in_receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            timestamp TEXT NOT NULL,
            note TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            unit TEXT,
            category TEXT,
            price REAL DEFAULT 0,
            stock INTEGER DEFAULT 0
        )
    """)



    cur.execute("PRAGMA table_info(products)")
    columns = [col[1] for col in cur.fetchall()]
    if "attributes" not in columns:
        cur.execute("ALTER TABLE products ADD COLUMN attributes TEXT")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_in (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_out_receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            timestamp TEXT,
            note TEXT
        )
    """)

    cur.execute("PRAGMA table_info(stock_out)")
    columns = [col[1] for col in cur.fetchall()]
    if "receipt_id" not in columns:
        cur.execute("ALTER TABLE stock_out ADD COLUMN receipt_id INTEGER")

    cur.execute("PRAGMA table_info(stock_in)")
    columns = [col[1] for col in cur.fetchall()]
    if "receipt_id" not in columns:
        cur.execute("ALTER TABLE stock_in ADD COLUMN receipt_id INTEGER")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_out (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    # Đảm bảo cột price tồn tại
    ensure_price_column(cur)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            date TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(invoice_id) REFERENCES invoices(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    # Tạo user mặc định nếu chưa có
    cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        address TEXT
       )
    """)

    cur.execute("PRAGMA table_info(stock_out_receipts)")
    columns = [col[1] for col in cur.fetchall()]
    if "customer_id" not in columns:
        cur.execute("ALTER TABLE stock_out_receipts ADD COLUMN customer_id INTEGER REFERENCES customers(id)")

    conn.commit()
    conn.close()


    
