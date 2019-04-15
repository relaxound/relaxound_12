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
from ..unit.product_category_exporter import WpCategoryExport
from odoo.exceptions import Warning


_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):

    """ Models for woocommerce product category """
    _inherit = 'product.category'

    image_id = fields.Char('Image id')
    slug = fields.Char('Slug')
    image = fields.Binary("Image",
                          help="This field holds the image used as image for the cateogry")
    woo_id = fields.Char(string='woo_id')
    desc = fields.Text(string="Description")

    @api.model
    def get_backend(self):
        return self.env['wordpress.configure'].search([]).ids
    backend_id = fields.Many2many(comodel_name='wordpress.configure',
                                  string='Website',
                                  store=True,
                                  readonly=False,
                                  required=False,
                                  default=get_backend,
                                  )
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.category',
                                      string='Category mapping',
                                      inverse_name='category_id',
                                      readonly=False,
                                      required=False,
                                      )

    @api.model
    def create(self, vals):
        """ Override create method to export"""
        category_id = super(ProductCategory, self).create(vals)
        return category_id

    @api.multi
    def write(self, vals):
        """ Override write method to export when any details is changed """
        category = super(ProductCategory, self).write(vals)
        return category

    @api.multi
    def sync_category(self):
        for backend in self.backend_id:
            self.with_delay().export(backend)
        return

    @api.multi
    @job
    def export(self, backend):
        """ export product details, save slug and create or update backend mapper """
        if len(self.ids)>1:
            for obj in self:
                obj.with_delay().export(backend)
            return
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('category_id', '=', self.id)], limit=1)
        method = 'category'
        arguments = [mapper.woo_id or None, self]

        export = WpCategoryExport(backend)
        res = export.export_product_category(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            self.write({'slug': res['data']['slug']})
            if res['data']['image']:
                image_id = res['data']['image']['id']
            else:
                image_id = None
            mapper.write({'category_id': self.id, 'backend_id': backend.id, 'woo_id': res[
                         'data']['id'], 'image_id': image_id})
        elif (res['status'] == 200 or res['status'] == 201):
            self.write({'slug': res['data']['slug']})
            if res['data']['image']:
                image_id = res['data']['image']['id']
            else:
                image_id = None
            self.backend_mapping.create({'category_id': self.id, 'backend_id': backend.id, 'woo_id': res[
                                        'data']['id'], 'image_id': image_id})
        elif (res['status'] == 400 and res['data']['code'] == 'term_exists'):
            if 'resource_id' in res['data']['data'].keys():
                self.backend_mapping.create({'category_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['data']['resource_id']})
        return


class ProductCategoryMapping(models.Model):

    """ Model to store woocommerce id for particular product category"""
    _name = 'wordpress.odoo.category'

    category_id = fields.Many2one(comodel_name='product.category',
                                  string='Product Category',
                                  ondelete='cascade',
                                  readonly=False,
                                  required=True,
                                  )

    backend_id = fields.Many2one(comodel_name='wordpress.configure',
                                 string='Website',
                                 ondelete='set null',
                                 store=True,
                                 readonly=False,
                                 required=False,
                                 )
    image_id = fields.Char('Image id')
    woo_id = fields.Char(string='woo_id')


def import_record(cr, uid, ids, context=None):
    """ Import a record from woocommerce """
    importer.run(woo_id)
