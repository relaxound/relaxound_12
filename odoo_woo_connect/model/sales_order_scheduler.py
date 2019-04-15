from odoo import models, fields, api
from datetime import datetime,timedelta

class Sales_Order_Scheduler(models.Model):
	_inherit = 'sale.order'

	wp_id = fields.Char(string="Wordpress Id")

	def sale_order_scheduler(self):
		yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%d-%mT%H:%M:%S')
		sale_order = self.env['wordpress.configure'].search([])
		for sale_id in sale_order:
			self.importer(sale_id, yesterday)
