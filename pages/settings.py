import streamlit as st
from auth.session import logout_user
from services.product_service import fetch_customers, delete_customer,update_customer,create_customer

def settings_page():
    st.title("⚙️ Cài đặt hệ thống")
    st.subheader("📋 Danh sách khách hàng")

    customers = fetch_customers()

    if not customers:
        st.info("ℹ️ Chưa có khách hàng nào trong hệ thống.")
        return

    for cid, name, phone, address in customers:
        with st.expander(f"👤 {name} (ID:{cid})", expanded=False):
            st.write(f"📞 SĐT: {phone}")
            st.write(f"🏠 Địa chỉ: {address}")

            edit_mode = st.checkbox(f"✏️ Sửa thông tin – {cid}")
            if edit_mode:
                new_name = st.text_input(f"Tên mới – {cid}", value=name, key=f"name_{cid}")
                new_phone = st.text_input(f"SĐT mới – {cid}", value=phone, key=f"phone_{cid}")
                new_address = st.text_input(f"Địa chỉ mới – {cid}", value=address, key=f"addr_{cid}")
                if st.button(f"💾 Lưu thay đổi – {cid}"):
                    update_customer(cid, new_name, new_phone, new_address)
                    st.success("✅ Đã cập nhật thông tin khách hàng.")

            if st.button(f"🗑️ Xoá khách hàng – {cid}"):
                delete_customer(cid)
                st.success(f"✅ Đã xoá khách hàng {name}")

    if st.button("🚪 Đăng xuất"):
        logout_user()