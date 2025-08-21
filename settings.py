import streamlit as st
from database import list_users, add_user, delete_user, current_user, logout_user

def settings_page():
    st.subheader("⚙️ Cài đặt")
    me = current_user()
    if not me or me.get("role") != "admin":
        st.warning("Bạn không có quyền truy cập mục này.")
        if st.button("Đăng xuất"):
            logout_user(); st.rerun()
        return

    st.markdown("### 👤 Người dùng")
    with st.form("add_user_form"):
        u = st.text_input("Tên đăng nhập mới")
        p = st.text_input("Mật khẩu", type="password")
        role = st.selectbox("Vai trò", ["admin","staff"])
        ok = st.form_submit_button("Thêm người dùng")
    if ok:
        if not u or not p:
            st.error("Nhập đủ username/mật khẩu")
        else:
            try:
                add_user(u, p, role)
                st.success("Đã thêm user")
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi: {e}")

    rows = list_users()
    for r in rows:
        cols = st.columns([4,2,2,2])
        cols[0].write(f"**{r['username']}**")
        cols[1].write(r["role"])
        cols[2].write("Đang đăng nhập" if r["is_logged_in"] else "")
        if cols[3].button("Xóa", key=f"del_{r['id']}"):
            delete_user(r["id"]); st.rerun()

    st.markdown("---")
    if st.button("🚪 Đăng xuất"):
        logout_user(); st.rerun()
