-- ==============================================================================
-- CƠ SỞ DỮ LIỆU: THU THẬP VÀ QUẢN LÝ DỮ LIỆU CÁNH TAY ROBOT PHÂN LOẠI SẢN PHẨM
-- Hệ thống phân loại sản phẩm trong nhà kho thông minh tự động (3 Bậc Tự Do - 3-DOF)
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- 1. Bảng Cánh tay robot công nghiệp (Có góc quay 3 bậc và kiện hàng tham gia)
CREATE TABLE IF NOT EXISTS ThietBiRobot (
    MaRobot TEXT PRIMARY KEY NOT NULL,          -- Ví dụ: 'RB01', 'RB02'
    TenRobot TEXT NOT NULL,                     -- Tên robot phân loại
    ViTriBuaPhanLoai TEXT NOT NULL,             -- Khu vực làm việc: 'Line 1', 'Line 2'
    TrangThai TEXT NOT NULL CHECK(TrangThai IN ('DangChay', 'SanSang', 'BaoTri', 'Loi')),
    NhietDoKhopNoi REAL NOT NULL DEFAULT 40.0,  -- Nhiệt độ động cơ (°C)
    TocDoGap REAL NOT NULL DEFAULT 25.0,        -- Chu kỳ gắp (sản phẩm/phút)
    GocBac1 REAL NOT NULL DEFAULT 0.0,          -- Góc quay đế xoay Joint 1 (-90° đến +90°)
    GocBac2 REAL NOT NULL DEFAULT 45.0,         -- Góc nâng cánh tay dưới Joint 2 (0° đến 120°)
    GocBac3 REAL NOT NULL DEFAULT 0.0,          -- Góc xoay cổ tay kẹp Joint 3 (-45° đến +45°)
    KienHangHienTai TEXT DEFAULT '--',          -- Kiện hàng robot vừa gắp / đang tham gia
    LanBaoTriCuoi TEXT,
    CapNhatLanCuoi TEXT NOT NULL
);

-- 2. Bảng Danh mục phân loại sản phẩm
CREATE TABLE IF NOT EXISTS LoaiSanPham (
    MaLoai TEXT PRIMARY KEY NOT NULL,           -- 'SP_TIEUCHUAN', 'SP_CONGKENG', 'SP_DEVO'
    TenLoai TEXT NOT NULL,                      -- Tên nhóm hàng
    ThungDich TEXT NOT NULL,                    -- Vị trí thùng/khay chứa đích: 'BIN_A', 'BIN_B'
    KhoiLuongChuan REAL NOT NULL                -- Khối lượng chuẩn (kg)
);

-- 3. Bảng Nhật ký phân loại sản phẩm (Có góc quay và thời gian hành trình)
CREATE TABLE IF NOT EXISTS NhatKyPhanLoai (
    MaPK INTEGER PRIMARY KEY AUTOINCREMENT,
    MaRobot TEXT NOT NULL REFERENCES ThietBiRobot(MaRobot),
    MaSanPham TEXT NOT NULL,                    -- Mã Barcode / QR: 'PKG-100234'
    MaLoai TEXT NOT NULL REFERENCES LoaiSanPham(MaLoai),
    KhoiLuong REAL NOT NULL,                    -- Khối lượng đo được (kg)
    ThoiGian TEXT NOT NULL,                     -- Thời điểm robot thực hiện gắp phân loại
    TrangThaiPhanLoai TEXT NOT NULL CHECK(TrangThaiPhanLoai IN ('ThanhCong', 'LoiNhanDien', 'RoiHang', 'SaiThung')),
    GocBac1 REAL NOT NULL DEFAULT 0.0,          -- Góc bậc 1 lúc gắp vào thùng đích
    GocBac2 REAL NOT NULL DEFAULT 45.0,         -- Góc bậc 2 lúc hạ gắp
    GocBac3 REAL NOT NULL DEFAULT 0.0,          -- Góc bậc 3 lúc định hướng
    ThoiGianHanhTrinh REAL NOT NULL DEFAULT 1.8, -- Thời gian hoàn thành chu kỳ hành trình (giây)
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
