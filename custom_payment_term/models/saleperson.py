from odoo import models, fields, api, _


class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', oldname='payment_term',store=1)


	@api.onchange('partner_id')
	def payment_term(self):
		if not self.partner_id.property_payment_term_id:
			res=self.env['account.payment.term'].search([])
			for item in res:
				if item.name=='14 days after receipt of invoice':
					self.update({'payment_term_id':item.id})


