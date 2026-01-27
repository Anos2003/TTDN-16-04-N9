# 🚀 Quick Start - AI Chatbot Assistant

## 5 phút để bắt đầu sử dụng AI Chatbot!

### ⚡ Cài đặt nhanh

```bash
# 1. Restart Odoo
sudo systemctl restart odoo

# 2. Update Apps List (trong Odoo UI)
Apps → ⋮ → Update Apps List

# 3. Install module
Apps → Tìm "AI Chatbot" → Install
```

### 🎯 Sử dụng ngay

1. **Mở Chat Nội Bộ** → Chọn một phòng chat
2. **Click tab "🤖 AI Assistant"**
3. **Gõ `@ai` và câu hỏi:**

```
@ai có bao nhiêu task?
@ai tóm tắt chat hôm nay
@ai tạo task kiểm tra hệ thống
```

### 📚 5 lệnh AI cơ bản

#### 1. **Hỏi về task**
```
@ai có bao nhiêu task chưa xong?
@ai task nào sắp deadline?
@ai ai đang làm task gì?
```

#### 2. **Tóm tắt chat**
```
@ai tóm tắt chat hôm nay
@ai recap tuần này
```

#### 3. **Tạo task mới**
```
@ai tạo task viết báo cáo
@ai tạo task khẩn cấp fix bug
```

#### 4. **Cảnh báo deadline**
```
@ai task nào trễ hạn?
@ai cảnh báo deadline
```

#### 5. **Gợi ý task**
```
@ai nên làm gì tiếp theo?
@ai gợi ý task
```

### 🎨 Giao diện

```
┌─────────────────────────────────┐
│  🤖 AI Assistant - Trợ lý      │
├─────────────────────────────────┤
│                                 │
│  👤 User: @ai có bao nhiêu     │
│     task?                       │
│                                 │
│  🤖 AI: Hiện có **15 task**    │
│     chưa hoàn thành.            │
│                                 │
├─────────────────────────────────┤
│  🤖 @ai  [input...]   📤 Gửi   │
└─────────────────────────────────┘
```

### ⚠️ Lưu ý

- **BẮT BUỘC** gõ `@ai` ở đầu tin nhắn
- AI chỉ hoạt động trong tab "🤖 AI Assistant"
- Response time: 1-3 giây

### 🐛 Gặp vấn đề?

```bash
# Check log
tail -f /var/log/odoo/odoo.log | grep ai_chatbot

# Reinstall
Apps → AI Chatbot → Uninstall → Install lại

# Clear cache
Settings → Technical → Clear cache
```

### 💡 Tips & Tricks

- **Tóm tắt nhanh**: `@ai recap`
- **Kiểm tra deadline**: `@ai deadline`
- **Tạo task nhanh**: `@ai task [tên task]`
- **Xem tình trạng**: `@ai status`

---

🎉 **Chúc bạn sử dụng AI Chatbot hiệu quả!**

Xem thêm chi tiết: [README.md](README.md)
