# -*- coding: utf-8 -*-
{
    'name': "Relaxound",

    'summary': """
        Module is developed for total overdue """,

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
    'depends': ['base','sale','purchase','crm'],

    # always loaded
    'data': [
            'views/views.xml',
    ],
}
