# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sum Of Quantities',
    'version': '10.0',
    'category': 'Base',
    'license': 'AGPL-3',
    'author': "Odoo Tips",
    'website': 'http://www.gotodoo.com/',
    'currency': 'EUR',
    'price': 19.00,
    'depends': ['base', 'sale', 'account', 'purchase', 'rs_document_layout'
                ],
    'images': ['images/main_screenshot.png'],
    'data': [
             'views/sale_order_view.xml',
             'views/account_invoice_view.xml',
             'views/res_partner_view.xml',
             'views/report_invoice.xml',
             'views/purchase_order.xml',
             ],
    'installable': True,
    'application': True,
}
