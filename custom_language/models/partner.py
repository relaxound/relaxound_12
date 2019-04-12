# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
	_inherit = 'res.partner'


	@api.model
	def create(self, vals):
		res=super(ResPartner,self).create(vals)

		pro=self.env['res.country'].search([('id','=',res.country_id.id)])

		if pro.code=='DE' or pro.code=='AT' or pro.code=='CH':
			abc=self.env['res.lang'].search([])
			for item in abc:
				if item.code=='de_DE':
					 res.lang=item.code


		return res



	@api.multi
	def write(self, vals):
		if 'country_id' in vals.keys():
			pro=self.env['res.country'].search([('id','=',vals['country_id'])])

			if pro.code=='DE' or pro.code=='AT' or pro.code=='CH':
				abc=self.env['res.lang'].search([])
				for item in abc:
					if item.code=='de_DE' :
						vals['lang']=item.code

			else:
				vals['lang']='en_US'

					
		return super(ResPartner,self).write(vals)
	
	


