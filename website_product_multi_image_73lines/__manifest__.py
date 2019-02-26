# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Website Product Multi Image By 73Lines',
    'description': 'Website Product Multi Image By 73Lines',
    'category': 'Website',
    'version': '1.3',
    'author': '73Lines',
    'data': [
        'views/product_view.xml',
        'views/assets.xml',
        'views/website_sale_template.xml',
        'security/ir.model.access.csv'
    ],
    'images': [
        'static/description/website_product_multi_image.jpg',
    ],
    'depends': ['website_sale'],
    'price': 30,
    'license': 'OEEL-1',
    'currency': 'EUR',
}
