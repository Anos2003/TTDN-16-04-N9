# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta


class CongViecExtend(models.Model):
    _inherit = 'cong_viec'

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
        """Lấy các thông báo liên quan đến công việc này"""
        for record in self:
            notifications = self.env['thong_bao.notification'].search([
                ('related_model', '=', 'cong_viec'),
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
            'domain': [('related_model', '=', 'cong_viec'), ('related_id', '=', self.id)],
            'context': {'default_related_model': 'cong_viec', 'default_related_id': self.id},
        }

    @api.model
    def create(self, vals):
        """Gửi thông báo khi công việc mới được tạo"""
        result = super().create(vals)
        
        try:
            if result:
                # Lấy thông tin dự án
                project_name = result.du_an_id.name if result.du_an_id else "không xác định"
                priority_dict = dict(result._fields["priority"].selection)
                priority_level = priority_dict.get(result.priority, "bình thường")
                
                # Tạo message HTML đẹp
                base_message = f'''
                    <div style="font-family: Arial, sans-serif;">
                        <h3 style="color: #2C3E50;">📋 Công việc mới</h3>
                        <p><strong>Tên công việc:</strong> {result.name}</p>
                        <p><strong>Dự án:</strong> {project_name}</p>
                        <p><strong>Mức độ ưu tiên:</strong> <span class="badge">{priority_level}</span></p>
                '''
                
                if result.ngay_bat_dau:
                    base_message += f'<p><strong>📅 Ngày bắt đầu:</strong> {result.ngay_bat_dau}</p>'
                if result.ngay_ket_thuc:
                    base_message += f'<p><strong>⏰ Thời hạn:</strong> {result.ngay_ket_thuc}</p>'
                if result.mo_ta:
                    mo_ta_short = result.mo_ta[:200] + '...' if len(result.mo_ta) > 200 else result.mo_ta
                    base_message += f'<p><strong>Mô tả:</strong><br/>{mo_ta_short}</p>'
                
                base_message += '</div>'
                
                # Nếu có người thực hiện, gửi thông báo cho họ
                if result.assigned_to_id and result.assigned_to_id.user_id:
                    user_message = base_message.replace('📋 Công việc mới', '🎯 Bạn được giao công việc mới')
                    
                    self.env['thong_bao.notification'].create_notification(
                        name=f'🎯 Công việc mới: {result.name}',
                        message=user_message,
                        recipient_ids=[result.assigned_to_id.user_id.id],
                        notification_type='info',
                        priority='high' if result.priority in ['critical', 'high'] else 'normal',
                        related_model='cong_viec',
                        related_id=result.id,
                        deadline=result.ngay_ket_thuc if result.ngay_ket_thuc else None,
                        icon='fa-tasks'
                    )
                
                # Thông báo cho quản lý dự án (nếu khác người thực hiện)
                if result.du_an_id and result.du_an_id.quan_ly_id and result.du_an_id.quan_ly_id.user_id:
                    manager_user = result.du_an_id.quan_ly_id.user_id
                    # Chỉ gửi nếu manager khác người thực hiện
                    if not result.assigned_to_id or manager_user.id != result.assigned_to_id.user_id.id:
                        manager_message = base_message
                        if result.assigned_to_id:
                            manager_message = manager_message.replace('</div>', 
                                f'<p><strong>👤 Người thực hiện:</strong> {result.assigned_to_id.name}</p></div>')
                        
                        self.env['thong_bao.notification'].create_notification(
                            name=f'📊 Công việc mới trong dự án: {result.name}',
                            message=manager_message,
                            recipient_ids=[manager_user.id],
                            notification_type='info',
                            priority='normal',
                            related_model='cong_viec',
                            related_id=result.id,
                            icon='fa-project-diagram'
                        )
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f'Không thể gửi thông báo cho công việc mới: {e}')
        
        return result

    def write(self, vals):
        """Gửi thông báo khi cập nhật công việc"""
        result = super().write(vals)
        
        try:
            # Nếu có thay đổi trạng thái
            if 'trang_thai' in vals:
                for record in self:
                    status_dict = dict(record._fields["trang_thai"].selection)
                    status_display = status_dict.get(vals["trang_thai"], "không xác định")
                    project_name = record.du_an_id.name if record.du_an_id else "không xác định"
                    
                    # Xác định loại thông báo và độ ưu tiên dựa trên trạng thái
                    notif_config = {
                        'done': ('success', 'normal', '✅'),
                        'cancelled': ('error', 'normal', '❌'),
                        'blocked': ('warning', 'high', '🚫'),
                        'review': ('info', 'normal', '👀'),
                        'in_progress': ('info', 'normal', '🚀'),
                    }
                    
                    notif_type, priority, icon = notif_config.get(vals["trang_thai"], ('info', 'normal', '📝'))
                    
                    message = f'''
                        <div style="font-family: Arial, sans-serif;">
                            <h3>{icon} Cập nhật trạng thái công việc</h3>
                            <p><strong>Công việc:</strong> {record.name}</p>
                            <p><strong>Dự án:</strong> {project_name}</p>
                            <p><strong>Trạng thái mới:</strong> <span class="badge badge-{notif_type}">{status_display}</span></p>
                        </div>
                    '''
                    
                    # Thông báo cho người thực hiện
                    if record.assigned_to_id and record.assigned_to_id.user_id:
                        self.env['thong_bao.notification'].create_notification(
                            name=f'{icon} Cập nhật: {record.name}',
                            message=message,
                            recipient_ids=[record.assigned_to_id.user_id.id],
                            notification_type=notif_type,
                            priority=priority,
                            related_model='cong_viec',
                            related_id=record.id,
                            icon='fa-tasks'
                        )
                    
                    # Thông báo cho quản lý dự án
                    if record.du_an_id and record.du_an_id.quan_ly_id and record.du_an_id.quan_ly_id.user_id:
                        manager_user = record.du_an_id.quan_ly_id.user_id
                        # Chỉ gửi nếu manager khác người thực hiện
                        if not record.assigned_to_id or manager_user.id != record.assigned_to_id.user_id.id:
                            manager_message = message
                            if record.assigned_to_id:
                                manager_message = manager_message.replace('</div>', 
                                    f'<p><strong>Người thực hiện:</strong> {record.assigned_to_id.name}</p></div>')
                            
                            self.env['thong_bao.notification'].create_notification(
                                name=f'📊 Cập nhật công việc: {record.name}',
                                message=manager_message,
                                recipient_ids=[manager_user.id],
                                notification_type=notif_type,
                                priority='normal',
                                related_model='cong_viec',
                                related_id=record.id,
                                icon='fa-project-diagram'
                            )
            
            # Nếu có thay đổi người thực hiện
            if 'assigned_to_id' in vals and vals['assigned_to_id']:
                for record in self:
                    new_employee = self.env['nhan_vien'].browse(vals['assigned_to_id'])
                    
                    # Gửi thông báo cho nhân viên mới
                    if new_employee.user_id:
                        message = f'''
                            <div style="font-family: Arial, sans-serif;">
                                <h3>🎯 Bạn được giao công việc mới</h3>
                                <p><strong>Công việc:</strong> {record.name}</p>
                                <p><strong>Dự án:</strong> {record.du_an_id.name if record.du_an_id else "Không xác định"}</p>
                        '''
                        if record.ngay_ket_thuc:
                            message += f'<p><strong>⏰ Thời hạn:</strong> {record.ngay_ket_thuc}</p>'
                        if record.priority:
                            priority_dict = dict(record._fields["priority"].selection)
                            priority_label = priority_dict.get(record.priority, "")
                            message += f'<p><strong>Mức độ ưu tiên:</strong> {priority_label}</p>'
                        message += '</div>'
                        
                        self.env['thong_bao.notification'].create_notification(
                            name=f'🎯 Công việc mới: {record.name}',
                            message=message,
                            recipient_ids=[new_employee.user_id.id],
                            notification_type='success',
                            priority='high',
                            related_model='cong_viec',
                            related_id=record.id,
                            deadline=record.ngay_ket_thuc if record.ngay_ket_thuc else None,
                            icon='fa-user-check'
                        )
            
            # Nếu thay đổi ngày kết thúc
            if 'ngay_ket_thuc' in vals and vals['ngay_ket_thuc']:
                for record in self:
                    message = f'''
                        <div style="font-family: Arial, sans-serif;">
                            <h3>⏰ Cập nhật thời hạn</h3>
                            <p><strong>Công việc:</strong> {record.name}</p>
                            <p><strong>Thời hạn mới:</strong> <span style="color: #E74C3C; font-weight: bold;">{vals["ngay_ket_thuc"]}</span></p>
                        </div>
                    '''
                    
                    # Thông báo cho người thực hiện
                    if record.assigned_to_id and record.assigned_to_id.user_id:
                        self.env['thong_bao.notification'].create_notification(
                            name=f'⏰ Cập nhật thời hạn: {record.name}',
                            message=message,
                            recipient_ids=[record.assigned_to_id.user_id.id],
                            notification_type='warning',
                            priority='high',
                            related_model='cong_viec',
                            related_id=record.id,
                            deadline=vals["ngay_ket_thuc"],
                            icon='fa-clock'
                        )
            
            # Nếu thay đổi ưu tiên sang cao hoặc rất cao
            if 'priority' in vals and vals["priority"] in ['high', 'critical']:
                for record in self:
                    priority_dict = dict(record._fields["priority"].selection)
                    priority_display = priority_dict.get(vals["priority"], "không xác định")
                    
                    message = f'''
                        <div style="font-family: Arial, sans-serif;">
                            <h3>🔴 Cập nhật mức độ ưu tiên</h3>
                            <p><strong>Công việc:</strong> {record.name}</p>
                            <p><strong>Mức độ ưu tiên:</strong> <span style="color: #E74C3C; font-weight: bold;">{priority_display}</span></p>
                            <p style="color: #E67E22;">⚠️ Vui lòng ưu tiên xử lý công việc này!</p>
                        </div>
                    '''
                    
                    # Thông báo cho người thực hiện
                    if record.assigned_to_id and record.assigned_to_id.user_id:
                        self.env['thong_bao.notification'].create_notification(
                            name=f'🔴 Ưu tiên cao: {record.name}',
                            message=message,
                            recipient_ids=[record.assigned_to_id.user_id.id],
                            notification_type='urgent',
                            priority='critical',
                            related_model='cong_viec',
                            related_id=record.id,
                            icon='fa-exclamation-triangle'
                        )
        
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f'Không thể gửi thông báo cập nhật công việc: {e}')
        
        return result
