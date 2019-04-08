# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class InvoiceJournal(models.Model):
	_inherit = 'sale.order'

	journal_id = fields.Many2one('account.journal', string="Journal", required=True)




	@api.multi
	def action_view_invoice(self):
		res=super(InvoiceJournal,self).action_view_invoice()
		res1=self.env['account.invoice'].search([])
		pro=self.env['res.partner'].search([])
		pro1=self.env['account.journal'].search([])
		for item in pro:
			if item==self.partner_id:
				if item.customer and not item.is_retailer:
					for cust in res1:
						if cust.partner_id==self.partner_id:
							for temp in pro1:
								if temp.name=='Export Invoices':
									res1.update({'journal_id':temp.id})

				elif item.is_retailer and item.customer:
					for cust in res1:
						if cust.partner_id==self.partner_id:
							for temp in pro1:
								if temp.name=='Retail Invoices':
									res1.update({'journal_id':temp.id})

				else:
					res1.update({'journal_id':'Tax Invoices'})


		return res
