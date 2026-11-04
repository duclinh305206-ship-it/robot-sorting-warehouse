"""
Script chạy xem nhanh toàn bộ kết quả trong CSDL (warehouse_robot.db)
Dành cho việc kiểm tra nhanh ngay trong Terminal VS Code.
"""

import sqlite3
import os
import pandas as pd
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

DB_PATH = os.path.join(os.path.dirname(__file__), "warehouse_robot.db")

def xem_ket_qua():
    conn = sqlite3.connect(DB_PATH)
    
    print("=" * 80)
    print("🤖 1. DANH SÁCH & TRẠNG THÁI CÁC CÁNH TAY ROBOT (ThietBiRobot)")
    print("=" * 80)
    df_robots = pd.read_sql_query("SELECT MaRobot, TenRobot, TrangThai, NhietDoKhopNoi, TocDoGap, CapNhatLanCuoi FROM ThietBiRobot", conn)
    print(df_robots.to_string(index=False))
    
    print("\n" + "=" * 80)
    print("📦 2. DANH MỤC PHÂN LOẠI HÀNG HÓA (LoaiSanPham)")
    print("=" * 80)
    df_cats = pd.read_sql_query("SELECT * FROM LoaiSanPham", conn)
    print(df_cats.to_string(index=False))
    
    print("\n" + "=" * 80)
    print("📋 3. NHẬT KÝ PHÂN LOẠI GẦN NHẤT (NhatKyPhanLoai - 10 dòng mới nhất)")
    print("=" * 80)
    df_logs = pd.read_sql_query("""
        SELECT 
            l.MaPK, l.MaRobot, l.MaSanPham, c.TenLoai, 
            l.KhoiLuong, l.ThoiGian, l.TrangThaiPhanLoai
        FROM NhatKyPhanLoai l
        JOIN LoaiSanPham c ON l.MaLoai = c.MaLoai
        ORDER BY l.MaPK DESC
        LIMIT 10
    """, conn)
    print(df_logs.to_string(index=False))

    print("\n" + "=" * 80)
    print("📊 4. TỔNG HỢP NĂNG SUẤT GẮP THEO TỪNG ROBOT (SQL GROUP BY)")
    print("=" * 80)
    df_stats = pd.read_sql_query("""
        SELECT 
            MaRobot,
            COUNT(*) AS TongSoKien,
            SUM(CASE WHEN TrangThaiPhanLoai = 'ThanhCong' THEN 1 ELSE 0 END) AS ThanhCong,
            SUM(CASE WHEN TrangThaiPhanLoai != 'ThanhCong' THEN 1 ELSE 0 END) AS SoKienLoi
        FROM NhatKyPhanLoai
        GROUP BY MaRobot
    """, conn)
    print(df_stats.to_string(index=False))
    print("=" * 80)

    conn.close()

if __name__ == "__main__":
    xem_ket_qua()
