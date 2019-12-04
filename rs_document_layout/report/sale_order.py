from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    price_tax = fields.Float(compute='_compute_amount',digits=dp.get_precision('Product Price'), string='Total Tax', readonly=True, store=True)
    single_unit=fields.Integer(string="Single Unit")

    @api.onchange('product_id','product_uom_qty')
    def custom_quantity(self):
        if self.product_id.name:
            if '20x' in self.product_id.name or '20X' in self.product_id.name:
                self.update({'single_unit':self.product_uom_qty*20}) 

            elif '80x' in self.product_id.name or '80X' in self.product_id.name:
                self.update({'single_unit':self.product_uom_qty*80})

            else:
                self.update({'single_unit':self.product_uom_qty})





    @api.multi
    def _prepare_invoice_line(self, qty):
        res=super(SaleOrderLine,self)._prepare_invoice_line(qty)
        res.update({'single_unit':self.single_unit})
        

        return res