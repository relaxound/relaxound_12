# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class CustomSaleOrder(models.Model):
	_inherit = "sale.order"
	is_note = fields.Boolean(compute='onchange_partner_id_credit_1',string="Is Note", default=False)
	

	@api.onchange('partner_id')
	def onchange_partner_id_credit_1(self):
		for rec in self:
			if rec.partner_id.comment:
				rec.is_note = True

