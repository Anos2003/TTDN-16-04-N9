#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import psycopg2
from datetime import datetime, timedelta

conn = psycopg2.connect(
    host='db',
    database='danganh1009',
    user='odoo',
    password='odoo'
)
cur = conn.cursor()

# Check if NV001 already exists
cur.execute("SELECT id FROM nhan_vien WHERE ma_dinh_danh = 'NV001'")
if cur.fetchone():
    print("✅ Demo data đã tồn tại! Update thông tin...")
    
    # Update existing records
    employees = [
        ('NV001', 'Nguyễn', 'Văn An', '1990-03-15', 'Hà Nội', '123 Láng Hạ, Ba Đình, Hà Nội', 'nguyenvanan@company.vn', '0901234567', 35000000, '2018-01-15'),
        ('NV002', 'Trần', 'Thị Bình', '1992-07-22', 'Hải Phòng', '456 Lê Lợi, Ngô Quyền, Hải Phòng', 'binh.tran@company.vn', '0901234568', 28000000, '2019-03-10'),
        ('NV003', 'Lê', 'Hoàng Cường', '1988-11-08', 'Đà Nẵng', '789 Trần Phú, Hải Châu, Đà Nẵng', 'cuong.le@company.vn', '0901234569', 40000000, '2017-06-01'),
        ('NV004', 'Phạm', 'Minh Đức', '1995-05-30', 'TP.HCM', '321 Nguyễn Huệ, Q.1, TP.HCM', 'duc.pham@company.vn', '0901234570', 25000000, '2020-09-15'),
        ('NV005', 'Hoàng', 'Thu Hà', '1993-09-12', 'Hà Nội', '654 Hoàng Quốc Việt, Cầu Giấy, Hà Nội', 'ha.hoang@company.vn', '0901234571', 32000000, '2018-11-20'),
        ('NV006', 'Vũ', 'Quốc Khánh', '1991-02-18', 'Nghệ An', '147 Quang Trung, TP Vinh, Nghệ An', 'khanh.vu@company.vn', '0901234572', 27000000, '2019-07-01'),
        ('NV007', 'Đặng', 'Thùy Linh', '1994-06-25', 'Huế', '258 Lê Duẩn, TP Huế', 'linh.dang@company.vn', '0901234573', 29000000, '2020-02-14'),
        ('NV008', 'Bùi', 'Văn Minh', '1989-12-03', 'Cần Thơ', '369 Trần Hưng Đạo, Ninh Kiều, Cần Thơ', 'minh.bui@company.vn', '0901234574', 38000000, '2017-08-22'),
        ('NV009', 'Ngô', 'Thị Nga', '1996-04-17', 'Hà Nội', '741 Giải Phóng, Hoàng Mai, Hà Nội', 'nga.ngo@company.vn', '0901234575', 22000000, '2021-05-10'),
        ('NV010', 'Trịnh', 'Công Phúc', '1990-10-09', 'Quảng Ninh', '852 Hạ Long, TP Hạ Long, Quảng Ninh', 'phuc.trinh@company.vn', '0901234576', 33000000, '2018-04-30'),
    ]
    
    print("🔄 Đang update thông tin 10 nhân viên IT...")
    for emp in employees:
        ma, ho, ten, ngay_sinh, que_quan, dia_chi, email, sdt, luong, ngay_vao = emp
        name = f"{ho} {ten}"
        
        cur.execute("""
            UPDATE nhan_vien 
            SET ho=%s, ten=%s, name=%s, ngay_sinh=%s, que_quan=%s, dia_chi=%s,
                email=%s, so_dien_thoai=%s, luong=%s, ngay_vao_lam=%s, 
                trang_thai='active', write_date=NOW()
            WHERE ma_dinh_danh = %s
        """, (ho, ten, name, ngay_sinh, que_quan, dia_chi, email, sdt, luong, ngay_vao, ma))
        
        if cur.rowcount > 0:
            print(f"✓ Updated {ma}: {name} - {luong:,.0f} VNĐ")
    
    conn.commit()
    cur.close()
    conn.close()
    print("\n✅ Đã update thành công!")
    exit(0)

