# -*- coding: utf-8 -*-
{
    'name': "quan_ly_du_an",

    'summary': "Quản lý dự án",

    'description': "Module quản lý dự án và các chức năng liên quan.",

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Project',
    'version': '0.2',
    'license': 'LGPL-3',

    'depends': ['base', 'mail', 'nhan_su'],

    'data': [
        'views/du_an.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],

    'installable': True,
    'application': True,
}