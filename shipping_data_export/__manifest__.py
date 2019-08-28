# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Shipping Data Export',
    'version': '12.0',
    'category': 'Base',
    'license': 'AGPL-3',
    'author': "Odoo Tips",
    'website': 'http://www.gotodoo.com/',
    'currency': 'EUR',
    'price': 19.00,
    'depends': ['base', 'stock', 'sale_stock','sale_management'
                ],

    'images': ['images/main_screenshot.png'],
    'data': [
        'views/sale_order_view.xml',
        'data/shipping_data.xml',
             ],
    'installable': True,
    'application': True,
}
