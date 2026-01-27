# -*- coding: utf-8 -*-
{
    'name': "💬 Chat Nội Bộ",
    'summary': "Hệ thống chat nội bộ công ty - Liên kết với dự án và nhân viên",
    'description': """
        💬 Hệ Thống Chat Nội Bộ
        ======================
        
        Tính năng chính:
        - 💬 Tạo phòng chat cho nhóm, dự án, bộ phận
        - 👥 Thêm nhân viên từ Quản lý Nhân sự vào phòng chat
        - 📊 Mỗi dự án có phòng chat riêng
        - 📝 Gửi tin nhắn text, file đính kèm
        - ✅ Đọc/chưa đọc tin nhắn
        - 🔔 Thông báo tin nhắn mới
        - 🔍 Tìm kiếm tin nhắn
        - 📎 File đính kèm
        
        Phiên bản 1.0
    """,
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Productivity',
    'version': '1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'bus',
        'nhan_su',
        'quan_ly_du_an',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/chat_room_data.xml',
        'views/chat_room_views.xml',
        'views/chat_message_views.xml',
        'views/chat_window_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'chat_noi_bo/static/src/css/chat_window.css',
            'chat_noi_bo/static/src/js/chat_window.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'version': '1.0.2',  # Increment version to force reload
}
