# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "DHL Shipping DE",
    'summary': 'DHL Shipping DE module for Relaxound',
    'author': "Level9",
    'website': "https://www.level9.de",
    'category': 'Technical Settings',
    "description": """
        Delivery-Implementierung für DHL
    """,
    'version': '12.0',
    'depends': ['delivery_base', 'delivery',
                'mail'],
    'data': [
        # 'data/delivery_dhl_data.xml',
        # 'views/delivery_dhl_view.xml',
        'stock/stock_picking_view.xml',
        'sale/sale_order_view.xml',
        'account/account_invoice_view.xml'
    ],
    'demo': [
        # 'data/delivery_dhl_demo_data.xml'
    ],
}
