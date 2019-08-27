from odoo import models, fields, api,_


class retailer_email(models.Model):
	_inherit = 'res.partner'
	email2=fields.Char("Email2")
	email3=fields.Char("Email3")