# 10 IT Employees with full information
employees = [
    ('NV001', 'Nguyễn', 'Văn An', '1990-03-15', 'Hà Nội', '123 Láng Hạ, Ba Đình, Hà Nội', 'nguyenvanan@company.vn', '0901234567', 35000000, '2018-01-15'),
    ('NV002', 'Trần', 'Thị Bình', '1992-07-22', 'Hải Phòng', '456 Lê Lợi, Ngô Quyền, Hải Phòng', 'binh.tran@company.vn', '0901234568', 28000000, '2019-03-10'),
    ('NV003', 'Lê', 'Hoàng Cường', '1988-11-08', 'Đà Nẵng', '789 Trần Phú, Hải Châu, Đà Nẵng', 'cuong.le@company.vn', '0901234569', 40000000, '2017-06-01'),
    ('NV004', 'Phạm', 'Minh Đức', '1995-05-30', 'TP.HCM', '321 Nguyễn Huệ, Q.1, TP.HCM', 'duc.pham@company.vn', '0901234570', 25000000, '2020-09-15'),
    ('NV005', 'Hoàng', 'Thu Hà', '1993-09-12', 'Hà Nội', '654 Hoàng Quốc Việt, Cầu Giấy, Hà Nội', 'ha.hoang@company.vn', '0901234571', 32000000, '2018-11-20'),
    ('NV006', 'Vũ', 'Quốc Khánh', '1991-02-18', 'Nghệ An', '147 Quang Trung, TP Vinh, Nghệ An', 'khanh.vu@company.vn', '0901234572', 27000000, '2019-07-01'),
    ('NV007', 'Đặng', 'Thùy Linh', '1994-06-25', 'Huế', '258 Lê Duẩn, TP Huế', 'linh.dang@company.vn', '0901234573', 29000000, '2020-02-14'),
    ('NV008', 'Bùi', 'Văn Minh', '1989-12-03', 'Cần Thơ', '369 Trần Hưng Đạo, Ninh Kiều, Cần Thơ', 'minh.bui@company.vn', '0901234574', 38000000, '2017-08-22'),
    ('NV009', 'Ngô', 'Thị Nga', '1996-04-17', 'Hà Nội', '741 Giải Phóng, Hoàng Mai, Hà Nội', 'nga.ngo@company.vn', '0901234575', 22000000, '2021-05-10'),
    ('NV010', 'Trịnh', 'Công Phúc', '1990-10-09', 'Quảng Ninh', '852 Hạ Long, TP Hạ Long, Quảng Ninh', 'phuc.trinh@company.vn', '0901234576', 33000000, '2018-04-30'),
]

print("🔄 Đang insert 10 nhân viên IT với đầy đủ thông tin...")
for emp in employees:
    ma, ho, ten, ngay_sinh, que_quan, dia_chi, email, sdt, luong, ngay_vao = emp
    name = f"{ho} {ten}"
    
    cur.execute("""
        INSERT INTO nhan_vien 
        (ma_dinh_danh, ho, ten, name, ngay_sinh, que_quan, dia_chi, 
         email, so_dien_thoai, luong, ngay_vao_lam, trang_thai,
         create_date, write_date, create_uid, write_uid)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), 2, 2)
    """, (ma, ho, ten, name, ngay_sinh, que_quan, dia_chi, email, sdt, luong, ngay_vao, 'active'))
    
    print(f"✓ {ma}: {name} - {email} - {luong:,.0f} VNĐ")

conn.commit()
cur.close()
conn.close()

print("\n✅ Đã thêm thành công 10 nhân viên IT!")
print("📋 Vào QLNS → Quản lý nhân viên để xem danh sách!")
