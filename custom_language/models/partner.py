# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
	_inherit = 'res.partner'


	@api.onchange('country_id')
	def onchange_country(self):
		if self.country_id.code=='DE' or self.country_id.code=='AT' or self.country_id.code=='CH':
			self.update({'lang': 'de_DE'})
			# abc=self.env['res.lang'].search([])
			# for item in abc:
			# 	if item.code=='de_DE':
			# 			self.update({'lang':item.code})

		elif self.country_id.code == 'FR':
			self.update({'lang': 'fr_CH'})

		else:
			self.update({'lang': 'en_US'})
	


