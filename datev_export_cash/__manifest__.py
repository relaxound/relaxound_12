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
    'name': 'Cash Registers Export to Datev',
    'version': '1.0 (9.0)',
    'category': 'Accounting & Finance',
    'complexity': 'normal',
    'description': """
     This module allows DATEV export of cash registers

     Format: DATEV XML Interface Online 3.0
     As an accountant you can export cash registers in DATEV XML Online Format. The document package includes
     xml files of exported cash registers.

     DATEV is the leading accounting software in germany used by many
     tax advisors.
    
    """,
    'author': 'openfellas',
    'depends': ['base', 'datev_export_base', 'account', 'sale'],
    "data": [
                'wizard/datev_export_cash_view.xml',
                'account/views/account_view.xml'
    ],
    'demo_xml': [],
    'installable': True,
}