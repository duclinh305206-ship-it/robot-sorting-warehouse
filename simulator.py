"""
Bộ giả lập dữ liệu cánh tay robot phân loại sản phẩm (Simulator)
Mô phỏng động học 3 bậc tự do (3-DOF), góc quay và thời gian hành trình.
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

# Góc định vị chuẩn tương ứng với từng thùng phân loại đích (BIN_A, BIN_B, BIN_C, BIN_D)
TARGET_BIN_ANGLES = {
    "SP_TIEUCHUAN": -45.0,  # Thùng BIN_A ở góc -45 độ
    "SP_CONGKENG": 60.0,    # Thùng BIN_B ở góc +60 độ
    "SP_DEVO": -20.0,       # Thùng BIN_C ở góc -20 độ
    "SP_DIENTU": 35.0       # Thùng BIN_D ở góc +35 độ
}

SIMULATOR_STOP_EVENT = False

def simulate_step():
    global SIMULATOR_STOP_EVENT
    if SIMULATOR_STOP_EVENT:
        return

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

    # ĐỘNG HỌC 3 BẬC TỰ DO (3-DOF KINEMATICS):
    # Bậc 1: Góc xoay đế theo vị trí thùng đích (cộng rung sai số ±2 độ)
    base_angle = TARGET_BIN_ANGLES.get(cat_id, 0.0)
    goc_bac1 = round(base_angle + random.uniform(-2.0, 2.0), 1)
    # Bậc 2: Góc hạ cánh tay nâng (gắp hàng thường ở 65 - 85 độ)
    goc_bac2 = round(random.uniform(65.0, 85.0), 1)
    # Bậc 3: Góc xoay cổ tay điều chỉnh đầu kẹp (-25 đến +25 độ)
    goc_bac3 = round(random.uniform(-25.0, 25.0), 1)

    # HÀNH TRÌNH THỜI GIAN:
    # Chu kỳ hoàn thành gắp hàng từ băng tải tới thùng đích (1.2 đến 2.6 giây)
    thoi_gian_hanh_trinh = round(random.uniform(1.2, 2.6), 2)

    new_temp = round(random.uniform(41.0, 52.0), 1)
    new_speed = round(random.uniform(26.0, 35.0), 1)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 1. Ghi nhật ký phân loại đầy đủ góc 3 bậc & thời gian hành trình
    cur.execute("""
        INSERT INTO NhatKyPhanLoai (
            MaRobot, MaSanPham, MaLoai, KhoiLuong, ThoiGian, 
            TrangThaiPhanLoai, GocBac1, GocBac2, GocBac3, ThoiGianHanhTrinh, GhiChu
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (robot_id, barcode, cat_id, weight, now_str, status, goc_bac1, goc_bac2, goc_bac3, thoi_gian_hanh_trinh, "Giả lập 3-DOF"))

    # 2. Cập nhật góc quay hiện tại và kiện hàng đang tham gia cho Robot
    cur.execute("""
        UPDATE ThietBiRobot
        SET NhietDoKhopNoi = ?, TocDoGap = ?, CapNhatLanCuoi = ?,
            GocBac1 = ?, GocBac2 = ?, GocBac3 = ?, KienHangHienTai = ?
        WHERE MaRobot = ?
    """, (new_temp, new_speed, now_str, goc_bac1, goc_bac2, goc_bac3, barcode, robot_id))

    # Cảnh báo nếu nhiệt độ vượt ngưỡng 50 độ
    if new_temp > 50.0:
        cur.execute("""
            INSERT INTO NhatKyCanhBao (MaRobot, ThoiGian, LoaiCanhBao, MucDo, NoiDung)
            VALUES (?, ?, 'CanhBaoNhiet', 'TrungBinh', ?)
        """, (robot_id, now_str, f"Khớp nối {robot_id} đạt {new_temp}°C, cần chú ý làm mát."))

    conn.commit()
    conn.close()
    print(f"[{now_str}] {robot_id} gắp {barcode} -> Bậc 1: {goc_bac1}° | Bậc 2: {goc_bac2}° | Bậc 3: {goc_bac3}° | Hành trình: {thoi_gian_hanh_trinh}s ({status})")

def run_loop(interval=2, count=None):
    global SIMULATOR_STOP_EVENT
    print("=== BẮT ĐẦU GIẢ LẬP CÁNH TAY ROBOT 3 BẬC (Ctrl+C để dừng) ===")
    step = 0
    try:
        while not SIMULATOR_STOP_EVENT:
            simulate_step()
            step += 1
            if count and step >= count:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nĐã dừng bộ giả lập.")

if __name__ == "__main__":
    run_loop(interval=2, count=None)
