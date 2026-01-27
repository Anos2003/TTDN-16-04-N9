from odoo import models, fields, api


class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Phòng ban'

    name = fields.Char("Tên phòng ban", required=True)
    mo_ta = fields.Text("Mô tả")


class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Chức vụ'

    name = fields.Char("Tên chức vụ", required=True)
    mo_ta = fields.Text("Mô tả")


class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'

    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    ho = fields.Char("Họ", required=True)
    ten = fields.Char("Tên", required=True)
    name = fields.Char("Họ và tên", compute="_compute_name", store=True)
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    dia_chi = fields.Text("Địa chỉ")
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban")
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ")
    luong = fields.Float("Lương")
    ngay_vao_lam = fields.Date("Ngày vào làm")
    trang_thai = fields.Selection([
        ('active', 'Đang làm việc'),
        ('inactive', 'Nghỉ việc'),
    ], string="Trạng thái", default='active')
    user_id = fields.Many2one('res.users', string="Người dùng hệ thống")

    @api.depends('ho', 'ten')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.ho} {record.ten}" if record.ho and record.ten else ""
