# -*- coding: utf-8 -*-
{
    'name': "Set Tags",

    'summary': """
        Module is developed to set tags """,

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
    'depends': ['sale','account','contacts'],

    # always loaded
    'data': [
            'wizard/set_tag_wizard.xml',
            'wizard/set_tag_res_partner.xml',

    ],
}
