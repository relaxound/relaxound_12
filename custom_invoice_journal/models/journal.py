from odoo import models, fields, api, _


class InvoiceJournalField(models.Model):
	_inherit = 'account.invoice'



	@api.onchange('partner_id')
	def onchange_partner(self):
		pro=self.env['res.partner'].search([])
		pro1=self.env['account.journal'].search([])
		for item in pro:
			if item==self.partner_id:
				if item.customer and not item.is_retailer:
					for temp in pro1:
						if temp.name=='Export Invoices':
							self.update({'journal_id':temp.id})


				elif item.customer and item.is_retailer:
					for temp in pro1:
						if temp.name=='Retail Invoices':
							self.update({'journal_id':temp.id})

				else:
					self.update({'journal_id':'Tax Invoices'})