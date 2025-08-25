import streamlit as st
from auth.session import logout_user

def settings_page():
    st.title("⚙️ Cài đặt")
    if st.button("🚪 Đăng xuất"):
        logout_user()