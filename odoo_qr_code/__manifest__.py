# -*- coding: utf-8 -*-
{
    'name': "Odoo QR Code",
    'summary': """
        Creates QR Code for Products and can be used for Product Lable and other scanning purposes.""",
    'description': """
        Creates QR Code for Products and can be used for Product Lable and other scanning purposes.
    """,
    'author': "TechSpawn Solutions",
    'website': "https://www.techspawn.com",
    'license': "OPL-1",
    'price': 10.00,
    'currency': 'EUR',
    'category': 'Product',
    'version': '0.1',
    'depends': ['base', 'product', 'sale'],
    'data': [
        'views/views.xml',
    ],
    'installable': True,
    'images': [
        'static/description/main.jpg',
    ],
}