# -*- coding: utf-8 -*-
from odoo import models, fields, api


class NhanVienExtend(models.Model):
    _inherit = 'nhan_vien'

    # Trường liên kết với thông báo
    notification_ids = fields.One2many(
        'thong_bao.notification', 
        compute='_compute_notifications',
        string="Thông báo liên quan"
    )
    notification_count = fields.Integer(
        "Số thông báo", 
        compute='_compute_notifications'
    )

    def _compute_notifications(self):
        """Lấy các thông báo liên quan đến nhân viên này"""
        for record in self:
            notifications = self.env['thong_bao.notification'].search([
                ('related_model', '=', 'nhan_vien'),
                ('related_id', '=', record.id)
            ])
            record.notification_ids = notifications
            record.notification_count = len(notifications)

    def action_view_notifications(self):
        """Action để xem các thông báo liên quan"""
        self.ensure_one()
        return {
            'name': f'Thông báo - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'thong_bao.notification',
            'view_mode': 'tree,form',
            'domain': [('related_model', '=', 'nhan_vien'), ('related_id', '=', self.id)],
            'context': {'default_related_model': 'nhan_vien', 'default_related_id': self.id},
        }

    @api.model
    def create(self, vals):
        """Gửi thông báo khi nhân viên mới được tạo"""
        result = super().create(vals)
        
        try:
            # Tạo thông báo cho tất cả người quản lý HR
            hr_managers = self.env['res.users'].search([
                '|', ('groups_id', 'ilike', 'hr'),
                ('login', '=', 'admin')
            ])
            
            if hr_managers:
                message = f'<p>Nhân viên <strong>{result.name}</strong> ({result.ma_dinh_danh}) đã được tạo trong hệ thống.</p>'
                if result.phong_ban_id:
                    message += f'<p>📍 Phòng ban: {result.phong_ban_id.name}</p>'
                if result.chuc_vu_id:
                    message += f'<p>💼 Chức vụ: {result.chuc_vu_id.name}</p>'
                if result.ngay_vao_lam:
                    message += f'<p>📅 Ngày vào làm: {result.ngay_vao_lam}</p>'
                
                self.env['thong_bao.notification'].create_notification(
                    name=f'🆕 Nhân viên mới: {result.name}',
                    message=message,
                    recipient_ids=hr_managers.ids,
                    notification_type='success',
                    priority='normal',
                    related_model='nhan_vien',
                    related_id=result.id,
                    icon='fa-user-plus'
                )
        except Exception as e:
            # Log lỗi nhưng không block việc tạo nhân viên
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f'Không thể gửi thông báo cho nhân viên mới: {e}')
        
        return result

    def write(self, vals):
        """Gửi thông báo khi cập nhật thông tin quan trọng của nhân viên"""
        result = super().write(vals)
        
        try:
            # Các trường quan trọng cần thông báo
            important_fields = {
                'trang_thai': ('⚠️ Thay đổi trạng thái', 'warning', 'high'),
                'phong_ban_id': ('🔄 Thay đổi phòng ban', 'info', 'normal'),
                'chuc_vu_id': ('💼 Thay đổi chức vụ', 'info', 'normal'),
                'luong': ('💰 Thay đổi lương', 'warning', 'high'),
            }
            
            for field, (title_prefix, notif_type, priority) in important_fields.items():
                if field in vals:
                    for record in self:
                        # Tạo message chi tiết
                        message = f'<p><strong>{record.name}</strong> ({record.ma_dinh_danh})</p>'
                        
                        if field == 'trang_thai':
                            status_display = dict(record._fields["trang_thai"].selection).get(vals["trang_thai"])
                            message += f'<p>Trạng thái: <span class="badge badge-{notif_type}">{status_display}</span></p>'
                        elif field == 'phong_ban_id':
                            new_dept = self.env['phong_ban'].browse(vals['phong_ban_id'])
                            message += f'<p>Phòng ban mới: {new_dept.name if new_dept else "Không xác định"}</p>'
                        elif field == 'chuc_vu_id':
                            new_position = self.env['chuc_vu'].browse(vals['chuc_vu_id'])
                            message += f'<p>Chức vụ mới: {new_position.name if new_position else "Không xác định"}</p>'
                        elif field == 'luong':
                            message += f'<p>Lương mới: {vals["luong"]:,.0f} VNĐ</p>'
                        
                        # Tìm người nhận thông báo
                        recipients = self.env['res.users'].search([
                            '|', ('groups_id', 'ilike', 'hr'),
                            ('login', '=', 'admin')
                        ])
                        
                        if recipients:
                            self.env['thong_bao.notification'].create_notification(
                                name=f'{title_prefix}: {record.name}',
                                message=message,
                                recipient_ids=recipients.ids,
                                notification_type=notif_type,
                                priority=priority,
                                related_model='nhan_vien',
                                related_id=record.id,
                                icon='fa-user-edit'
                            )
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f'Không thể gửi thông báo cập nhật nhân viên: {e}')
        
        return result
