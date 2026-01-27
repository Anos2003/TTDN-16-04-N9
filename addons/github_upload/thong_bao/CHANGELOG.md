# 📬 CHANGELOG - Module Thông Báo

## [2.0.0] - 2026-01-19

### ✨ Tính Năng Mới

#### 🎨 Giao Diện
- **Kanban View**: Tổ chức thông báo theo trạng thái với drag & drop
- **Calendar View**: Xem lịch thông báo theo thời gian
- **Form View hiện đại**:
  - Stat buttons hiển thị thống kê (Người nhận, Đã đọc, Quá hạn)
  - Progress bar cho tỉ lệ đã đọc
  - Status bar workflow
  - Chatter để theo dõi và thảo luận
- **Tree View nâng cao**:
  - Decorations theo trạng thái
  - Optional columns
  - Progress bar widget

#### 🔔 Chức Năng
- **5 loại thông báo**:
  - 📋 Thông tin
  - ⚠️ Cảnh báo
  - ✅ Thành công
  - ❌ Lỗi
  - 🚨 Khẩn cấp (mới)

- **4 mức độ ưu tiên**:
  - 🔵 Thấp
  - 🟡 Bình thường
  - 🟠 Cao
  - 🔴 Rất cao (mới)

- **Tags**: Phân loại thông báo linh hoạt với màu sắc
- **Thời hạn**: 
  - Quản lý deadline
  - Cảnh báo quá hạn
  - Tính ngày còn lại

- **Thống kê**:
  - Tổng người nhận
  - Số người đã đọc
  - Tỉ lệ % đã đọc

- **Trạng thái mới**:
  - Nháp
  - Đã gửi
  - Đã đọc
  - Lưu trữ (mới)

#### 🔧 Kỹ Thuật
- **Computed Fields**:
  - `short_description`: Mô tả ngắn từ nội dung
  - `related_name`: Tên record liên quan
  - `is_read`: Kiểm tra người dùng đã đọc
  - `is_overdue`: Kiểm tra quá hạn
  - `days_until_deadline`: Ngày còn lại
  - `total_recipients`, `total_read`, `read_percentage`: Thống kê

- **Business Methods**:
  - `create_notification()`: Tạo thông báo nâng cao
  - `mark_as_read()`: Đánh dấu đã đọc
  - `mark_as_unread()`: Đánh dấu chưa đọc
  - `action_archive()`: Lưu trữ
  - `action_send()`: Gửi thông báo
  - `action_view_related()`: Xem chi tiết liên quan

- **Mail Integration**:
  - Kế thừa `mail.thread` và `mail.activity.mixin`
  - Tự động gửi thông báo Odoo nội bộ
  - Tracking thay đổi

#### 🎯 Search & Filters
- **15+ filters**:
  - Thông báo của tôi
  - Chưa đọc / Đã đọc
  - Theo loại thông báo
  - Theo mức độ ưu tiên
  - Quá hạn / Có thời hạn
  - Theo thời gian (Hôm nay, Tuần này, Tháng này)

- **Group By**:
  - Loại thông báo
  - Ưu tiên
  - Trạng thái
  - Người tạo
  - Tags
  - Ngày tạo

#### 💅 Styling
- Custom CSS với:
  - Gradient buttons
  - Smooth transitions
  - Hover effects
  - Badge colors
  - Progress bar animations
  - Responsive design

---

## [1.0.0] - Ban đầu

### Tính Năng Cơ Bản
- Form view đơn giản
- Tree view cơ bản
- Search view
- 4 loại thông báo
- 3 mức độ ưu tiên
- 3 trạng thái
- Liên kết với module khác

---

## 📊 So Sánh Phiên Bản

| Tính năng | v1.0 | v2.0 |
|-----------|------|------|
| Views | 3 | 6 |
| Loại thông báo | 4 | 5 |
| Mức ưu tiên | 3 | 4 |
| Trạng thái | 3 | 4 |
| Computed fields | 1 | 8 |
| Business methods | 2 | 6 |
| Filters | 8 | 15+ |
| Tags | ❌ | ✅ |
| Deadline | ❌ | ✅ |
| Progress bar | ❌ | ✅ |
| Chatter | ❌ | ✅ |
| Custom CSS | ❌ | ✅ |
| Mail integration | ❌ | ✅ |

---

## 🚀 Hướng Dẫn Nâng Cấp

### Bước 1: Backup Database
```bash
pg_dump -U odoo -d your_database > backup_before_upgrade.sql
```

### Bước 2: Cập nhật module
```bash
cd /mnt/extra-addons/thong_bao
git pull  # hoặc copy files mới
```

### Bước 3: Nâng cấp trong Odoo
1. Vào Apps
2. Tìm "Thông báo"
3. Click "Upgrade"
4. Hoặc dùng CLI:
```bash
odoo -u thong_bao -d your_database
```

### Bước 4: Clear cache
```bash
# Xóa __pycache__
find /mnt/extra-addons/thong_bao -type d -name __pycache__ -exec rm -rf {} +

# Restart Odoo
sudo systemctl restart odoo
```

---

## ⚠️ Breaking Changes

### API Changes
- `create_notification()` có thêm parameters: `deadline`, `tag_ids`, `icon`
- Field `message` đổi từ Text sang Html
- Thêm required constraint cho `recipient_ids`

### Database Migration
Các field mới sẽ tự động được tạo khi upgrade:
- `short_description`
- `icon`
- `color`
- `tag_ids`
- `deadline`
- `is_overdue`
- `days_until_deadline`
- `total_recipients`
- `total_read`
- `read_percentage`

---

## 🐛 Bug Fixes
- Fix lỗi đánh dấu đã đọc không cập nhật trạng thái
- Fix lỗi hiển thị người nhận
- Cải thiện performance computed fields

---

## 📝 Notes
- Module yêu cầu Odoo 15.0 trở lên
- Tương thích với module `mail`
- CSS tương thích với Bootstrap 4

---

## 👨‍💻 Contributors
- Your Team

## 📄 License
LGPL-3
