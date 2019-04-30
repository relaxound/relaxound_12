# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Customer Sequence',
    'version': '12.0',
    'category': 'Base',
    'license': 'AGPL-3',
    'author': "Techspawn Solutons",
    'website': "http://www.techspawn.com",
    'currency': 'EUR',
    'price': 19.00,
    'depends': ['base', 'sale','sale_management', 'account',
                ],

    'images': ['images/main_screenshot.png'],
    'data': [
             'views/res_partner_view.xml',
             'views/sale_order_view.xml',
             'data/res_partner_sequence.xml',
             ],
    'installable': True,
    'application': True,
}
