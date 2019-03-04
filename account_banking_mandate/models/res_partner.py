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
    def _compute_mandate_count(self):
        mandate_data = self.env['account.banking.mandate'].read_group(
            [('partner_id', 'in', self.ids)], ['partner_id'], ['partner_id'])
        mapped_data = dict([
            (mandate['partner_id'][0], mandate['partner_id_count'])
            for mandate in mandate_data])
        for partner in self:
            partner.mandate_count = mapped_data.get(partner.id, 0)

    @api.multi
    def _compute_mandate_ids(self):
        # Dict for reducing the duplicated searches on parent/child partners
        company_id = self.env.context.get('force_company', False)
        if company_id:
            company = self.env['res.company'].browse(company_id)
        else:
            company = self.env['res.company']._company_default_get(
                'account.banking.mandate')

        mandates_dic = {}
        for partner in self:
            commercial_partner_id = partner.commercial_partner_id.id
            if commercial_partner_id in mandates_dic:
                partner.mandate_ids = mandates_dic[commercial_partner_id]
            else:
                mandates = partner.commercial_partner_id.bank_ids.mapped(
                    'mandate_ids').filtered(
                    lambda x: x.state == 'valid' and x.company_id == company)
                first_mandate_ids = mandates[:1].id
                partner.mandate_ids = first_mandate_ids
                mandates_dic[commercial_partner_id] = first_mandate_ids
