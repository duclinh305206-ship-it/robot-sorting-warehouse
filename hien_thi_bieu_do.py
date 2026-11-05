"""
Hiển thị biểu đồ phân tích và bảng số liệu riêng biệt (dạng cửa sổ đồ họa popup)
Sử dụng trực tiếp Matplotlib và Seaborn.
"""

import sqlite3
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Cấu hình tiếng Việt / hiển thị đẹp cho Matplotlib
plt.rcParams['font.sans-serif'] = 'Segoe UI'
plt.rcParams['axes.unicode_minus'] = False

DB_PATH = os.path.join(os.path.dirname(__file__), "warehouse_robot.db")

def hien_thi_bieu_do_va_so_lieu():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Đọc dữ liệu nhật ký phân loại và robot
    df_logs = pd.read_sql_query("""
        SELECT 
            l.MaPK, l.MaRobot, r.TenRobot, l.MaSanPham,
            c.TenLoai, l.KhoiLuong, l.ThoiGian, l.TrangThaiPhanLoai
        FROM NhatKyPhanLoai l
        JOIN ThietBiRobot r ON l.MaRobot = r.MaRobot
        JOIN LoaiSanPham c ON l.MaLoai = c.MaLoai
        ORDER BY l.MaPK DESC
    """, conn)
    
    df_robots = pd.read_sql_query("SELECT * FROM ThietBiRobot", conn)
    conn.close()

    if df_logs.empty:
        print("Chưa có dữ liệu phân loại trong database!")
        return

    # 2. In số liệu thống kê ra màn hình Console
    print("=" * 75)
    print("📊 BẢNG TỔNG HỢP SỐ LIỆU PHÂN LOẠI ROBOT")
    print("=" * 75)
    total_sorted = len(df_logs)
    success_count = len(df_logs[df_logs["TrangThaiPhanLoai"] == "ThanhCong"])
    fail_count = total_sorted - success_count
    rate = (success_count / total_sorted * 100) if total_sorted > 0 else 0
    
    print(f"• Tổng số kiện đã gắp:     {total_sorted} kiện")
    print(f"• Phân loại thành công:    {success_count} kiện ({rate:.1f}%)")
    print(f"• Lỗi / Rơi hàng:          {fail_count} kiện")
    print("-" * 75)
    
    # Bảng gom nhóm theo Robot
    stats_robot = df_logs.groupby("MaRobot").agg(
        TongKien=('MaPK', 'count'),
        ThanhCong=('TrangThaiPhanLoai', lambda x: (x == 'ThanhCong').sum()),
        Loi=('TrangThaiPhanLoai', lambda x: (x != 'ThanhCong').sum())
    ).reset_index()
    print("SỐ LIỆU THEO TỪNG ROBOT:")
    print(stats_robot.to_string(index=False))
    print("=" * 75)

    # 3. Tạo cửa sổ đồ họa riêng (Figure Window) với 2 biểu đồ
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.canvas.manager.set_window_title("HỆ THỐNG PHÂN TÍCH BIỂU ĐỒ CÁNH TAY ROBOT")

    # Biểu đồ 1: Số lượng sản phẩm theo từng nhóm phân loại (Barplot)
    cat_counts = df_logs["TenLoai"].value_counts().reset_index()
    cat_counts.columns = ["TenLoai", "SoLuong"]
    sns.barplot(data=cat_counts, x="TenLoai", y="SoLuong", palette="Blues_r", ax=ax1)
    ax1.set_title("Số lượng kiện hàng theo từng nhóm phân loại", fontsize=13, fontweight='bold', pad=12)
    ax1.set_xlabel("Loại sản phẩm", fontsize=11)
    ax1.set_ylabel("Số lượng đã gắp", fontsize=11)
    ax1.tick_params(axis='x', rotation=15)
    for p in ax1.patches:
        ax1.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='bottom', fontsize=10, xytext=(0, 3), textcoords='offset points')

    # Biểu đồ 2: So sánh hiệu suất từng cánh tay robot (Countplot với hue)
    sns.countplot(data=df_logs, x="MaRobot", hue="TrangThaiPhanLoai", palette="Set2", ax=ax2)
    ax2.set_title("Hiệu suất gắp hàng của từng cánh tay Robot", fontsize=13, fontweight='bold', pad=12)
    ax2.set_xlabel("Mã cánh tay Robot", fontsize=11)
    ax2.set_ylabel("Số lượt gắp", fontsize=11)
    ax2.legend(title="Kết quả gắp")
    for p in ax2.patches:
        val = int(p.get_height()) if not pd.isna(p.get_height()) else 0
        if val > 0:
            ax2.annotate(f"{val}", (p.get_x() + p.get_width() / 2., p.get_height()),
                         ha='center', va='bottom', fontsize=10, xytext=(0, 3), textcoords='offset points')

    plt.suptitle(f"BÁO CÁO GIÁM SÁT VẬN HÀNH NHÀ KHO (Tổng: {total_sorted} kiện - Tỷ lệ đạt: {rate:.1f}%)", fontsize=15, fontweight='bold', color='#003366')
    plt.tight_layout()

    print("\n-> Đang mở cửa sổ biểu đồ riêng... (Đóng cửa sổ biểu đồ để hoàn tất)")
    # Mở cửa sổ biểu đồ popup riêng biệt
    plt.show()

if __name__ == "__main__":
    hien_thi_bieu_do_va_so_lieu()
