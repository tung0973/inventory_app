import streamlit as st
from database import init_db, login, current_user, logout_user

def login_page():
    st.title("🔐 Đăng nhập")
    init_db()
    u = st.text_input("Tên đăng nhập", value="admin")
    p = st.text_input("Mật khẩu", type="password", value="admin")
    remember = st.checkbox("Ghi nhớ đăng nhập", value=True)
    if st.button("Đăng nhập", use_container_width=True):
        user = login(u, p)
        if user:
            st.success("Đăng nhập thành công")
            # is_logged_in đã lưu DB; Streamlit rerun để vào app
            st.rerun()
        else:
            st.error("Sai tài khoản hoặc mật khẩu")

def get_current_user():
    init_db()
    return current_user()

def logout():
    logout_user()
    st.rerun()
