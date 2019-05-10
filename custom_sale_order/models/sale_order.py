from odoo import models, fields, api, _


class CustomSaleOrder(models.Model):
	_inherit = 'sale.order'
	amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
	
	@api.depends('order_line.price_total')
	def _amount_all(self):
		
		for order in self:
			amount_untaxed = amount_tax = 0.0
			for line in order.order_line:
				amount_untaxed += line.price_subtotal
				amount_tax += line.price_tax
			if order.partner_id.vat and 'EU' in order.partner_id.property_account_position_id.name:
				order.update({
					'amount_untaxed': amount_untaxed,
					'amount_tax': 0.0,
					'amount_total': amount_untaxed + amount_tax,
				})
			else:
				order.update({
					'amount_untaxed': amount_untaxed,
					'amount_tax': amount_tax,
					'amount_total': amount_untaxed + amount_tax,
				})
			
