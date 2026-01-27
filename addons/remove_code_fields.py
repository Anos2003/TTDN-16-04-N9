#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để xóa cột 'code' khỏi bảng du_an và cong_viec trong database
"""

import psycopg2
import sys

def remove_code_columns():
    """Xóa cột code khỏi các bảng"""
    try:
        # Kết nối database
        conn = psycopg2.connect(
            dbname="danganh1009",
            user="odoo",
            password="odoo",
            host="db"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("=== BẮT ĐẦU XÓA CỘT CODE ===\n")
        
        # Kiểm tra và xóa cột code từ bảng du_an
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'du_an' AND column_name = 'code'
        """)
        if cur.fetchone():
            print("✓ Tìm thấy cột 'code' trong bảng 'du_an', đang xóa...")
            cur.execute("ALTER TABLE du_an DROP COLUMN IF EXISTS code CASCADE")
            print("  → Đã xóa thành công!\n")
        else:
            print("✓ Cột 'code' không tồn tại trong bảng 'du_an'\n")
        
        # Kiểm tra và xóa cột code từ bảng cong_viec
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'cong_viec' AND column_name = 'code'
        """)
        if cur.fetchone():
            print("✓ Tìm thấy cột 'code' trong bảng 'cong_viec', đang xóa...")
            cur.execute("ALTER TABLE cong_viec DROP COLUMN IF EXISTS code CASCADE")
            print("  → Đã xóa thành công!\n")
        else:
            print("✓ Cột 'code' không tồn tại trong bảng 'cong_viec'\n")
        
        # Xóa thông tin field trong ir_model_fields
        print("✓ Dọn dẹp metadata trong ir_model_fields...")
        cur.execute("""
            DELETE FROM ir_model_fields 
            WHERE name = 'code' 
            AND model IN ('du_an', 'cong_viec')
        """)
        print(f"  → Đã xóa {cur.rowcount} record\n")
        
        cur.close()
        conn.close()
        
        print("=== HOÀN TẤT ===")
        print("\n✅ Đã xóa cột 'code' thành công!")
        print("👉 Bây giờ bạn có thể khởi động lại Odoo server.")
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ LỖI DATABASE: {e}")
        return False
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        return False

if __name__ == '__main__':
    success = remove_code_columns()
    sys.exit(0 if success else 1)
