# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Custom Retailer',
    'version': '12.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'author': "Techspawn",
    'website': 'http://www.Techspawn.com/',
    'depends': ['purchase'],

    'data': [
             'views/res_partner_view.xml',
             
             ],
    'installable': True,
    'application': True,
}
