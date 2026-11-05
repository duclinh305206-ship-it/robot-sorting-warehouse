"""
ỨNG DỤNG GIÁM SÁT & QUẢN LÝ CÁNH TAY ROBOT PHÂN LOẠI SẢN PHẨM (STREAMLIT)
Phục vụ 4 yêu cầu bài tập lớn:
1. Biểu đồ (Charts)
2. Truy vấn (Query & Filter)
3. Máy móc đang hoạt động (Robot Status)
4. Số lượng hiện tại (KPIs)
"""

import sqlite3
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import threading
import time
from simulator import simulate_step

st.set_page_config(page_title="Robot Sorting Warehouse Dashboard", layout="wide", page_icon="🤖")

DB_PATH = os.path.join(os.path.dirname(__file__), "warehouse_robot.db")

# Quản lý luồng chạy ngầm của bộ giả lập trong session_state
if "simulator_running" not in st.session_state:
    st.session_state.simulator_running = False

def background_simulator():
    while st.session_state.get("simulator_running", False):
        try:
            simulate_step()
        except Exception:
            pass
        time.sleep(2)

def start_simulator():
    if not st.session_state.simulator_running:
        st.session_state.simulator_running = True
        thread = threading.Thread(target=background_simulator, daemon=True)
        thread.start()

def stop_simulator():
    st.session_state.simulator_running = False

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_data():
    conn = get_connection()
    try:
        df_robots = pd.read_sql_query("SELECT * FROM ThietBiRobot", conn)
        df_categories = pd.read_sql_query("SELECT * FROM LoaiSanPham", conn)
        df_logs = pd.read_sql_query("""
            SELECT 
                l.MaPK, l.MaRobot, r.TenRobot, l.MaSanPham,
                c.TenLoai, l.KhoiLuong, l.ThoiGian, l.TrangThaiPhanLoai, l.GhiChu
            FROM NhatKyPhanLoai l
            JOIN ThietBiRobot r ON l.MaRobot = r.MaRobot
            JOIN LoaiSanPham c ON l.MaLoai = c.MaLoai
            ORDER BY l.MaPK DESC
        """, conn)
        df_alerts = pd.read_sql_query("SELECT * FROM NhatKyCanhBao ORDER BY MaBao DESC LIMIT 10", conn)
    finally:
        conn.close()
    return df_robots, df_categories, df_logs, df_alerts

df_robots, df_categories, df_logs, df_alerts = load_data()

# ----------------- TIÊU ĐỀ HỆ THỐNG -----------------
st.title("🏭 HỆ THỐNG GIÁM SÁT & QUẢN LÝ CÁNH TAY ROBOT")
st.caption("Đề tài: Thu thập và quản lí dữ liệu các cánh tay robot công nghiệp của hệ thống phân loại sản phẩm trong nhà kho tự động.")

# ----------------- THANH ĐIỀU KHIỂN ROBOT TRỰC TIẾP (GỢI Ý 1) -----------------
st.subheader("🕹️ Điều khiển dây chuyền Robot")
ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1.5, 1.5, 1.5, 3.5])

with ctrl1:
    if not st.session_state.simulator_running:
        if st.button("▶️ KHỞI ĐỘNG DÂY CHUYỀN", type="primary", use_container_width=True):
            start_simulator()
            st.rerun()
    else:
        if st.button("⏹️ DỪNG DÂY CHUYỀN", type="secondary", use_container_width=True):
            stop_simulator()
            st.rerun()

with ctrl2:
    if st.button("🔄 Làm mới dữ liệu", use_container_width=True):
        st.rerun()

with ctrl3:
    if st.button("🗑️ Reset nhật ký", use_container_width=True):
        conn = get_connection()
        try:
            conn.execute("DELETE FROM NhatKyPhanLoai")
            conn.execute("DELETE FROM NhatKyCanhBao")
            conn.commit()
            st.success("Đã reset!")
        finally:
            conn.close()
        st.rerun()

with ctrl4:
    if st.session_state.simulator_running:
        st.info("🟢 **DÂY CHUYỀN ĐANG CHẠY NGẦM:** Robot đang tự động gắp hàng mỗi 2 giây. (Bấm F5 hoặc 'Làm mới' để xem số liệu tăng liên tục!)")
    else:
        st.caption("⚪ **Dây chuyền đang tạm dừng.** Bấm 'KHỞI ĐỘNG DÂY CHUYỀN' để robot bắt đầu gắp hàng.")

st.divider()

# ----------------- 4. SỐ LƯỢNG HIỆN TẠI (KPIs) -----------------
st.subheader("📊 1. Thống kê & Số lượng hiện tại")
total_sorted = len(df_logs)
success_count = len(df_logs[df_logs["TrangThaiPhanLoai"] == "ThanhCong"])
fail_count = total_sorted - success_count
success_rate = (success_count / total_sorted * 100) if total_sorted > 0 else 0
active_robots = len(df_robots[df_robots["TrangThai"] == "DangChay"])

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Tổng sản phẩm đã phân loại", f"{total_sorted:,} kiện")
kpi2.metric("Phân loại thành công", f"{success_count:,} kiện", f"{success_rate:.1f}%")
kpi3.metric("Số kiện lỗi / rơi hàng", f"{fail_count:,} kiện", delta_color="inverse")
kpi4.metric("Robot đang chạy (Active)", f"{active_robots} / {len(df_robots)}")

