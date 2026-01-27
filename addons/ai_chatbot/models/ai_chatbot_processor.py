# -*- coding: utf-8 -*-
"""
AI Chatbot Processor - Xử lý logic AI và tạo phản hồi

Tích hợp với:
- chat.room: Phòng chat nội bộ
- chat.message: Tin nhắn chat
- cong_viec: Quản lý công việc/task
- du_an: Quản lý dự án
"""

from odoo import models, fields, api, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class AIChatbotProcessor(models.AbstractModel):
    _name = 'ai.chatbot.processor'
    _description = 'AI Chatbot Processor - Xử lý logic AI'

    @api.model
    def process_message(self, room_id, message_content, sender_id=None):
        """
        Xử lý tin nhắn và tạo phản hồi AI
        
        Args:
            room_id (int): ID phòng chat
            message_content (str): Nội dung tin nhắn
            sender_id (int): ID nhân viên gửi
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'intent': str,
                'confidence': float,
                'processing_time': float
            }
        """
        start_time = datetime.now()
        
        try:
            # 1. Phát hiện intent
            detector = self.env['ai.intent.detector']
            intent_result = detector.detect_intent(message_content)
            
            intent = intent_result['intent']
            confidence = intent_result['confidence']
            entities = intent_result['entities']
            
            _logger.info(f"Detected intent: {intent} (confidence: {confidence})")
            
            # 2. Lấy thông tin phòng chat
            room = self.env['chat.room'].browse(room_id)
            if not room.exists():
                return {
                    'success': False,
                    'error': 'Phòng chat không tồn tại',
                    'intent': intent,
                    'confidence': confidence
                }
            
            # 3. Xử lý theo intent và từ khóa đặc biệt
            message_lower = message_content.lower()
            
            # Xử lý các lệnh đặc biệt
            if 'phân tích' in message_lower or 'analytics' in message_lower:
                response = self._handle_analytics(room, entities, message_content)
            elif 'tasks của tôi' in message_lower or 'my tasks' in message_lower or 'mytasks' in message_lower:
                response = self._handle_my_tasks(room, entities, sender_id)
            elif 'hôm nay' in message_lower or 'today' in message_lower:
                response = self._handle_today_tasks(room, entities, sender_id)
            elif 'tìm kiếm' in message_lower or 'search' in message_lower:
                response = self._handle_search(room, entities, message_content)
            elif 'ưu tiên cao' in message_lower or 'priority' in message_lower:
                response = self._handle_priority_tasks(room, entities, message_content)
            elif 'tips' in message_lower or 'mẹo' in message_lower:
                response = self._handle_tips(room, entities, message_content)
            elif 'động viên' in message_lower or 'motivation' in message_lower:
                response = self._handle_motivation(room, entities, message_content)
            elif 'thống kê' in message_lower or 'stats' in message_lower:
                response = self._handle_stats(room, entities, message_content)
            else:
                # Xử lý theo intent
                handlers = {
                    'question': self._handle_question,
                    'summary': self._handle_summary,
                    'task_creation': self._handle_task_creation,
                    'warning': self._handle_warning,
                    'suggestion': self._handle_suggestion,
                }
                
                handler = handlers.get(intent)
                if not handler:
                    response = "Xin lỗi, tôi chưa hiểu yêu cầu của bạn. Hãy thử lại với câu hỏi khác."
                else:
                    response = handler(room, entities, message_content)
            
            # 4. Tính thời gian xử lý
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'message': response,
                'intent': intent,
                'confidence': confidence,
                'processing_time': processing_time
            }
            
        except Exception as e:
            _logger.error(f"Error processing AI message: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'message': "Đã xảy ra lỗi khi xử lý tin nhắn. Vui lòng thử lại."
            }
    
    def _handle_question(self, room, entities, message):
        """Xử lý câu hỏi về task, dự án, deadline"""
        question_type = entities.get('question_type', 'general')
        target = entities.get('target', 'task')
        filters = entities.get('filters', {})
        
        # Lấy dự án liên kết với phòng chat (nếu có)
        project = None
        if hasattr(room, 'project_id') and room.project_id:
            project = room.project_id
        
        if target == 'task':
            return self._answer_task_question(question_type, filters, project, message)
        elif target == 'project':
            return self._answer_project_question(question_type, project)
        else:
            return self._answer_general_question(message)
    
    def _answer_task_question(self, question_type, filters, project, message):
        """Trả lời câu hỏi về task"""
        Task = self.env['cong_viec']
        
        # Build domain
        domain = []
        if project:
            domain.append(('du_an_id', '=', project.id))
        
        if filters.get('state') == 'todo':
            domain.append(('trang_thai', '!=', 'done'))
        elif filters.get('state') == 'done':
            domain.append(('trang_thai', '=', 'done'))
        
        tasks = Task.search(domain)
        
        if question_type == 'count':
            count = len(tasks)
            project_text = f" trong dự án **{project.name}**" if project else ""
            
            if filters.get('state') == 'todo':
                return f"Hiện có **{count} task chưa hoàn thành**{project_text}."
            elif filters.get('state') == 'done':
                return f"Đã hoàn thành **{count} task**{project_text}."
            else:
                return f"Tổng cộng có **{count} task**{project_text}."
        
        elif question_type == 'deadline':
            urgent_tasks = tasks.filtered(lambda t: t.ngay_ket_thuc and 
                                         fields.Date.from_string(t.ngay_ket_thuc) <= 
                                         datetime.now().date() + timedelta(days=3))
            
            if not urgent_tasks:
                return "Không có task nào sắp đến deadline trong 3 ngày tới."
            
            response = f"**{len(urgent_tasks)} task sắp đến deadline:**\n"
            for task in urgent_tasks[:5]:
                deadline = fields.Date.from_string(task.ngay_ket_thuc)
                days_left = (deadline - datetime.now().date()).days
                response += f"\n• **{task.name}** - Còn {days_left} ngày"
            
            return response
        
        elif question_type == 'status':
            if not tasks:
                return "Không có task nào."
            
            todo = tasks.filtered(lambda t: t.trang_thai != 'done')
            done = tasks.filtered(lambda t: t.trang_thai == 'done')
            
            return (f"📊 **Tình trạng task:**\n"
                   f"• Chưa xong: {len(todo)}\n"
                   f"• Đã hoàn thành: {len(done)}\n"
                   f"• Tổng: {len(tasks)}")
        
        else:
            # General question
            if not tasks:
                return "Không tìm thấy task nào."
            
            return (f"Hiện có **{len(tasks)} task**. "
                   f"Hãy hỏi cụ thể hơn, ví dụ:\n"
                   f"• Bao nhiêu task chưa xong?\n"
                   f"• Task nào sắp deadline?\n"
                   f"• Ai đang làm task gì?")
    
    def _answer_project_question(self, question_type, project):
        """Trả lời câu hỏi về dự án"""
        if not project:
            projects = self.env['du_an'].search([])
            return f"Hiện có **{len(projects)} dự án** đang hoạt động."
        
        tasks = self.env['cong_viec'].search([('du_an_id', '=', project.id)])
        todo_tasks = tasks.filtered(lambda t: t.trang_thai != 'done')
        done_tasks = tasks.filtered(lambda t: t.trang_thai == 'done')
        
        progress = (len(done_tasks) / len(tasks) * 100) if tasks else 0
        
        return (f"📊 **Dự án: {project.name}**\n\n"
               f"• Tổng task: {len(tasks)}\n"
               f"• Đã hoàn thành: {len(done_tasks)}\n"
               f"• Đang làm: {len(todo_tasks)}\n"
               f"• Tiến độ: {progress:.1f}%")
    
    def _answer_general_question(self, message):
        """Trả lời câu hỏi chung"""
        return ("Tôi có thể giúp bạn:\n"
               "• Hỏi về task và deadline\n"
               "• Tóm tắt cuộc trò chuyện\n"
               "• Tạo task mới\n"
               "• Cảnh báo task trễ\n"
               "• Gợi ý task tiếp theo\n\n"
               "Hãy gõ @ai trước câu hỏi!")
    
    def _handle_summary(self, room, entities, message):
        """Tóm tắt cuộc trò chuyện"""
        time_range = entities.get('time_range', 'today')
        
        # Xác định thời gian
        if time_range == 'today':
            start_date = datetime.now().replace(hour=0, minute=0, second=0)
            period_text = "hôm nay"
        elif time_range == 'this_week':
            start_date = datetime.now() - timedelta(days=datetime.now().weekday())
            period_text = "tuần này"
        elif time_range == 'this_month':
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0)
            period_text = "tháng này"
        else:
            start_date = datetime.now() - timedelta(days=30)
            period_text = "30 ngày qua"
        
        # Lấy tin nhắn
        messages = self.env['chat.message'].search([
            ('room_id', '=', room.id),
            ('create_date', '>=', start_date),
            ('message_type', '=', 'text'),
            ('content', 'not ilike', '@ai'),  # Loại bỏ tin nhắn @ai
        ], order='create_date asc', limit=50)
        
        if not messages:
            return f"Không có tin nhắn nào {period_text}."
        
        # Đếm tin nhắn theo người gửi
        sender_stats = {}
        for msg in messages:
            sender_name = msg.sender_id.name if msg.sender_id else 'Unknown'
            sender_stats[sender_name] = sender_stats.get(sender_name, 0) + 1
        
        # Tạo summary
        response = f"📝 **Tóm tắt chat {period_text}:**\n\n"
        response += f"• Tổng tin nhắn: {len(messages)}\n"
        response += f"• Thành viên tham gia: {len(sender_stats)}\n\n"
        
        # Top contributors
        top_senders = sorted(sender_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        response += "👥 **Người chat nhiều nhất:**\n"
        for sender, count in top_senders:
            response += f"• {sender}: {count} tin nhắn\n"
        
        # Từ khóa quan trọng (đơn giản)
        important_keywords = ['deadline', 'urgent', 'khẩn cấp', 'quan trọng', 'task']
        important_messages = [msg for msg in messages 
                            if any(kw in msg.content.lower() for kw in important_keywords)]
        
        if important_messages:
            response += f"\n⚠️ **{len(important_messages)} tin nhắn quan trọng** được nhắc đến."
        
        return response
    
    def _handle_task_creation(self, room, entities, message):
        """Tạo task mới từ chat"""
        title = entities.get('title', 'Task mới từ chat')
        priority = entities.get('priority', 'normal')
        
        # Map priority
        priority_map = {
            'low': 'low',
            'normal': 'medium',
            'high': 'high'
        }
        
        # Lấy dự án từ room (nếu có)
        project_id = None
        if hasattr(room, 'project_id') and room.project_id:
            project_id = room.project_id.id
        
        try:
            # Tạo task
            task = self.env['cong_viec'].create({
                'name': title,
                'mo_ta': f"Task được tạo từ chat: {room.name}\nNội dung gốc: {message}",
                'priority': priority_map.get(priority, 'medium'),
                'du_an_id': project_id,
                'trang_thai': 'todo',
                'ngay_ket_thuc': fields.Date.today() + timedelta(days=7),
            })
            
            response = (f"✅ **Đã tạo task mới:**\n\n"
                       f"• Tên: **{task.name}**\n"
                       f"• Độ ưu tiên: {priority}\n")
            
            if project_id:
                response += f"• Dự án: {room.project_id.name}\n"
            
            response += f"\nTask ID: #{task.id}"
            
            return response
            
        except Exception as e:
            _logger.error(f"Error creating task: {str(e)}")
            return f"❌ Không thể tạo task. Lỗi: {str(e)}"
    
    def _handle_warning(self, room, entities, message):
        """Cảnh báo về task trễ, deadline"""
        Task = self.env['cong_viec']
        
        # Lấy dự án từ room
        project_id = None
        if hasattr(room, 'project_id') and room.project_id:
            project_id = room.project_id.id
        
        domain = []
        if project_id:
            domain.append(('du_an_id', '=', project_id))
        
        # Task quá hạn
        overdue_domain = domain + [
            ('ngay_ket_thuc', '<', fields.Date.today()),
            ('trang_thai', '!=', 'done')
        ]
        overdue_tasks = Task.search(overdue_domain)
        
        # Task sắp hết hạn (3 ngày)
        upcoming_domain = domain + [
            ('ngay_ket_thuc', '>=', fields.Date.today()),
            ('ngay_ket_thuc', '<=', fields.Date.today() + timedelta(days=3)),
            ('trang_thai', '!=', 'done')
        ]
        upcoming_tasks = Task.search(upcoming_domain)
        
        if not overdue_tasks and not upcoming_tasks:
            return "✅ Tất cả task đều ổn! Không có task nào trễ hạn hay sắp đến deadline."
        
        response = "⚠️ **CẢNH BÁO DEADLINE:**\n\n"
        
        if overdue_tasks:
            response += f"🔴 **{len(overdue_tasks)} task ĐÃ QUÁ HẠN:**\n"
            for task in overdue_tasks[:5]:
                days_overdue = (datetime.now().date() - fields.Date.from_string(task.ngay_ket_thuc)).days
                response += f"• **{task.name}** - Trễ {days_overdue} ngày\n"
            
            if len(overdue_tasks) > 5:
                response += f"• ... và {len(overdue_tasks) - 5} task khác\n"
        
        if upcoming_tasks:
            response += f"\n🟡 **{len(upcoming_tasks)} task SẮP ĐẾN HẠN (3 ngày):**\n"
            for task in upcoming_tasks[:5]:
                deadline = fields.Date.from_string(task.ngay_ket_thuc)
                days_left = (deadline - datetime.now().date()).days
                response += f"• **{task.name}** - Còn {days_left} ngày\n"
        
        return response
    
    def _handle_suggestion(self, room, entities, message):
        """Gợi ý task tiếp theo"""
        Task = self.env['cong_viec']
        
        # Lấy dự án từ room
        project_id = None
        if hasattr(room, 'project_id') and room.project_id:
            project_id = room.project_id.id
        
        domain = [('trang_thai', '!=', 'done')]
        if project_id:
            domain.append(('du_an_id', '=', project_id))
        
        # Ưu tiên:
        # 1. Task có độ ưu tiên cao
        # 2. Task sắp đến deadline
        # 3. Task chưa ai nhận
        
        high_priority = Task.search(domain + [('priority', 'in', ['high', 'critical'])], 
                                    order='ngay_ket_thuc asc', limit=3)
        
        upcoming_deadline = Task.search(
            domain + [('ngay_ket_thuc', '<=', fields.Date.today() + timedelta(days=7))],
            order='ngay_ket_thuc asc',
            limit=3
        )
        
        unassigned = Task.search(domain + [('assigned_to_id', '=', False)], limit=3)
        
        if not high_priority and not upcoming_deadline and not unassigned:
            return "✅ Tuyệt vời! Không có task nào cần ưu tiên ngay. Hãy nghỉ ngơi hoặc làm task khác."
        
        response = "💡 **GỢI Ý TASK NÊN LÀM TIẾP:**\n\n"
        
        if high_priority:
            response += "🔴 **Task ưu tiên cao:**\n"
            for task in high_priority:
                response += f"• **{task.name}**"
                if task.ngay_ket_thuc:
                    response += f" (Deadline: {task.ngay_ket_thuc})"
                response += "\n"
        
        if upcoming_deadline:
            response += "\n⏰ **Task sắp đến deadline (7 ngày):**\n"
            for task in upcoming_deadline:
                days_left = (fields.Date.from_string(task.ngay_ket_thuc) - datetime.now().date()).days
                response += f"• **{task.name}** - Còn {days_left} ngày\n"
        
        if unassigned:
            response += "\n👤 **Task chưa ai nhận:**\n"
            for task in unassigned:
                response += f"• **{task.name}**\n"
        
        response += "\n_Hãy chọn task phù hợp với kỹ năng và thời gian của bạn!_"
        
        return response
    
    def _handle_analytics(self, room, entities, message):
        """Phân tích hiệu suất làm việc"""
        Task = self.env['cong_viec']
        
        # Lấy tasks 30 ngày qua
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        domain = [('create_date', '>=', thirty_days_ago)]
        
        if hasattr(room, 'project_id') and room.project_id:
            domain.append(('du_an_id', '=', room.project_id.id))
        
        tasks = Task.search(domain)
        
        if not tasks:
            return "📊 Chưa có dữ liệu để phân tích."
        
        # Thống kê
        total = len(tasks)
        completed = tasks.filtered(lambda t: t.trang_thai == 'done')
        in_progress = tasks.filtered(lambda t: t.trang_thai == 'in_progress')
        overdue = tasks.filtered(lambda t: t.ngay_ket_thuc and 
                                 fields.Date.from_string(t.ngay_ket_thuc) < datetime.now().date() and
                                 t.trang_thai != 'done')
        
        completion_rate = (len(completed) / total * 100) if total > 0 else 0
        
        # Phân tích theo priority
        high_priority = tasks.filtered(lambda t: t.priority in ['high', 'critical'])
        completed_high = high_priority.filtered(lambda t: t.trang_thai == 'done')
        
        response = "📊 **PHÂN TÍCH HIỆU SUẤT (30 NGÀY):**\n\n"
        response += f"📈 **Tổng quan:**\n"
        response += f"• Tổng tasks: {total}\n"
        response += f"• Hoàn thành: {len(completed)} ({completion_rate:.1f}%)\n"
        response += f"• Đang làm: {len(in_progress)}\n"
        response += f"• Trễ hạn: {len(overdue)}\n\n"
        
        response += f"🎯 **Tasks ưu tiên cao:**\n"
        response += f"• Tổng: {len(high_priority)}\n"
        response += f"• Đã xong: {len(completed_high)}\n\n"
        
        # Đánh giá
        if completion_rate >= 80:
            response += "✅ **Đánh giá: Xuất sắc!** Tiếp tục duy trì!"
        elif completion_rate >= 60:
            response += "👍 **Đánh giá: Tốt!** Cố gắng thêm nữa!"
        elif completion_rate >= 40:
            response += "⚠️ **Đánh giá: Trung bình.** Cần cải thiện."
        else:
            response += "🔴 **Đánh giá: Cần chú ý!** Hãy tập trung hơn."
        
        return response
    
    def _handle_my_tasks(self, room, entities, sender_id):
        """Lấy danh sách tasks của người dùng hiện tại"""
        if not sender_id:
            return "❌ Không xác định được người dùng."
        
        Task = self.env['cong_viec']
        user = self.env['res.users'].browse(sender_id)
        
        # Tìm nhân viên tương ứng
        employee = self.env['nhan_vien'].search([('user_id', '=', user.id)], limit=1)
        
        if not employee:
            return "❌ Không tìm thấy thông tin nhân viên."
        
        # Lấy tasks được gán
        my_tasks = Task.search([
            ('assigned_to_id', '=', employee.id),
            ('trang_thai', '!=', 'done')
        ], order='ngay_ket_thuc asc')
        
        if not my_tasks:
            return "✅ Bạn không có task nào! Hãy liên hệ quản lý để nhận việc mới."
        
        response = f"📋 **TASKS CỦA BẠN ({len(my_tasks)}):**\n\n"
        
        # Nhóm theo trạng thái
        todo = my_tasks.filtered(lambda t: t.trang_thai == 'todo')
        in_progress = my_tasks.filtered(lambda t: t.trang_thai == 'in_progress')
        review = my_tasks.filtered(lambda t: t.trang_thai == 'review')
        
        if in_progress:
            response += "🔵 **Đang làm:**\n"
            for task in in_progress[:3]:
                deadline_text = f" (Deadline: {task.ngay_ket_thuc})" if task.ngay_ket_thuc else ""
                response += f"• {task.name}{deadline_text}\n"
        
        if review:
            response += "\n🟡 **Đang review:**\n"
            for task in review[:3]:
                response += f"• {task.name}\n"
        
        if todo:
            response += f"\n⚪ **Chưa bắt đầu ({len(todo)}):**\n"
            for task in todo[:3]:
                deadline_text = f" (Deadline: {task.ngay_ket_thuc})" if task.ngay_ket_thuc else ""
                response += f"• {task.name}{deadline_text}\n"
            
            if len(todo) > 3:
                response += f"• ... và {len(todo) - 3} task khác\n"
        
        return response
    
    def _handle_today_tasks(self, room, entities, sender_id):
        """Tasks cần làm hôm nay"""
        Task = self.env['cong_viec']
        today = fields.Date.today()
        
        domain = [
            ('ngay_ket_thuc', '=', today),
            ('trang_thai', '!=', 'done')
        ]
        
        if hasattr(room, 'project_id') and room.project_id:
            domain.append(('du_an_id', '=', room.project_id.id))
        
        today_tasks = Task.search(domain, order='priority desc')
        
        if not today_tasks:
            return "✅ Không có task nào deadline hôm nay! Có thể làm task khác."
        
        response = f"📅 **TASKS HÔM NAY ({len(today_tasks)}):**\n\n"
        
        for task in today_tasks:
            priority_icon = {'low': '🔵', 'medium': '🟡', 'high': '🔴', 'critical': '🔴🔴'}.get(task.priority, '⚪')
            assignee = task.assigned_to_id.name if task.assigned_to_id else 'Chưa gán'
            response += f"{priority_icon} **{task.name}** - {assignee}\n"
        
        response += "\n💪 _Chúc bạn một ngày làm việc hiệu quả!_"
        
        return response
    
    def _handle_search(self, room, entities, message):
        """Tìm kiếm tasks theo từ khóa"""
        # Extract search keyword
        keyword = entities.get('keyword', '')
        
        if not keyword:
            # Try to extract from message
            words = message.replace('@ai', '').replace('tìm kiếm', '').replace('search', '').strip()
            keyword = words[:50] if words else ''
        
        if not keyword:
            return "🔍 Vui lòng cung cấp từ khóa tìm kiếm. Ví dụ: `/search bug login`"
        
        Task = self.env['cong_viec']
        
        domain = [
            '|', '|',
            ('name', 'ilike', keyword),
            ('mo_ta', 'ilike', keyword),
            ('du_an_id.name', 'ilike', keyword)
        ]
        
        results = Task.search(domain, limit=10)
        
        if not results:
            return f"🔍 Không tìm thấy task nào với từ khóa: **{keyword}**"
        
        response = f"🔍 **TÌM THẤY {len(results)} TASK:**\n_(từ khóa: {keyword})_\n\n"
        
        for task in results:
            status_icon = {
                'todo': '⚪',
                'in_progress': '🔵',
                'review': '🟡',
                'done': '✅',
                'cancelled': '❌',
                'blocked': '🚫'
            }.get(task.trang_thai, '⚪')
            
            project_name = task.du_an_id.name if task.du_an_id else 'N/A'
            response += f"{status_icon} **{task.name}**\n"
            response += f"   Dự án: {project_name} | ID: #{task.id}\n"
        
        return response
    
    def _handle_priority_tasks(self, room, entities, message):
        """Lấy các tasks có priority cao"""
        Task = self.env['cong_viec']
        
        domain = [
            ('priority', 'in', ['high', 'critical']),
            ('trang_thai', '!=', 'done')
        ]
        
        if hasattr(room, 'project_id') and room.project_id:
            domain.append(('du_an_id', '=', room.project_id.id))
        
        priority_tasks = Task.search(domain, order='ngay_ket_thuc asc', limit=10)
        
        if not priority_tasks:
            return "✅ Không có task ưu tiên cao nào!"
        
        response = f"🔴 **TASKS ƯU TIÊN CAO ({len(priority_tasks)}):**\n\n"
        
        for task in priority_tasks:
            priority_text = "🔴🔴 CRITICAL" if task.priority == 'critical' else "🔴 HIGH"
            assignee = task.assigned_to_id.name if task.assigned_to_id else 'Chưa gán'
            deadline = f" | Deadline: {task.ngay_ket_thuc}" if task.ngay_ket_thuc else ""
            
            response += f"{priority_text}\n"
            response += f"• **{task.name}**\n"
            response += f"  {assignee}{deadline}\n\n"
        
        return response
    
    def _handle_tips(self, room, entities, message):
        """Đưa ra tips làm việc hiệu quả"""
        import random
        
        tips = [
            "💡 **Pomodoro Technique**: Làm việc tập trung 25 phút, nghỉ 5 phút. Lặp lại 4 lần rồi nghỉ 15-30 phút.",
            "💡 **Eat the Frog**: Làm task khó nhất và quan trọng nhất vào đầu ngày khi năng lượng còn cao.",
            "💡 **2-Minute Rule**: Nếu task mất dưới 2 phút, làm ngay lập tức thay vì lên lịch.",
            "💡 **Time Blocking**: Chia ngày thành các khối thời gian cố định cho từng loại công việc.",
            "💡 **Eisenhower Matrix**: Phân loại task theo 4 nhóm: Quan trọng-Gấp, Quan trọng-Không gấp, Không quan trọng-Gấp, Không quan trọng-Không gấp.",
            "💡 **Single-Tasking**: Tập trung 100% vào 1 task thay vì làm nhiều việc cùng lúc.",
            "💡 **Break Down**: Chia task lớn thành các task nhỏ 1-2 giờ để dễ quản lý.",
            "💡 **Energy Management**: Làm việc sáng tạo khi năng lượng cao, việc đơn giản khi mệt.",
            "💡 **No Notification**: Tắt thông báo khi làm việc để tránh bị gián đoạn.",
            "💡 **Daily Review**: Dành 10 phút cuối ngày review công việc và lên kế hoạch ngày mai.",
        ]
        
        tip = random.choice(tips)
        return tip + "\n\n_Áp dụng ngay để nâng cao hiệu suất!_ 🚀"
    
    def _handle_motivation(self, room, entities, message):
        """Động viên tinh thần"""
        import random
        
        quotes = [
            "🚀 **\"Success is not final, failure is not fatal: it is the courage to continue that counts.\"**\n- Winston Churchill",
            "💪 **\"The only way to do great work is to love what you do.\"**\n- Steve Jobs",
            "⭐ **\"Believe you can and you're halfway there.\"**\n- Theodore Roosevelt",
            "🌟 **\"It always seems impossible until it's done.\"**\n- Nelson Mandela",
            "🔥 **\"Don't watch the clock; do what it does. Keep going.\"**\n- Sam Levenson",
            "✨ **\"The future depends on what you do today.\"**\n- Mahatma Gandhi",
            "💫 **\"Quality is not an act, it is a habit.\"**\n- Aristotle",
            "🎯 **\"Focus on being productive instead of busy.\"**\n- Tim Ferriss",
        ]
        
        quote = random.choice(quotes)
        
        # Thêm thống kê nhỏ để động viên
        Task = self.env['cong_viec']
        completed_today = Task.search_count([
            ('trang_thai', '=', 'done'),
            ('write_date', '>=', fields.Date.today())
        ])
        
        if completed_today > 0:
            quote += f"\n\n🎉 Team đã hoàn thành **{completed_today} task** hôm nay! Tuyệt vời!"
        
        return quote
    
    def _handle_stats(self, room, entities, message):
        """Thống kê tổng quan"""
        Task = self.env['cong_viec']
        Project = self.env['du_an']
        
        # Overall stats
        total_tasks = Task.search_count([])
        total_projects = Project.search_count([])
        
        # Task by status
        todo = Task.search_count([('trang_thai', '=', 'todo')])
        in_progress = Task.search_count([('trang_thai', '=', 'in_progress')])
        review = Task.search_count([('trang_thai', '=', 'review')])
        done = Task.search_count([('trang_thai', '=', 'done')])
        
        # This week
        week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        completed_this_week = Task.search_count([
            ('trang_thai', '=', 'done'),
            ('write_date', '>=', week_start)
        ])
        
        response = "📊 **THỐNG KÊ TỔNG QUAN:**\n\n"
        response += f"📂 **Dự án:** {total_projects}\n"
        response += f"📋 **Tổng tasks:** {total_tasks}\n\n"
        
        response += "📈 **Trạng thái tasks:**\n"
        response += f"• ⚪ Chưa làm: {todo}\n"
        response += f"• 🔵 Đang làm: {in_progress}\n"
        response += f"• 🟡 Review: {review}\n"
        response += f"• ✅ Hoàn thành: {done}\n\n"
        
        response += f"🎯 **Tuần này:** {completed_this_week} tasks hoàn thành\n"
        
        if done > 0:
            completion_rate = (done / total_tasks * 100) if total_tasks > 0 else 0
            response += f"\n📊 **Tỷ lệ hoàn thành:** {completion_rate:.1f}%"
        
        return response
