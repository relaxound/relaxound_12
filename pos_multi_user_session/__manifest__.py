# -*- coding: utf-8 -*-
{
    'name': "pos_multi_user_session",

    'summary': """
        Module is developed for login multiple users to same pos session """,

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
    'depends': ['base','sale','point_of_sale','pos_restaurant'],

    # always loaded
    'data': [
            'views/point_of_sale_dashboard.xml',
    ],
}
