# -*- coding: utf-8 -*-
from odoo import models, api


class NhanVienExtend(models.Model):
    _inherit = 'nhan_vien'

    @api.model
    def create(self, vals):
        """Gửi thông báo khi tạo nhân viên mới"""
        result = super().create(vals)
        
        # Thông báo cho quản lý khi có nhân viên mới
        if result:
            # Tìm tất cả quản lý HR (admin)
            admin_users = self.env['res.users'].search([('login', '=', 'admin')])
            
            if admin_users:
                self.env['thong_bao.notification'].create_notification(
                    name=f'Nhân viên mới: {result.name}',
                    message=f'Nhân viên "{result.name}" đã được thêm vào hệ thống. Phòng ban: {result.phong_ban_id.name if result.phong_ban_id else "Chưa xác định"}.',
                    recipient_ids=admin_users.ids,
                    notification_type='info',
                    priority='normal',
                    related_model='nhan_vien',
                    related_id=result.id,
                )
        
        return result

    def write(self, vals):
        """Gửi thông báo khi cập nhật thông tin nhân viên"""
        result = super().write(vals)
        
        # Nếu thay đổi trạng thái
        if 'trang_thai' in vals:
            for record in self:
                status_dict = dict(record._fields["trang_thai"].selection)
                status_text = status_dict.get(vals['trang_thai'], "không xác định")
                admin_users = self.env['res.users'].search([('login', '=', 'admin')])
                
                if admin_users:
                    self.env['thong_bao.notification'].create_notification(
                        name=f'Cập nhật nhân viên: {record.name}',
                        message=f'Nhân viên "{record.name}" đã được cập nhật trạng thái: {status_text}.',
                        recipient_ids=admin_users.ids,
                        notification_type='info',
                        priority='normal',
                        related_model='nhan_vien',
                        related_id=record.id,
                    )
        
        # Nếu thay đổi phòng ban
        if 'phong_ban_id' in vals:
            for record in self:
                dept_name = self.env['phong_ban'].browse(vals['phong_ban_id']).name if vals['phong_ban_id'] else "không xác định"
                admin_users = self.env['res.users'].search([('login', '=', 'admin')])
                
                if admin_users:
                    self.env['thong_bao.notification'].create_notification(
                        name=f'Thay đổi phòng ban: {record.name}',
                        message=f'Nhân viên "{record.name}" đã được chuyển đến phòng ban: {dept_name}.',
                        recipient_ids=admin_users.ids,
                        notification_type='info',
                        priority='normal',
                        related_model='nhan_vien',
                        related_id=record.id,
                    )
        
        # Nếu thay đổi chức vụ
        if 'chuc_vu_id' in vals:
            for record in self:
                job_name = self.env['chuc_vu'].browse(vals['chuc_vu_id']).name if vals['chuc_vu_id'] else "không xác định"
                admin_users = self.env['res.users'].search([('login', '=', 'admin')])
                
                if admin_users:
                    self.env['thong_bao.notification'].create_notification(
                        name=f'Thay đổi chức vụ: {record.name}',
                        message=f'Nhân viên "{record.name}" đã được cập nhật chức vụ: {job_name}.',
                        recipient_ids=admin_users.ids,
                        notification_type='info',
                        priority='normal',
                        related_model='nhan_vien',
                        related_id=record.id,
                    )
        
        return result
