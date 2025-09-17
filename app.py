import streamlit as st
from auth.login_page import login_page
from auth.session import get_current_user
from pages.products import product_page
from pages.stock_in import stock_in_page
from pages.stock_out import stock_out_page
from pages.invoices import invoices_page
from pages.settings import settings_page
from database import init_db
from components.mobile_css import mobile_css
from components.bottom_nav import bottom_nav

# Cấu hình giao diện
st.set_page_config(page_title="Inventory App", layout="wide")
mobile_css()
init_db()



# Danh sách route
ROUTES = {
    "products": product_page,
    "in": stock_in_page,
    "out": stock_out_page,
    "invoices": invoices_page,
    "settings": settings_page,
}

def main():
    # Kiểm tra đăng nhập
    user = get_current_user()
    if not user:
        login_page()
        return

    # Lấy trang hiện tại từ session_state
    if "page" not in st.session_state:
        st.session_state.page = "products"
    page = st.session_state.page

    # Header
    col1, col2 = st.columns([7, 5])
    with col1:
        st.markdown("### Inventory App")
    with col2:
        st.markdown(
            f"<div style='text-align:right'>Xin chào, <b>{user['username']}</b></div>",
            unsafe_allow_html=True
        )

    # Chạy trang tương ứng
    with st.spinner("🔄 Đang tải trang..."):
        ROUTES.get(page, product_page)()
    

    # Bottom navigation (cập nhật page trong session_state)
    bottom_nav()
    

if __name__ == "__main__":
    main()