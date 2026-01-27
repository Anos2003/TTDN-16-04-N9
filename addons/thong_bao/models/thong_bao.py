# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta


class ThongBao(models.Model):
    _name = 'thong_bao.notification'
    _description = 'Thông báo'
    _order = 'priority desc, create_date desc'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Thông tin cơ bản
    name = fields.Char("Tiêu đề", required=True, index=True, tracking=True)
    message = fields.Html("Nội dung", required=True, tracking=True)
    short_description = fields.Char("Mô tả ngắn", compute="_compute_short_description", store=True)
    
    # Phân loại
    notification_type = fields.Selection([
        ('info', '📋 Thông tin'),
        ('warning', '⚠️ Cảnh báo'),
        ('success', '✅ Thành công'),
        ('error', '❌ Lỗi'),
        ('urgent', '🚨 Khẩn cấp'),
    ], string="Loại thông báo", default='info', required=True, tracking=True)
    
    priority = fields.Selection([
        ('low', '🔵 Thấp'),
        ('normal', '🟡 Bình thường'),
        ('high', '🟠 Cao'),
        ('critical', '🔴 Rất cao'),
    ], string="Ưu tiên", default='normal', required=True, index=True, tracking=True)
    
    # Giao diện
    icon = fields.Char("Icon", help="Font Awesome icon class, ví dụ: fa-bell, fa-info-circle")
    color = fields.Integer("Màu sắc", default=0)
    
    # Tags để phân loại
    tag_ids = fields.Many2many('thong_bao.tag', string="Tags")
    
    # Liên kết với các module
    related_model = fields.Char("Model liên quan", index=True)
    related_id = fields.Integer("ID liên quan", index=True)
    related_name = fields.Char("Tên liên quan", compute="_compute_related_name", store=True)
    
    # Thông tin người nhận
    employee_recipient_ids = fields.Many2many('nhan_vien', relation='thong_bao_employee_recipient_rel',
                                              column1='notification_id', column2='employee_id',
                                              string="👥 Chọn nhân viên", required=True,
                                              help="Chọn nhân viên từ module quản lý nhân sự. Nhân viên phải có tài khoản người dùng.")
    recipient_ids = fields.Many2many('res.users', relation='thong_bao_recipient_rel', 
                                     column1='notification_id', column2='user_id', 
                                     string="👤 Người nhận (Users)",
                                     help="Tự động từ nhân viên đã chọn.")
    read_by_ids = fields.Many2many('res.users', relation='thong_bao_read_rel',
                                   column1='notification_id', column2='user_id',
                                   string="Đã đọc bởi")
    is_read = fields.Boolean("Đã đọc", compute="_compute_is_read", store=False)
    
    # Thời hạn
    deadline = fields.Datetime("Thời hạn", tracking=True)
    is_overdue = fields.Boolean("Quá hạn", compute="_compute_is_overdue", store=False)
    days_until_deadline = fields.Integer("Ngày còn lại", compute="_compute_days_until_deadline", store=False)
    
    # Thông tin tạo
    created_by_id = fields.Many2one('res.users', string="Được tạo bởi", 
                                    default=lambda self: self.env.user, readonly=True)
    create_date = fields.Datetime("Ngày tạo", readonly=True)
    
    # Trạng thái
    state = fields.Selection([
        ('draft', 'Nháp'),
        ('sent', 'Đã gửi'),
        ('read', 'Đã đọc'),
        ('archived', 'Lưu trữ'),
    ], string="Trạng thái", default='draft', required=True, index=True, tracking=True)
    
    # Computed fields
    total_recipients = fields.Integer("Tổng người nhận", compute="_compute_recipient_stats", store=True)
    total_read = fields.Integer("Đã đọc", compute="_compute_recipient_stats", store=True)
    read_percentage = fields.Float("% Đã đọc", compute="_compute_recipient_stats", store=True)

    # === Computed Methods ===
    @api.depends('message')
    def _compute_short_description(self):
        """Tạo mô tả ngắn từ nội dung"""
        for record in self:
            if record.message:
                # Loại bỏ HTML tags và lấy 100 ký tự đầu
                import re
                text = re.sub('<[^<]+?>', '', record.message)
                record.short_description = text[:100] + '...' if len(text) > 100 else text
            else:
                record.short_description = ''

    @api.depends('related_model', 'related_id')
    def _compute_related_name(self):
        """Lấy tên của record liên quan"""
        for record in self:
            if record.related_model and record.related_id:
                try:
                    related_record = self.env[record.related_model].browse(record.related_id)
                    if related_record.exists():
                        record.related_name = related_record.display_name
                    else:
                        record.related_name = False
                except Exception:
                    record.related_name = False
            else:
                record.related_name = False

    @api.depends('read_by_ids')
    def _compute_is_read(self):
        """Kiểm tra người dùng hiện tại đã đọc chưa"""
        for record in self:
            record.is_read = self.env.user in record.read_by_ids

    @api.depends('deadline')
    def _compute_is_overdue(self):
        """Kiểm tra quá hạn"""
        for record in self:
            if record.deadline:
                record.is_overdue = record.deadline < fields.Datetime.now() and record.state != 'read'
            else:
                record.is_overdue = False

    @api.depends('deadline')
    def _compute_days_until_deadline(self):
        """Tính số ngày còn lại đến deadline"""
        for record in self:
            if record.deadline:
                delta = record.deadline - fields.Datetime.now()
                record.days_until_deadline = delta.days
            else:
                record.days_until_deadline = 0

    @api.depends('recipient_ids', 'read_by_ids')
    def _compute_recipient_stats(self):
        """Tính thống kê người nhận và đã đọc"""
        for record in self:
            record.total_recipients = len(record.recipient_ids)
            record.total_read = len(record.read_by_ids)
            if record.total_recipients > 0:
                record.read_percentage = (record.total_read / record.total_recipients) * 100
            else:
                record.read_percentage = 0.0

    # === Onchange Methods ===
    @api.onchange('employee_recipient_ids')
    def _onchange_employee_recipient_ids(self):
        """Tự động chuyển từ nhân viên sang users và yêu cầu nhân viên phải có user_id"""
        if self.employee_recipient_ids:
            # Kiểm tra nhân viên không có user trước
            employees_without_user = self.employee_recipient_ids.filtered(lambda e: not e.user_id)
            if employees_without_user:
                employee_names = ', '.join(employees_without_user.mapped('name'))
                # Xóa các nhân viên không có user khỏi danh sách
                self.employee_recipient_ids = [(3, emp.id) for emp in employees_without_user]
                return {
                    'warning': {
                        'title': '❌ Không thể chọn nhân viên',
                        'message': f'Các nhân viên sau chưa có tài khoản người dùng và đã bị loại bỏ:\n\n{employee_names}\n\n⚠️ Vui lòng liên kết tài khoản người dùng cho nhân viên này trước khi gửi thông báo.\n\nVào: Quản lý Nhân sự > Nhân viên > Chọn nhân viên > Trường "Người dùng hệ thống"'
                    }
                }
            
            # Lấy users từ nhân viên có user_id
            users = self.employee_recipient_ids.mapped('user_id')
            if users:
                self.recipient_ids = [(6, 0, users.ids)]

    # === Business Methods ===
    @api.model
    def create_notification(self, name, message, recipient_ids=None, notification_type='info', 
                          priority='normal', related_model=None, related_id=None, deadline=None, 
                          tag_ids=None, icon=None):
        """
        Hàm tiện ích để tạo thông báo
        Args:
            name: Tiêu đề thông báo
            message: Nội dung thông báo
            recipient_ids: Danh sách ID người nhận
            notification_type: Loại thông báo (info, warning, success, error, urgent)
            priority: Ưu tiên (low, normal, high, critical)
            related_model: Model liên quan
            related_id: ID của record liên quan
            deadline: Thời hạn thông báo
            tag_ids: Danh sách tag IDs
            icon: Font Awesome icon
        """
        if recipient_ids is None:
            recipient_ids = []
        
        vals = {
            'name': name,
            'message': message,
            'recipient_ids': [(6, 0, recipient_ids)],
            'notification_type': notification_type,
            'priority': priority,
            'related_model': related_model,
            'related_id': related_id,
            'state': 'sent',
        }
        
        if deadline:
            vals['deadline'] = deadline
        if tag_ids:
            vals['tag_ids'] = [(6, 0, tag_ids)]
        if icon:
            vals['icon'] = icon
        
        notification = self.create(vals)
        
        # Gửi thông báo Odoo nội bộ
        for user_id in recipient_ids:
            user = self.env['res.users'].browse(user_id)
            if user.exists() and user.partner_id:
                notification.message_post(
                    body=message,
                    subject=name,
                    partner_ids=[user.partner_id.id],
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                )
        
        return notification

    def mark_as_read(self):
        """Đánh dấu thông báo là đã đọc"""
        for notification in self:
            if self.env.user not in notification.read_by_ids:
                notification.read_by_ids = [(4, self.env.user.id)]
            
            # Nếu tất cả người nhận đã đọc, chuyển sang trạng thái 'read'
            if len(notification.read_by_ids) >= len(notification.recipient_ids):
                notification.state = 'read'

    def mark_as_unread(self):
        """Đánh dấu chưa đọc"""
        for notification in self:
            if self.env.user in notification.read_by_ids:
                notification.read_by_ids = [(3, self.env.user.id)]
            notification.state = 'sent'

    def action_archive(self):
        """Lưu trữ thông báo"""
        self.write({'state': 'archived'})

    def action_send(self):
        """Gửi thông báo (chuyển từ draft sang sent)"""
        self.write({'state': 'sent'})
        
        # Gửi thông báo Odoo
        for notification in self:
            for user in notification.recipient_ids:
                if user.partner_id:
                    notification.message_post(
                        body=notification.message,
                        subject=notification.name,
                        partner_ids=[user.partner_id.id],
                        message_type='notification',
                        subtype_xmlid='mail.mt_comment',
                    )

    def action_view_related(self):
        """Xem record liên quan"""
        self.ensure_one()
        if self.related_model and self.related_id:
            # Đánh dấu là đã đọc khi xem
            self.mark_as_read()
            
            return {
                'name': 'Chi tiết',
                'type': 'ir.actions.act_window',
                'res_model': self.related_model,
                'res_id': self.related_id,
                'view_mode': 'form',
                'target': 'current',
            }


class ThongBaoTag(models.Model):
    """Tags để phân loại thông báo"""
    _name = 'thong_bao.tag'
    _description = 'Tag thông báo'
    _order = 'name'

    name = fields.Char("Tên tag", required=True)
    color = fields.Integer("Màu sắc", default=0)
    notification_count = fields.Integer("Số thông báo", compute="_compute_notification_count")

    @api.depends('notification_count')
    def _compute_notification_count(self):
        """Đếm số thông báo theo tag"""
        for tag in self:
            tag.notification_count = self.env['thong_bao.notification'].search_count([
                ('tag_ids', 'in', tag.id)
            ])
