import streamlit as st
from database import list_products, add_or_update_product, log_stock_in
from datetime import datetime

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

def stock_in_page():
    st.subheader("⬆️ Nhập kho nhiều sản phẩm")

    rows = list_products()
    if not rows:
        st.info("Chưa có sản phẩm. Vui lòng import ở mục Sản phẩm.")
        return

    product_options = [f"{r['name']} (tồn {r['stock']})" for r in rows]
    product_map = {f"{r['name']} (tồn {r['stock']})": r for r in rows}

    num_items = st.number_input("Số sản phẩm cần nhập", min_value=1, max_value=20, step=1, value=1)

    entries = []
    for i in range(num_items):
        st.markdown(f"### 🧾 Sản phẩm #{i+1}")
        col1, col2 = st.columns([2, 1])
        with col1:
            selected = st.selectbox(f"Chọn sản phẩm #{i+1}", product_options, key=f"product_{i}")
        with col2:
            qty = st.number_input(f"Số lượng nhập #{i+1}", min_value=0, step=1, value=0, key=f"qty_{i}")

        product = product_map[selected]
        current_price = _safe_float(product['price'], default=0.0)
        current_stock = _safe_int(product['stock'], default=0)

        updated_price = st.number_input(
            f"Cập nhật giá (tuỳ chọn) #{i+1}",
            min_value=0.0,
            step=1000.0,
            value=current_price,
            key=f"price_{i}"
        )

        entries.append({
            "name": product["name"],
            "sku": product["sku"],
            "unit": product["unit"],
            "price": updated_price,
            "stock": current_stock + qty,  # ✅ Cộng thêm vào tồn kho
            "added_qty": qty,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    if st.button("💾 Ghi phiếu nhập tất cả"):
        for item in entries:
            add_or_update_product(
                name=item["name"],
                price=item["price"],
                stock=item["stock"],
                sku=item["sku"],
                unit=item["unit"]
            )
            # 📊 Ghi lịch sử nhập kho
            log_stock_in(
                name=item["name"],
                sku=item["sku"],
                qty=item["added_qty"],
                price=item["price"],
                time=item["timestamp"]
            )
        st.success("✅ Đã nhập kho và lưu lịch sử cho tất cả sản phẩm!")