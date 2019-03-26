# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class BusinessSector(models.Model):
	_inherit = 'res.partner'


	business_sec = fields.Selection([
        ('sec1', 'Beauty / Wellness'),
        ('sec2', 'Books'), 
        ('sec3', 'Gardening'),
        ('sec4', 'Gastronomy'),
        ('sec5', 'Presents / Gifts'),
        ('sec6', 'Art / Culture')
        ('sec7', 'Home Living')
        ('sec8', 'Misc')], string='Business Sector:')






