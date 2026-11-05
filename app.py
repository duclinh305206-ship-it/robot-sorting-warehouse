"""
ỨNG DỤNG GIÁM SÁT & QUẢN LÝ CÁNH TAY ROBOT PHÂN LOẠI SẢN PHẨM (STREAMLIT)
Phiên bản Nâng cao: Động học 3 Bậc tự do (3-DOF), Góc quay, Hành trình & Kiện hàng tham gia.
"""

import sqlite3
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import threading
import time
from streamlit_autorefresh import st_autorefresh
from simulator import simulate_step

st.set_page_config(page_title="Hệ Thống Giám Sát Robot 3 Bậc", layout="wide", page_icon="🦾")

# TỰ ĐỘNG LÀM MỚI MỖI 2 GIÂY (LIVE REAL-TIME STREAMING KHÔNG CẦN BẤM NÚT)
st_autorefresh(interval=2000, key="robot_live_refresh")

# Cấu hình font cho Matplotlib
plt.rcParams['font.sans-serif'] = 'Segoe UI'
plt.rcParams['axes.unicode_minus'] = False

DB_PATH = os.path.join(os.path.dirname(__file__), "warehouse_robot.db")

# Biến kiểm soát dừng chạy luồng ngầm cấp tiến trình
STOP_FLAG_FILE = os.path.join(os.path.dirname(__file__), ".simulator_running")

def background_simulator():
    while os.path.exists(STOP_FLAG_FILE):
        try:
            simulate_step()
        except Exception:
            pass
        time.sleep(2)

def start_simulator():
    if not os.path.exists(STOP_FLAG_FILE):
        with open(STOP_FLAG_FILE, "w") as f:
            f.write("running")
        st.session_state.simulator_running = True
        thread = threading.Thread(target=background_simulator, daemon=True)
        thread.start()

def stop_simulator():
    if os.path.exists(STOP_FLAG_FILE):
        os.remove(STOP_FLAG_FILE)
    st.session_state.simulator_running = False

is_running = os.path.exists(STOP_FLAG_FILE)
st.session_state.simulator_running = is_running

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
                c.TenLoai, l.KhoiLuong, l.ThoiGian, l.TrangThaiPhanLoai,
                l.GocBac1, l.GocBac2, l.GocBac3, l.ThoiGianHanhTrinh, l.GhiChu
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

# ----------------- BANNER THÔNG BÁO VỪA GẮP THÀNH CÔNG KIỆN HÀNG MỚI -----------------
if not df_logs.empty:
    latest_item = df_logs.iloc[0]
    st.success(f"""
    📦 **VỪA GẮP THÀNH CÔNG:** Robot **{latest_item['MaRobot']}** ({latest_item['TenRobot']}) vừa phân loại xong kiện **`{latest_item['MaSanPham']}`** | 
    Nhóm: **{latest_item['TenLoai']}** ({latest_item['KhoiLuong']} kg) | 
    🔄 Góc 3 bậc: `B1: {latest_item['GocBac1']}°`, `B2: {latest_item['GocBac2']}°`, `B3: {latest_item['GocBac3']}°` | 
    ⚡ Hành trình: `{latest_item['ThoiGianHanhTrinh']} giây` | Lúc `{latest_item['ThoiGian']}`
    """)

# ----------------- THANH ĐIỀU KHIỂN DÂY CHUYỀN -----------------
st.subheader("🕹️ Điều khiển vận hành dây chuyền")
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
            conn.execute("UPDATE ThietBiRobot SET KienHangHienTai = '--', GocBac1 = 0.0, GocBac2 = 45.0, GocBac3 = 0.0")
            conn.commit()
            st.success("Đã reset!")
        finally:
            conn.close()
        st.rerun()

with ctrl4:
    if st.session_state.simulator_running:
        st.info("🟢 **DÂY CHUYỀN ĐANG CHẠY:** Robot đang gắp hàng và xoay các góc bậc ngầm. Bấm F5 hoặc 'Làm mới' để xem số liệu cập nhật.")
    else:
        st.caption("⚪ **Dây chuyền đang tạm dừng.** Bấm 'KHỞI ĐỘNG' để kích hoạt cánh tay robot gắp hàng.")

