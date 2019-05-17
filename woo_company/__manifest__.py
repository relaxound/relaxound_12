# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Woocommerce Company',
    'version': '10.0',
    'category': 'Base',
    'license': 'AGPL-3',
    'author': "Odoo Tips",
    'website': 'http://www.gotodoo.com/',
    'currency': 'EUR',
    'price': 19.00,
    'depends': ['base', 'woo_commerce_ept', 'account', 'rs_document_layout',
                ],

    'images': ['images/main_screenshot.png'],
    'data': [
             'views/res_partner_view.xml',
             'views/account_invoice_view.xml',
             'report/layout_account_invoice.xml',
             ],
    'installable': True,
    'application': True,
}
