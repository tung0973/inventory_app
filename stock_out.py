import streamlit as st
from database import list_products, add_or_update_product

def stock_out_page():
    st.subheader("⬇️ Xuất kho (bán nhanh)")
    rows = list_products()
    if not rows:
        st.info("Chưa có sản phẩm. Vui lòng import ở mục Sản phẩm."); return
    names = {f"{r['name']} (tồn {r['stock']})": r for r in rows}
    sel = st.selectbox("Chọn sản phẩm", list(names.keys()))
    qty = st.number_input("Số lượng xuất", min_value=0, step=1, value=0)
    if st.button("💾 Ghi phiếu xuất"):
        r = names[sel]
        add_or_update_product(r["name"], price=r["price"], stock=-qty, sku=r["sku"], unit=r["unit"])
        st.success("Đã xuất kho")
