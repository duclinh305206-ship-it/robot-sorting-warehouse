-- ==============================================================================
-- CƠ SỞ DỮ LIỆU: THU THẬP VÀ QUẢN LÝ DỮ LIỆU CÁNH TAY ROBOT PHÂN LOẠI SẢN PHẨM
-- Hệ thống phân loại sản phẩm trong nhà kho thông minh tự động
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- 1. Bảng Cánh tay robot công nghiệp
CREATE TABLE IF NOT EXISTS ThietBiRobot (
    MaRobot TEXT PRIMARY KEY NOT NULL,          -- Ví dụ: 'RB01', 'RB02'
    TenRobot TEXT NOT NULL,                     -- Tên robot phân loại
    ViTriBuaPhanLoai TEXT NOT NULL,             -- Khu vực làm việc: 'BangTai_A1', 'BangTai_A2'
    TrangThai TEXT NOT NULL CHECK(TrangThai IN ('DangChay', 'SanSang', 'BaoTri', 'Loi')),
    NhietDoKhopNoi REAL NOT NULL DEFAULT 40.0,  -- Nhiệt độ động cơ (°C)
    TocDoGap REAL NOT NULL DEFAULT 25.0,        -- Chu kỳ gắp (sản phẩm/phút)
    LanBaoTriCuoi TEXT,
    CapNhatLanCuoi TEXT NOT NULL
);

-- 2. Bảng Danh mục phân loại sản phẩm
CREATE TABLE IF NOT EXISTS LoaiSanPham (
    MaLoai TEXT PRIMARY KEY NOT NULL,           -- 'SP_TIEUCHUAN', 'SP_CONGKENG', 'SP_DEVO'
    TenLoai TEXT NOT NULL,                      -- Tên nhóm hàng
    ThungDich TEXT NOT NULL,                    -- Vị trí thùng/khay chứa đích: 'BIN_01', 'BIN_02'
    KhoiLuongChuan REAL NOT NULL                -- Khối lượng chuẩn (kg)
);

-- 3. Bảng Nhật ký phân loại sản phẩm (Dữ liệu hoạt động cốt lõi)
CREATE TABLE IF NOT EXISTS NhatKyPhanLoai (
    MaPK INTEGER PRIMARY KEY AUTOINCREMENT,
    MaRobot TEXT NOT NULL REFERENCES ThietBiRobot(MaRobot),
    MaSanPham TEXT NOT NULL,                    -- Mã Barcode / QR: 'PRD-100234'
    MaLoai TEXT NOT NULL REFERENCES LoaiSanPham(MaLoai),
    KhoiLuong REAL NOT NULL,                    -- Khối lượng đo được (kg)
    ThoiGian TEXT NOT NULL,                     -- Thời điểm robot thực hiện gắp phân loại
    TrangThaiPhanLoai TEXT NOT NULL CHECK(TrangThaiPhanLoai IN ('ThanhCong', 'LoiNhanDien', 'RoiHang', 'SaiThung')),
    GhiChu TEXT
);

-- 4. Bảng Lịch sử Cảm biến & Cảnh báo sức khỏe robot
CREATE TABLE IF NOT EXISTS NhatKyCanhBao (
    MaBao INTEGER PRIMARY KEY AUTOINCREMENT,
    MaRobot TEXT NOT NULL REFERENCES ThietBiRobot(MaRobot),
    ThoiGian TEXT NOT NULL,
    LoaiCanhBao TEXT NOT NULL CHECK(LoaiCanhBao IN ('CanhBaoNhiet', 'LoiDongCo', 'LoiKipGap', 'GiamTocDo')),
    MucDo TEXT NOT NULL CHECK(MucDo IN ('Thap', 'TrungBinh', 'NghiemTrong')),
    NoiDung TEXT NOT NULL
);

-- Tạo Index để truy vấn và vẽ biểu đồ nhanh
CREATE INDEX IF NOT EXISTS idx_phanloai_thoigian ON NhatKyPhanLoai(ThoiGian);
CREATE INDEX IF NOT EXISTS idx_phanloai_robot ON NhatKyPhanLoai(MaRobot);
CREATE INDEX IF NOT EXISTS idx_phanloai_trangthai ON NhatKyPhanLoai(TrangThaiPhanLoai);

