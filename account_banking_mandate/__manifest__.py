# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Openfellas (http://openfellas.com) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract support@openfellas.com
#
##############################################################################

{
    'name': "Account Banking Mandate",
    'summary': "Banking mandates",
    'author': "Openfellas",
    'category': 'Accounting &amp; Finance',
    'version': '1.0',
    'depends': ['account', 'account_bank_statement_import'],
    'data': [
        'views/account_banking_mandate_view.xml',
        'views/account_invoice_view.xml',
        'views/account_payment_view.xml',
        # 'views/res_partner_bank_view.xml',
        'data/mandate_reference_sequence.xml',
        # 'data/report_paperformat.xml',
        'security/mandate_security.xml',
        'security/ir.model.access.csv',
        # 'reports/account_banking_mandate_view.xml',
        # 'reports/account_banking_mandate.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}