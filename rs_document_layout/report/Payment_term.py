from odoo import models, fields, api, _


class payment(models.Model):
    _inherit = 'sale.order'
    @api.onchange('partner_id')
    def onchange_payment_term(self):
    	self.ensure_one()
    	if self.partner_id.property_payment_term_id:
    		pass

    	else:
    		self.payment_term_id = 67
    		# self.payment_term_id.name == '14 days after receipt of invoice'


