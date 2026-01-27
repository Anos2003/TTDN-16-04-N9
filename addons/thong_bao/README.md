# 📬 Module Thông Báo - Odoo

Module quản lý thông báo thông minh với giao diện hiện đại cho hệ thống Odoo.

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Odoo](https://img.shields.io/badge/odoo-15.0+-brightgreen.svg)
![License](https://img.shields.io/badge/license-LGPL--3-orange.svg)

---

## 📋 Mục Lục

- [Giới thiệu](#giới-thiệu)
- [Tính năng](#tính-năng)
- [Cài đặt](#cài-đặt)
- [Sử dụng](#sử-dụng)
- [Cấu hình](#cấu-hình)
- [API](#api)
- [Screenshots](#screenshots)
- [Changelog](#changelog)
- [License](#license)

---

## 🎯 Giới Thiệu

Module **Thông Báo** là một giải pháp toàn diện để quản lý thông báo trong hệ thống Odoo. Module tích hợp hoàn hảo với:

- 👥 **Quản lý nhân sự** (nhan_su)
- ✅ **Quản lý công việc** (quan_ly_cong_viec)
- 📊 **Quản lý dự án** (quan_ly_du_an)

### Điểm Nổi Bật

✨ **Giao diện hiện đại** - Kanban, Calendar, Form views với UI/UX đẹp mắt  
🔔 **Đa dạng loại thông báo** - 5 loại với emoji và màu sắc riêng  
🎯 **Ưu tiên linh hoạt** - 4 mức độ ưu tiên  
🏷️ **Tags phân loại** - Tổ chức thông báo dễ dàng  
⏰ **Quản lý thời hạn** - Cảnh báo quá hạn thông minh  
📊 **Thống kê chi tiết** - Theo dõi tỉ lệ đọc và người nhận  
🔗 **Liên kết module** - Kết nối với các records khác  
💬 **Chatter tích hợp** - Theo dõi và thảo luận  

---

## ✨ Tính Năng

### 🎨 Giao Diện

#### Kanban View
- Tổ chức thông báo theo trạng thái
- Drag & drop để thay đổi trạng thái
- Progress bar hiển thị tỉ lệ đã đọc
- Badge ưu tiên và loại thông báo
- Avatar người tạo

#### Calendar View
- Xem lịch thông báo theo thời gian
- Màu sắc theo mức độ ưu tiên
- Hiển thị deadline

#### Form View
- **Stat buttons**: Người nhận, Đã đọc, Quá hạn, Liên kết
- **Progress bar**: Tỉ lệ % đã đọc
- **Status bar**: Workflow trạng thái
- **Chatter**: Messages, Activities, Followers
- **Tabs**: Nội dung, Người nhận, Liên kết

#### Tree View
- Decorations theo trạng thái
- Optional columns
- Badges với màu sắc
- Progress bar widget

### 🔔 Loại Thông Báo

| Loại | Icon | Màu sắc | Mô tả |
|------|------|---------|-------|
| Thông tin | 📋 | Blue | Thông báo thông thường |
| Cảnh báo | ⚠️ | Yellow | Cần chú ý |
| Thành công | ✅ | Green | Hoàn thành tốt |
| Lỗi | ❌ | Red | Có vấn đề |
| Khẩn cấp | 🚨 | Dark Red | Cần xử lý ngay |

### 🎯 Mức Độ Ưu Tiên

| Mức độ | Icon | Màu sắc |
|--------|------|---------|
| Thấp | 🔵 | Blue |
| Bình thường | 🟡 | Yellow |
| Cao | 🟠 | Orange |
| Rất cao | 🔴 | Red |

### 🔧 Chức Năng Nâng Cao

#### Quản Lý Thời Hạn
- Đặt deadline cho thông báo
- Tính số ngày còn lại
- Cảnh báo quá hạn tự động
- Highlight thông báo quá hạn

#### Thống Kê
- Tổng số người nhận
- Số người đã đọc
- Tỉ lệ % đã đọc
- Progress bar trực quan

#### Tags
- Tạo tags tùy chỉnh
- Màu sắc phân biệt
- Đếm số thông báo theo tag
- Filter theo tags

#### Liên Kết Module
- Liên kết với bất kỳ model nào
- Hiển thị tên record liên quan
- Button xem chi tiết
- Tự động đánh dấu đã đọc khi xem

---

## 🚀 Cài Đặt

### Yêu Cầu

- Odoo 15.0 hoặc cao hơn
- Python 3.7+
- Modules phụ thuộc:
  - `base`
  - `mail`
  - `nhan_su`
  - `quan_ly_cong_viec`
  - `quan_ly_du_an`

### Các Bước Cài Đặt

1. **Clone module vào addons path**
```bash
cd /mnt/extra-addons
git clone [repository-url] thong_bao
```

2. **Cập nhật danh sách apps**
```bash
# Restart Odoo server
sudo systemctl restart odoo

# Hoặc dùng CLI
odoo --addons-path=/mnt/extra-addons --update=all
```

3. **Cài đặt module trong Odoo**
   - Vào **Apps** menu
   - Bỏ filter "Apps"
   - Tìm "Thông báo"
   - Click **Install**

4. **Hoặc cài đặt qua CLI**
```bash
odoo -i thong_bao -d your_database
```

---

## 📖 Sử Dụng

### Tạo Thông Báo Thủ Công

1. Vào menu **📬 Thông báo** → **📬 Danh sách thông báo**
2. Click **Tạo mới**
3. Điền thông tin:
   - Tiêu đề
   - Nội dung (hỗ trợ HTML)
   - Loại thông báo
   - Mức độ ưu tiên
   - Người nhận
   - Thời hạn (tùy chọn)
   - Tags (tùy chọn)
4. Click **Gửi thông báo**

### Tạo Thông Báo Tự Động (Code)

```python
# Trong method của bạn
notification = self.env['thong_bao.notification'].create_notification(
    name='Công việc mới được giao',
    message='<p>Bạn có công việc mới: <b>Hoàn thành báo cáo</b></p>',
    recipient_ids=[user.id for user in users],
    notification_type='info',
    priority='high',
    related_model='cong_viec',
    related_id=task.id,
    deadline=fields.Datetime.now() + timedelta(days=7),
    icon='fa-tasks'
)
```

### Đánh Dấu Đã Đọc

**Thủ công:**
- Mở thông báo
- Click button **✅ Đánh dấu đã đọc**

**Tự động:**
- Khi click vào button **👁️ Xem chi tiết liên quan**

**Code:**
```python
notification.mark_as_read()
```

### Lọc Thông Báo

Module cung cấp nhiều filters:

- **📬 Thông báo của tôi**: Thông báo bạn nhận được
- **📭 Chưa đọc**: Thông báo chưa đọc
- **✅ Đã đọc**: Thông báo đã đọc
- **🚨 Khẩn cấp**: Thông báo khẩn cấp
- **⏰ Quá hạn**: Thông báo quá thời hạn
- **📅 Có thời hạn**: Thông báo có deadline

---

## ⚙️ Cấu Hình

### Tạo Tags

1. Vào **📬 Thông báo** → **🏷️ Tags**
2. Click **Tạo mới**
3. Nhập tên tag
4. Chọn màu sắc
5. Lưu

### Quyền Truy Cập

Mặc định, tất cả users có quyền:
- Đọc (Read)
- Tạo (Create)
- Sửa (Write)
- Xóa (Unlink)

Để tùy chỉnh, sửa file `security/ir.model.access.csv`

---

## 🔌 API

### Model: `thong_bao.notification`

#### Methods

##### `create_notification()`
Tạo thông báo mới.

**Parameters:**
- `name` (str): Tiêu đề *
- `message` (str): Nội dung HTML *
- `recipient_ids` (list): Danh sách user IDs *
- `notification_type` (str): 'info', 'warning', 'success', 'error', 'urgent'
- `priority` (str): 'low', 'normal', 'high', 'critical'
- `related_model` (str): Model name
- `related_id` (int): Record ID
- `deadline` (datetime): Thời hạn
- `tag_ids` (list): Tag IDs
- `icon` (str): Font Awesome class

**Returns:** `thong_bao.notification` record

**Example:**
```python
notification = self.env['thong_bao.notification'].create_notification(
    name='Test Notification',
    message='<p>This is a test</p>',
    recipient_ids=[1, 2, 3],
    notification_type='info',
    priority='normal'
)
```

##### `mark_as_read()`
Đánh dấu thông báo đã đọc bởi user hiện tại.

```python
notification.mark_as_read()
```

##### `mark_as_unread()`
Đánh dấu thông báo chưa đọc.

```python
notification.mark_as_unread()
```

##### `action_archive()`
Lưu trữ thông báo.

```python
notification.action_archive()
```

##### `action_send()`
Gửi thông báo (chuyển từ draft sang sent).

```python
notification.action_send()
```

##### `action_view_related()`
Mở form view của record liên quan.

```python
return notification.action_view_related()
```

### Model: `thong_bao.tag`

#### Fields
- `name` (Char): Tên tag
- `color` (Integer): Màu sắc (0-11)
- `notification_count` (Integer): Số thông báo

---

## 📸 Screenshots

### Kanban View
![Kanban View](static/description/screenshot_kanban.png)

### Form View
![Form View](static/description/screenshot_form.png)

### Calendar View
![Calendar View](static/description/screenshot_calendar.png)

---

## 📝 Changelog

Xem [CHANGELOG.md](CHANGELOG.md) để biết chi tiết các thay đổi.

---

## 🤝 Đóng Góp

Chúng tôi welcome contributions! 

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

---

## 📄 License

Module này được phát hành dưới giấy phép [LGPL-3](LICENSE).

---

## 💬 Hỗ Trợ

Nếu bạn gặp vấn đề hoặc có câu hỏi:

- 📧 Email: support@yourcompany.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourrepo/issues)
- 📚 Documentation: [Wiki](https://github.com/yourrepo/wiki)

---

## 👨‍💻 Authors

- Your Team - *Initial work*

---

## 🙏 Acknowledgments

- Odoo Community
- Bootstrap
- Font Awesome
- All contributors

---

Made with ❤️ by Your Team