st.divider()

# ----------------- 1. SỐ LƯỢNG HIỆN TẠI (KPIs) -----------------
st.subheader("📊 1. Thống kê & Số lượng hiện tại")
total_sorted = len(df_logs)
success_count = len(df_logs[df_logs["TrangThaiPhanLoai"] == "ThanhCong"])
fail_count = total_sorted - success_count
success_rate = (success_count / total_sorted * 100) if total_sorted > 0 else 0
active_robots = len(df_robots[df_robots["TrangThai"] == "DangChay"])
avg_cycle = df_logs["ThoiGianHanhTrinh"].mean() if not df_logs.empty else 0.0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Tổng sản phẩm đã gắp", f"{total_sorted:,} kiện")
kpi2.metric("Phân loại thành công", f"{success_count:,} kiện", f"{success_rate:.1f}%")
kpi3.metric("Số kiện lỗi / rơi", f"{fail_count:,} kiện", delta_color="inverse")
kpi4.metric("Robot đang chạy", f"{active_robots} / {len(df_robots)}")
kpi5.metric("Chu kỳ hành trình TB", f"{avg_cycle:.2f} giây")

st.divider()

# ----------------- 2. MÁY MÓC ĐANG HOẠT ĐỘNG & GÓC QUAY 3 BẬC -----------------
st.subheader("🦾 2. Giám sát Động học & Góc quay Cánh tay Robot (3 Bậc Tự Do)")
r_cols = st.columns(len(df_robots))

for idx, (_, row) in enumerate(df_robots.iterrows()):
    with r_cols[idx]:
        status_color = "🟢" if row["TrangThai"] == "DangChay" else ("🟡" if row["TrangThai"] == "SanSang" else "🔴")
        st.markdown(f"### {status_color} {row['MaRobot']}")
        st.write(f"**{row['TenRobot']}**")
        st.write(f"📍 **Vị trí:** `{row['ViTriBuaPhanLoai']}`")
        st.write(f"📦 **Kiện đang tham gia:** `{row.get('KienHangHienTai', '--')}`")
        
        # Hộp hiển thị góc quay 3 bậc
        st.info(f"""
        **GÓC QUAY 3 BẬC HIỆN TẠI:**
        - 🔄 **Bậc 1 (Đế xoay):** `{row.get('GocBac1', 0.0)}°`
        - 📐 **Bậc 2 (Cánh tay nâng):** `{row.get('GocBac2', 45.0)}°`
        - ✋ **Bậc 3 (Cổ tay kẹp):** `{row.get('GocBac3', 0.0)}°`
        """)

        # TÍNH TOÁN VÀ VẼ ĐỒNG HỒ ĐO HIỆU SUẤT OEE
        r_logs = df_logs[df_logs["MaRobot"] == row["MaRobot"]]
        r_total = len(r_logs)
        if r_total > 0:
            # 1. Availability: Mức sẵn sàng (nếu đang chạy là 95%, sẵn sàng 80%, bảo trì 0%)
            avail = 0.95 if row["TrangThai"] == "DangChay" else (0.80 if row["TrangThai"] == "SanSang" else 0.0)
            # 2. Performance: Hiệu suất tốc độ gắp (so với chuẩn 35 sp/phút)
            perf = min(1.0, row["TocDoGap"] / 35.0)
            # 3. Quality: Tỷ lệ hàng đạt (thành công / tổng số)
            r_success = len(r_logs[r_logs["TrangThaiPhanLoai"] == "ThanhCong"])
            qual = r_success / r_total
            oee_val = round(avail * perf * qual * 100, 1)
        else:
            oee_val = 85.0 if row["TrangThai"] == "DangChay" else 0.0

        # Thanh đo phần trăm OEE
        st.write(f"📈 **Chỉ số OEE (Hiệu suất):** `{oee_val}%`")
        oee_color = "🟢 Tốt" if oee_val >= 80 else ("🟡 Trung bình" if oee_val >= 60 else "🔴 Kém")
        st.progress(min(1.0, max(0.0, oee_val / 100.0)), text=f"Đánh giá OEE: {oee_color}")
        
        st.write(f"🌡️ **Nhiệt độ khớp:** `{row['NhietDoKhopNoi']} °C`")
        st.write(f"⚡ **Tốc độ:** `{row['TocDoGap']} sp/phút`")
        st.caption(f"Cập nhật: {row['CapNhatLanCuoi']}")

