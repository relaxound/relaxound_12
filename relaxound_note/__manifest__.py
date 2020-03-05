# -*- coding: utf-8 -*-
{
    'name': "relaxound",

    'summary': """
        Module is developed to manage customers detail""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Techspawn Solutons",
    'website': "http://www.techspawn.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0',
    # any module necessary for this one to work correctly
    'depends': ['base','sale','hr','hr_holidays'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}