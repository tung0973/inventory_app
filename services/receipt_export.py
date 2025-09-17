from html2image import Html2Image
import os
import base64
import streamlit as st


def convert_number_to_text(number):
    return f"{number:,}".replace(",", ".") + " cái"
def export_receipt_as_image(code, items, timestamp, note):
    hti = Html2Image(output_path="exported_receipts")

    html = f"""


<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            background-color: #fdfdfd;  /* 🌤 Nền sáng dịu */
            color: #222;                /* 🖋 Chữ đậm hơn */
            padding: 30px;
            line-height: 1.6;
        }}
        .title {{
            text-align: center;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #004080;  /* 🔵 Tiêu đề màu xanh đậm */
        }}
        .info {{
            margin-bottom: 15px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #ccc;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #e6f0ff;  /* 🔹 Nền tiêu đề bảng */
            color: #003366;
        }}
        .total {{
            margin-top: 20px;
            font-weight: bold;
            color: #000;
        }}
        .amount-text {{
            font-style: italic;
            margin-top: 5px;
            color: #444;
        }}
    </style>
</head>
<body>
    <div class="title">PHIẾU NHẬP HÀNG</div>
    <div class="info">
        <b>Mã phiếu:</b> {code}<br>
        <b>Ngày:</b> {timestamp}<br>
        <b>Ghi chú:</b> {note if note else "Không có"}
    </div>

    <table>
        <tr><th>STT</th><th>Tên sản phẩm</th><th>Số lượng</th><th>Đơn vị</th></tr>
        {''.join([f"<tr><td>{i+1}</td><td>{name}</td><td>{qty}</td><td>cái</td></tr>" for i, (_, _, name, qty) in enumerate(items)])}
    </table>

    <div class="total">
        Tổng số lượng: {sum(qty for _, _, _, qty in items)} cái
    </div>
    <div class="amount-text">
        ({convert_number_to_text(sum(qty for _, _, _, qty in items))} cái)
    </div>
</body>
</html>

"""

    filename = f"{code}.png"
    hti.screenshot(html_str=html, save_as=filename)
    filepath = os.path.join("exported_receipts", filename)

    st.image(filepath, caption=f"🧾 Phiếu nhập {code}")

    with open(filepath, "rb") as f:
        img_bytes = f.read()
        st.download_button(
            label="📥 Tải về ảnh phiếu nhập",
            data=img_bytes,
            file_name=filename,
            mime="image/png"
        )