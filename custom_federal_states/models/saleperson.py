from odoo import models, fields, api, _


class Saleperson(models.Model):
	_inherit = 'res.country.state'

	user_id = fields.Many2one('res.users', string='Salesperson')