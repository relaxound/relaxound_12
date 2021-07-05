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
        list = [347596, 349835, 463928, 368086, 368182, 368525, 455778, 455779, 472348, 369809, 370066, 370067, 370121, 370245, 370403, 370404, 470278, 441960, 386198, 386549, 386550, 387626, 389397, 499561, 499563, 499562, 349836, 349837, 399111, 409010, 345513, 345514, 345515, 471223, 471224, 345507, 345508, 489185, 489186, 457599, 457601, 457602, 457603, 457600, 457604, 345509, 345510, 345511, 345512, 489609, 489610]
        for j in list:
            p = int(j)
            all_customers = self.env['res.partner'].search([('id','=',p)])
            error_msg1 = _('all customer====== (%s)') % (all_customers)
            _logger.info(error_msg1)
            for i in all_customers:
                try:
                    if i.customer == True and i.supplier == False and i.is_retailer == False and i.property_product_pricelist.name == "Public Pricelist":
                        change_pricelist =self.env['product.pricelist'].search([('id','=',824)]).id
                        i.property_product_pricelist = change_pricelist
                        error_msg = _('property_product_pricelist====== (%s)') % (i.property_product_pricelist.name)
                        _logger.info(error_msg)
                except Exception:
                    error_msg2 = _('INVALID ID====== (%s)') % (i)
                    _logger.info(error_msg2)
                    pass
