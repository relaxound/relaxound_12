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

from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    mandate_id = fields.Many2one(
        'account.banking.mandate', string='Direct Debit Mandate',
        domain=[('state', '=', 'valid')], readonly=True,
        states={'draft': [('readonly', False)], 'open': [('readonly', False)], 'proforma': [('readonly', False)], 'proforma2': [('readonly', False)]})
