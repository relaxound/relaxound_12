# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class BusinessSector(models.Model):
	_inherit = 'res.partner'


	business_sec = fields.Selection([
        ('sec1', 'Sector1'),
        ('sec2', 'Sector2'), 
        ('sec3', 'Sector3')], string='Business Sector:')



