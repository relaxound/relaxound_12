from odoo import models, fields, api, _


class OrderLine(models.Model):
    _inherit = 'sale.order.line'

    single_unit=fields.Float(string="Single Unit")

    
    @api.onchange('product_id','product_uom_qty')
    def change_qty(self):
    	pro=self.product_id.name
    	if pro:
	    	if '20x' in pro or '20X' in pro:
	    		self.update({'single_unit':self.product_uom_qty*20})

	    	elif '80x' in pro or '80X' in pro:
	    		self.update({'single_unit':self.product_uom_qty*80})
        
            





    @api.multi
    def _prepare_invoice_line(self, qty):
        res=super(OrderLine,self)._prepare_invoice_line(qty)
        res.update({'single_unit':self.single_unit})
        

        return res