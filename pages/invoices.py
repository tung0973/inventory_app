import streamlit as st
from services.invoice_service import fetch_invoices, fetch_invoice_items, add_invoice

def invoices_page():
    st.title("🧾 Quản lý hóa đơn")

    # Danh sách hóa đơn
    invs = fetch_invoices()
    for inv_id, code, date, total in invs:
        with st.expander(f"{code} – {date} – ₫{total:,.0f}"):
            items = fetch_invoice_items(inv_id)
            for name, qty, price in items:
                st.write(f"{name}: {qty} × ₫{price:,.0f}")

    # Thêm hóa đơn mới
    st.subheader("➕ Tạo hóa đơn")
    with st.form("inv_form"):
        code = st.text_input("Mã hóa đơn")
        date = st.date_input("Ngày")
        total = st.number_input("Tổng tiền", step=1000.0)
        submitted = st.form_submit_button("Tạo hóa đơn")
        if submitted:
            add_invoice(code, str(date), total, [])
            st.success("Đã tạo hóa đơn mới")