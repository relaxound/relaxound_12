from odoo import models, fields, api, _


class InvoiceJournal(models.Model):
    _inherit = 'account.invoice'

    order_by = fields.Many2one('res.partner', string="Order By")
    order_date = fields.Date(string='Order Date')