st.divider()

# ----------------- 3. MÁY MÓC ĐANG HOẠT ĐỘNG -----------------
st.subheader("🦾 2. Trạng thái các cánh tay robot công nghiệp")
r_cols = st.columns(len(df_robots))
for idx, (_, row) in enumerate(df_robots.iterrows()):
    with r_cols[idx]:
        status_color = "🟢" if row["TrangThai"] == "DangChay" else ("🟡" if row["TrangThai"] == "SanSang" else "🔴")
        st.markdown(f"### {status_color} {row['MaRobot']}")
        st.write(f"**{row['TenRobot']}**")
        st.write(f"📍 **Vị trí:** {row['ViTriBuaPhanLoai']}")
        st.write(f"⚙️ **Trạng thái:** `{row['TrangThai']}`")
        st.write(f"🌡️ **Nhiệt độ khớp:** `{row['NhietDoKhopNoi']} °C`")
        st.write(f"⚡ **Tốc độ gắp:** `{row['TocDoGap']} sp/phút`")
        st.caption(f"Cập nhật: {row['CapNhatLanCuoi']}")

st.divider()

# ----------------- 1. BIỂU ĐỒ TRỰC QUAN HÓA -----------------
st.subheader("📈 3. Biểu đồ phân tích vận hành")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("##### Số lượng sản phẩm theo từng nhóm phân loại")
    if not df_logs.empty:
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        cat_counts = df_logs["TenLoai"].value_counts().reset_index()
        cat_counts.columns = ["TenLoai", "SoLuong"]
        sns.barplot(data=cat_counts, x="TenLoai", y="SoLuong", palette="Blues_d", ax=ax1)
        ax1.set_xlabel("Loại sản phẩm")
        ax1.set_ylabel("Số lượng đã gắp")
        plt.xticks(rotation=20)
        st.pyplot(fig1)
        plt.close(fig1)
    else:
        st.info("Chưa có dữ liệu để vẽ biểu đồ.")

with chart_col2:
    st.write("##### Hiệu suất phân loại theo từng cánh tay robot")
    if not df_logs.empty:
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        sns.countplot(data=df_logs, x="MaRobot", hue="TrangThaiPhanLoai", palette="Set2", ax=ax2)
        ax2.set_xlabel("Mã cánh tay Robot")
        ax2.set_ylabel("Số lượt gắp")
        ax2.legend(title="Kết quả")
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.info("Chưa có dữ liệu để vẽ biểu đồ.")

st.divider()

# ----------------- 2. TRUY VẤN VÀ BỘ LỌC -----------------
st.subheader("🔍 4. Truy vấn nhật ký phân loại (Query & Filter)")

with st.expander("🛠️ Bộ lọc tìm kiếm dữ liệu", expanded=True):
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        robot_list = ["Tất cả"] + list(df_robots["MaRobot"].unique())
        selected_robot = st.selectbox("Chọn Cánh tay Robot:", robot_list)
        
    with f_col2:
        status_list = ["Tất cả"] + list(df_logs["TrangThaiPhanLoai"].unique())
        selected_status = st.selectbox("Trạng thái phân loại:", status_list)
        
    with f_col3:
        category_list = ["Tất cả"] + list(df_categories["TenLoai"].unique())
        selected_category = st.selectbox("Loại sản phẩm:", category_list)

filtered_logs = df_logs.copy()

if selected_robot != "Tất cả":
    filtered_logs = filtered_logs[filtered_logs["MaRobot"] == selected_robot]

if selected_status != "Tất cả":
    filtered_logs = filtered_logs[filtered_logs["TrangThaiPhanLoai"] == selected_status]

if selected_category != "Tất cả":
    filtered_logs = filtered_logs[filtered_logs["TenLoai"] == selected_category]

# Định dạng tô màu cho bảng dữ liệu: Thành công -> Xanh lá nhẹ, Lỗi/Rơi hàng -> Đỏ nhạt
def highlight_status(row):
    status = row["TrangThaiPhanLoai"]
    if status == "ThanhCong":
        return ["background-color: #d4edda; color: #155724; font-weight: bold;" if col == "TrangThaiPhanLoai" else "" for col in row.index]
    elif status in ["RoiHang", "LoiNhanDien", "SaiThung"]:
        return ["background-color: #f8d7da; color: #721c24; font-weight: bold;" if col == "TrangThaiPhanLoai" else "" for col in row.index]
    return ["" for _ in row.index]

st.write(f"Tìm thấy **{len(filtered_logs)}** bản ghi phù hợp (🟢 Xanh = Thành công | 🔴 Đỏ = Sự cố/Lỗi):")
styled_df = filtered_logs.style.apply(highlight_status, axis=1)
st.dataframe(styled_df, use_container_width=True, hide_index=True)

csv_data = filtered_logs.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Tải kết quả truy vấn (CSV)",
    data=csv_data,
    file_name="nhat_ky_phan_loai.csv",
    mime="text/csv"
)

if not df_alerts.empty:
    with st.expander("⚠️ Nhật ký cảnh báo hệ thống gần nhất"):
        st.dataframe(df_alerts, use_container_width=True, hide_index=True)
