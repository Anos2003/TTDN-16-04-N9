#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để update modules trong Odoo database
Chạy script này thay vì upgrade qua UI nếu gặp lỗi
"""

import psycopg2
import sys

def update_modules():
    try:
        # Connect to database
        conn = psycopg2.connect(
            dbname='danganh1009',
            user='odoo',
            password='odoo',
            host='db'
        )
        cur = conn.cursor()
        
        print("🔄 UPDATING ODOO MODULES")
        print("=" * 60)
        
        # Modules to update
        modules = ['nhan_su', 'quan_ly_du_an', 'quan_ly_cong_viec', 'thong_bao']
        
        for module in modules:
            print(f"\n📦 Module: {module}")
            
            # Check if module exists
            cur.execute("""
                SELECT id, name, state 
                FROM ir_module_module 
                WHERE name = %s
            """, (module,))
            
            result = cur.fetchone()
            
            if result:
                module_id, name, state = result
                print(f"   ✅ Module tồn tại (ID: {module_id}, State: {state})")
                
                # Mark for upgrade
                cur.execute("""
                    UPDATE ir_module_module 
                    SET state = 'to upgrade'
                    WHERE name = %s AND state = 'installed'
                """, (module,))
                
                if cur.rowcount > 0:
                    print(f"   ✅ Đã đánh dấu để upgrade")
                else:
                    print(f"   ℹ️  Module state: {state} (không cần upgrade)")
                    
            else:
                print(f"   ⚠️  Module chưa được cài đặt")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ ĐÃ CẬP NHẬT DATABASE!")
        print("\n📝 BƯỚC TIẾP THEO:")
        print("   Restart Odoo để apply changes:")
        print("   docker-compose restart")
        print("\n   Hoặc trong Odoo UI:")
        print("   Settings → Activate Developer Mode")
        print("   Apps → Update Apps List")
        print("   Modules sẽ tự động upgrade")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        return False

if __name__ == "__main__":
    success = update_modules()
    sys.exit(0 if success else 1)
