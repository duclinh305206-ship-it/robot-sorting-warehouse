# DỰ ÁN NHÓM: HỆ THỐNG GIÁM SÁT CÁNH TAY ROBOT PHÂN LOẠI SẢN PHẨM

Đề tài: **Thu thập và quản lí dữ liệu các cánh tay robot công nghiệp của hệ thống phân loại sản phẩm trong nhà kho tự động.**

---

## 📁 Danh sách tệp trong thư mục:
- `schema_robot.sql`: File SQL định nghĩa cấu trúc bảng (`ThietBiRobot`, `LoaiSanPham`, `NhatKyPhanLoai`, `NhatKyCanhBao`).
- `warehouse_robot.db`: Database SQLite lưu trữ dữ liệu thực tế.
- `init_db.py`: Script khởi tạo database từ `schema_robot.sql`.
- `simulator.py`: Bộ giả lập hoạt động robot (gắp hàng, đo nhiệt độ khớp nối, ghi log).
- `app.py`: Giao diện Web Dashboard Streamlit (Biểu đồ, Bảng truy vấn, Trạng thái máy móc, Chỉ số KPI).
- `xem_ket_qua.py`: In nhanh toàn bộ dữ liệu CSDL ngay trên cửa sổ Terminal.
- `requirements.txt`: Các thư viện phụ thuộc (`streamlit`, `pandas`, `matplotlib`, `seaborn`).

---

## 🚀 Cách chạy trên Terminal VS Code:

### 1. Xem kết quả nhanh trong Terminal:
```powershell
.\.venv\Scripts\python.exe xem_ket_qua.py
```

### 2. Chạy giả lập Robot (sinh thêm dữ liệu):
```powershell
.\.venv\Scripts\python.exe simulator.py
```

### 3. Chạy giao diện Web Dashboard:
```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```
*(Mở trình duyệt xem tại: `http://localhost:8501`)*
