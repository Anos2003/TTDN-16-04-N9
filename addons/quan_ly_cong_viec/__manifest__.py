# -*- coding: utf-8 -*-
{
    'name': "quan_ly_cong_viec",

    'summary': "Quản lý công việc",

    'description': "Module quản lý công việc và các chức năng liên quan.",

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Project',
    'version': '0.1',
    'license': 'LGPL-3',

    'depends': ['base', 'mail', 'nhan_su', 'quan_ly_du_an'],

    'data': [
        'views/cong_viec.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],

    'installable': True,
    'application': True,
}