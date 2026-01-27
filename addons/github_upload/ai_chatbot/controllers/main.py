# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class AIChatbotController(http.Controller):
    
    @http.route('/ai_chatbot/process_message', type='json', auth='user', methods=['POST'])
    def process_message(self, room_id, message, **kwargs):
        """
        Xử lý tin nhắn chat và tạo phản hồi AI
        
        Args:
            room_id (int): ID phòng chat
            message (str): Nội dung tin nhắn
            
        Returns:
            dict: Kết quả xử lý
        """
        try:
            # Kiểm tra message có @ai không
            if not message.lower().strip().startswith('@ai'):
                return {
                    'success': False,
                    'error': 'Message must start with @ai'
                }
            
            # Lấy nhân viên hiện tại
            current_employee = request.env['nhan_vien'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not current_employee:
                return {
                    'success': False,
                    'error': 'Nhân viên không tồn tại'
                }
            
            # Tạo tin nhắn user
            user_message = request.env['chat.message'].create({
                'room_id': room_id,
                'sender_id': current_employee.id,
                'content': message,
                'message_type': 'text',
            })
            
            # Xử lý AI
            processor = request.env['ai.chatbot.processor']
            result = processor.process_message(
                room_id=room_id,
                message_content=message,
                sender_id=current_employee.id
            )
            
            if result.get('success'):
                # Tạo tin nhắn AI response
                ai_message = request.env['chat.message'].create_ai_response(
                    room_id=room_id,
                    content=result['message'],
                    intent=result.get('intent'),
                    confidence=result.get('confidence'),
                    processing_time=result.get('processing_time')
                )
                
                return {
                    'success': True,
                    'user_message_id': user_message.id,
                    'ai_message_id': ai_message.id,
                    'message': result['message'],
                    'intent': result.get('intent'),
                    'confidence': result.get('confidence'),
                }
            else:
                return result
                
        except Exception as e:
            _logger.error(f"Error in process_message: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/ai_chatbot/get_messages', type='json', auth='user', methods=['POST'])
    def get_messages(self, room_id, limit=50, **kwargs):
        """
        Lấy danh sách tin nhắn trong phòng chat
        
        Args:
            room_id (int): ID phòng chat
            limit (int): Số lượng tin nhắn tối đa
            
        Returns:
            dict: Danh sách tin nhắn
        """
        try:
            messages = request.env['chat.message'].search([
                ('room_id', '=', room_id)
            ], order='create_date asc', limit=limit)
            
            message_list = []
            for msg in messages:
                message_list.append({
                    'id': msg.id,
                    'sender_id': msg.sender_id.id if msg.sender_id else False,
                    'sender_name': msg.sender_id.name if msg.sender_id else 'AI Assistant',
                    'content': msg.content,
                    'is_ai_response': msg.is_ai_response,
                    'create_date': msg.create_date.isoformat() if msg.create_date else False,
                    'message_type': msg.message_type,
                })
            
            return {
                'success': True,
                'messages': message_list
            }
            
        except Exception as e:
            _logger.error(f"Error in get_messages: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'messages': []
            }
    
    @http.route('/ai_chatbot/send_message', type='json', auth='user', methods=['POST'])
    def send_message(self, room_id, message, **kwargs):
        """
        Gửi tin nhắn và xử lý AI nếu có @ai
        
        Args:
            room_id (int): ID phòng chat
            message (str): Nội dung tin nhắn
            
        Returns:
            dict: Kết quả
        """
        try:
            is_ai_message = message.lower().strip().startswith('@ai')
            
            if is_ai_message:
                # Xử lý qua AI
                return self.process_message(room_id, message)
            else:
                # Tin nhắn thường
                current_employee = request.env['nhan_vien'].search([
                    ('user_id', '=', request.env.user.id)
                ], limit=1)
                
                if not current_employee:
                    return {
                        'success': False,
                        'error': 'Nhân viên không tồn tại'
                    }
                
                user_message = request.env['chat.message'].create({
                    'room_id': room_id,
                    'sender_id': current_employee.id,
                    'content': message,
                    'message_type': 'text',
                })
                
                return {
                    'success': True,
                    'message_id': user_message.id
                }
                
        except Exception as e:
            _logger.error(f"Error in send_message: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
