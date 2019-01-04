# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning

class CustomSaleOrder(models.Model):
	_inherit = "sale.order"
	is_note = fields.Boolean(compute='onchange_partner_id_credit_1',string="Is Note", default=False)

	@api.multi
	def onchange_partner_id_credit_1(self):

		if self.partner_id.comment:
			self.is_note = True

