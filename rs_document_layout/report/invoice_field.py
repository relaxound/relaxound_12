from odoo import models, fields, api, _


class InvoiceJournal(models.Model):
    _inherit = 'account.invoice'

    order_by = fields.Many2one('res.partner', string="Order By")
    order_date = fields.Date(string='Order Date')
    amount_tax = fields.Monetary(string='Tax',store=True, readonly=True, compute='_compute_amount')



    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        if self.partner_id.vat and 'EU' in self.partner_id.property_account_position_id.name:
            self.amount_tax = 0.0
            self.amount_total = self.amount_untaxed
            amount_total_company_signed = self.amount_total
            amount_untaxed_signed = self.amount_untaxed
            if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
                currency_id = self.currency_id
                amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
                amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
            sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
            self.amount_total_company_signed = amount_total_company_signed * sign
            self.amount_total_signed = self.amount_total * sign
            self.amount_untaxed_signed = amount_untaxed_signed * sign
        else:
            self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
            self.amount_total = self.amount_untaxed + self.amount_tax
            amount_total_company_signed = self.amount_total
            amount_untaxed_signed = self.amount_untaxed
            if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
                currency_id = self.currency_id
                amount_total_company_signed = currency_id._convert(self.amount_total, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
                amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id, self.company_id, self.date_invoice or fields.Date.today())
            sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
            self.amount_total_company_signed = amount_total_company_signed * sign
            self.amount_total_signed = self.amount_total * sign
            self.amount_untaxed_signed = amount_untaxed_signed * sign
