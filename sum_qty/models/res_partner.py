# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = "Res Partner last Invoice"

    date_last_invoice = fields.Date('Last Invoice', compute='get_last_date', store=True)

#    @api.depends('total_invoiced')

    def get_last_date(self):
        for partner in self:
            invoice = self.env['account.invoice'].search([('partner_id', '=', partner.id)], order='date_invoice desc', limit=1)
            partner.date_last_invoice = invoice and invoice.date_invoice or False

    def get_last_date_cron(self):
        for partner in self.env['res.partner'].search([]):
            invoice = self.env['account.invoice'].search([('partner_id', '=', partner.id)], order='date_invoice desc', limit=1)
            partner.date_last_invoice = invoice and invoice.date_invoice or False
