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
    _inherit = 'account.payment.line'

    mandate_id = fields.Many2one(
        comodel_name='account.banking.mandate', string='Direct Debit Mandate',
        domain=[('state', '=', 'valid')])
    # mandate_required = fields.Boolean(
    #     related='order_id.payment_method_id.mandate_required', readonly=True)

    @api.multi
    @api.constrains('mandate_id', 'partner_bank_id')
    def _check_mandate_bank_link(self):
        for pline in self:
            if (pline.mandate_id and pline.partner_bank_id and
                    pline.mandate_id.partner_bank_id !=
                    pline.partner_bank_id):
                raise ValidationError(_(
                    "The payment line number %s has the bank account "
                    "'%s' which is not attached to the mandate '%s' (this "
                    "mandate is attached to the bank account '%s').") %
                    (pline.name,
                     pline.partner_bank_id.acc_number,
                     pline.mandate_id.unique_mandate_reference,
                     pline.mandate_id.partner_bank_id.acc_number))

    @api.multi
    @api.constrains('mandate_id', 'company_id')
    def _check_company_constrains(self):
        for pline in self:
            if pline.mandate_id.company_id and pline.mandate_id.company_id != \
                    pline.company_id:
                raise ValidationError(_(
                    "The payment line number %s a different company than "
                    "that of the linked mandate %s).") %
                    (pline.name,
                     pline.mandate_id.display_name))

    @api.multi
    def draft2open_payment_line_check(self):
        res = super(AccountPaymentLine, self).draft2open_payment_line_check()
        if self.mandate_required and not self.mandate_id:
            raise UserError(_(
                'Missing Mandate on payment line %s') % self.name)
        return res
