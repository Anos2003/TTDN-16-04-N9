#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import psycopg2

conn = psycopg2.connect(
    host='db',
    database='danganh1009',
    user='odoo',
    password='odoo'
)
cur = conn.cursor()

# 10 Phòng ban
phong_ban_list = [
    ('Phòng Kỹ thuật', 'Phát triển sản phẩm và công nghệ'),
    ('Phòng Phát triển Phần mềm', 'Lập trình và phát triển ứng dụng'),
    ('Phòng Kiểm thử', 'Đảm bảo chất lượng sản phẩm'),
    ('Phòng Hạ tầng CNTT', 'Quản lý server, network, database'),
    ('Phòng Bảo mật', 'An toàn thông tin và bảo mật hệ thống'),
    ('Phòng Kinh doanh', 'Phát triển thị trường và khách hàng'),
    ('Phòng Hành chính Nhân sự', 'Quản lý nhân sự và hành chính'),
    ('Phòng Kế toán Tài chính', 'Quản lý tài chính doanh nghiệp'),
    ('Phòng Marketing', 'Truyền thông và quảng bá thương hiệu'),
    ('Phòng Dự án', 'Quản lý và điều phối dự án'),
]

print("🔄 Đang thêm 10 phòng ban...")
phong_ban_ids = {}
for i, (name, mo_ta) in enumerate(phong_ban_list, 1):
    cur.execute("""
        INSERT INTO phong_ban (name, mo_ta, create_date, write_date, create_uid, write_uid)
        VALUES (%s, %s, NOW(), NOW(), 2, 2)
        ON CONFLICT DO NOTHING
        RETURNING id
    """, (name, mo_ta))
    
    result = cur.fetchone()
    if result:
        phong_ban_ids[name] = result[0]
        print(f"✓ {name}")
    else:
        # Already exists, get ID
        cur.execute("SELECT id FROM phong_ban WHERE name = %s", (name,))
        result = cur.fetchone()
        if result:
            phong_ban_ids[name] = result[0]
            print(f"✓ {name} (đã tồn tại)")

conn.commit()

# 10 Chức vụ
chuc_vu_list = [
    ('Giám đốc Kỹ thuật', 'Lãnh đạo bộ phận kỹ thuật'),
    ('Trưởng phòng', 'Quản lý phòng ban'),
    ('Phó phòng', 'Hỗ trợ quản lý phòng ban'),
    ('Kỹ sư trưởng', 'Chuyên gia kỹ thuật cao cấp'),
    ('Kỹ sư', 'Nhân viên kỹ thuật'),
    ('Lập trình viên Senior', 'Lập trình viên cấp cao'),
    ('Lập trình viên', 'Lập trình viên'),
    ('Chuyên viên', 'Nhân viên chuyên môn'),
    ('Nhân viên', 'Nhân viên thực hiện'),
    ('Thực tập sinh', 'Sinh viên thực tập'),
]

print("\n🔄 Đang thêm 10 chức vụ...")
chuc_vu_ids = {}
for i, (name, mo_ta) in enumerate(chuc_vu_list, 1):
    cur.execute("""
        INSERT INTO chuc_vu (name, mo_ta, create_date, write_date, create_uid, write_uid)
        VALUES (%s, %s, NOW(), NOW(), 2, 2)
        ON CONFLICT DO NOTHING
        RETURNING id
    """, (name, mo_ta))
    
    result = cur.fetchone()
    if result:
        chuc_vu_ids[name] = result[0]
        print(f"✓ {name}")
    else:
        # Already exists, get ID
        cur.execute("SELECT id FROM chuc_vu WHERE name = %s", (name,))
        result = cur.fetchone()
        if result:
            chuc_vu_ids[name] = result[0]
            print(f"✓ {name} (đã tồn tại)")

conn.commit()

# Gán phòng ban và chức vụ cho 10 nhân viên
assignments = [
    ('NV001', 'Phòng Phát triển Phần mềm', 'Kỹ sư trưởng'),
    ('NV002', 'Phòng Kiểm thử', 'Lập trình viên Senior'),
    ('NV003', 'Phòng Kỹ thuật', 'Giám đốc Kỹ thuật'),
    ('NV004', 'Phòng Phát triển Phần mềm', 'Lập trình viên'),
    ('NV005', 'Phòng Hạ tầng CNTT', 'Kỹ sư'),
    ('NV006', 'Phòng Bảo mật', 'Chuyên viên'),
    ('NV007', 'Phòng Marketing', 'Chuyên viên'),
    ('NV008', 'Phòng Dự án', 'Trưởng phòng'),
    ('NV009', 'Phòng Phát triển Phần mềm', 'Lập trình viên'),
    ('NV010', 'Phòng Hạ tầng CNTT', 'Kỹ sư trưởng'),
]

print("\n🔄 Đang gán phòng ban và chức vụ cho nhân viên...")
for ma_nv, phong_ban, chuc_vu in assignments:
    pb_id = phong_ban_ids.get(phong_ban)
    cv_id = chuc_vu_ids.get(chuc_vu)
    
    if pb_id and cv_id:
        cur.execute("""
            UPDATE nhan_vien 
            SET phong_ban_id = %s, chuc_vu_id = %s, write_date = NOW()
            WHERE ma_dinh_danh = %s
        """, (pb_id, cv_id, ma_nv))
        
        if cur.rowcount > 0:
            print(f"✓ {ma_nv}: {phong_ban} - {chuc_vu}")

conn.commit()
cur.close()
conn.close()

print("\n✅ Hoàn thành!")
print("📋 Đã thêm 10 phòng ban, 10 chức vụ và gán cho nhân viên!")
