from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta


class DuAn(models.Model):
    _name = 'du_an'
    _description = 'Dự án'
    _order = 'ngay_bat_dau desc, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Thông tin cơ bản (CHỈ GIỮ CÁC FIELD CÓ TRONG DATABASE)
    name = fields.Char("Tên dự án", required=True, index=True, tracking=True)
    mo_ta = fields.Text("Mô tả", tracking=True)
    
    # Lịch trình
    ngay_bat_dau = fields.Date("Ngày bắt đầu", required=True, tracking=True)
    ngay_ket_thuc = fields.Date("Ngày kết thúc dự kiến", required=True, tracking=True)
    
    # Quản lý
    quan_ly_id = fields.Many2one('nhan_vien', string="Quản lý dự án", ondelete='restrict', required=True, tracking=True)
    
    # Trạng thái
    trang_thai = fields.Selection([
        ('draft', 'Nháp'),
        ('planning', 'Lập kế hoạch'),
        ('in_progress', 'Đang thực hiện'),
        ('review', 'Đang đánh giá'),
        ('done', 'Hoàn thành'),
        ('cancelled', 'Hủy'),
    ], string="Trạng thái", default='draft', index=True, tracking=True)
    
    # Computed field để đếm công việc (không cần relationship trực tiếp)
    so_cong_viec = fields.Integer("Số công việc", compute='_compute_cong_viec_count')
    
    @api.depends()
    def _compute_cong_viec_count(self):
        """Đếm số công việc (sẽ hoạt động sau khi quan_ly_cong_viec được cài)"""
        for record in self:
            try:
                record.so_cong_viec = self.env['cong_viec'].search_count([('du_an_id', '=', record.id)])
            except Exception:
                record.so_cong_viec = 0

    # Action methods cho buttons
    def action_start(self):
        """Bắt đầu dự án"""
        for record in self:
            record.trang_thai = 'in_progress'
            record.message_post(body="Dự án đã được bắt đầu")
    
    def action_complete(self):
        """Hoàn thành dự án"""
        for record in self:
            record.trang_thai = 'done'
            record.message_post(body="Dự án đã hoàn thành")
    
    def action_cancel(self):
        """Hủy dự án"""
        for record in self:
            record.trang_thai = 'cancelled'
            record.message_post(body="Dự án đã bị hủy")

    # Các computed methods đã được xóa do field không tồn tại trong database
    # Nếu cần, hãy thêm lại các field vào database trước