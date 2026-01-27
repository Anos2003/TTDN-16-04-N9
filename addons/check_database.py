#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script kiểm tra và đồng bộ database với model
"""

import psycopg2
import sys

def check_database_schema():
    """Kiểm tra schema database"""
    try:
        conn = psycopg2.connect(
            dbname="danganh1009",
            user="odoo",
            password="odoo",
            host="db"
        )
        cur = conn.cursor()
        
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║         📊 KIỂM TRA DATABASE vs MODEL                   ║")
        print("╚═══════════════════════════════════════════════════════════╝\n")
        
        # Kiểm tra bảng du_an
        print("📋 BẢNG 'du_an':")
        print("─" * 60)
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'du_an' 
            ORDER BY ordinal_position
        """)
        
        du_an_columns = {}
        for row in cur.fetchall():
            col_name, data_type, nullable = row
            du_an_columns[col_name] = {'type': data_type, 'nullable': nullable}
            status = "✅" if col_name in ['id', 'name', 'mo_ta', 'ngay_bat_dau', 'ngay_ket_thuc', 'quan_ly_id', 'trang_thai'] else "⚠️"
            print(f"  {status} {col_name:<30} {data_type:<20} {nullable}")
        
        # Kiểm tra bảng cong_viec
        print("\n📋 BẢNG 'cong_viec':")
        print("─" * 60)
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'cong_viec' 
            ORDER BY ordinal_position
        """)
        
        cong_viec_columns = {}
        for row in cur.fetchall():
            col_name, data_type, nullable = row
            cong_viec_columns[col_name] = {'type': data_type, 'nullable': nullable}
            status = "✅" if col_name in ['id', 'name', 'mo_ta', 'du_an_id', 'assigned_to_id', 'ngay_bat_dau', 'ngay_ket_thuc', 'trang_thai', 'priority'] else "⚠️"
            print(f"  {status} {col_name:<30} {data_type:<20} {nullable}")
        
        # So sánh với model Python
        print("\n╔═══════════════════════════════════════════════════════════╗")
        print("║         🔍 SO SÁNH VỚI MODEL PYTHON                     ║")
        print("╚═══════════════════════════════════════════════════════════╝\n")
        
        required_du_an = ['id', 'name', 'mo_ta', 'ngay_bat_dau', 'ngay_ket_thuc', 
                          'quan_ly_id', 'trang_thai', 'create_uid', 'create_date', 
                          'write_uid', 'write_date']
        
        required_cong_viec = ['id', 'name', 'mo_ta', 'du_an_id', 'assigned_to_id', 
                              'ngay_bat_dau', 'ngay_ket_thuc', 'trang_thai', 'priority',
                              'create_uid', 'create_date', 'write_uid', 'write_date']
        
        print("DỰ ÁN (du_an):")
        missing_du_an = [col for col in required_du_an if col not in du_an_columns]
        extra_du_an = [col for col in du_an_columns.keys() 
                       if col not in required_du_an and not col.startswith('message_')]
        
        if missing_du_an:
            print(f"  ❌ Thiếu: {', '.join(missing_du_an)}")
        else:
            print("  ✅ Đầy đủ tất cả field cần thiết")
            
        if extra_du_an:
            print(f"  ⚠️  Thừa: {', '.join(extra_du_an)}")
        
        print("\nCÔNG VIỆC (cong_viec):")
        missing_cong_viec = [col for col in required_cong_viec if col not in cong_viec_columns]
        extra_cong_viec = [col for col in cong_viec_columns.keys() 
                          if col not in required_cong_viec and not col.startswith('message_')]
        
        if missing_cong_viec:
            print(f"  ❌ Thiếu: {', '.join(missing_cong_viec)}")
        else:
            print("  ✅ Đầy đủ tất cả field cần thiết")
            
        if extra_cong_viec:
            print(f"  ⚠️  Thừa: {', '.join(extra_cong_viec)}")
        
        # Kết luận
        print("\n╔═══════════════════════════════════════════════════════════╗")
        print("║         💡 KẾT LUẬN & KHUYẾN NGHỊ                       ║")
        print("╚═══════════════════════════════════════════════════════════╝\n")
        
        if not missing_du_an and not missing_cong_viec:
            print("✅ DATABASE ĐỒNG BỘ VỚI MODEL!")
            print("\n👉 Bạn có thể upgrade modules an toàn:")
            print("   1. Restart Docker: docker-compose restart")
            print("   2. Hoặc upgrade qua Odoo UI")
        else:
            print("❌ DATABASE CHƯA ĐỒNG BỘ!")
            print("\n👉 Cần thực hiện:")
            print("   1. Backup database trước:")
            print("      docker exec <postgres_container> pg_dump -U odoo danganh1009 > backup.sql")
            print("")
            print("   2. Restart Odoo và upgrade modules:")
            print("      docker-compose restart")
            print("      Vào Apps → Upgrade 'quan_ly_du_an' và 'quan_ly_cong_viec'")
            print("")
            print("   3. Odoo sẽ TỰ ĐỘNG tạo các cột thiếu trong database")
        
        cur.close()
        conn.close()
        
        return len(missing_du_an) == 0 and len(missing_cong_viec) == 0
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_database_schema()
    sys.exit(0 if success else 1)
