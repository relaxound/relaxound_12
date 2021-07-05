from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

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

    def new_pricelist(self):
        all_customers = self.env['res.partner'].search([('id','=',476721)])
        error_msg1 = _('all customer====== (%s)') % (all_customers)
        _logger.info(error_msg1)
        for i in all_customers:
            if i.customer == True and i.supplier == False and i.is_retailer == False and i.property_product_pricelist.name == "Public Pricelist":
                change_pricelist =self.env['product.pricelist'].search([('id','=',824)]).id
                i.property_product_pricelist = change_pricelist
                error_msg = _('property_product_pricelist====== (%s)') % (i.property_product_pricelist.name)
                _logger.info(error_msg)