-- ==============================================================================
-- DỮ LIỆU BAN ĐẦU (SEED DATA)
-- ==============================================================================

INSERT OR IGNORE INTO ThietBiRobot (MaRobot, TenRobot, ViTriBuaPhanLoai, TrangThai, NhietDoKhopNoi, TocDoGap, LanBaoTriCuoi, CapNhatLanCuoi) VALUES
('RB01', 'Cánh tay Robot Delta 01', 'Khu Tiếp Nhận - Line 1', 'DangChay', 46.5, 32.0, '2026-10-01', datetime('now', 'localtime')),
('RB02', 'Cánh tay Robot Delta 02', 'Khu Tiếp Nhận - Line 2', 'DangChay', 44.2, 30.0, '2026-10-05', datetime('now', 'localtime')),
('RB03', 'Cánh tay Robot 6 Trục 01', 'Khu Phân Loại Hàng Nặng', 'SanSang', 38.0, 18.5, '2026-09-20', datetime('now', 'localtime')),
('RB04', 'Cánh tay Robot SCARA 01', 'Khu Đóng Gói Hoàn Thiện', 'BaoTri', 35.0, 0.0, '2026-10-25', datetime('now', 'localtime'));

INSERT OR IGNORE INTO LoaiSanPham (MaLoai, TenLoai, ThungDich, KhoiLuongChuan) VALUES
('SP_TIEUCHUAN', 'Hàng Tiêu Chuẩn (Hộp Carton)', 'BIN_A', 1.5),
('SP_CONGKENG', 'Hàng Cồng Kềnh / Quá Khổ', 'BIN_B', 5.0),
('SP_DEVO', 'Hàng Dễ Vỡ (Thủy Tinh/Gốm)', 'BIN_C', 0.8),
('SP_DIENTU', 'Linh Kiện Điện Tử', 'BIN_D', 0.5);

INSERT OR IGNORE INTO NhatKyPhanLoai (MaRobot, MaSanPham, MaLoai, KhoiLuong, ThoiGian, TrangThaiPhanLoai, GhiChu) VALUES
('RB01', 'PKG-1001', 'SP_TIEUCHUAN', 1.48, datetime('now', '-30 minutes', 'localtime'), 'ThanhCong', 'Phân loại đúng đích'),
('RB01', 'PKG-1002', 'SP_DEVO', 0.81, datetime('now', '-28 minutes', 'localtime'), 'ThanhCong', 'Gắp nhẹ nhàng'),
('RB02', 'PKG-1003', 'SP_CONGKENG', 5.12, datetime('now', '-25 minutes', 'localtime'), 'ThanhCong', 'Phân loại đúng đích'),
('RB01', 'PKG-1004', 'SP_DIENTU', 0.52, datetime('now', '-22 minutes', 'localtime'), 'ThanhCong', 'Phân loại đúng đích'),
('RB02', 'PKG-1005', 'SP_TIEUCHUAN', 1.60, datetime('now', '-20 minutes', 'localtime'), 'RoiHang', 'Lực hút kẹp không đủ'),
('RB01', 'PKG-1006', 'SP_TIEUCHUAN', 1.51, datetime('now', '-18 minutes', 'localtime'), 'ThanhCong', 'Phân loại đúng đích'),
('RB02', 'PKG-1007', 'SP_DEVO', 0.79, datetime('now', '-15 minutes', 'localtime'), 'ThanhCong', 'Phân loại đúng đích'),
('RB01', 'PKG-1008', 'SP_CONGKENG', 5.40, datetime('now', '-12 minutes', 'localtime'), 'LoiNhanDien', 'Mã vạch mờ'),
('RB02', 'PKG-1009', 'SP_DIENTU', 0.49, datetime('now', '-10 minutes', 'localtime'), 'ThanhCong', 'Phân loại đúng đích'),
('RB01', 'PKG-1010', 'SP_TIEUCHUAN', 1.47, datetime('now', '-5 minutes', 'localtime'), 'ThanhCong', 'Phân loại đúng đích');
