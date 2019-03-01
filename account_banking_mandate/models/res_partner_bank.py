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


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    mandate_ids = fields.One2many(
        comodel_name='account.banking.mandate', inverse_name='partner_bank_id',
        string='Direct Debit Mandates',
        help='Banking mandates represents an authorization that the bank '
             'account owner gives to a company for a specific operation')


   