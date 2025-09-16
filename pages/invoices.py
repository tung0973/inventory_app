import streamlit as st
from collections import defaultdict
from services.product_service import (
    fetch_stock_out_receipts,
    update_receipt,
    fetch_customers,
)

def invoices_page():
    st.title("🧾 Quản lý Phiếu Xuất Kho")

    receipts = fetch_stock_out_receipts()
    grouped = defaultdict(list)
    for code, ts, note, customer_name, product_name, qty, price in receipts:
        grouped[code].append((ts, note, customer_name, product_name, qty, float(price)))

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

            if st.button(f"✏️ Sửa phiếu {code}", key=f"edit_{code}"):
                st.session_state["edit_code"] = code
                st.rerun()

    if "edit_code" in st.session_state:
        code = st.session_state["edit_code"]
        items = grouped[code]
        ts, note, customer_name, _, _, _ = items[0]

        customers = fetch_customers()
        customer_names = [c[1] for c in customers]
        customer_ids = [c[0] for c in customers]

        current_customer_id = next((c[0] for c in customers if c[1] == customer_name), None)
        selected_index = customer_ids.index(current_customer_id) if current_customer_id in customer_ids else 0

        st.markdown("---")
        st.subheader(f"✏️ Chỉnh sửa Phiếu `{code}`")

        with st.form("edit_form"):
            col1, col2 = st.columns(2)
            selected_customer_name = col1.selectbox("👤 Chọn khách hàng", customer_names, index=selected_index)
            new_ts = col2.text_input("🕒 Thời gian", value=ts)
            new_note = st.text_area("📝 Ghi chú", value=note)

            selected_customer = next((c for c in customers if c[1] == selected_customer_name), None)
            if selected_customer:
                st.markdown(f"📞 **SĐT:** {selected_customer[2] or 'Không có'}")
                st.markdown(f"🏠 **Địa chỉ:** {selected_customer[3] or 'Không có'}")

            customer_id = selected_customer[0] if selected_customer else None

            updated_items = []
            st.markdown("#### 📦 Sản phẩm")
            for i, (_, _, _, name, qty, price) in enumerate(items):
                with st.expander(f"Sản phẩm #{i+1}: {name}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    new_name = col1.text_input("Tên sản phẩm", value=name, key=f"name_{i}")
                    new_qty = col2.number_input("Số lượng", value=int(qty), min_value=1, key=f"qty_{i}")
                    new_price = col3.number_input("Đơn giá", value=float(price), min_value=0.0, key=f"price_{i}")
                    delete_flag = st.checkbox("❌ Xóa sản phẩm này", key=f"delete_{i}")
                    if not delete_flag:
                        updated_items.append((new_name, new_qty, new_price))

            st.markdown("#### ➕ Thêm sản phẩm mới")
            col1, col2, col3 = st.columns(3)
            new_name = col1.text_input("Tên sản phẩm mới", key="new_name")
            new_qty = col2.number_input("Số lượng mới", min_value=1, value=1, key="new_qty")
            new_price = col3.number_input("Đơn giá mới", min_value=0.0, value=0.0, key="new_price")
            if new_name:
                updated_items.append((new_name, new_qty, new_price))

            submitted = st.form_submit_button("💾 Lưu thay đổi")
            if submitted and customer_id:
                update_receipt(code, customer_id, new_ts, new_note, updated_items)
                st.success("✅ Phiếu đã được cập nhật!")
                del st.session_state["edit_code"]
                st.rerun()