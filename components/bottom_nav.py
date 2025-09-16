import streamlit as st

def bottom_nav():
    # Danh sách các trang và nhãn hiển thị
    pages = {
        "products": ("📦 Sản phẩm", "products"),
        "in":       ("📥 Nhập kho", "in"),
        "out":      ("📤 Xuất kho", "out"),
        "invoices": ("🧾 Hóa đơn", "invoices"),
        "settings": ("⚙️ Cài đặt", "settings")
    }

    # Trang đang được chọn
    active_page = st.session_state.get("page", "products")

    # CSS cho thanh điều hướng
    st.markdown("""
        <style>
            .bottom_nav {
                width: 100%;
                background-color: #f0f2f6;
                padding: 5px 5px;
                border-radius: 12px;
                box-shadow: 0 -2px 6px rgba(0,0,0,0.05);
                font-family: 'Segoe UI', sans-serif;
            }
            .nav-button {
                text-align: center;
                padding: 10px;
                border-radius: 8px;
                font-weight: 500;
                transition: background-color 0.2s ease;
            }
            .nav-button:hover {
                background-color: #e0e0e0;
            }
            .nav-active {
                background-color: #d0e0ff;
                color: #000;
            }
        </style>
    """, unsafe_allow_html=True)

    # Bắt đầu thanh điều hướng
    st.markdown('<div class="bottom_nav">', unsafe_allow_html=True)

    cols = st.columns(len(pages))
    for idx, (key, (label, param)) in enumerate(pages.items()):
        with cols[idx]:
            if active_page == key:
                st.markdown(f"<div class='nav-button nav-active'>{label}</div>", unsafe_allow_html=True)
            else:
                if st.button(label, key=f"nav_{key}"):
                    st.session_state.page = param
                    st.rerun()

    # Kết thúc thanh điều hướng
    st.markdown('</div>', unsafe_allow_html=True)