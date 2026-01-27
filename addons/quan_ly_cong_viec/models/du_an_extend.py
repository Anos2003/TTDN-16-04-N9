# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DuAnExtend(models.Model):
    _inherit = 'du_an'
    
    # Thêm relationship từ du_an sang cong_viec
    cong_viec_ids = fields.One2many('cong_viec', 'du_an_id', string="Danh sách công việc")
