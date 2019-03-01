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

from odoo import models, fields, api, exceptions, _


class PaymentLine(models.Model):
    _inherit = 'payment.line'

    mandate_id = fields.Many2one(
        comodel_name='account.banking.mandate', string='Direct Debit Mandate',
        domain=[('state', '=', 'valid')])

    @api.model
    def create(self, vals=None):
        """If the customer invoice has a mandate, take it
        otherwise, take the first valid mandate of the bank account
        """
        if vals is None:
            vals = {}
        partner_bank_id = vals.get('bank_id')
        move_line_id = vals.get('move_line_id')
        if (self.env.context.get('search_payment_order_type') == 'debit' and
                'mandate_id' not in vals):
            if move_line_id:
                line = self.env['account.move.line'].browse(move_line_id)
                if (line.invoice and line.invoice.type == 'out_invoice' and
                        line.invoice.mandate_id):
                    vals.update({
                        'mandate_id': line.invoice.mandate_id.id,
                        'bank_id': line.invoice.mandate_id.partner_bank_id.id,
                    })
            if partner_bank_id and 'mandate_id' not in vals:
                mandates = self.env['account.banking.mandate'].search(
                    [('partner_bank_id', '=', partner_bank_id),
                     ('state', '=', 'valid')])
                if mandates:
                    vals['mandate_id'] = mandates[0].id
        return super(PaymentLine, self).create(vals)

    @api.one
    @api.constrains('mandate_id', 'bank_id')
    def _check_mandate_bank_link(self):
        if (self.mandate_id and self.bank_id and
                self.mandate_id.partner_bank_id.id !=
                self.bank_id.id):
            raise exceptions.Warning(
                _("The payment line with reference '%s' has the bank account "
                  "'%s' which is not attached to the mandate '%s' (this "
                  "mandate is attached to the bank account '%s').") %
                (self.name,
                 self.env['res.partner.bank'].name_get(
                     [self.bank_id.id])[0][1],
                 self.mandate_id.unique_mandate_reference,
                 self.env['res.partner.bank'].name_get(
                     [self.mandate_id.partner_bank_id.id])[0][1]))
