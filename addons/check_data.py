#!/usr/bin/env python3
"""
Script kiểm tra dữ liệu trong database Odoo
Sử dụng: python3 check_data.py
"""

import psycopg2
from datetime import datetime

def connect_db():
    """Kết nối tới database"""
    return psycopg2.connect(
        dbname='danganh1009',
        user='odoo',
        password='odoo',
        host='db',
        port='5432'
    )

def check_nhan_vien(cur):
    """Kiểm tra nhân viên"""
    print("=" * 70)
    print("👥 NHÂN VIÊN")
    print("=" * 70)
    
    # Tổng số
    cur.execute("SELECT COUNT(*) FROM nhan_vien")
    total = cur.fetchone()[0]
    print(f"Tổng số nhân viên: {total}")
    
    # Nhân viên IT
    cur.execute("SELECT COUNT(*) FROM nhan_vien WHERE ma_dinh_danh LIKE 'NV0%'")
    it_count = cur.fetchone()[0]
    print(f"Nhân viên IT (NV001-NV010): {it_count}")
    
    # Top 5 lương cao nhất
    cur.execute("""
        SELECT name, luong, email 
        FROM nhan_vien 
        WHERE luong IS NOT NULL 
        ORDER BY luong DESC 
        LIMIT 5
    """)
    print("\n🏆 Top 5 lương cao nhất:")
    for name, luong, email in cur.fetchall():
        print(f"   • {name}: {luong:,.0f} VNĐ ({email})")
    
    # Theo trạng thái
    cur.execute("""
        SELECT trang_thai, COUNT(*) 
        FROM nhan_vien 
        GROUP BY trang_thai
    """)
    print("\n📊 Theo trạng thái:")
    for status, count in cur.fetchall():
        print(f"   • {status}: {count} người")

def check_du_an(cur):
    """Kiểm tra dự án"""
    print("\n" + "=" * 70)
    print("📂 DỰ ÁN")
    print("=" * 70)
    
    # Tổng số
    cur.execute("SELECT COUNT(*) FROM du_an")
    total = cur.fetchone()[0]
    print(f"Tổng số dự án: {total}")
    
    # Theo trạng thái
    cur.execute("""
        SELECT trang_thai, COUNT(*) 
        FROM du_an 
        GROUP BY trang_thai
        ORDER BY COUNT(*) DESC
    """)
    print("\n📊 Theo trạng thái:")
    for status, count in cur.fetchall():
        print(f"   • {status}: {count} dự án")
    
    # Dự án đang thực hiện
    cur.execute("""
        SELECT d.name, n.name as quan_ly
        FROM du_an d
        LEFT JOIN nhan_vien n ON d.quan_ly_id = n.id
        WHERE d.trang_thai = 'in_progress'
        LIMIT 5
    """)
    print("\n🚀 Dự án đang thực hiện:")
    for project, manager in cur.fetchall():
        print(f"   • {project} (PM: {manager})")

def check_cong_viec(cur):
    """Kiểm tra công việc"""
    print("\n" + "=" * 70)
    print("✅ CÔNG VIỆC")
    print("=" * 70)
    
    # Tổng số
    cur.execute("SELECT COUNT(*) FROM cong_viec")
    total = cur.fetchone()[0]
    print(f"Tổng số công việc: {total}")
    
    # Theo trạng thái
    cur.execute("""
        SELECT trang_thai, COUNT(*) 
        FROM cong_viec 
        GROUP BY trang_thai
        ORDER BY COUNT(*) DESC
    """)
    print("\n📊 Theo trạng thái:")
    status_icons = {
        'todo': '⚪',
        'in_progress': '🔵',
        'review': '🟡',
        'done': '✅',
        'cancelled': '❌',
        'blocked': '🚫'
    }
    for status, count in cur.fetchall():
        icon = status_icons.get(status, '⚪')
        print(f"   {icon} {status}: {count} tasks")
    
    # Theo priority
    cur.execute("""
        SELECT priority, COUNT(*) 
        FROM cong_viec 
        GROUP BY priority
        ORDER BY 
            CASE priority
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
            END
    """)
    print("\n🎯 Theo độ ưu tiên:")
    priority_icons = {
        'critical': '🔴🔴',
        'high': '🔴',
        'medium': '🟡',
        'low': '🔵'
    }
    for priority, count in cur.fetchall():
        icon = priority_icons.get(priority, '⚪')
        print(f"   {icon} {priority}: {count} tasks")
    
    # Tasks deadline hôm nay hoặc quá hạn
    cur.execute("""
        SELECT name, ngay_ket_thuc, priority
        FROM cong_viec
        WHERE ngay_ket_thuc <= CURRENT_DATE
        AND trang_thai != 'done'
        ORDER BY ngay_ket_thuc ASC
        LIMIT 5
    """)
    results = cur.fetchall()
    if results:
        print("\n⚠️ Tasks deadline hôm nay hoặc quá hạn:")
        for name, deadline, priority in results:
            icon = priority_icons.get(priority, '⚪')
            print(f"   {icon} {name} (Deadline: {deadline})")
    
    # Tasks theo người thực hiện
    cur.execute("""
        SELECT n.name, COUNT(c.id) as task_count
        FROM nhan_vien n
        LEFT JOIN cong_viec c ON n.id = c.assigned_to_id
        WHERE c.trang_thai != 'done'
        GROUP BY n.name
        HAVING COUNT(c.id) > 0
        ORDER BY task_count DESC
        LIMIT 5
    """)
    print("\n👤 Top người có nhiều tasks:")
    for name, count in cur.fetchall():
        print(f"   • {name}: {count} tasks")

def check_statistics(cur):
    """Thống kê tổng quan"""
    print("\n" + "=" * 70)
    print("📈 THỐNG KÊ TỔNG QUAN")
    print("=" * 70)
    
    # Tỷ lệ hoàn thành
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN trang_thai = 'done' THEN 1 ELSE 0 END) as completed
        FROM cong_viec
    """)
    total, completed = cur.fetchone()
    if total > 0:
        completion_rate = (completed / total) * 100
        print(f"Tỷ lệ hoàn thành công việc: {completion_rate:.1f}% ({completed}/{total})")
    
    # Trung bình lương
    cur.execute("""
        SELECT AVG(luong), MIN(luong), MAX(luong)
        FROM nhan_vien
        WHERE luong IS NOT NULL
    """)
    avg, min_sal, max_sal = cur.fetchone()
    if avg:
        print(f"Lương trung bình: {avg:,.0f} VNĐ")
        print(f"Lương thấp nhất: {min_sal:,.0f} VNĐ")
        print(f"Lương cao nhất: {max_sal:,.0f} VNĐ")
    
    # Tasks trung bình / người
    cur.execute("""
        SELECT 
            COUNT(DISTINCT assigned_to_id) as people_count,
            COUNT(*) as task_count
        FROM cong_viec
        WHERE assigned_to_id IS NOT NULL
        AND trang_thai != 'done'
    """)
    people, tasks = cur.fetchone()
    if people and people > 0:
        avg_tasks = tasks / people
        print(f"Trung bình tasks / người: {avg_tasks:.1f}")

def main():
    """Main function"""
    try:
        print("\n🔍 KIỂM TRA DỮ LIỆU DATABASE - DANGANH1009")
        print("Thời gian:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        conn = connect_db()
        cur = conn.cursor()
        
        check_nhan_vien(cur)
        check_du_an(cur)
        check_cong_viec(cur)
        check_statistics(cur)
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ HOÀN TẤT KIỂM TRA")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
