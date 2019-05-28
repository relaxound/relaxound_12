from odoo import models, fields, api, _


class InvoiceOrder(models.Model):
    _inherit = 'account.invoice.tax'

    @api.depends('invoice_id.invoice_line_ids')
    def _compute_base_amount(self):
        
        tax_grouped = {}
        for invoice in self.mapped('invoice_id'):
            tax_grouped[invoice.id] = invoice.get_taxes_values()
        for tax in self:
            tax.base = 0.0
            if tax.tax_id:
                print(tax.tax_id)
                key = tax.tax_id.get_grouping_key({
                    'tax_id': tax.tax_id.id,
                    'account_id': tax.account_id.id,
                    'account_analytic_id': tax.account_analytic_id.id,
                    'analytic_tag_ids': tax.analytic_tag_ids.ids or False,
                })
                if tax.invoice_id and key in tax_grouped[tax.invoice_id.id]:
                    tax.base = tax_grouped[tax.invoice_id.id][key]['base']
                else:

                    tax.base = list(tax_grouped[tax.invoice_id.id].values())[0]['base']
                    