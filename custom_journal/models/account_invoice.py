from odoo import models, fields, api, _


class sale_invoice_fun(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        pro1=self.env['account.journal'].search([])
        if self.origin[0]=='S' or self.origin[0]=='P' and self.origin[1]=='O':
            for item in pro1:
                if item.name=='Retail Invoices':
                    self.update({'journal_id':item.id})

        elif self.origin[0]=='0' or self.origin[0]=='1' or self.origin[0]=='2' or self.origin[0]=='3' or self.origin[0]=='4' or self.origin[0]=='5' or self.origin[0]=='6' or self.origin[0]=='7' or self.origin[0]=='8' or self.origin[0]=='9':
            for item in pro1:
                if item.name=='Customer Invoices':
                    self.update({'journal_id':item.id})

        else:
            for item in pro1:
                if item.name=='Export Invoices':
                    self.update({'journal_id':item.id})

        return super(sale_invoice_fun,self).action_invoice_open()