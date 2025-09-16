import streamlit as st
from collections import defaultdict
from services.product_service import (
    fetch_products,
    create_stock_out_receipt,
    fetch_stock_out_receipts
)
from services.product_service import (
    fetch_customers,
    create_customer
)

def stock_out_page():
    st.title("📤 Xuất kho nhiều sản phẩm")

    # --- Lấy dữ liệu ---
    products = fetch_products()
    customers = fetch_customers()

    if not products:
        st.warning("⚠️ Không có sản phẩm nào trong kho.")
        return

    product_options = {
        f"{p[1]} (ID:{p[0]}) – Tồn: {p[6]}": p for p in products
    }

    customer_options = {
        f"{c[1]} (ID:{c[0]})": c[0] for c in customers
    }

    # --- Form xuất kho ---
    with st.form("out_form"):
        st.subheader("🛒 Chọn sản phẩm và khách hàng")

        selected_products = st.multiselect("📦 Sản phẩm cần xuất", list(product_options.keys()))
        add_new_customer = st.checkbox("➕ Thêm khách hàng mới")

        customer_id = None
        note = st.text_input("📝 Ghi chú phiếu xuất", "")

        if add_new_customer or not customers:
            st.markdown("### 🆕 Nhập thông tin khách hàng mới")
            new_name = st.text_input("👤 Tên khách hàng")
            new_phone = st.text_input("📞 Số điện thoại")
            new_address = st.text_input("🏠 Địa chỉ")

            if new_name and new_phone:
                customer_id = create_customer(new_name, new_phone, new_address)
                st.success(f"✅ Đã thêm khách hàng: {new_name} (ID: {customer_id})")
            else:
                st.info("ℹ️ Vui lòng nhập đầy đủ tên và số điện thoại.")
        else:
            customer_list = ["-- Chọn khách hàng --"] + list(customer_options.keys())
            customer_name = st.selectbox("👤 Khách hàng", customer_list)

            if customer_name == "-- Chọn khách hàng --":
                st.info("ℹ️ Vui lòng chọn khách hàng để tiếp tục.")
            else:
                customer_id = customer_options.get(customer_name)

        # --- Nhập số lượng và đơn giá ---
        product_inputs = []
        for label in selected_products:
            p = product_options[label]
            pid = p[0]
            col1, col2 = st.columns(2)
            with col1:
                qty = st.number_input(
                    f"Số lượng – {label}",
                    min_value=1,
                    max_value=p[6],
                    step=1,
                    key=f"qty_{pid}"
                )
            with col2:
                price = st.number_input(
                    f"Đơn giá – {label}",
                    min_value=0.0,
                    step=100.0,
                    key=f"price_{pid}"
                )
            product_inputs.append({
                "product_id": pid,
                "quantity": qty,
                "price": price
            })

        submit = st.form_submit_button("📤 Xác nhận xuất kho")

        if submit:
            if not customer_id:
                st.warning("⚠️ Bạn chưa chọn hoặc thêm khách hàng.")
                return
            if not selected_products:
                st.warning("⚠️ Bạn chưa chọn sản phẩm nào.")
                return
            create_stock_out_receipt(product_inputs, note, customer_id)
            st.success("✅ Phiếu xuất đã được tạo và tồn kho đã cập nhật!")

    # --- Lịch sử phiếu xuất ---
    st.subheader("📜 Lịch sử phiếu xuất kho")
    receipts = fetch_stock_out_receipts()
    grouped = defaultdict(list)

    for code, ts, note, customer_name, product_name, qty, price in receipts:
        grouped[code].append((ts, note, customer_name, product_name, qty, price))

    for code, items in list(grouped.items())[:50]:
        ts, note, customer_name, _, _, _ = items[0]
        with st.expander(f"🧾 Phiếu xuất {code} – {ts}", expanded=False):
            st.caption(f"👤 Khách hàng: {customer_name}")
            if note:
                st.caption(f"📝 {note}")
            total = 0
            for _, _, _, name, qty, price in items:
                st.write(f"• {name}: –{qty} × {price:,.0f}đ")
                total += qty * price
            st.markdown(f"**💰 Tổng tiền:** {total:,.0f}đ")