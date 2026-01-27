# -*- coding: utf-8 -*-
"""
Extend chat.message model để thêm chức năng AI
"""

from odoo import models, fields, api


class ChatMessageExtend(models.Model):
    _inherit = 'chat.message'

    # Metadata cho AI messages
    is_ai_response = fields.Boolean("AI Response", default=False, index=True,
                                    help="Tin nhắn này được gửi bởi AI Assistant")
    
    ai_intent = fields.Selection([
        ('question', 'Câu hỏi'),
        ('summary', 'Tóm tắt'),
        ('task_creation', 'Tạo task'),
        ('warning', 'Cảnh báo'),
        ('suggestion', 'Gợi ý'),
    ], string="AI Intent", help="Loại yêu cầu AI xử lý")
    
    ai_confidence = fields.Float("AI Confidence", help="Độ tin cậy của AI (0-1)")
    
    ai_processing_time = fields.Float("Processing Time (s)", 
                                      help="Thời gian AI xử lý (giây)")
    
    @api.model
    def create_ai_response(self, room_id, content, intent=None, confidence=None, processing_time=None):
        """
        Tạo tin nhắn phản hồi từ AI
        
        Args:
            room_id (int): ID phòng chat
            content (str): Nội dung phản hồi
            intent (str): Intent được phát hiện
            confidence (float): Độ tin cậy
            processing_time (float): Thời gian xử lý
            
        Returns:
            chat.message: Tin nhắn AI được tạo
        """
        # Tìm AI user
        ai_user = self.env.ref('ai_chatbot.user_ai_assistant', raise_if_not_found=False)
        if not ai_user:
            ai_user = self.env['res.users'].sudo().search([('login', '=', 'ai_assistant')], limit=1)
        
        # Tìm nhân viên AI
        ai_employee = None
        if ai_user:
            ai_employee = self.env['nhan_vien'].sudo().search([('user_id', '=', ai_user.id)], limit=1)
        
        if not ai_employee:
            # Fallback: dùng user hiện tại
            current_employee = self.env['nhan_vien'].search([('user_id', '=', self.env.user.id)], limit=1)
            ai_employee = current_employee
        
        # Tạo tin nhắn
        message = self.sudo().create({
            'room_id': room_id,
            'sender_id': ai_employee.id if ai_employee else False,
            'content': content,
            'message_type': 'text',
            'is_ai_response': True,
            'ai_intent': intent,
            'ai_confidence': confidence,
            'ai_processing_time': processing_time,
        })
        
        return message
