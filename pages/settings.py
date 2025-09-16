import streamlit as st
from auth.session import logout_user
from services.product_service import fetch_customers, delete_customer

def settings_page():
    st.title("⚙️ Cài đặt")

    st.subheader("📋 Danh sách khách hàng")
    customers = fetch_customers()

    if not customers:
        st.info("ℹ️ Chưa có khách hàng nào trong hệ thống.")
        return

    for cid, name, phone, address in customers:
        with st.expander(f"👤 {name} (ID:{cid})", expanded=False):
            st.write(f"📞 SĐT: {phone}")
            st.write(f"🏠 Địa chỉ: {address}")
            # Tuỳ chọn chỉnh sửa hoặc xoá
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✏️ Sửa – {cid}"):
                    st.warning("🔧 Chức năng sửa đang được phát triển.")
            with col2:
                if st.button(f"🗑️ Xoá – {cid}"):
                    delete_customer(cid)
                    st.success(f"✅ Đã xoá khách hàng {name}")

    if st.button("🚪 Đăng xuất"):
        logout_user()