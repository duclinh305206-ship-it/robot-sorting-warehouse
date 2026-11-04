"""
Khởi tạo cơ sở dữ liệu SQLite cho dự án bài nhóm:
Hệ thống giám sát cánh tay robot phân loại sản phẩm.
"""

import sqlite3
import os
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DB_PATH = os.path.join(os.path.dirname(__file__), "warehouse_robot.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema_robot.sql")

def init_db():
    print(f"Đang tạo cơ sở dữ liệu tại: {DB_PATH}")
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("-> Khởi tạo CSDL thành công! Đã tạo file warehouse_robot.db")

if __name__ == "__main__":
    init_db()
