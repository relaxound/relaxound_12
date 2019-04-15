#    Techspawn Solutions Pvt. Ltd.
#    Copyright (C) 2016-TODAY Techspawn(<http://www.Techspawn.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import logging

# import xmlrpclib
from collections import defaultdict
from odoo.addons.queue_job.job import job
import base64
from odoo import models, fields, api, _
from ..unit.product_exporter import WpProductExport
from ..unit.product_coupon_exporter import WpProductCouponExport
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class ProductCoupons(models.Model):

    """ Models for product Coupons """
    _name = "product.coupon"
    _order = 'sequence, name'

    name = fields.Char(string="Name")
    type = fields.Selection([('fixed_cart', 'Cart Discount'),
                             ('percent', 'Percent Discount'),
                             ('fixed_product', 'Product Discount'),
                             ], required=True, default='fixed_cart',
                            string="Discount Type", help="Discount type.")
    amount = fields.Float('Amount')
    enable_free_shipping = fields.Boolean('Enable Free Shipping')
    expiry_date = fields.Datetime('Expiry Date', help="Coupon expiry date")

    minimum_amount = fields.Float('Minimum Amount')
    maximum_amount = fields.Float('Maximum Amount')
    individual_use = fields.Boolean('Individual Use')
    exclude_sale_items = fields.Boolean('Exclude Sale Items')
    product_ids = fields.Many2many(comodel_name='product.template',
                                   string='Product Ids',relation='product_ids_rel')
    exclude_product_ids = fields.Many2many(comodel_name='product.template',
                                           string='Exclude Product Ids',relation='exclude_product_ids_rel')
    product_category_ids = fields.Many2many(comodel_name='product.category',
                                            string='Product Category Ids',relation='product_category_ids_rel')
    exclude_product_category_ids = fields.Many2many(comodel_name='product.category',
                                                    string='Exclude Product Category Ids',relation='exclude_product_category_rel')
    customer_emails = fields.Many2many(comodel_name='res.partner',
                                       string='Restrict Customer',
                                       help="Restrict Customer Email")

    usage_limit = fields.Float('Usage Limit')
    usage_limit_per_user = fields.Integer('Usage limit per user')
    limit_usage_to_x_items = fields.Integer('Limit usage to x items')
    usage_count = fields.Float('Usage Count')

    sequence = fields.Integer('Sequence', help="Determine the display order")
    desc = fields.Text(string="Description")
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.product.coupon',
                                      string='Product coupon mapping',
                                      inverse_name='product_coupon_id',
                                      readonly=False,
                                      required=False,)
    backend_id = fields.Many2many(comodel_name='wordpress.configure',
                                  string='Website',
                                  store=True,
                                  readonly=False,
                                  required=True,
                                  )

    @api.model
    def create(self, vals):
        """ Override create method """
        backend_obj = self.env['wordpress.configure']
        backend_ids = backend_obj.search([('name', '!=', None)])
        vals['backend_id'] = [[6, 0, backend_ids.ids]]
        coupon_id = super(ProductCoupons, self).create(vals)
        return coupon_id

    @api.multi
    def write(self, vals):
        """ Override write method """
        if 'expiry_date' in vals.keys():
            if vals['expiry_date'] == '':
                vals['expiry_date'] = None
        coupon_id = super(ProductCoupons, self).write(vals)
        return coupon_id

    @api.multi
    def sync_coupon(self):
        for backend in self.backend_id:
            self.with_delay().export(backend)
        return

    @api.multi
    @job
    def export(self, backend):
        """ export product attributes, save slug and create or update backend mapper """
        if len(self.ids)>1:
            for obj in self:
                obj.with_delay().export(backend)
            return
        method = 'coupon'
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('product_coupon_id', '=', self.id)], limit=1)
        export = WpProductCouponExport(backend)
        arguments = [mapper.woo_id or None, self]
        res = export.export_product_coupon(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            mapper.write(
                {'product_coupon_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 200 or res['status'] == 201):
            self.backend_mapping.create(
                {'product_coupon_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 400 and res['data']['code'] == 'woocommerce_rest_coupon_code_already_exists'):
            if 'resource_id' in res['data']['data'].keys():
                self.backend_mapping.create(
                    {'product_coupon_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['data']['resource_id']})


class ProductCouponMapping(models.Model):

    """ Model to store woocommerce id for particular product"""
    _name = 'wordpress.odoo.product.coupon'
    product_coupon_id = fields.Many2one(comodel_name='product.coupon',
                                        string='Product coupon',
                                        ondelete='cascade',
                                        readonly=False,
                                        required=True,)

    backend_id = fields.Many2one(comodel_name='wordpress.configure',
                                 string='Website',
                                 ondelete='set null',
                                 store=True,
                                 readonly=False,
                                 required=False,)

    woo_id = fields.Char(string='Woo id')
