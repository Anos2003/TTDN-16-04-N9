# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DuAnExtend(models.Model):
    _inherit = 'du_an'

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
        """Lấy các thông báo liên quan đến dự án này"""
        for record in self:
            notifications = self.env['thong_bao.notification'].search([
                ('related_model', '=', 'du_an'),
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
            'domain': [('related_model', '=', 'du_an'), ('related_id', '=', self.id)],
            'context': {'default_related_model': 'du_an', 'default_related_id': self.id},
        }

    @api.model
    def create(self, vals):
        """Gửi thông báo khi dự án mới được tạo"""
        result = super().create(vals)
        
        try:
            # Tạo message HTML đẹp
            message = f'''
                <div style="font-family: Arial, sans-serif;">
                    <h3 style="color: #27AE60;">🎯 Dự án mới được tạo</h3>
                    <p><strong>Tên dự án:</strong> {result.name}</p>
            '''
            
            if result.quan_ly_id:
                message += f'<p><strong>👤 Quản lý dự án:</strong> {result.quan_ly_id.name}</p>'
            if result.ngay_bat_dau:
                message += f'<p><strong>📅 Ngày bắt đầu:</strong> {result.ngay_bat_dau}</p>'
            if result.ngay_ket_thuc:
                message += f'<p><strong>🏁 Ngày kết thúc dự kiến:</strong> {result.ngay_ket_thuc}</p>'
            if result.mo_ta:
                mo_ta_short = result.mo_ta[:200] + '...' if len(result.mo_ta) > 200 else result.mo_ta
                message += f'<p><strong>Mô tả:</strong><br/>{mo_ta_short}</p>'
            
            message += '</div>'
            
            # Tạo thông báo cho các quản lý cấp cao
            admin_users = self.env['res.users'].search([
                '|', ('groups_id', 'ilike', 'project'),
                ('login', '=', 'admin')
            ])
            
            if admin_users:
                self.env['thong_bao.notification'].create_notification(
                    name=f'🎯 Dự án mới: {result.name}',
                    message=message,
                    recipient_ids=admin_users.ids,
                    notification_type='success',
                    priority='normal',
                    related_model='du_an',
                    related_id=result.id,
                    icon='fa-project-diagram'
                )
            
            # Thông báo riêng cho quản lý dự án
            if result.quan_ly_id and result.quan_ly_id.user_id:
                manager_message = f'''
                    <div style="font-family: Arial, sans-serif;">
                        <h3 style="color: #3498DB;">👨‍💼 Bạn được giao quản lý dự án mới</h3>
                        <p><strong>Tên dự án:</strong> {result.name}</p>
                '''
                if result.ngay_bat_dau:
                    manager_message += f'<p><strong>📅 Ngày bắt đầu:</strong> {result.ngay_bat_dau}</p>'
                if result.ngay_ket_thuc:
                    manager_message += f'<p><strong>🏁 Ngày kết thúc dự kiến:</strong> {result.ngay_ket_thuc}</p>'
                if result.mo_ta:
                    manager_message += f'<p><strong>Mô tả:</strong><br/>{result.mo_ta[:300]}</p>'
                
                manager_message += '<p style="color: #E67E22; font-weight: bold;">⭐ Vui lòng kiểm tra và bắt đầu lập kế hoạch!</p></div>'
                
                self.env['thong_bao.notification'].create_notification(
                    name=f'👨‍💼 Quản lý dự án: {result.name}',
                    message=manager_message,
                    recipient_ids=[result.quan_ly_id.user_id.id],
                    notification_type='success',
                    priority='high',
                    related_model='du_an',
                    related_id=result.id,
                    deadline=result.ngay_bat_dau if result.ngay_bat_dau else None,
                    icon='fa-user-tie'
                )
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f'Không thể gửi thông báo cho dự án mới: {e}')
        
        return result

    def write(self, vals):
        """Gửi thông báo khi cập nhật dự án"""
        result = super().write(vals)
        
        try:
            # Nếu có thay đổi trạng thái
            if 'trang_thai' in vals:
                for record in self:
                    status_dict = dict(record._fields["trang_thai"].selection)
                    status_display = status_dict.get(vals["trang_thai"], "không xác định")
                    
                    # Xác định loại thông báo dựa trên trạng thái
                    notif_config = {
                        'done': ('success', '✅', 'Dự án đã hoàn thành thành công!'),
                        'cancelled': ('error', '❌', 'Dự án đã bị hủy.'),
                        'in_progress': ('info', '🚀', 'Dự án đang được triển khai.'),
                        'review': ('warning', '👀', 'Dự án đang trong giai đoạn đánh giá.'),
                        'planning': ('info', '📝', 'Dự án đang trong giai đoạn lập kế hoạch.'),
                    }
                    
                    notif_type, icon, description = notif_config.get(vals["trang_thai"], ('info', '📋', ''))
                    
                    message = f'''
                        <div style="font-family: Arial, sans-serif;">
                            <h3>{icon} Cập nhật trạng thái dự án</h3>
                            <p><strong>Dự án:</strong> {record.name}</p>
                            <p><strong>Trạng thái mới:</strong> <span class="badge badge-{notif_type}">{status_display}</span></p>
                            <p style="color: #7F8C8D;">{description}</p>
                        </div>
                    '''
                    
                    # Thông báo cho quản lý dự án
                    if record.quan_ly_id and record.quan_ly_id.user_id:
                        self.env['thong_bao.notification'].create_notification(
                            name=f'{icon} Cập nhật dự án: {record.name}',
                            message=message,
                            recipient_ids=[record.quan_ly_id.user_id.id],
                            notification_type=notif_type,
                            priority='high' if vals["trang_thai"] in ['done', 'cancelled'] else 'normal',
                            related_model='du_an',
                            related_id=record.id,
                            icon='fa-project-diagram'
                        )
                    
                    # Thông báo cho admin
                    admin_users = self.env['res.users'].search([
                        '|', ('groups_id', 'ilike', 'project'),
                        ('login', '=', 'admin')
                    ])
                    if admin_users:
                        admin_message = message.replace('</div>', 
                            f'<p><strong>Quản lý:</strong> {record.quan_ly_id.name if record.quan_ly_id else "Chưa xác định"}</p></div>')
                        
                        self.env['thong_bao.notification'].create_notification(
                            name=f'📊 Cập nhật dự án: {record.name}',
                            message=admin_message,
                            recipient_ids=admin_users.ids,
                            notification_type=notif_type,
                            priority='normal',
                            related_model='du_an',
                            related_id=record.id,
                            icon='fa-chart-line'
                        )
            
            # Nếu có thay đổi quản lý dự án
            if 'quan_ly_id' in vals and vals['quan_ly_id']:
                for record in self:
                    new_manager = self.env['nhan_vien'].browse(vals['quan_ly_id'])
                    
                    if new_manager.user_id:
                        message = f'''
                            <div style="font-family: Arial, sans-serif;">
                                <h3 style="color: #3498DB;">👨‍💼 Bạn được giao quản lý dự án</h3>
                                <p><strong>Dự án:</strong> {record.name}</p>
                        '''
                        if record.ngay_bat_dau:
                            message += f'<p><strong>📅 Ngày bắt đầu:</strong> {record.ngay_bat_dau}</p>'
                        if record.ngay_ket_thuc:
                            message += f'<p><strong>🏁 Ngày kết thúc:</strong> {record.ngay_ket_thuc}</p>'
                        
                        # Đếm số công việc trong dự án
                        try:
                            task_count = self.env['cong_viec'].search_count([('du_an_id', '=', record.id)])
                            if task_count > 0:
                                message += f'<p><strong>📋 Số công việc:</strong> {task_count}</p>'
                        except:
                            pass
                        
                        message += '<p style="color: #E67E22; font-weight: bold;">⭐ Vui lòng kiểm tra và tiếp tục quản lý!</p></div>'
                        
                        self.env['thong_bao.notification'].create_notification(
                            name=f'👨‍💼 Quản lý dự án mới: {record.name}',
                            message=message,
                            recipient_ids=[new_manager.user_id.id],
                            notification_type='success',
                            priority='high',
                            related_model='du_an',
                            related_id=record.id,
                            icon='fa-user-tie'
                        )
            
            # Nếu có thay đổi ngày kết thúc
            if 'ngay_ket_thuc' in vals and vals['ngay_ket_thuc']:
                for record in self:
                    message = f'''
                        <div style="font-family: Arial, sans-serif;">
                            <h3>⏰ Cập nhật thời hạn dự án</h3>
                            <p><strong>Dự án:</strong> {record.name}</p>
                            <p><strong>Ngày kết thúc mới:</strong> <span style="color: #E74C3C; font-weight: bold;">{vals["ngay_ket_thuc"]}</span></p>
                        </div>
                    '''
                    
                    # Thông báo cho quản lý dự án
                    if record.quan_ly_id and record.quan_ly_id.user_id:
                        self.env['thong_bao.notification'].create_notification(
                            name=f'⏰ Cập nhật thời hạn: {record.name}',
                            message=message,
                            recipient_ids=[record.quan_ly_id.user_id.id],
                            notification_type='warning',
                            priority='high',
                            related_model='du_an',
                            related_id=record.id,
                            deadline=vals["ngay_ket_thuc"],
                            icon='fa-clock'
                        )
        
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f'Không thể gửi thông báo cập nhật dự án: {e}')
        
        return result
        
        # Nếu có thay đổi trạng thái
        if 'trang_thai' in vals:
            for record in self:
                status_display = dict(record._fields["trang_thai"].selection).get(vals["trang_thai"])
                
                # Thông báo cho quản lý dự án
                if record.quan_ly_id and record.quan_ly_id.user_id:
                    self.env['thong_bao.notification'].create_notification(
                        name=f'Cập nhật dự án: {record.name}',
                        message=f'Dự án "{record.name}" - Trạng thái: {status_display}',
                        recipient_ids=[record.quan_ly_id.user_id.id],
                        notification_type='warning',
                        priority='high',
                        related_model='du_an',
                        related_id=record.id,
                    )
        
        # Nếu có thay đổi quản lý dự án
        if 'quan_ly_id' in vals:
            for record in self:
                if record.quan_ly_id and record.quan_ly_id.user_id:
                    self.env['thong_bao.notification'].create_notification(
                        name=f'Bạn được giao quản lý dự án: {record.name}',
                        message=f'Bạn đã được giao quản lý dự án "{record.name}".',
                        recipient_ids=[record.quan_ly_id.user_id.id],
                        notification_type='success',
                        priority='high',
                        related_model='du_an',
                        related_id=record.id,
                    )
        
        return result
