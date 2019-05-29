from odoo import models, fields, api, _


class OrderLine(models.Model):
    _inherit = 'account.invoice.line'

    single_unit=fields.Integer(string="Single Unit")

    @api.onchange('product_id','quantity')
    def custom_qty(self):
        if self.product_id.name:
            if '20x' in self.product_id.name or '20X' in self.product_id.name:
                self.update({'single_unit':self.quantity*20}) 

            else:
                self.update({'single_unit':self.quantity})