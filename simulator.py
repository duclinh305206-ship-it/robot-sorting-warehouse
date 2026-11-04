"""
Bộ giả lập dữ liệu cánh tay robot phân loại sản phẩm (Simulator)
Chạy ngầm để định kỳ sinh dữ liệu gắp hàng và cập nhật trạng thái robot vào SQLite.
"""

import sqlite3
import random
import time
import os
import sys
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), "warehouse_robot.db")

ROBOTS = ["RB01", "RB02", "RB03"]
CATEGORIES = ["SP_TIEUCHUAN", "SP_CONGKENG", "SP_DEVO", "SP_DIENTU"]
STATUS_OPTIONS = ["ThanhCong", "ThanhCong", "ThanhCong", "ThanhCong", "ThanhCong", "ThanhCong", "RoiHang", "LoiNhanDien"]

def simulate_step():
    robot_id = random.choice(ROBOTS)
    cat_id = random.choice(CATEGORIES)
    status = random.choice(STATUS_OPTIONS)
    
    base_weights = {
        "SP_TIEUCHUAN": 1.5,
        "SP_CONGKENG": 5.0,
        "SP_DEVO": 0.8,
        "SP_DIENTU": 0.5
    }
    weight = round(base_weights[cat_id] + random.uniform(-0.15, 0.15), 2)
    barcode = f"PKG-{random.randint(10000, 99999)}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_temp = round(random.uniform(41.0, 52.0), 1)
    new_speed = round(random.uniform(26.0, 35.0), 1)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO NhatKyPhanLoai (MaRobot, MaSanPham, MaLoai, KhoiLuong, ThoiGian, TrangThaiPhanLoai, GhiChu)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (robot_id, barcode, cat_id, weight, now_str, status, "Giả lập tự động"))

    cur.execute("""
        UPDATE ThietBiRobot
        SET NhietDoKhopNoi = ?, TocDoGap = ?, CapNhatLanCuoi = ?
        WHERE MaRobot = ?
    """, (new_temp, new_speed, now_str, robot_id))

    if new_temp > 50.0:
        cur.execute("""
            INSERT INTO NhatKyCanhBao (MaRobot, ThoiGian, LoaiCanhBao, MucDo, NoiDung)
            VALUES (?, ?, 'CanhBaoNhiet', 'TrungBinh', ?)
        """, (robot_id, now_str, f"Khớp nối {robot_id} đạt {new_temp}°C, cần chú ý làm mát."))

    conn.commit()
    conn.close()
    print(f"[{now_str}] Robot {robot_id} -> Gắp {barcode} ({cat_id}) -> Kết quả: {status} | Temp: {new_temp}°C")

def run_loop(interval=3, count=None):
    print("=== BẮT ĐẦU GIẢ LẬP CÁNH TAY ROBOT (Ctrl+C để dừng) ===")
    step = 0
    try:
        while True:
            simulate_step()
            step += 1
            if count and step >= count:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nĐã dừng bộ giả lập.")

if __name__ == "__main__":
    # Chạy liên tục không ngừng (mỗi 2 giây gắp 1 kiện). Muốn dừng bấm Ctrl + C
    run_loop(interval=2, count=None)
