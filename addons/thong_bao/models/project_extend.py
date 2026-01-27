# -*- coding: utf-8 -*-
from odoo import models, api


class DuAnExtend(models.Model):
    _inherit = 'du_an'

    @api.model
    def create(self, vals):
        """Gửi thông báo khi tạo dự án mới"""
        result = super().create(vals)
        
        # Thông báo cho tất cả quản lý
        if result:
            admin_users = self.env['res.users'].search([('login', '=', 'admin')])
            
            if admin_users:
                project_manager = ""
                if result.quan_ly_id:
                    project_manager = f" - Quản lý: {result.quan_ly_id.name}"
                
                self.env['thong_bao.notification'].create_notification(
                    name=f'Dự án mới: {result.name}',
                    message=f'Dự án "{result.name}" đã được tạo.{project_manager}',
                    recipient_ids=admin_users.ids,
                    notification_type='success',
                    priority='normal',
                    related_model='du_an',
                    related_id=result.id,
                )
            
            # Thông báo cho quản lý dự án
            if result.quan_ly_id and result.quan_ly_id.user_id:
                self.env['thong_bao.notification'].create_notification(
                    name=f'Bạn được giao quản lý dự án: {result.name}',
                    message=f'Bạn đã được giao quản lý dự án "{result.name}". Ngày bắt đầu: {result.ngay_bat_dau if result.ngay_bat_dau else "Không xác định"}',
                    recipient_ids=[result.quan_ly_id.user_id.id],
                    notification_type='success',
                    priority='high',
                    related_model='du_an',
                    related_id=result.id,
                )
        
        return result

    def write(self, vals):
        """Gửi thông báo khi cập nhật dự án"""
        result = super().write(vals)
        
        # Nếu thay đổi trạng thái
        if 'trang_thai' in vals:
            for record in self:
                status_dict = dict(record._fields["trang_thai"].selection)
                status_name = status_dict.get(vals['trang_thai'], "không xác định")
                admin_users = self.env['res.users'].search([('login', '=', 'admin')])
                
                if admin_users:
                    self.env['thong_bao.notification'].create_notification(
                        name=f'Cập nhật dự án: {record.name}',
                        message=f'Dự án "{record.name}" đã được chuyển đến trạng thái: {status_name}.',
                        recipient_ids=admin_users.ids,
                        notification_type='info',
                        priority='normal',
                        related_model='du_an',
                        related_id=record.id,
                    )
        
        # Nếu thay đổi quản lý dự án
        if 'quan_ly_id' in vals:
            for record in self:
                new_manager = self.env['nhan_vien'].browse(vals['quan_ly_id']) if vals['quan_ly_id'] else None
                admin_users = self.env['res.users'].search([('login', '=', 'admin')])
                
                if admin_users:
                    manager_name = new_manager.name if new_manager else "chưa xác định"
                    self.env['thong_bao.notification'].create_notification(
                        name=f'Thay đổi quản lý dự án: {record.name}',
                        message=f'Quản lý dự án "{record.name}" đã được thay đổi thành: {manager_name}.',
                        recipient_ids=admin_users.ids,
                        notification_type='info',
                        priority='normal',
                        related_model='du_an',
                        related_id=record.id,
                    )
                
                # Gửi thông báo cho quản lý mới (nếu có)
                if new_manager and new_manager.user_id:
                    self.env['thong_bao.notification'].create_notification(
                        name=f'Bạn được giao quản lý dự án: {record.name}',
                        message=f'Bạn đã được giao quản lý dự án "{record.name}".',
                        recipient_ids=[new_manager.user_id.id],
                        notification_type='info',
                        priority='high',
                        related_model='du_an',
                        related_id=record.id,
                    )
        
        # Nếu thay đổi ngày kết thúc
        if 'ngay_ket_thuc' in vals:
            for record in self:
                admin_users = self.env['res.users'].search([('login', '=', 'admin')])
                
                if admin_users and vals['ngay_ket_thuc']:
                    self.env['thong_bao.notification'].create_notification(
                        name=f'Cập nhật thời hạn: {record.name}',
                        message=f'Dự án "{record.name}" có thời hạn mới: {vals["ngay_ket_thuc"]}.',
                        recipient_ids=admin_users.ids,
                        notification_type='warning',
                        priority='normal',
                        related_model='du_an',
                        related_id=record.id,
                    )
        
        return result

