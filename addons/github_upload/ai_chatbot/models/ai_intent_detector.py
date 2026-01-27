# -*- coding: utf-8 -*-
"""
AI Intent Detector - Phát hiện ý định người dùng từ tin nhắn chat

Hỗ trợ 5 loại intent chính:
1. question - Câu hỏi về task, deadline, assignee
2. summary - Yêu cầu tóm tắt cuộc trò chuyện
3. task_creation - Tạo task mới từ chat
4. warning - Cảnh báo về deadline, task trễ
5. suggestion - Gợi ý task tiếp theo
"""

from odoo import models, api
import re
from datetime import datetime


class AIIntentDetector(models.AbstractModel):
    _name = 'ai.intent.detector'
    _description = 'AI Intent Detector - Phát hiện ý định người dùng'

    @api.model
    def detect_intent(self, message):
        """
        Phát hiện intent từ tin nhắn
        
        Args:
            message (str): Nội dung tin nhắn
            
        Returns:
            dict: {
                'intent': str (question/summary/task_creation/warning/suggestion),
                'confidence': float (0-1),
                'entities': dict (các thông tin trích xuất được)
            }
        """
        message = self.extract_message_content(message)
        message_lower = message.lower()
        
        # 1. Kiểm tra yêu cầu TÓM TẮT
        summary_patterns = [
            r'tóm tắt',
            r'summary',
            r'tổng kết',
            r'recap',
            r'tóm lược',
            r'điểm lại',
        ]
        
        if any(re.search(pattern, message_lower) for pattern in summary_patterns):
            return {
                'intent': 'summary',
                'confidence': 0.9,
                'entities': self._extract_time_range(message)
            }
        
        # 2. Kiểm tra TẠO TASK
        task_creation_patterns = [
            r'tạo (task|nhiệm vụ|công việc)',
            r'create task',
            r'add task',
            r'thêm (task|nhiệm vụ)',
            r'làm.*task',
        ]
        
        if any(re.search(pattern, message_lower) for pattern in task_creation_patterns):
            return {
                'intent': 'task_creation',
                'confidence': 0.85,
                'entities': self.extract_task_info(message)
            }
        
        # 3. Kiểm tra CẢNH BÁO
        warning_patterns = [
            r'(task|nhiệm vụ|công việc).*(trễ|muộn|chậm|quá hạn)',
            r'deadline',
            r'sắp (hết hạn|đến hạn)',
            r'(task|nhiệm vụ).*(nào|gì).*(cần ưu tiên|khẩn cấp)',
        ]
        
        if any(re.search(pattern, message_lower) for pattern in warning_patterns):
            return {
                'intent': 'warning',
                'confidence': 0.88,
                'entities': {}
            }
        
        # 4. Kiểm tra GỢI Ý
        suggestion_patterns = [
            r'(nên|cần) làm (gì|task nào)',
            r'làm (tiếp|gì tiếp theo)',
            r'suggest',
            r'gợi ý',
            r'recommend',
            r'(task|nhiệm vụ) (nào|gì) tiếp theo',
        ]
        
        if any(re.search(pattern, message_lower) for pattern in suggestion_patterns):
            return {
                'intent': 'suggestion',
                'confidence': 0.87,
                'entities': {}
            }
        
        # 5. Mặc định: CÂU HỎI
        return {
            'intent': 'question',
            'confidence': 0.75,
            'entities': self.extract_question_entities(message)
        }
    
    def extract_message_content(self, message):
        """Loại bỏ @ai prefix và khoảng trắng thừa"""
        message = re.sub(r'@ai\s*', '', message, flags=re.IGNORECASE)
        return message.strip()
    
    def _extract_time_range(self, message):
        """Trích xuất khoảng thời gian từ tin nhắn"""
        message_lower = message.lower()
        
        if 'hôm nay' in message_lower or 'today' in message_lower:
            return {'time_range': 'today'}
        elif 'tuần này' in message_lower or 'this week' in message_lower:
            return {'time_range': 'this_week'}
        elif 'tháng này' in message_lower or 'this month' in message_lower:
            return {'time_range': 'this_month'}
        
        return {'time_range': 'all'}
    
    def extract_task_info(self, message):
        """
        Trích xuất thông tin để tạo task
        
        Returns:
            dict: {
                'title': str,
                'description': str,
                'priority': str (low/normal/high),
                'deadline': date
            }
        """
        entities = {}
        
        # Trích xuất tên task (phần sau "tạo task")
        title_match = re.search(
            r'(?:tạo|create|add|thêm)\s*(?:task|nhiệm vụ|công việc)\s+(.+?)(?:\.|$|với|có)',
            message,
            re.IGNORECASE
        )
        if title_match:
            entities['title'] = title_match.group(1).strip()
        else:
            entities['title'] = message
        
        # Trích xuất priority
        if re.search(r'(khẩn cấp|urgent|high|cao|gấp)', message, re.IGNORECASE):
            entities['priority'] = 'high'
        elif re.search(r'(thấp|low)', message, re.IGNORECASE):
            entities['priority'] = 'low'
        else:
            entities['priority'] = 'normal'
        
        # Trích xuất deadline (đơn giản)
        deadline_match = re.search(
            r'(?:deadline|hạn|đến ngày|trước)\s*(\d{1,2}[-/]\d{1,2})',
            message,
            re.IGNORECASE
        )
        if deadline_match:
            entities['deadline'] = deadline_match.group(1)
        
        return entities
    
    def extract_question_entities(self, message):
        """
        Trích xuất entities từ câu hỏi
        
        Returns:
            dict: {
                'question_type': str (count/status/deadline/assignee),
                'target': str (task/project/employee),
                'filters': dict
            }
        """
        message_lower = message.lower()
        entities = {
            'question_type': 'general',
            'target': 'task',
            'filters': {}
        }
        
        # Xác định question type
        if re.search(r'(bao nhiêu|how many|số lượng|count)', message_lower):
            entities['question_type'] = 'count'
        elif re.search(r'(trạng thái|status|tình trạng)', message_lower):
            entities['question_type'] = 'status'
        elif re.search(r'(deadline|hạn|khi nào)', message_lower):
            entities['question_type'] = 'deadline'
        elif re.search(r'(ai|who|người nào|assignee)', message_lower):
            entities['question_type'] = 'assignee'
        
        # Xác định target
        if re.search(r'(dự án|project)', message_lower):
            entities['target'] = 'project'
        elif re.search(r'(nhân viên|employee|người)', message_lower):
            entities['target'] = 'employee'
        
        # Filters
        if re.search(r'(chưa|chưa xong|chưa hoàn thành)', message_lower):
            entities['filters']['state'] = 'todo'
        elif re.search(r'(đã xong|hoàn thành|completed)', message_lower):
            entities['filters']['state'] = 'done'
        
        return entities
