from odoo import models, fields, api, _


class sale_order_fun(models.Model):
	_inherit = 'sale.order'

	@api.multi
	def action_view_invoice(self):
		res=super(sale_order_fun,self).action_view_invoice()
		res1=self.env['account.invoice'].search([])
		pro1=self.env['account.journal'].search([])
		if self.name[0]=='S' or self.name[0]=='P' and self.name[1]=='O':
			for item in pro1:
				if item.name=='Retailer Invoices':
					res1.update({'journal_id':item.id})
		elif self.name[0]=='0' or self.name[0]=='1' or self.name[0]=='2' or self.name[0]=='3' or self.name[0]=='4' or self.name[0]=='5' or self.name[0]=='6' or self.name[0]=='7' or self.name[0]=='8' or self.name[0]=='9':
			for item in pro1:
				if item.name=='Customer Invoices':
					res1.update({'journal_id':item.id})

		else:
			for item in pro1:
				if item.name=='Export Invoices':
					res1.update({'journal_id':item.id})

		return res