# -*- coding: utf-8 -*-
{
    'name': "PoS Order To Sale Order",

    'summary': """
        Module is developed to set POS order to sale order """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Techspawn Solutons",
    'website': "http://www.techspawn.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': '"Point Of Sale"',
    'version': '12.0',
    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    "data": [
        "views/view_pos_config.xml",
        "views/assets.xml",
    ],
    "qweb": ["static/src/xml/pos_order_to_sale_order.xml"],
}
