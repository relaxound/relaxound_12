# -*- coding: utf-8 -*-

from odoo import models, fields

class ProductColor(models.Model):
    _name = 'product.color'
    _description ='Color Module'
    name = fields.Char('Name', translate=True, required=True)
    

