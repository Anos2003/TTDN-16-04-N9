#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để enable lại các cron jobs cần thiết
Chỉ enable những cron jobs quan trọng, tránh lỗi connection
"""

import psycopg2
import sys

def enable_essential_crons():
    try:
        conn = psycopg2.connect(
            dbname='danganh1009',
            user='odoo',
            password='odoo',
            host='db'
        )
        cur = conn.cursor()
        
        print("🔄 ENABLE LẠI CRON JOBS CẦN THIẾT")
        print("=" * 60)
        
        # Danh sách cron jobs NÊN ENABLE (chỉ những cái quan trọng)
        essential_crons = [
            'Mail: Email Queue Manager',  # Gửi email
            'Base: Auto-vacuum internal data',  # Cleanup database
        ]
        
        # KHÔNG ENABLE các cron này (gây lỗi hoặc không cần):
        # - 'Publisher: Update Notification' (không cần)
        # - 'SMS: SMS Queue Manager' (nếu không dùng SMS)
        # - 'Partner Autocomplete' (không cần)
        # - 'Snailmail' (không cần)
        
        for cron_name in essential_crons:
            cur.execute("""
                UPDATE ir_cron 
                SET active = true 
                WHERE cron_name = %s
            """, (cron_name,))
            
            if cur.rowcount > 0:
                print(f"   ✅ Enabled: {cron_name}")
            else:
                print(f"   ⚠️  Not found: {cron_name}")
        
        conn.commit()
        
        # Hiển thị trạng thái
        cur.execute("""
            SELECT cron_name, active 
            FROM ir_cron 
            ORDER BY id
        """)
        
        print("\n📊 TRẠNG THÁI TẤT CẢ CRON JOBS:")
        print("-" * 60)
        for cron_name, active in cur.fetchall():
            status = "✅ ACTIVE" if active else "⏸️  DISABLED"
            print(f"   {status} {cron_name}")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ HOÀN TẤT!")
        print("\n📝 LƯU Ý:")
        print("   - Chỉ enable 2 cron jobs quan trọng nhất")
        print("   - Các cron khác bị disable để tránh lỗi connection")
        print("   - Bật thêm cron nếu cần qua Odoo UI:")
        print("     Settings → Technical → Automation → Scheduled Actions")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        return False

if __name__ == "__main__":
    success = enable_essential_crons()
    sys.exit(0 if success else 1)
