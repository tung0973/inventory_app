import streamlit as st
from auth.session import login_user

def login_page():
    st.title("🔒 Đăng nhập")
    with st.form("login_form"):
        username = st.text_input("Tên đăng nhập")
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng nhập")
        if submitted:
            if login_user(username.strip(), password.strip()):
                st.rerun()
            else:
                st.error("❌ Sai tên đăng nhập hoặc mật khẩu")