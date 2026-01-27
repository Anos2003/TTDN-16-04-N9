# -*- coding: utf-8 -*-
{
    'name': '🤖 AI Chatbot Assistant',
    'version': '15.0.1.0.0',
    'category': 'Productivity',
    'summary': 'AI Assistant tích hợp vào Chat Nội Bộ để quản lý task và project',
    'description': """
AI Chatbot Assistant cho Chat Nội Bộ

Tính năng:
- Tích hợp AI Assistant trực tiếp vào phòng chat nội bộ
- Trả lời câu hỏi về task, deadline, assignee, dự án
- Tóm tắt cuộc trò chuyện trong phòng chat
- Tạo task mới từ chat
- Cảnh báo deadline và task trễ
- Gợi ý task tiếp theo dựa trên priority
- Phân tích tình hình dự án

Cách sử dụng:
Trong bất kỳ phòng chat nào, gõ @ai trước câu hỏi.
Ví dụ: @ai có bao nhiêu task? hoặc @ai tóm tắt chat hôm nay
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'nhan_su',
        'chat_noi_bo',
        'quan_ly_cong_viec',
        'quan_ly_du_an',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ai_user_data.xml',
        'data/demo_data.xml',
        'views/chat_room_views.xml',
    ],
    
    # CSS và JS files
    'assets': {
        'web.assets_backend': [
            'ai_chatbot/static/src/css/chat_widget.css',
            'ai_chatbot/static/src/css/floating_widget.css',
            'ai_chatbot/static/src/js/chat_widget.js',
            'ai_chatbot/static/src/js/chat_window_extend.js',
            'ai_chatbot/static/src/js/floating_widget.js',
        ],
    },
    'qweb': [
        'static/src/xml/chat_widget.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
