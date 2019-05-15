from odoo import models, fields, api, _


class CustomInvoiceOrder(models.Model):
    _inherit = 'account.invoice'


    @api.onchange('partner_id','invoice_line_ids')
    def onchange_invoice(self):
        if self.partner_id.vat and 'EU' in self.partner_id.property_account_position_id.name:
            self.invoice_line_ids.update({'invoice_line_tax_ids':None})
            self.update({'tax_line_ids':None})



    