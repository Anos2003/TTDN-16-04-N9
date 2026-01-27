from odoo import models, fields, api


class CongViec(models.Model):
    _name = 'cong_viec'
    _description = 'Công việc'
    _order = 'priority desc, ngay_ket_thuc, name'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Thông tin cơ bản (CHỈ GIỮ CÁC FIELD CÓ TRONG DATABASE)
    name = fields.Char("Tên công việc", required=True, index=True, tracking=True)
    mo_ta = fields.Text("Mô tả chi tiết", tracking=True)
    
    # Liên kết
    du_an_id = fields.Many2one('du_an', string="Dự án", ondelete='cascade', required=True, index=True, tracking=True)
    assigned_to_id = fields.Many2one('nhan_vien', string="Người thực hiện", ondelete='set null', index=True, tracking=True)
    
    # Thời gian
    ngay_bat_dau = fields.Date("Ngày bắt đầu", tracking=True)
    ngay_ket_thuc = fields.Date("Ngày kết thúc dự kiến", required=True, tracking=True)
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('todo', 'Chưa bắt đầu'),
        ('in_progress', 'Đang thực hiện'),
        ('review', 'Đang đánh giá'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Hủy'),
        ('blocked', 'Bị chặn'),
    ], string="Trạng thái", default='todo', index=True, tracking=True)
    
    # Ưu tiên
    priority = fields.Selection([
        ('low', '🔵 Thấp'),
        ('medium', '🟡 Trung bình'),
        ('high', '🔴 Cao'),
        ('critical', '🔴 Rất cao'),
    ], string="Mức độ ưu tiên", default='medium', index=True, tracking=True)

    # Action methods cho buttons
    def action_start(self):
        """Bắt đầu công việc"""
        for record in self:
            record.trang_thai = 'in_progress'
            if not record.ngay_bat_dau:
                record.ngay_bat_dau = fields.Date.today()
            record.message_post(body="Công việc đã được bắt đầu")
    
    def action_review(self):
        """Gửi đánh giá"""
        for record in self:
            record.trang_thai = 'review'
            record.message_post(body="Công việc đã gửi đánh giá")
    
    def action_done(self):
        """Hoàn thành công việc"""
        for record in self:
            record.trang_thai = 'done'
            record.message_post(body="Công việc đã hoàn thành")
    
    def action_cancel(self):
        """Hủy công việc"""
        for record in self:
            record.trang_thai = 'cancelled'
            record.message_post(body="Công việc đã bị hủy")