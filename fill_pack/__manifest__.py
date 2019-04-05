# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Fill in Packs',
    'version': '10.0',
    'category': 'Base',
    'license': 'AGPL-3',
    'author': "Odoo Tips",
    'website': 'http://www.gotodoo.com/',
    'currency': 'EUR',
    'price': 19.00,
    'depends': ["base", "stock", "sale_stock","sale_management","sale"],

    'images': ['images/main_screenshot.png'],
    'data': [
             'views/stock_picking_view.xml'
             ],
    'installable': True,
    'application': True,
}
