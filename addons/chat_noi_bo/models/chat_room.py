# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class ChatRoom(models.Model):
    _name = 'chat.room'
    _description = 'Phòng chat'
    _order = 'last_message_date desc, create_date desc'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Thông tin cơ bản
    name = fields.Char("Tên phòng chat", required=True, tracking=True)
    description = fields.Text("Mô tả")
    
    # Loại phòng chat
    room_type = fields.Selection([
        ('general', '💬 Chat chung'),
        ('project', '📊 Chat dự án'),
        ('department', '🏢 Chat phòng ban'),
        ('private', '🔒 Chat riêng tư'),
    ], string="Loại phòng chat", default='general', required=True, tracking=True)
    
    # Phòng thông báo (chỉ admin/manager gửi được)
    is_announcement_room = fields.Boolean("Phòng thông báo", default=False,
                                          help="Nếu bật, chỉ quản lý/admin mới gửi được tin nhắn")
    
    # Liên kết
    project_id = fields.Many2one('du_an', string="Dự án", ondelete='cascade',
                                 help="Nếu là chat dự án, liên kết với dự án")
    department_id = fields.Many2one('phong_ban', string="Phòng ban", ondelete='set null',
                                    help="Nếu là chat phòng ban")
    
    # Thành viên
    member_ids = fields.Many2many('nhan_vien', relation='chat_room_member_rel',
                                  column1='room_id', column2='employee_id',
                                  string="👥 Thành viên")
    member_user_ids = fields.Many2many('res.users', relation='chat_room_user_rel',
                                       column1='room_id', column2='user_id',
                                       string="Users", compute='_compute_member_users',
                                       store=True)
    member_count = fields.Integer("Số thành viên", compute='_compute_member_count', store=True)
    
    # Người tạo
    created_by_id = fields.Many2one('res.users', string="Người tạo",
                                    default=lambda self: self.env.user, readonly=True)
    
    # Tin nhắn
    message_ids = fields.One2many('chat.message', 'room_id', string="Tin nhắn")
    message_count = fields.Integer("Số tin nhắn", compute='_compute_message_count', store=True)
    last_message_id = fields.Many2one('chat.message', string="Tin nhắn cuối", 
                                      compute='_compute_last_message', store=True)
    last_message_date = fields.Datetime("Thời gian tin nhắn cuối",
                                        compute='_compute_last_message', store=True)
    last_message_preview = fields.Char("Xem trước tin nhắn", 
                                       compute='_compute_last_message', store=True)
    
    # Tin nhắn chưa đọc
    unread_count = fields.Integer("Số tin nhắn chưa đọc", compute='_compute_unread_count')
    
    # Trạng thái
    active = fields.Boolean("Hoạt động", default=True)
    is_archived = fields.Boolean("Đã lưu trữ", default=False)
    
    # Avatar/Icon
    avatar = fields.Binary("Avatar phòng chat")
    color = fields.Integer("Màu sắc", default=0)

    # === Computed Methods ===
    @api.depends('member_ids', 'member_ids.user_id')
    def _compute_member_users(self):
        """Tự động lấy users từ nhân viên"""
        for room in self:
            users = room.member_ids.filtered(lambda e: e.user_id).mapped('user_id')
            room.member_user_ids = [(6, 0, users.ids)] if users else [(5, 0, 0)]
    
    @api.depends('member_ids')
    def _compute_member_count(self):
        """Đếm số thành viên"""
        for room in self:
            room.member_count = len(room.member_ids)
    
    @api.depends('message_ids')
    def _compute_message_count(self):
        """Đếm số tin nhắn"""
        for room in self:
            room.message_count = len(room.message_ids)
    
    @api.depends('message_ids', 'message_ids.create_date')
    def _compute_last_message(self):
        """Lấy tin nhắn cuối cùng"""
        for room in self:
            last_msg = room.message_ids.sorted('create_date', reverse=True)[:1]
            if last_msg:
                room.last_message_id = last_msg.id
                room.last_message_date = last_msg.create_date
                # Tạo preview ngắn gọn
                if last_msg.message_type == 'text':
                    preview = last_msg.content[:50] + '...' if len(last_msg.content) > 50 else last_msg.content
                    room.last_message_preview = f"{last_msg.sender_id.name}: {preview}"
                else:
                    room.last_message_preview = f"{last_msg.sender_id.name}: [File đính kèm]"
            else:
                room.last_message_id = False
                room.last_message_date = False
                room.last_message_preview = "Chưa có tin nhắn nào"
    
    def _compute_unread_count(self):
        """Đếm số tin nhắn chưa đọc của user hiện tại"""
        for room in self:
            # Tìm nhân viên của user hiện tại
            current_employee = self.env['nhan_vien'].search([('user_id', '=', self.env.user.id)], limit=1)
            if current_employee:
                # Đếm tin nhắn chưa đọc trong phòng này
                unread = self.env['chat.message'].search_count([
                    ('room_id', '=', room.id),
                    ('sender_id', '!=', current_employee.id),  # Không tính tin nhắn của chính mình
                    ('read_by_ids', 'not in', [current_employee.id])  # Chưa có trong danh sách đã đọc
                ])
                room.unread_count = unread
            else:
                room.unread_count = 0

    # === Onchange Methods ===
    @api.onchange('room_type')
    def _onchange_room_type(self):
        """Reset các field khi thay đổi loại phòng"""
        if self.room_type != 'project':
            self.project_id = False
        if self.room_type != 'department':
            self.department_id = False
    
    # @api.onchange('project_id')
    # def _onchange_project_id(self):
    #     """Tự động thêm thành viên từ dự án"""
    #     if self.project_id:
    #         self.name = f"Chat dự án: {self.project_id.name}"
    #         # Thêm quản lý dự án
    #         if self.project_id.quan_ly_id:
    #             self.member_ids = [(4, self.project_id.quan_ly_id.id)]
    
    @api.onchange('department_id')
    def _onchange_department_id(self):
        """Tự động đặt tên từ phòng ban"""
        if self.department_id:
            self.name = f"Chat phòng ban: {self.department_id.name}"

    # === Business Methods ===
    @api.model
    def get_accessible_rooms(self):
        """Lấy danh sách phòng chat mà user có thể truy cập
        - Admin/Manager: Tất cả phòng chat
        - User thường: Chỉ phòng mà họ là thành viên
        """
        current_employee = self.env['nhan_vien'].search([('user_id', '=', self.env.user.id)], limit=1)
        
        # Check nếu là admin hoặc manager
        is_admin = self.env.user.has_group('base.group_system') or \
                   self.env.user.has_group('base.group_erp_manager')
        
        if is_admin:
            # Admin thấy tất cả phòng chat
            rooms = self.search([('active', '=', True)], order='last_message_date desc, create_date desc')
        elif current_employee:
            # User thường chỉ thấy phòng mà họ là thành viên
            rooms = self.search([
                ('active', '=', True),
                ('member_ids', 'in', [current_employee.id])
            ], order='last_message_date desc, create_date desc')
        else:
            rooms = self.browse([])
        
        # Return data
        result = []
        for room in rooms:
            result.append({
                'id': room.id,
                'name': room.name,
                'room_type': room.room_type,
                'last_message_date': room.last_message_date.isoformat() if room.last_message_date else False,
                'unread_count': room.unread_count,
            })
        return result
    
    def action_view_messages(self):
        """Xem tin nhắn trong phòng chat"""
        self.ensure_one()
        # Tìm nhân viên của user hiện tại
        current_employee = self.env['nhan_vien'].search([('user_id', '=', self.env.user.id)], limit=1)
        return {
            'name': f'💬 {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'chat.message',
            'view_mode': 'tree,form',
            'domain': [('room_id', '=', self.id)],
            'context': {
                'default_room_id': self.id,
                'default_sender_id': current_employee.id if current_employee else False,
            },
        }
    
    def action_send_message(self):
        """Mở wizard gửi tin nhắn nhanh"""
        self.ensure_one()
        # Tìm nhân viên của user hiện tại
        current_employee = self.env['nhan_vien'].search([('user_id', '=', self.env.user.id)], limit=1)
        return {
            'name': 'Gửi tin nhắn',
            'type': 'ir.actions.act_window',
            'res_model': 'chat.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_room_id': self.id,
                'default_sender_id': current_employee.id if current_employee else False,
            },
        }
    
    def action_archive_room(self):
        """Lưu trữ phòng chat"""
        self.write({'is_archived': True, 'active': False})
    
    def action_unarchive_room(self):
        """Kích hoạt lại phòng chat"""
        self.write({'is_archived': False, 'active': True})
    
    # @api.model
    # def create_project_room(self, project_id):
    #     """Tạo phòng chat cho dự án"""
    #     project = self.env['du_an'].browse(project_id)
    #     if not project.exists():
    #         return False
    #     
    #     # Kiểm tra đã có phòng chat chưa
    #     existing_room = self.search([
    #         ('room_type', '=', 'project'),
    #         ('project_id', '=', project_id)
    #     ], limit=1)
    #     
    #     if existing_room:
    #         return existing_room
    #     
    #     # Tạo phòng chat mới
    #     members = []
    #     if project.quan_ly_id:
    #         members.append(project.quan_ly_id.id)
    #     
    #     room = self.create({
    #         'name': f"Chat dự án: {project.name}",
    #         'room_type': 'project',
    #         'project_id': project_id,
    #         'member_ids': [(6, 0, members)] if members else False,
    #         'description': f'Phòng chat cho dự án {project.name}'
    #     })
    #     
    #     return room
