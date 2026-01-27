# -*- coding: utf-8 -*-
{
    'name': "nhan_su",

    'summary': "Quản lý nhân sự",

    'description': "Module quản lý nhân viên và các chức năng liên quan.",

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Human Resources',
    'version': '0.1',
    'license': 'LGPL-3',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',
        'views/nhan_vien.xml',
        'views/menu.xml',
    ],

    'installable': True,
    'application': True,
}
