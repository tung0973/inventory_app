import streamlit as st
from database import get_conn
from utils.helpers import safe_int, safe_float
from services.product_service import get_product_history

# 🔒 Cache danh mục sản phẩm
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

# 🔒 Cache danh sách sản phẩm theo điều kiện lọc
@st.cache_data(ttl=60)
def get_filtered_products(search, selected_category):
    conn = get_conn()
    cur = conn.cursor()

    sql = "SELECT id, name, price, stock FROM products WHERE 1=1"
    params = []

    if search:
        sql += " AND name LIKE ?"
        params.append(f"%{search}%")

    if selected_category and selected_category != "Tất cả":
        sql += " AND category = ?"
        params.append(selected_category)

    sql += " ORDER BY name"
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

# 🛠️ Cập nhật thông tin sản phẩm
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

# 🧩 Trang quản lý sản phẩm
def product_page():
    st.header("📦 Danh sách sản phẩm")

    # 1. Bộ lọc tìm kiếm và danh mục
    col_search, col_category = st.columns([2, 2])
    with col_search:
        search = st.text_input("🔍 Tìm kiếm theo tên sản phẩm", "")
    with col_category:
        categories = get_categories()
        selected_category = st.selectbox("📂 Lọc theo danh mục", ["Tất cả"] + categories)

    # 2. Reset phân trang khi thay đổi bộ lọc
    if "last_filter" not in st.session_state:
        st.session_state.last_filter = (search, selected_category)

    if (search, selected_category) != st.session_state.last_filter:
        st.session_state.page_number = 1
        st.session_state.last_filter = (search, selected_category)

    # 3. Phân trang
    PAGE_SIZE = 10
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1

    # 4. Truy vấn sản phẩm đã lọc
    all_rows = get_filtered_products(search, selected_category)
    total_pages = max(1, (len(all_rows) + PAGE_SIZE - 1) // PAGE_SIZE)
    start = (st.session_state.page_number - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    rows = all_rows[start:end]

    # 5. Hiển thị kết quả
    st.caption(f"🔎 Có {len(all_rows)} sản phẩm phù hợp.")
    st.subheader(f"📄 Trang {st.session_state.page_number} / {total_pages}")

    if not rows:
        st.info("Không có sản phẩm phù hợp.")
        return

    for pid, name, raw_price, raw_stock in rows:
        tồn_kho = safe_int(raw_stock)
        giá = safe_float(raw_price)

        with st.expander(f"🛒 {name} — 📦 Tồn kho: {tồn_kho}", expanded=False):
            # Chỉnh sửa sản phẩm
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

            # Lịch sử xuất nhập
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

    # 6. Điều hướng phân trang
    col_prev, col_info, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.session_state.page_number > 1:
            if st.button("⬅️ Trang trước"):
                st.session_state.page_number -= 1
                st.rerun()
    with col_next:
        if st.session_state.page_number < total_pages:
            if st.button("➡️ Trang tiếp theo"):
                st.session_state.page_number += 1
                st.rerun()