st.divider()

# ----------------- 3. BIỂU ĐỒ TRỰC QUAN HÓA -----------------
st.subheader("📈 3. Biểu đồ phân tích vận hành & Hành trình")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("##### Số lượng sản phẩm theo từng nhóm phân loại")
    if not df_logs.empty:
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        cat_counts = df_logs["TenLoai"].value_counts().reset_index()
        cat_counts.columns = ["TenLoai", "SoLuong"]
        sns.barplot(data=cat_counts, x="TenLoai", y="SoLuong", palette="Blues_r", ax=ax1)
        ax1.set_xlabel("Loại sản phẩm")
        ax1.set_ylabel("Số lượng đã gắp")
        plt.xticks(rotation=15)
        for p in ax1.patches:
            ax1.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                         ha='center', va='bottom', fontsize=9, xytext=(0, 2), textcoords='offset points')
        st.pyplot(fig1)
        plt.close(fig1)
    else:
        st.info("Chưa có dữ liệu để vẽ biểu đồ.")

with chart_col2:
    st.write("##### Phân bổ Thời gian hành trình gắp hàng (Giây)")
    if not df_logs.empty:
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        sns.boxplot(data=df_logs, x="MaRobot", y="ThoiGianHanhTrinh", palette="Set2", ax=ax2)
        ax2.set_xlabel("Mã cánh tay Robot")
        ax2.set_ylabel("Thời gian hành trình (giây)")
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.info("Chưa có dữ liệu để vẽ biểu đồ.")

st.divider()

# ----------------- 4. TRUY VẤN VÀ BỘ LỌC (CÓ CÁC CỘT GÓC QUAY 3 BẬC) -----------------
st.subheader("🔍 4. Truy vấn nhật ký phân loại (Góc quay & Hành trình)")

with st.expander("🛠️ Bộ lọc tìm kiếm dữ liệu", expanded=True):
    f_col1, f_col2, f_col3 = st.columns(3)
    
    with f_col1:
        robot_list = ["Tất cả"] + list(df_robots["MaRobot"].unique())
        selected_robot = st.selectbox("Chọn Cánh tay Robot:", robot_list)
        
    with f_col2:
        status_list = ["Tất cả"] + list(df_logs["TrangThaiPhanLoai"].unique()) if not df_logs.empty else ["Tất cả"]
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

# Tô màu trạng thái
def highlight_status(row):
    status = row["TrangThaiPhanLoai"]
    if status == "ThanhCong":
        return ["background-color: #d4edda; color: #155724; font-weight: bold;" if col == "TrangThaiPhanLoai" else "" for col in row.index]
    elif status in ["RoiHang", "LoiNhanDien", "SaiThung"]:
        return ["background-color: #f8d7da; color: #721c24; font-weight: bold;" if col == "TrangThaiPhanLoai" else "" for col in row.index]
    return ["" for _ in row.index]

st.write(f"Tìm thấy **{len(filtered_logs)}** bản ghi phù hợp (🟢 Xanh = Thành công | 🔴 Đỏ = Lỗi):")
styled_df = filtered_logs.style.apply(highlight_status, axis=1)
st.dataframe(styled_df, use_container_width=True, hide_index=True)

csv_data = filtered_logs.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Tải kết quả truy vấn (CSV)",
    data=csv_data,
    file_name="nhat_ky_phan_loai_3dof.csv",
    mime="text/csv"
)

if not df_alerts.empty:
    with st.expander("⚠️ Nhật ký cảnh báo hệ thống gần nhất"):
        st.dataframe(df_alerts, use_container_width=True, hide_index=True)
