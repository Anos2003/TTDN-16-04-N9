# -*- coding: utf-8 -*-
{
    'name': "📬 Thông báo",
    'summary': "Hệ thống quản lý thông báo thông minh với UI hiện đại",
    'description': """
        📬 Hệ Thống Quản Lý Thông Báo
        =============================
        
        Module thông báo nâng cao liên kết với các module:
        - 👥 Quản lý nhân sự (nhan_su)
        - ✅ Quản lý công việc (quan_ly_cong_viec)
        - 📊 Quản lý dự án (quan_ly_du_an)
        
        ✨ Tính năng nổi bật:
        - 🎨 Giao diện hiện đại với Kanban, Calendar views
        - 🔔 5 loại thông báo: Thông tin, Cảnh báo, Thành công, Lỗi, Khẩn cấp
        - 🎯 4 mức độ ưu tiên
        - 🏷️ Tags để phân loại
        - ⏰ Quản lý thời hạn và cảnh báo quá hạn
        - 📊 Thống kê người nhận và tỉ lệ đã đọc
        - 🔗 Liên kết với các module khác
        - 💬 Chatter để theo dõi và thảo luận
        
        Phiên bản 2.0 - Nâng cấp toàn diện
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Productivity',
    'version': '2.0.0',
    'license': 'LGPL-3',
    'depends': [
        'base', 
        'mail',
        'nhan_su', 
        'quan_ly_cong_viec', 
        'quan_ly_du_an'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/thong_bao.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'thong_bao/static/src/css/thong_bao.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}

