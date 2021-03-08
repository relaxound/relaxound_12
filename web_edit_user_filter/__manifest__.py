# Copyright 2019 Onestein
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Edit User Filters',
    'category': 'Extra Tools',
    'version': '12.0.1.0.1',
    'development_status': 'Production/Stable',
    'author': 'Onestein,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/web',
    'depends': [
        'web','sale',
    ],
    'data': [
        'templates/assets.xml',
        # 'wizard/wizard.xml',
        # 'views/views.xml',
        # 'security/ir.model.access.csv',

    ],
    'qweb': [
        'static/src/xml/backend.xml'
    ],
    'installable': True,
}
