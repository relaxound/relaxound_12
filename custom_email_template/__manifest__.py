# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Custom Email template',
    'version': '12.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'author': "Techspawn",
    'website': 'http://www.Techspawn.com/',
    'depends': ['sale','purchase','mail'],

    'data': [
            'data/sale_order_template.xml',
            'data/purchase_order_sample.xml',
            'data/invoice_sample.xml',
            'data/invoice_sample_test.xml',
            'data/mail_data.xml',
            # 'report/sale_order.xml',        
             ],
    'installable': True,
    'application': True,
}
