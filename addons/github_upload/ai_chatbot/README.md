# 🤖 AI Chatbot Assistant - Tích hợp Chat Nội Bộ

Module AI Chatbot tích hợp trực tiếp vào hệ thống **Chat Nội Bộ** để hỗ trợ quản lý công việc và dự án thông minh.

## ✨ Tính năng

### 1. **Trả lời câu hỏi thông minh**
- Hỏi về số lượng task, deadline, người phụ trách
- Tình trạng dự án, tiến độ
- Thống kê công việc theo filter

**Ví dụ:**
```
@ai có bao nhiêu task chưa xong?
@ai task nào sắp deadline?
@ai ai đang làm task gì?
@ai dự án đang ra sao?
```

### 2. **Tóm tắt cuộc trò chuyện**
- Tóm tắt chat hôm nay, tuần này, tháng này
- Thống kê người tham gia nhiều nhất
- Highlight tin nhắn quan trọng

**Ví dụ:**
```
@ai tóm tắt chat hôm nay
@ai recap tuần này
@ai tổng kết tháng này
```

### 3. **Tạo task từ chat**
- Tự động tạo task với độ ưu tiên
- Liên kết với dự án (nếu phòng chat có dự án)
- Parse deadline từ tin nhắn

**Ví dụ:**
```
@ai tạo task kiểm tra database
@ai tạo task khẩn cấp fix bug login
@ai add task viết báo cáo deadline 15/12
```

### 4. **Cảnh báo deadline & task trễ**
- Danh sách task đã quá hạn
- Task sắp đến hạn (3 ngày)
- Mức độ khẩn cấp

**Ví dụ:**
```
@ai task nào trễ hạn?
@ai cảnh báo deadline
@ai task nào cần ưu tiên?
```

### 5. **Gợi ý task tiếp theo**
- Gợi ý task dựa trên độ ưu tiên
- Task sắp deadline (7 ngày)
- Task chưa ai nhận

**Ví dụ:**
```
@ai nên làm gì tiếp theo?
@ai gợi ý task
@ai làm task nào tiếp?
```

## 📦 Cài đặt

### Yêu cầu
- Odoo 15.0 Community Edition
- Module **chat_noi_bo** (Chat Nội Bộ)
- Module **quan_ly_cong_viec** (Quản lý Công việc)
- Module **quan_ly_du_an** (Quản lý Dự án)

### Bước 1: Copy module vào addons
```bash
cp -r ai_chatbot /mnt/extra-addons/
```

### Bước 2: Restart Odoo
```bash
sudo systemctl restart odoo
```

### Bước 3: Update Apps List
1. Vào Odoo UI
2. **Apps** → Click **⋮** (góc phải) → **Update Apps List**

### Bước 4: Cài đặt module
1. Trong **Apps**, tìm kiếm "**AI Chatbot**"
2. Click **Install**

## 🚀 Sử dụng

### 1. Mở phòng chat
- Vào **Chat Nội Bộ** (menu chính)
- Chọn một phòng chat bất kỳ

### 2. Mở tab AI Assistant
- Click vào tab **"🤖 AI Assistant"** trong form view
- Giao diện chat AI sẽ hiển thị

### 3. Chat với AI
- Gõ `@ai` trước câu hỏi
- Ví dụ: `@ai có bao nhiêu task?`
- AI sẽ phản hồi trong vài giây

### 4. Tin nhắn thường
- Gõ tin nhắn không có `@ai` sẽ là tin nhắn chat bình thường
- Không trigger AI processing

## 🏗️ Kiến trúc

### Models
- **ai.intent.detector**: Phát hiện ý định người dùng (5 intent types)
- **ai.chatbot.processor**: Xử lý logic AI và tạo phản hồi
- **chat.message (extend)**: Thêm metadata cho AI messages

### Controllers
- `/ai_chatbot/process_message`: Xử lý tin nhắn AI
- `/ai_chatbot/get_messages`: Lấy lịch sử chat
- `/ai_chatbot/send_message`: Gửi tin nhắn (tự động phát hiện @ai)

### Views
- **chat_room_views.xml**: Thêm tab "🤖 AI Assistant" vào chat.room
- **JavaScript**: Auto-refresh, typing indicator, message rendering
- **CSS**: Gradient design, animations

## 🎯 Intent Detection

Module sử dụng **rule-based intent detection** với regex patterns:

1. **question**: Câu hỏi về task, dự án (mặc định)
2. **summary**: Từ khóa "tóm tắt", "summary", "recap"
3. **task_creation**: "tạo task", "create task", "add task"
4. **warning**: "trễ", "deadline", "sắp hết hạn"
5. **suggestion**: "nên làm gì", "gợi ý", "suggest"

## 📊 Database Schema

### New Fields in `chat.message`
```python
is_ai_response = Boolean  # Tin nhắn từ AI?
ai_intent = Selection      # Intent type
ai_confidence = Float      # Độ tin cậy (0-1)
ai_processing_time = Float # Thời gian xử lý (giây)
```

## 🔒 Security

- AI Assistant user: `ai_assistant` / `ai_assistant_2026`
- Nhân viên AI được tạo tự động
- Access rights cho tất cả user

## 🐛 Troubleshooting

### Module không hiện trong Apps?
```bash
# 1. Kiểm tra addons path
cat /etc/odoo/odoo.conf | grep addons_path

# 2. Restart Odoo
sudo systemctl restart odoo

# 3. Check log
tail -f /var/log/odoo/odoo.log | grep ai_chatbot
```

### Lỗi khi cài đặt?
```bash
# Install với debug mode
odoo-bin -c /etc/odoo/odoo.conf \
  -d danganh1009 \
  -i ai_chatbot \
  --log-level=debug \
  --stop-after-init
```

### Tab AI Assistant không hiển thị?
- Kiểm tra đã cài module **chat_noi_bo** chưa
- Clear cache: Settings → Technical → Clear cache
- Hard refresh: Ctrl + Shift + R

### AI không phản hồi?
- Kiểm tra user `ai_assistant` đã được tạo chưa
- Kiểm tra nhân viên AI có trong database
- Check log: `/var/log/odoo/odoo.log`

## 🔄 Update Module

```bash
# Qua UI
Apps → Tìm "AI Chatbot" → Click "Upgrade"

# Qua command line
odoo-bin -c /etc/odoo/odoo.conf \
  -d danganh1009 \
  -u ai_chatbot \
  --stop-after-init
```

## 📝 Roadmap

- [ ] Tích hợp GPT API (OpenAI, Claude)
- [ ] Multi-language support (English, Vietnamese)
- [ ] Voice input/output
- [ ] Sentiment analysis
- [ ] Task auto-assignment AI
- [ ] Meeting summarization
- [ ] Smart notifications

## 🤝 Đóng góp

Phát hiện bug hoặc có ý tưởng mới? Tạo issue hoặc pull request!

## 📄 License

LGPL-3

## 👨‍💻 Author

Your Company - 2026

---

💡 **Mẹo**: Dùng `@ai` ở đầu tin nhắn để kích hoạt AI Assistant!
