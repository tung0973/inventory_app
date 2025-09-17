from PIL import Image, ImageDraw, ImageFont
import os
import streamlit as st
def export_receipt_as_image(code, items, timestamp, note):
    # Kích thước ảnh
    width, height = 800, 600 + len(items) * 40
    img = Image.new("RGB", (width, height), color="#fdfdfd")
    draw = ImageDraw.Draw(img)

    # Font mặc định (hoặc dùng font .ttf nếu có)
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 18)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    y = 30
    draw.text((width//2 - 100, y), "PHIẾU NHẬP HÀNG", font=font_title, fill="#004080")
    y += 40
    draw.text((50, y), f"Mã phiếu: {code}", font=font_text, fill="#000")
    y += 30
    draw.text((50, y), f"Thời gian: {timestamp}", font=font_text, fill="#000")
    y += 30
    draw.text((50, y), f"Ghi chú: {note if note else 'Không có'}", font=font_text, fill="#444")
    y += 40

    # Tiêu đề bảng
    draw.text((50, y), "STT", font=font_text, fill="#003366")
    draw.text((120, y), "Tên sản phẩm", font=font_text, fill="#003366")
    draw.text((500, y), "Số lượng", font=font_text, fill="#003366")
    draw.text((650, y), "Đơn vị", font=font_text, fill="#003366")
    y += 30

    # Dòng sản phẩm
    for i, (_, _, name, qty) in enumerate(items):
        draw.text((50, y), str(i+1), font=font_text, fill="#000")
        draw.text((120, y), name, font=font_text, fill="#000")
        draw.text((500, y), str(qty), font=font_text, fill="#000")
        draw.text((650, y), "cái", font=font_text, fill="#000")
        y += 30

    # Tổng số lượng
    total_qty = sum(qty for _, _, _, qty in items)
    y += 20
    draw.text((50, y), f"Tổng số lượng: {total_qty} cái", font=font_text, fill="#000")

    # Lưu ảnh
    os.makedirs("exported_receipts", exist_ok=True)
    filepath = os.path.join("exported_receipts", f"{code}.png")
    img.save(filepath)

    # Hiển thị ảnh và nút tải về
    st.image(filepath, caption=f"🧾 Phiếu nhập {code}")
    with open(filepath, "rb") as f:
        st.download_button("📥 Tải về ảnh phiếu nhập", data=f.read(), file_name=f"{code}.png", mime="image/png")