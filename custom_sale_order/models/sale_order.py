from odoo import models, fields, api, _


class CustomSaleOrder(models.Model):
	_inherit = 'sale.order'


	@api.onchange('order_line')
	def custom_tax(self):
		if self.partner_id.country_id.name=='Germany':
			taxx=self.env['account.tax'].search([])
			for item in taxx:
				if item.name=="19% Umsatzsteuer":
					self.order_line.update({'tax_id':item})


	@api.multi
	def action_view_invoice(self):
		res=super(CustomSaleOrder,self).action_view_invoice()
		if self.partner_id.country_id.name=='Germany':
			res1=self.env['account.invoice'].search([])
			for cust in res1:
				if cust.partner_id==self.partner_id:
					taxx=self.env['account.tax'].search([])
					for item in taxx:
						if item.name=="19% Umsatzsteuer":
							cust.invoice_line_ids.update({'invoice_line_tax_ids':item})
		return res



