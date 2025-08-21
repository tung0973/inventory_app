import streamlit as st
from auth import login_page, get_current_user, logout
from products import product_page
from stock_in import stock_in_page
from stock_out import stock_out_page
from invoices import invoices_page
from settings import settings_page
from database import init_db
from utils import mobile_css, bottom_nav

ROUTES = {
    "products": product_page,
    "in": stock_in_page,
    "out": stock_out_page,
    "invoices": invoices_page,
    "settings": settings_page,
}

def main():
    st.set_page_config(page_title="Inventory App", layout="wide")
    mobile_css()
    init_db()

    user = get_current_user()
    if not user:
        login_page(); return

    # routing by query param
    qp = st.query_params
    page = qp.get("page") or "products"
    if isinstance(page, list):
        page = page[0]

    # header
    col1, col2 = st.columns([7,5])
    with col1: st.markdown("### Inventory App")
    with col2: st.markdown(f"<div style='text-align:right'>Xin chào, <b>{user['username']}</b></div>", unsafe_allow_html=True)

    ROUTES.get(page, product_page)()

    bottom_nav(page)

if __name__ == "__main__":
    main()
