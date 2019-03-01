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

from odoo import models, fields, api


class ResPartnerBank(models.Model):
    _inherit = 'res.partner'

    mandate_ids = fields.One2many(
        comodel_name='account.banking.mandate', inverse_name='partner_id',
        string='Direct Debit Mandates',
        help='Banking mandates represents an authorization that the bank '
             'account owner gives to a company for a specific operation')

    mandates_count = fields.Integer(string='# of Mandates', compute='_get_mandates', readonly=True)

    @api.multi
    def _get_mandates(self):
        for partner in self:
            partner.mandates_count = len(set(partner.mandate_ids))


    @api.constrains('company_id')
    def _company_constrains(self):
        for rpb in self:
            if self.env['account.banking.mandate'].sudo().search(
                    [('partner_bank_id', '=', rpb.id),
                     ('company_id', '!=', rpb.company_id.id)], limit=1):
                raise ValidationError(
                    _("You cannot change the company of Partner Bank %s, "
                      "as there exists mandates referencing it that "
                      "belong to another company.") % (rpb.display_name,))