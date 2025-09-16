import streamlit as st
from database import get_conn
from utils.helpers import safe_int, safe_float
from services.product_service import get_product_history

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

# 🔒 Cache toàn bộ sản phẩm theo điều kiện
@st.cache_data(ttl=60)
def get_filtered_products(search, selected):
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

    sql += " ORDER BY name"
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

    # 1. Tìm kiếm và lọc danh mục
    search = st.text_input("🔍 Tìm kiếm sản phẩm", "")
    categories = get_categories()
    selected = st.selectbox("📂 Chọn danh mục", ["Tất cả"] + categories)

    # 2. Phân trang
    PAGE_SIZE = 10
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1

    # 3. Truy vấn toàn bộ sản phẩm đã lọc
    all_rows = get_filtered_products(search, selected)
    total_pages = max(1, (len(all_rows) + PAGE_SIZE - 1) // PAGE_SIZE)
    start = (st.session_state.page_number - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    rows = all_rows[start:end]

    if not rows:
        st.info("Không có sản phẩm phù hợp.")
        return

    # 4. Hiển thị sản phẩm theo dạng thẻ
    st.subheader(f"📄 Trang {st.session_state.page_number} / {total_pages}")
    for pid, name, raw_price, raw_stock in rows:
        tồn_kho = safe_int(raw_stock)
        giá = safe_float(raw_price)

        with st.expander(f"🛒 {name} — 📦 Tồn kho: {tồn_kho}", expanded=False):
            col_name, col_price, col_stock = st.columns(3)
            with col_name:
                new_name = st.text_input("Tên", value=name, key=f"name_{pid}")
            with col_price:
                new_price = st.number_input("Giá (₫)", value=giá, key=f"price_{pid}")
            with col_stock:
                new_stock = st.number_input("Tồn kho", value=tồn_kho, key=f"stock_{pid}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Lưu", key=f"save_{pid}"):
                    update_product(pid, new_name, new_price, new_stock)
                    st.success("✅ Đã cập nhật sản phẩm.")
                    st.rerun()
            with col2:
                confirm = st.checkbox("Xác nhận xóa", key=f"confirm_{pid}")
                if st.button("🗑️ Xóa", key=f"delete_{pid}"):
                    if confirm:
                        delete_product(pid)
                        st.warning("🗑️ Đã xóa sản phẩm.")
                        st.rerun()
                    else:
                        st.error("❗ Vui lòng xác nhận trước khi xóa.")

            # 📜 Lịch sử xuất nhập
            history = get_product_history(pid)[:10]
            st.markdown("### 📜 Lịch sử xuất nhập")
            if history:
                for t_type, qty, time, receipt_id in history:
                    icon = "📥" if t_type == "nhập" else "📤"
                    st.markdown(f"{icon} **{t_type.capitalize()}** {qty} cái — `{time}`")
                    if receipt_id:
                        st.caption(f"🧾 Mã phiếu: {receipt_id}")
            else:
                st.info("Chưa có lịch sử xuất nhập.")

    # 5. Điều hướng phân trang
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.session_state.page_number > 1:
            if st.button("⬅️ Trang trước"):
                st.session_state.page_number -= 1
                st.rerun()
    with col3:
        if st.session_state.page_number < total_pages:
            if st.button("➡️ Trang tiếp theo"):
                st.session_state.page_number += 1
                st.rerun()