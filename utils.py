import streamlit as st

PAGES = [
    ("📦 Sản phẩm","products"),
    ("⬆️ Nhập kho","in"),
    ("⬇️ Xuất kho","out"),
    ("🧾 Hóa đơn","invoices"),
    ("⚙️ Cài đặt","settings"),
]

def mobile_css():
    st.markdown("""
    <style>
    .block-container { padding-bottom: 5.5rem; }
    .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0;
        display:flex; gap:8px; padding:8px; background:#ffffffee; backdrop-filter: blur(6px);
        border-top:1px solid #e9ecef; z-index:9999; }
    .bottom-nav a { flex:1; text-align:center; padding:8px 6px; border:1px solid #e9ecef;
        border-radius:12px; text-decoration:none; color:#111; font-size:0.9rem; }
    .bottom-nav a.active { background:#111; color:#fff; }
    #MainMenu, footer { display:none; }
    </style>
    """, unsafe_allow_html=True)

def bottom_nav(active_key: str):
    html = ["<div class='bottom-nav'>"]
    for label, key in PAGES:
        cls = "active" if key == active_key else ""
        html.append(f"<a class='{cls}' href='?page={key}'>{label}</a>")
    html.append("</div>")
    st.markdown("\n".join(html), unsafe_allow_html=True)
