import streamlit as st
from database import get_conn


def _safe_float(v, default=0.0):
    try:
        return float(v) if v is not None else default
    except:
        return default


def _safe_int(v, default=0):
    try:
        return int(v) if v is not None else default
    except:
        return default


def update_product(product_id, name, sku, unit, category, price, stock):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE products
        SET name=?, sku=?, unit=?, category=?, price=?, stock=?
        WHERE id=?
    """, (name, sku, unit, category, price, stock, product_id))
    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


def product_page():
    st.title("📦 Quản lý sản phẩm")

    # --- Tìm kiếm sản phẩm ---
    search = st.text_input("🔍 Tìm kiếm theo Tên hoặc Mã hàng (SKU)", "").strip()

    # --- Lấy dữ liệu từ DB ---
    conn = get_conn()
    cur = conn.cursor()

    if search:
        cur.execute("""
            SELECT * FROM products 
            WHERE name LIKE ? COLLATE NOCASE 
               OR sku LIKE ? COLLATE NOCASE
            ORDER BY name
        """, (f"%{search}%", f"%{search}%"))
    else:
        cur.execute("SELECT * FROM products ORDER BY name")

    rows = cur.fetchall()
    columns = [col[0] for col in cur.description]
    conn.close()

    if not rows:
        st.info("Không tìm thấy sản phẩm nào.")
        return

    # --- Hiển thị danh sách sản phẩm ---
    for r in rows:
        row = dict(zip(columns, r))
        pid = row.get("id")
        name = row.get("name", "-")
        sku = row.get("sku", "-")
        unit = row.get("unit", "-")
        category = row.get("category", "-")
        price = _safe_float(row.get("price", 0), 0)
        stock = _safe_int(row.get("stock", 0), 0)

        stock_color = "red" if stock <= 5 else "green"

        with st.container(border=True):
            # --- Thông tin tóm tắt ---
            c1, c2 = st.columns([7, 3])
            with c1:
                st.markdown(
                    f"""
                    <div style="font-size:16px; font-weight:bold">{name}</div>
                    <div style="font-size:13px; color:gray">
                        SKU: {sku} · {unit} <br>
                        Nhóm: {category}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    f"""
                    <div style="text-align:right; font-size:14px">
                        Giá: <b>₫ {price:,.0f}</b><br>
                        <span style="color:{stock_color}">Tồn: {stock}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # --- Expander chỉnh sửa / xóa ---
            with st.expander("✏️ Chỉnh sửa / 🗑️ Xóa sản phẩm"):
                # --- Form sửa ---
                with st.form(f"edit_form_{pid}"):
                    new_name = st.text_input("Tên sản phẩm", value=name)
                    new_sku = st.text_input("Mã SKU", value=sku)
                    new_unit = st.text_input("Đơn vị", value=unit)
                    new_category = st.text_input("Nhóm", value=category)
                    new_price = st.number_input("Giá", value=float(price), step=1000.0)
                    new_stock = st.number_input("Tồn kho", value=stock, step=1)

                    c1, c2 = st.columns(2)
                    with c1:
                        submitted = st.form_submit_button("💾 Lưu thay đổi")
                    with c2:
                        delete_clicked = st.form_submit_button("🗑️ Xóa", type="primary")

                    if submitted:
                        update_product(pid, new_name, new_sku, new_unit, new_category, new_price, new_stock)
                        st.success("✅ Đã cập nhật sản phẩm!")
                        st.experimental_rerun()

                # --- Xác nhận xóa ---
                if delete_clicked:
                    st.warning(f"⚠️ Bạn có chắc chắn muốn xóa **{name}**?")
                    confirm = st.checkbox(f"✅ Tôi đồng ý xóa sản phẩm {name}", key=f"confirm_{pid}")
                    if confirm:
                        delete_product(pid)
                        st.success(f"🗑️ Đã xóa sản phẩm **{name}**")
                        st.experimental_rerun()
