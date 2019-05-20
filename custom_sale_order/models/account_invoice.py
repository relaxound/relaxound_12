from odoo import models, fields, api, _


class CustomInvoiceOrder(models.Model):
    _inherit = 'account.invoice'


    @api.onchange('invoice_line_ids')
    def onchange_invoice(self):
        if self.partner_id.country_id.name=='Germany':
            taxx=self.env['account.tax'].search([])
            for item in taxx:
                if item.name=="19% Umsatzsteuer":
                    self.invoice_line_ids.update({'invoice_line_tax_ids':item})



    