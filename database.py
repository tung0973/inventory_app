import sqlite3

DB_PATH = "inventory.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Bật ràng buộc khóa ngoại
    cur.execute("PRAGMA foreign_keys = ON")

    # ===== TẠO BẢNG =====

    # Người dùng
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Sản phẩm
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

    # Phiếu nhập kho
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_in_receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            timestamp TEXT NOT NULL,
            note TEXT
        )
    """)

    # Chi tiết nhập kho
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_in (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    # Phiếu xuất kho
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_out_receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            timestamp TEXT,
            note TEXT
        )
    """)

    # Chi tiết xuất kho
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_out (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
    """)

    # Hóa đơn
    cur.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            date TEXT NOT NULL,
            total REAL NOT NULL
        )
    """)

    # Chi tiết hóa đơn
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

    # Khách hàng
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
    """)

    conn.commit()

    # ===== THÊM CỘT BỔ SUNG =====

    def add_column_if_missing(table, column, definition):
        cur.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cur.fetchall()]
        if column not in columns:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            conn.commit()

    add_column_if_missing("products", "attributes", "TEXT")
    add_column_if_missing("stock_in", "receipt_id", "INTEGER")
    add_column_if_missing("stock_out", "receipt_id", "INTEGER")
    add_column_if_missing("stock_out", "price", "REAL DEFAULT 0")
    add_column_if_missing("stock_out_receipts", "customer_id", "INTEGER REFERENCES customers(id)")

    # ===== TẠO USER MẶC ĐỊNH =====

    cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin"))

    conn.commit()
    conn.close()