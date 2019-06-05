from odoo import models, fields, api, _


class sale_order_fun(models.Model):
	_inherit = 'sale.order'



	@api.multi
	def _prepare_invoice(self):
		self.ensure_one()
		pro1=self.env['account.journal'].search([])
		if self.name[0]=='S' or self.name[0]=='P' and self.name[1]=='O':
			for item in pro1:
				if item.name=='Retailer Invoices':
					invoice_vals = {
						'name': self.client_order_ref or '',
						'origin': self.name,
						'type': 'out_invoice',
						'account_id': self.partner_invoice_id.property_account_receivable_id.id,
						'partner_id': self.partner_invoice_id.id,
						'partner_shipping_id': self.partner_shipping_id.id,
						'journal_id': item.id,
						'currency_id': self.pricelist_id.currency_id.id,
						'comment': self.note,
						'payment_term_id': self.payment_term_id.id,
						'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
						'company_id': self.company_id.id,
						'user_id': self.user_id and self.user_id.id,
						'team_id': self.team_id.id,
						'transaction_ids': [(6, 0, self.transaction_ids.ids)],
					}
					return invoice_vals

		elif self.name[0]=='0' or self.name[0]=='1' or self.name[0]=='2' or self.name[0]=='3' or self.name[0]=='4' or self.name[0]=='5' or self.name[0]=='6' or self.name[0]=='7' or self.name[0]=='8' or self.name[0]=='9':
			for item in pro1:
				if item.name=='Customer Invoices':
					invoice_vals = {
						'name': self.client_order_ref or '',
						'origin': self.name,
						'type': 'out_invoice',
						'account_id': self.partner_invoice_id.property_account_receivable_id.id,
						'partner_id': self.partner_invoice_id.id,
						'partner_shipping_id': self.partner_shipping_id.id,
						'journal_id': item.id,
						'currency_id': self.pricelist_id.currency_id.id,
						'comment': self.note,
						'payment_term_id': self.payment_term_id.id,
						'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
						'company_id': self.company_id.id,
						'user_id': self.user_id and self.user_id.id,
						'team_id': self.team_id.id,
						'transaction_ids': [(6, 0, self.transaction_ids.ids)],
					}
					return invoice_vals

		else:
			journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
			if not journal_id:
				raise UserError(_('Please define an accounting sales journal for this company.'))
			invoice_vals = {
				'name': self.client_order_ref or '',
				'origin': self.name,
				'type': 'out_invoice',
				'account_id': self.partner_invoice_id.property_account_receivable_id.id,
				'partner_id': self.partner_invoice_id.id,
				'partner_shipping_id': self.partner_shipping_id.id,
				'journal_id': journal_id,
				'currency_id': self.pricelist_id.currency_id.id,
				'comment': self.note,
				'payment_term_id': self.payment_term_id.id,
				'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
				'company_id': self.company_id.id,
				'user_id': self.user_id and self.user_id.id,
				'team_id': self.team_id.id,
				'transaction_ids': [(6, 0, self.transaction_ids.ids)],
			}
			return invoice_vals
