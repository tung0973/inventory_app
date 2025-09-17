import streamlit as st
from datetime import datetime
from services.product_service import fetch_products, fetch_stock_in_receipts, record_stock_in_receipt
from services.product_service import update_stock_from_excel
from services.product_service import delete_stock_in_receipt, edit_stock_in_receipt  # Thêm các hàm xử lý
from services.receipt_export import export_receipt_as_image


def stock_in_page():
    st.title("📥 Nhập kho")

    tab1, tab2 = st.tabs(["🔧 Nhập thủ công", "📄 Nhập từ Excel"])

    with tab1:
        show_manual_stock_in()

    with tab2:
        import_stock_page()


def show_manual_stock_in():
    products = fetch_products()
    product_dict = {p[0]: p[1] for p in products}

    selected_ids = st.multiselect(
        "Chọn sản phẩm cần nhập",
        options=list(product_dict.keys()),
        format_func=lambda x: f"{product_dict[x]} (ID:{x})"
    )

    selected_date = st.date_input("Ngày nhập kho", value=datetime.today())
    selected_time = st.time_input("Giờ nhập kho", value=datetime.now().time())
    timestamp = datetime.combine(selected_date, selected_time).strftime("%Y-%m-%d %H:%M:%S")

    note = st.text_input("Ghi chú phiếu nhập", placeholder="Ví dụ: Nhập hàng từ nhà cung cấp A")

    entries = []
    with st.form("multi_stock_in_form"):
        for pid in selected_ids:
            qty = st.number_input(
                f"Số lượng cho {product_dict[pid]}",
                min_value=1,
                step=1,
                key=f"qty_{pid}"
            )
            entries.append((pid, qty))

        submitted = st.form_submit_button("Tạo phiếu nhập")
        if submitted:
            code = record_stock_in_receipt(entries, timestamp, note)
            st.success(f"✅ Đã tạo phiếu nhập **{code}** với {len(entries)} sản phẩm vào lúc {timestamp}")
            st.rerun()

    # 📜 Lịch sử phiếu nhập kho
    st.subheader("📜 Lịch sử phiếu nhập kho")
    receipts = fetch_stock_in_receipts()

    from collections import defaultdict
    grouped = defaultdict(list)
    for code, ts, note, name, qty in receipts:
        grouped[code].append((ts, note, name, qty))

    for code, items in list(grouped.items())[:50]:
        ts, note, _, _ = items[0]
        with st.expander(f"🧾 Phiếu nhập {code} – {ts}", expanded=False):
            if note:
                st.caption(f"📝 {note}")
            for _, _, name, qty in items:
                st.write(f"• {name}: +{qty}")

            col1, col2,col3 = st.columns(3)
            with col1:
                if st.button(f"✏️ Sửa phiếu {code}", key=f"edit_{code}"):
                    st.session_state.editing_code = code
            with col2:
                if st.button(f"🗑️ Xóa phiếu {code}", key=f"delete_{code}"):
                    st.session_state.confirm_delete = code
            with col3:
                if st.button(f"📸 Xuất ảnh phiếu {code}", key=f"export_{code}"):
                    export_receipt_as_image(code, items, ts, note)

            # Xác nhận xóa
            if st.session_state.get("confirm_delete") == code:
                st.warning(f"⚠️ Bạn có chắc muốn xóa phiếu nhập {code}?")
                confirm_col1, confirm_col2 = st.columns(2)
                with confirm_col1:
                    if st.button("✅ Xác nhận", key=f"confirm_yes_{code}"):
                        delete_stock_in_receipt(code)
                        st.success(f"✅ Đã xóa phiếu nhập {code}")
                        del st.session_state.confirm_delete
                        st.rerun()
                with confirm_col2:
                    if st.button("❌ Hủy", key=f"confirm_no_{code}"):
                        del st.session_state.confirm_delete

    # Form sửa phiếu nhập
    if "editing_code" in st.session_state:
        edit_stock_in_receipt(st.session_state.editing_code)

import streamlit as st
import pandas as pd
from services.product_service import update_stock_from_excel

def import_stock_page():
    st.subheader("📄 Nhập tồn kho từ Excel")

    uploaded_file = st.file_uploader("📤 Tải lên file Excel (.xlsx hoặc .csv)", type=["xlsx", "csv"])

    if uploaded_file:
        try:
            # Đọc file
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.success("✅ Đã đọc dữ liệu từ file")
            st.write("📋 Các cột có trong file:", df.columns.tolist())

            required_columns = {"sku", "name", "stock"}
            if not required_columns.issubset(set(df.columns)):
                st.error("❌ File thiếu cột bắt buộc: sku, name, stock")
                return

            # 👉 Làm sạch dữ liệu cột 'stock'
            df['stock'] = pd.to_numeric(df['stock'], errors='coerce').fillna(0).astype(int)

            # 👉 Hiển thị sản phẩm có tồn kho bằng 0 để kiểm tra
            zero_stock_items = df[df['stock'] == 0]
            if not zero_stock_items.empty:
                st.warning("⚠️ Có sản phẩm có tồn kho bằng 0:")
                st.dataframe(zero_stock_items)

            st.dataframe(df)

            if st.button("🚀 Cập nhật tồn kho"):
                update_stock_from_excel(df)
                st.success("🎉 Đã cập nhật tồn kho thành công")
                st.rerun()

        except Exception as e:
            st.error(f"⚠️ Lỗi khi xử lý file: {e}")

