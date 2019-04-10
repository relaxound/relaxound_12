# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
	_inherit = 'res.partner'


	@api.onchange('zip')
	def onchange_zip(self):
		pro=self.env['res.better.zip'].search([])
		for item in pro:
			if self.zip == item.name:
				self.update({'user_id':item.user_id})

