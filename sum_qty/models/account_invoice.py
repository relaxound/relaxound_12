# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    _description = "Account Invoice Sum Qty"

    qty_delivered = fields.Integer("Total Qty", compute='_get_delivered_qty')

    @api.multi
    def sum_qty(self):
        qty = 0
        for invoice in self:
            for line in invoice.invoice_line_ids:
                if line.product_id.type != 'service':
                    qty = qty + line.quantity
        return int(qty)

    @api.multi
    def _get_delivered_qty(self):
        for invoice in self:
            qty = invoice.sum_qty()
            invoice.qty_delivered = qty
