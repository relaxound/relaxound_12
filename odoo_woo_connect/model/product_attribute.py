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
from ..unit.product_attribute_exporter import WpProductAttributeExport
from odoo.exceptions import Warning


_logger = logging.getLogger(__name__)


class ProductAttribute(models.Model):

    """ Models for woocommerce product attributes """
    _inherit = 'product.attribute'

    slug = fields.Char('Slug')

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

    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.attribute',
                                      string='Attribute mapping',
                                      inverse_name='attribute_id',
                                      readonly=False,
                                      required=False,
                                      )

    # visible and variant here
    visible = fields.Boolean(string="Visible", help="Visible on product page", default=True)

    value_order_by = fields.Selection(
        selection=[('menu_order', 'Custome Order'),
                  ('name', 'Name'),
                  ('name_num', 'Name(Numeric)'),
                  ('id', 'Term ID')],
        string='Order By',
        default='menu_order', help='To Sort Attribute Values In Order'
    )

    @api.model
    def create(self, vals):
        """ Override create method """
        backend_obj = self.env['wordpress.configure']
        backend_ids = backend_obj.search([('name', '!=', None)])
        vals['backend_id'] = [[6, 0, backend_ids.ids]]
        attribute_id = super(ProductAttribute, self).create(vals)
        return attribute_id

    @api.multi
    def write(self, vals):
        """ Override write method to export when any details is changed """
        attribute = super(ProductAttribute, self).write(vals)
        return attribute

    @api.multi
    def sync_attribute(self):
        for backend in self.backend_id:
            self.with_delay().export(backend)
        return

    @api.multi
    def sync_product_attribute_multi(self):
        for value in self:
            value.sync_attribute()

    @api.multi
    @job
    def export(self, backend):
        """ export product attributes, save slug and create or update backend mapper """
        if len(self.ids)>1:
            for obj in self:
                obj.with_delay().export(backend)
                obj.value_ids.with_delay().export(backend)
            return
        method = 'attribute'
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('attribute_id', '=', self.id)], limit=1)
        export = WpProductAttributeExport(backend)
        arguments = [mapper.woo_id or None, self]
        res = export.export_product_attribute(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            self.write({'slug': res['data']['slug']})
            mapper.write(
                {'attribute_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 200 or res['status'] == 201):
            self.write({'slug': res['data']['slug']})
            self.backend_mapping.create(
                {'attribute_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 400 and res['data']['code'] == 'woocommerce_rest_invalid_product_attribute_slug_already_exists'):
            if 'resource_id' in res['data']['data'].keys():
                self.backend_mapping.create(
                    {'attribute_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['data']['resource_id']})


def import_record(cr, uid, ids, context=None):
    """ Import a record from woocommerce """
    importer.run(woo_id)


class ProductAttributeMapping(models.Model):

    """ Model to store woocommerce id for particular product attribute """
    _name = 'wordpress.odoo.attribute'

    attribute_id = fields.Many2one(comodel_name='product.attribute',
                                   string='Product Attribute',
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

    woo_id = fields.Char(string='woo_id')


class ProductAttributeValue(models.Model):

    """ Models for woocommerce product attribute value """
    _inherit = 'product.attribute.value'

    slug = fields.Char('Slug')
    backend_id = fields.Many2many(comodel_name='wordpress.configure',
                                  string='Website',
                                  store=True,
                                  readonly=False,
                                  required=False,
                                  )
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.attribute.value',
                                      string='Attribute value mapping',
                                      inverse_name='attribute_value_id',
                                      readonly=False,
                                      required=False,
                                      )

    @api.model
    def create(self, vals):
        """ Override create method """
        backend_obj = self.env['wordpress.configure']
        backend_ids = backend_obj.search([('name', '!=', None)])
        vals['backend_id'] = [[6, 0, backend_ids.ids]]
        attribute_value = super(ProductAttributeValue, self).create(vals)
        return attribute_value

    @api.multi
    def write(self, vals):
        """ Override write method to export when any details is changed """
        attribute_value = super(ProductAttributeValue, self).write(vals)
        return attribute_value

    @api.multi
    def sync_attribute_value(self):
        for backend in self.backend_id:
            self.with_delay().export(backend)
        return

    @api.multi
    def sync_product_attribute_value_multi(self):
        for value in self:
            value.sync_attribute_value()

    @api.multi
    @job
    def export(self, backend):
        """ export product attribute value details, and create or update backend mapper """
        if len(self.ids)>1:
            for obj in self:
                obj.with_delay().export(backend)
            return
        if len(self.ids) == 0:
            return
        method = 'attribute_value'
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('attribute_value_id', '=', self.id)], limit=1)
        attr_mapper = self.attribute_id.backend_mapping.search(
            [('backend_id', '=', backend.id), ('attribute_id', '=', self.attribute_id.id)], limit=1)
        export = WpProductAttributeExport(backend)
        arguments = [mapper.woo_id or None, self, attr_mapper]
        res = export.export_product_attribute_value(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            self.write({'slug': res['data']['slug']})
            mapper.write({'attribute_value_id': self.id,
                          'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 200 or res['status'] == 201):
            self.write({'slug': res['data']['slug']})
            self.backend_mapping.create(
                {'attribute_value_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 400 and res['data']['code']=='term_exists'):
            if 'resource_id' in res['data']['data'].keys():
                self.backend_mapping.create(
                    {'attribute_value_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['data']['resource_id']})


class ProductAttributeValueMapping(models.Model):

    """ Model to store woocommerce id for particular product attribute value"""
    _name = 'wordpress.odoo.attribute.value'

    attribute_value_id = fields.Many2one(comodel_name='product.attribute.value',
                                         string='Product Attribute Value',
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

    woo_id = fields.Char(string='woo_id')
