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


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    exported_to_datev = fields.Boolean(string='Exported to Datev', default=False, track_visibility='onchange')

    @api.multi
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        rec = super(AccountBankStatement, self).copy(default)
        rec.write({'exported_to_datev': False})
        return rec

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    bu_code_b = fields.Char('BU Code (B)', default='0')
    bu_code_u = fields.Char('BU Code (U)', default='0')
    # bu_code_u = fields.Char(string='BU Code (U)', compute='_calculate_bu_code_u', readonly=True)

    # @api.one
    # @api.depends("invoice_line_tax_ids")
    # def _calculate_bu_code_u(self):
    #     for line in self:
    #         line.bu_code_u = '0'
    #         if line.invoice_line_tax_ids and line.invoice_line_tax_ids[0]:
    #             line.bu_code_u =  line.invoice_line_tax_ids[0].bu_code_u
