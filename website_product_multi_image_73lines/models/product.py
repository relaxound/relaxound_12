# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class product_images(models.Model):
    _name = 'product.images'
    _description = "Add Multiple Image in Product"

    sequence = fields.Integer('Sort Order')
    name = fields.Char('Image Label', translate=True)
    image = fields.Binary('Image')
    product_tmpl_id = fields.Many2one('product.template', 'Product')


class product_template(models.Model):
    _inherit = 'product.template'
    _description = "Multiple Images"

    images = fields.One2many('product.images', 'product_tmpl_id',
                             string='Images1')
    multi_image = fields.Boolean("Multiple Images?")
