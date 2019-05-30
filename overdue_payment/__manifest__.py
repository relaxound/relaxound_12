# -*- coding: utf-8 -*-
# module template
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Partner Overdue Payment',
    'version': '12.0',
    'category': 'Tools',
    'license': 'AGPL-3',
    'author': "Odoo Tips",
    'website': 'http://www.gotodoo.com/',
    'depends': ['base', 'account', 'sale','account_banking_mandate','mail'
                ],

    'images': ['images/main_screenshot.png'],
    'data': [
             'views/res_partner_view.xml',
             'reports/reports.xml',
             'reports/report_overdue.xml',
             'reports/report_overdue_document.xml',
             'data/mail_template_data.xml',
             # 'data/mail_data.xml',
             'data/partner_data.xml',
             ],
    'installable': True,
    'application': True,
}
