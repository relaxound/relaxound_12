from odoo import models, fields, api, _


class CustomInvoiceCorrect(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_correct(self, vals_list):
        invoice_idd = [self.id]
        for rec in invoice_idd:
            obj = self.env['account.invoice.line'].search([('invoice_id','=',rec)])
            obj._compute_price()
        return vals_list
        # return super(CustomInvoiceCorrect,self).invoice_correct(vals_list)

class UpdateNewPricelist(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def new_pricelist(self):
        all_customers = self.env['res.partner'].search([])
        print("all customer=========== ",all_customers)
        for i in all_customers:
            if i.customer == True and i.supplier == False and i.is_retailer == False and i.property_product_pricelist.name == "Public Pricelist":
                print("customer========",i)
                i.property_product_pricelist = self.env['product.pricelist'].search([('id','=','824')])
                print("property_product_pricelist=====",i.property_product_pricelist)
