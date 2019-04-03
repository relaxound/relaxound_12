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
    'name': 'Automatic Export to Datev Cash Registers',
    'version': '1.0 (9.0)',
    'category': 'Accounting & Finance',
    'complexity': 'normal',
    'description': """
     This module allows DATEV export Cash Registers automatically

     Format: DATEV XML Interface Online 3.0
     As an accountant you can export customer and supplier invoices and 
     refunds in DATEV XML Online Format. The document package includes
     the original electronical invoice from odoo as .pdf attachment 
     and the account move. 

     DATEV is the leading accounting software in germany used by many
     tax advisors.
    
    """,
    'author': 'openfellas',
    'depends': ['base', 'datev_export_cash'],
    "data": [
        'data/config_data.xml',
        'company_view.xml',
        'account/views/account_view.xml',
        'data/datev_export_cash_cron.xml',
    ],
    'demo_xml': [],
    'installable': True,
}