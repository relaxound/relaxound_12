from odoo import models, fields, api, _


class CustomSaleOrder(models.Model):
	_inherit = 'sale.order'


	@api.onchange('partner_id','order_line')
	def custom_tax(self):
		if self.partner_id.vat:
			self.order_line.update({'tax_id':None})


	@api.multi
	def action_view_invoice(self):
		res=super(CustomSaleOrder,self).action_view_invoice()
		if self.partner_id.vat:
			res1=self.env['account.invoice'].search([])
			for cust in res1:
				if cust.partner_id==self.partner_id:
					cust.invoice_line_ids.update({'invoice_line_tax_ids':None})
		return res



