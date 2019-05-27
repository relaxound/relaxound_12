from odoo import models, fields, api, _


class CustomInvoiceOrder(models.Model):
    _inherit = 'account.invoice'


    @api.onchange('invoice_line_ids')
    def onchange_invoice(self):
        if self.invoice_line_ids:
            if self.partner_id.country_id or self.partner_id.property_account_position_id:
                if self.partner_id.country_id.name=='Germany':
                    taxx=self.env['account.tax'].search([])
                    pro=self.env['account.invoice.tax'].search([])
                    for item in taxx:
                        if item.name=="19% Umsatzsteuer":
                            for o, invoice_line in enumerate(self.invoice_line_ids):
                                invoice_line.update({'invoice_line_tax_ids':item})
                            for p, res in enumerate(self.tax_line_ids):
                                if p == o: 
                                    res.update({'amount_total': (res.base * item.amount) / 100,
                                                              'name': item.name,
                                                              'tax_id': item.id,
                                                              })
                elif self.partner_id.country_id and self.partner_id.property_account_position_id:
                    if self.partner_id.country_id.name!='Germany' and 'EU' in self.partner_id.property_account_position_id.name:
                        self.invoice_line_ids.update({'invoice_line_tax_ids':None})
                        self.tax_line_ids.update({'tax_id':None})



    