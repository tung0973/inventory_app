import streamlit as st
from database import get_conn
from utils.helpers import safe_int, safe_float

# 🔒 Cache danh mục
@st.cache_data(ttl=300)
def get_categories():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT category 
        FROM products 
        WHERE category IS NOT NULL 
        ORDER BY category
    """)
    categories = [row[0] for row in cur.fetchall()]
    conn.close()
    return categories

# 🔒 Cache sản phẩm theo điều kiện
@st.cache_data(ttl=60)
def get_products(search, selected, page_number, page_size):
    conn = get_conn()
    cur = conn.cursor()

    sql = "SELECT id, name, price, stock FROM products WHERE 1=1"
    params = []

    if search:
        sql += " AND name LIKE ?"
        params.append(f"%{search}%")

    if selected != "Tất cả":
        sql += " AND category = ?"
        params.append(selected)

    sql += " ORDER BY name LIMIT ? OFFSET ?"
    offset = (page_number - 1) * page_size
    params.extend([page_size, offset])

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

# 🛠️ Cập nhật sản phẩm
def update_product(id, name, price, stock):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE products
        SET name = ?, price = ?, stock = ?
        WHERE id = ?
    """, (name, price, stock, id))
    conn.commit()
    conn.close()

# 🗑️ Xóa sản phẩm
def delete_product(id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()

# 🧩 Trang chính
def product_page():
    st.header("📦 Danh sách sản phẩm")

    # 1. Tìm kiếm
    search = st.text_input("🔍 Tìm kiếm sản phẩm", "")

    # 2. Chọn danh mục
    categories = get_categories()
    options = ["Tất cả"] + categories
    selected = st.selectbox("📂 Chọn danh mục", options)

    # 3. Phân trang
    PAGE_SIZE = 20
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1

    # 4. Truy vấn sản phẩm
    rows = get_products(search, selected, st.session_state.page_number, PAGE_SIZE)

    if not rows:
        st.info("Không có sản phẩm phù hợp.")
        return

    # 5. Hiển thị sản phẩm
    st.subheader(f"📄 Trang {st.session_state.page_number}")
    for pid, name, raw_price, raw_stock in rows:
        tồn_kho = safe_int(raw_stock)
        with st.expander(f"{name} - 📦 Tồn kho: {tồn_kho} "):
            new_name  = st.text_input("Tên sản phẩm", value=name, key=f"name_{pid}")
            new_price = st.number_input("Giá (₫)", value=safe_float(raw_price), key=f"price_{pid}")
            new_stock = st.number_input("Tồn kho", value=tồn_kho, key=f"stock_{pid}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Lưu thay đổi", key=f"save_{pid}"):
                    update_product(pid, new_name, new_price, new_stock)
                    st.success("✅ Đã cập nhật sản phẩm.")
                    st.rerun()
            with col2:
                confirm = st.checkbox("Tôi xác nhận muốn xóa", key=f"confirm_{pid}")
                if st.button("🗑️ Xóa sản phẩm", key=f"delete_{pid}"):
                    if confirm:
                        delete_product(pid)
                        st.warning("🗑️ Đã xóa sản phẩm.")
                        st.rerun()
                    else:
                        st.error("❗ Vui lòng xác nhận trước khi xóa.")

    # 6. Điều hướng phân trang
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.page_number > 1:
            if st.button("⬅️ Trang trước"):
                st.session_state.page_number -= 1
                st.rerun()
    with col3:
        if len(rows) == PAGE_SIZE:
            if st.button("➡️ Trang tiếp theo"):
                st.session_state.page_number += 1
                st.rerun()