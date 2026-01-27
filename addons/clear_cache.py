#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để clear Odoo cache và update module metadata
"""

import psycopg2
import sys

def clear_odoo_cache():
    """Clear cache và update metadata"""
    try:
        conn = psycopg2.connect(
            dbname="danganh1009",
            user="odoo",
            password="odoo",
            host="db"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("=== BẮT ĐẦU CLEAR CACHE VÀ UPDATE METADATA ===\n")
        
        # 1. Xóa tất cả cached field definitions cho du_an và cong_viec
        print("1. Xóa ir_model_fields cho field 'code'...")
        cur.execute("""
            DELETE FROM ir_model_fields 
            WHERE name = 'code' 
            AND model IN ('du_an', 'cong_viec')
        """)
        print(f"   → Đã xóa {cur.rowcount} field definition\n")
        
        # 2. Update module state
        print("2. Update trạng thái modules...")
        cur.execute("""
            UPDATE ir_module_module 
            SET state = 'to upgrade' 
            WHERE name IN ('quan_ly_du_an', 'quan_ly_cong_viec')
        """)
        print(f"   → Đã đánh dấu {cur.rowcount} module để upgrade\n")
        
        # 3. Clear registry cache
        print("3. Clear ir_model cache...")
        cur.execute("""
            UPDATE ir_model 
            SET info = NULL 
            WHERE model IN ('du_an', 'cong_viec')
        """)
        print(f"   → Đã clear cache của {cur.rowcount} model\n")
        
        # 4. Kiểm tra các cột hiện tại trong bảng du_an
        print("4. Kiểm tra cột hiện tại trong bảng 'du_an':")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'du_an' 
            ORDER BY ordinal_position
        """)
        for row in cur.fetchall():
            print(f"   - {row[0]} ({row[1]})")
        
        print("\n5. Kiểm tra cột hiện tại trong bảng 'cong_viec':")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'cong_viec' 
            ORDER BY ordinal_position
        """)
        for row in cur.fetchall():
            print(f"   - {row[0]} ({row[1]})")
        
        cur.close()
        conn.close()
        
        print("\n=== HOÀN TẤT ===")
        print("\n✅ Đã clear cache thành công!")
        print("👉 Bây giờ cần RESTART Odoo server để áp dụng thay đổi.")
        print("👉 Sau khi restart, vào Apps → Update Apps List")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = clear_odoo_cache()
    sys.exit(0 if success else 1)
