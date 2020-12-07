# -*- coding: utf-8 -*-
{
    'name': "pos_multi_session_odoo",

    'summary': """
        Module is developed for multi session synchronisation. """,

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
    'depends': ['base','bus','sale','point_of_sale'],

    # always loaded
    'data': [
            'security/ir.model.access.csv',
            'views/custom_pos_view.xml',
            'views/pos_multi_session.xml',
    ],
}
