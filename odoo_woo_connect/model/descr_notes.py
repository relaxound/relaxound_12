from odoo import api , fields, models

class DescriptionQuote(models.Model):

	_inherit = 'product.template'

	description_quotation = fields.Text(
        'Description',
        help="A precise description of the Product, used only for internal information purposes.")
	description_pickings = fields.Text('Description on Picking')

