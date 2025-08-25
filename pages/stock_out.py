import streamlit as st
from services.product_service import fetch_products, create_stock_out_receipt, fetch_stock_out_receipts

def stock_out_page():
    st.title("📤 Xuất kho nhiều sản phẩm")

    products = fetch_products()
    options = {f"{p[1]} (ID:{p[0]}) – Tồn: {p[6]}": p for p in products}

    with st.form("out_form"):
        selected = st.multiselect("Chọn sản phẩm cần xuất", list(options.keys()))
        product_inputs = []

        for label in selected:
            p = options[label]
            pid = p[0]
            col1, col2 = st.columns(2)
            with col1:
                qty = st.number_input(f"Số lượng – {label}", min_value=1, max_value=p[6], step=1, key=f"qty_{pid}")
            with col2:
                price = st.number_input(f"Đơn giá – {label}", min_value=0.0, step=100.0, key=f"price_{pid}")
            product_inputs.append({"product_id": pid, "quantity": qty, "price": price})

        note = st.text_input("Ghi chú phiếu xuất", "")
        submit = st.form_submit_button("📤 Xuất kho")

        if submit and product_inputs:
            create_stock_out_receipt(product_inputs, note)
            st.success("✅ Đã xuất kho và cập nhật tồn kho thành công!")

    st.subheader("📜 Lịch sử phiếu xuất kho")
    receipts = fetch_stock_out_receipts()

    from collections import defaultdict
    grouped = defaultdict(list)
    for code, ts, note, name, qty, price in receipts:
        grouped[code].append((ts, note, name, qty, price))

    for code, items in list(grouped.items())[:50]:
        ts, note, _, _, _ = items[0]
        with st.expander(f"🧾 Phiếu xuất {code} – {ts}", expanded=False):
            if note:
                st.caption(f"📝 {note}")
            total = 0
            for _, _, name, qty, price in items:
                st.write(f"• {name}: –{qty} × {price:,.0f}đ")
                total += qty * price
            st.markdown(f"**💰 Tổng tiền:** {total:,.0f}đ")