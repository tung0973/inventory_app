Inventory App (Mini KiotViet)
=============================

✅ Đăng nhập / Đăng xuất (user mặc định: admin / admin, lưu trạng thái trong SQLite)
✅ Menu dưới cố định (icon + chữ)
✅ Quản lý người dùng trong ⚙️ Cài đặt (Admin)
✅ Quản lý sản phẩm + 📥 Import Excel/CSV (.xlsx/.xlsb/.csv)
✅ Nhập kho / Xuất kho nhanh
✅ (Placeholder) Hóa đơn

Cách chạy
---------
1) Tạo môi trường và cài thư viện:
   pip install -r requirements.txt

2) Chạy ứng dụng:
   streamlit run app.py

File Excel mẫu
--------------
Cột bắt buộc: name, price, stock
Tuỳ chọn: sku, unit
