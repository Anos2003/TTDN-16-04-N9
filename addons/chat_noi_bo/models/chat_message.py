# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import datetime


class ChatMessage(models.Model):
    _name = 'chat.message'
    _description = 'Tin nhắn chat'
    _order = 'create_date desc'
    _rec_name = 'content'

    # Phòng chat
    room_id = fields.Many2one('chat.room', string="Phòng chat", required=True, 
                              ondelete='cascade', index=True)
    
    # Người gửi
    sender_id = fields.Many2one('nhan_vien', string="Người gửi", required=True,
                                default=lambda self: self.env['nhan_vien'].search([('user_id', '=', self.env.user.id)], limit=1).id)
    sender_user_id = fields.Many2one('res.users', string="User", 
                                     related='sender_id.user_id', store=True)
    
    # Nội dung
    message_type = fields.Selection([
        ('text', '📝 Văn bản'),
        ('file', '📎 File đính kèm'),
        ('image', '🖼️ Hình ảnh'),
        ('notification', '🔔 Thông báo hệ thống'),
    ], string="Loại tin nhắn", default='text', required=True)
    
    content = fields.Text("Nội dung", required=True)
    
    # File đính kèm
    attachment_ids = fields.Many2many('ir.attachment', relation='chat_message_attachment_rel',
                                      column1='message_id', column2='attachment_id',
                                      string="File đính kèm")
    attachment_count = fields.Integer("Số file", compute='_compute_attachment_count')
    
    # Trạng thái đọc
    read_by_ids = fields.Many2many('nhan_vien', relation='chat_message_read_rel',
                                   column1='message_id', column2='employee_id',
                                   string="Đã đọc bởi")
    read_count = fields.Integer("Số người đã đọc", compute='_compute_read_count')
    is_read_by_me = fields.Boolean("Tôi đã đọc", compute='_compute_is_read_by_me')
    
    # Reply/Thread
    parent_id = fields.Many2one('chat.message', string="Trả lời tin nhắn", ondelete='set null')
    reply_count = fields.Integer("Số phản hồi", compute='_compute_reply_count')
    
    # Thời gian
    create_date = fields.Datetime("Thời gian gửi", readonly=True)
    
    # Reactions (emoji)
    reaction_ids = fields.One2many('chat.message.reaction', 'message_id', string="Reactions")

    # === Computed Methods ===
    @api.depends('attachment_ids')
    def _compute_attachment_count(self):
        """Đếm số file đính kèm"""
        for message in self:
            message.attachment_count = len(message.attachment_ids)
    
    @api.depends('read_by_ids')
    def _compute_read_count(self):
        """Đếm số người đã đọc"""
        for message in self:
            message.read_count = len(message.read_by_ids)
    
    def _compute_is_read_by_me(self):
        """Kiểm tra tôi đã đọc chưa"""
        current_employee = self.env['nhan_vien'].search([('user_id', '=', self.env.user.id)], limit=1)
        for message in self:
            message.is_read_by_me = current_employee in message.read_by_ids if current_employee else False
    
    @api.depends('parent_id')
    def _compute_reply_count(self):
        """Đếm số phản hồi"""
        for message in self:
            message.reply_count = self.search_count([('parent_id', '=', message.id)])

    # === Business Methods ===
    @api.model
    def create(self, vals):
        """Tạo tin nhắn và gửi thông báo"""
        # Kiểm tra quyền gửi tin nhắn trong phòng thông báo
        room = self.env['chat.room'].browse(vals.get('room_id'))
        if room.is_announcement_room:
            # Chỉ admin/manager mới gửi được
            is_admin = self.env.user.has_group('base.group_system') or \
                       self.env.user.has_group('base.group_erp_manager')
            if not is_admin:
                raise exceptions.UserError(
                    '📢 Phòng này chỉ dành cho thông báo từ Ban Quản Lý.\n'
                    'Bạn không có quyền gửi tin nhắn vào đây.'
                )
        
        message = super().create(vals)
        
        # Tự động đánh dấu người gửi đã đọc
        if message.sender_id:
            message.read_by_ids = [(4, message.sender_id.id)]
        
        # Gửi bus notification cho realtime
        try:
            message._notify_new_message()
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f'Không thể gửi bus notification: {e}')
        
        # Gửi thông báo cho các thành viên khác
        try:
            message._send_notification()
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f'Không thể gửi thông báo chat: {e}')
        
        return message
    
    def _notify_new_message(self):
        """Gửi bus notification realtime cho tin nhắn mới"""
        self.ensure_one()
        
        # Lấy thông tin tin nhắn để gửi
        message_data = {
            'id': self.id,
            'room_id': self.room_id.id,
            'sender_id': [self.sender_id.id, self.sender_id.ten],
            'content': self.content,
            'message_type': self.message_type,
            'create_date': self.create_date.isoformat() if self.create_date else False,
            'is_read_by_me': False,
        }
        
        # Gửi notification đến channel của room
        channel = f'chat_room_{self.room_id.id}'
        self.env['bus.bus']._sendone(channel, 'chat.message/new', message_data)
    
    def _send_notification(self):
        """Gửi thông báo cho thành viên phòng chat"""
        self.ensure_one()
        
        # Lấy danh sách thành viên trừ người gửi
        recipients = self.room_id.member_ids.filtered(lambda m: m != self.sender_id and m.user_id)
        
        if recipients and self.env['ir.model'].search([('model', '=', 'thong_bao.notification')], limit=1):
            # Tạo thông báo
            recipient_users = recipients.mapped('user_id')
            
            message_preview = self.content[:100] if self.message_type == 'text' else '[File đính kèm]'
            
            self.env['thong_bao.notification'].sudo().create({
                'name': f'💬 Tin nhắn mới từ {self.sender_id.name}',
                'message': f'''
                    <div style="font-family: Arial, sans-serif;">
                        <h3>💬 Tin nhắn mới trong {self.room_id.name}</h3>
                        <p><strong>Từ:</strong> {self.sender_id.name}</p>
                        <p><strong>Nội dung:</strong></p>
                        <blockquote style="border-left: 3px solid #3498DB; padding-left: 10px; color: #555;">
                            {message_preview}
                        </blockquote>
                    </div>
                ''',
                'recipient_ids': [(6, 0, recipient_users.ids)],
                'notification_type': 'info',
                'priority': 'normal',
                'related_model': 'chat.room',
                'related_id': self.room_id.id,
                'icon': 'fa-comments',
                'state': 'sent',
            })
    
    def action_mark_as_read(self):
        """Đánh dấu đã đọc"""
        current_employee = self.env['nhan_vien'].search([('user_id', '=', self.env.user.id)], limit=1)
        if current_employee:
            for message in self:
                if current_employee not in message.read_by_ids:
                    message.read_by_ids = [(4, current_employee.id)]
    
    def action_reply(self):
        """Trả lời tin nhắn"""
        self.ensure_one()
        # Tìm nhân viên của user hiện tại
        current_employee = self.env['nhan_vien'].search([('user_id', '=', self.env.user.id)], limit=1)
        return {
            'name': 'Trả lời tin nhắn',
            'type': 'ir.actions.act_window',
            'res_model': 'chat.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_room_id': self.room_id.id,
                'default_parent_id': self.id,
                'default_sender_id': current_employee.id if current_employee else False,
            },
        }


class ChatMessageReaction(models.Model):
    _name = 'chat.message.reaction'
    _description = 'Reaction tin nhắn'
    _rec_name = 'emoji'

    message_id = fields.Many2one('chat.message', string="Tin nhắn", required=True, ondelete='cascade')
    employee_id = fields.Many2one('nhan_vien', string="Nhân viên", required=True, ondelete='cascade')
    emoji = fields.Char("Emoji", required=True, size=10)
    create_date = fields.Datetime("Thời gian", readonly=True)
