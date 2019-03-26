# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
	_inherit = 'res.partner'


	@api.model
	def create(self, vals):
		import pdb
		pdb.set_trace()
		res=super(ResPartner,self).create(vals)

		pro=self.env['res.country'].search([('id','=',res.country_id.id)])

		if pro.code=='DE' or pro.code=='AT' or pro.code=='CH':
			abc=self.env['res.lang'].search([])
			for item in abc:
				if item.code=='de_CH':
					 res.lang=item.code


		return res


