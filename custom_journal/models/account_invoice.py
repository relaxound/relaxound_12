from odoo import models, fields, api, _


class sale_invoice_fun(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        res=self.env['res.partner'].search([])
        pro1=self.env['account.journal'].search([])
        if self.partner_id.customer and self.partner_id.is_retailer:
            for item in pro1:
                if item.name=='Retail Invoices':
                    self.update({'journal_id':item.id})

        elif self.partner_id.customer:
            for item in pro1:
                if item.name=='Customer Invoices':
                    self.update({'journal_id':item.id})

        else:
            for item in pro1:
                if item.name=='Export Invoices':
                    self.update({'journal_id':item.id})

        return super(sale_invoice_fun,self).action_invoice_open()