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



    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        # import pdb;pdb.set_trace()
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product = self.product_id.with_context(
                warehouse=self.order_id.warehouse_id.id,
                lang=self.order_id.partner_id.lang or self.env.user.lang or 'en_US'
            )
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            # if float_compare(product.virtual_available, product_qty, precision_digits=precision) == -1:
            #     is_available = self._check_routing()
            #     if not is_available:                   
            #         message =  _('You plan to sell %s %s of %s but you only have %s %s available in %s warehouse.') % \
            #                 (self.product_uom_qty, self.product_uom.name, self.product_id.name, product.virtual_available, product.uom_id.name, self.order_id.warehouse_id.name)
            #         # We check if some products are available in other warehouses.
            #         if float_compare(product.virtual_available, self.product_id.virtual_available, precision_digits=precision) == -1:
            #             message += _('\nThere are %s %s available across all warehouses.\n\n') % \
            #                     (self.product_id.virtual_available, product.uom_id.name)
            #             for warehouse in self.env['stock.warehouse'].search([]):
            #                 quantity = self.product_id.with_context(warehouse=warehouse.id).virtual_available
            #                 if quantity > 0:
            #                     message += "%s: %s %s\n" % (warehouse.name, quantity, self.product_id.uom_id.name)
            #         warning_mess = {
            #             'title': _('Not enough inventory!'),
            #             'message' : message
            #         }
            #         return {'warning': warning_mess}
        return {}