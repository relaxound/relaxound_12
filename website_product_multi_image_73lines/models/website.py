# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.##############
from odoo import api, fields, models, tools
#from odoo.osv import orm


class website(models.Model):
    _inherit = 'website'

    def get_multiple_images(self, product_id=None):

        data = []
        uid = self._uid
        ids = self.ids
        product_img_data = False

        if product_id:
            pi_pool = self.env['product.images']
            product_ids = pi_pool.search([('product_tmpl_id', '=', product_id)],order="sequence asc")
            if product_ids:
                for image in product_ids:
                    product_img_data = self.env['product.images'].browse(image.id)
                    data.append(product_img_data)
        return data
