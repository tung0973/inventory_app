import streamlit as st

def bottom_nav():
    pages = {
        "products": ("📦 Sản phẩm", "products"),
        "in":       ("📥 Nhập kho", "in"),
        "out":      ("📤 Xuất kho", "out"),
        "invoices": ("🧾 Hóa đơn", "invoices"),
        "settings": ("⚙️ Cài đặt", "settings")
    }

    active_page = st.session_state.get("page", "products")

    # CSS nâng cấp
    st.markdown("""
        <style>
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #f9f9f9;
            padding: 0.5rem 1rem;
            box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
            z-index: 9999;
        }
        .nav-button {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 0.5rem;
            width: 100%;
            text-align: center;
            transition: all 0.2s ease;
            cursor: pointer;
            font-weight: 500;
        }
        .nav-button:hover {
            background-color: #e6f0ff;
            border-color: #3399ff;
        }
        .nav-active {
            background-color: #3399ff;
            color: white;
            border: 1px solid #3399ff;
        }
        </style>
        <div class="bottom-nav">
    """, unsafe_allow_html=True)

    cols = st.columns(len(pages))
    for idx, (key, (label, param)) in enumerate(pages.items()):
        with cols[idx]:
            if active_page == key:
                st.markdown(f"<div class='nav-button nav-active'>{label}</div>", unsafe_allow_html=True)
            else:
                if st.button(label, key=f"nav_{key}"):
                    st.session_state.page = param
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Tạo khoảng trống để tránh che nội dung cuối trang
    st.markdown("<div style='height: 100px'></div>", unsafe_allow_html=True)