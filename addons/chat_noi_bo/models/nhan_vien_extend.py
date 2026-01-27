# -*- coding: utf-8 -*-
from odoo import models, fields, api


class NhanVienExtend(models.Model):
    _inherit = 'nhan_vien'

    # Phòng chat
    chat_room_ids = fields.Many2many('chat.room', relation='chat_room_member_rel',
                                     column1='employee_id', column2='room_id',
                                     string="Phòng chat tham gia")
    chat_room_count = fields.Integer("Số phòng chat", compute='_compute_chat_room_count')
    
    # Tin nhắn
    message_sent_count = fields.Integer("Tin nhắn đã gửi", compute='_compute_message_stats')
    
    @api.model
    def create(self, vals):
        """Tạo nhân viên mới và tự động thêm vào phòng chat chung"""
        employee = super(NhanVienExtend, self).create(vals)
        
        # Tự động thêm vào 2 phòng chat mặc định
        # 1. Phòng Chat Chung - Toàn Công Ty
        general_room = self.env.ref('chat_noi_bo.chat_room_general', raise_if_not_found=False)
        if general_room:
            general_room.write({
                'member_ids': [(4, employee.id)]
            })
        
        # 2. Phòng Thông Báo Chung
        announcement_room = self.env.ref('chat_noi_bo.chat_room_announcement', raise_if_not_found=False)
        if announcement_room:
            announcement_room.write({
                'member_ids': [(4, employee.id)]
            })
        
        return employee
    
    def _compute_chat_room_count(self):
        """Đếm số phòng chat"""
        for employee in self:
            employee.chat_room_count = len(employee.chat_room_ids)
    
    def _compute_message_stats(self):
        """Thống kê tin nhắn"""
        for employee in self:
            employee.message_sent_count = self.env['chat.message'].search_count([
                ('sender_id', '=', employee.id)
            ])
    
    def action_view_chat_rooms(self):
        """Xem các phòng chat tham gia"""
        self.ensure_one()
        return {
            'name': f'Phòng chat của {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'chat.room',
            'view_mode': 'tree,form',
            'domain': [('member_ids', 'in', self.id)],
        }
