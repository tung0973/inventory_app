import streamlit as st

def bottom_nav():
    # 📄 Danh sách các trang và nhãn hiển thị
    pages = {
        "products": "📦 Sản phẩm",
        "in": "📥 Nhập kho",
        "out": "📤 Xuất kho",
        "invoices": "🧾 Hóa đơn",
        "settings": "⚙️ Cài đặt"
    }

    # 🧭 Trang đang được chọn
    active_page = st.session_state.get("page", "products")

    # 🎨 CSS cho thanh điều hướng
    st.markdown("""
    <style>
        .bottom_nav {
            display: flex;
            justify-content: space-between;
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 12px;
            box-shadow: 0 -2px 6px rgba(0,0,0,0.05);
            margin-top: 20px;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 999;
            animation: slideUp 0.3s ease-out;
        }
        @keyframes slideUp {
            from { transform: translateY(100%); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .nav-button {
            flex: 1;
            text-align: center;
            padding: 10px 0;
            margin: 0 4px;
            border-radius: 8px;
            font-weight: 500;
            background-color: transparent;
            border: none;
            cursor: pointer;
            transition: background-color 0.2s ease;
            font-size: 16px;
        }
        .nav-button:hover {
            background-color: #e0e0e0;
        }
        .nav-active {
            background-color: #d0e0ff;
            color: #000;
            box-shadow: inset 0 0 5px rgba(0,0,0,0.1);
        }
    </style>
    """, unsafe_allow_html=True)

    # 🚀 Bắt đầu thanh điều hướng
    st.markdown('<div class="bottom_nav">', unsafe_allow_html=True)

    # 🔘 Tạo các nút điều hướng chia đều
    cols = st.columns(len(pages))
    for i, (key, label) in enumerate(pages.items()):
        with cols[i]:
            if active_page == key:
                st.markdown(f"<div class='nav-button nav-active'>{label}</div>", unsafe_allow_html=True)
            else:
                if st.button(label, key=f"nav_{key}"):
                    st.session_state.page = key
                    st.rerun()

    # 🔚 Kết thúc thanh điều hướng
    st.markdown('</div>', unsafe_allow_html=True)