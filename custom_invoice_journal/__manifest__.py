# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Custom Invoice Journal',
    'version': '12.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'author': "Techspawn",
    'website': 'http://www.Techspawn.com/',
    'depends': ['base', 'account', 'sale', 'customer_sequence'],

    'data': [ 
            'views/res_partner.xml'            
             ],
    'installable': True,
    'application': True,
}
