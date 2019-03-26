# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Delivery Base",
    'description': """
        Grundmodul für Delivery-Implementierungen, das allgemeine Funktionen bereitstellt.
    """,
    'author': "Level9",
    'website': "https://www.level9.de",
    'category': 'Technical Settings',
    'version': '1.0',
    'depends': ['stock'],
    'data': [
        'stock/stock_picking_view.xml'
    ],
    'demo': [
    ],
}
