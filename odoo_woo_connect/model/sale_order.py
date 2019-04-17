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
# from odoo.addons.queue_job.job import job
import base64
from odoo import models, fields, api, _
from ..unit.sale_order_exporter import WpSaleOrderExport
from ..unit.sale_order_importer import WpSaleOrderImport
from odoo.exceptions import Warning


_logger = logging.getLogger(__name__)


class SalesOrder(models.Model):

    """ Models for woocommerce sales order """
    _inherit = 'sale.order'

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
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.sale.order',
                                      string='Sale order mapping',
                                      inverse_name='order_id',
                                      readonly=False,
                                      required=False,
                                      )

    @api.model
    def create(self, vals):
        """ Override create method to export"""
        _logger.info("create vals %s", vals)
        if 'partner_id' in vals.keys():
            vals['partner_id'] = int(vals['partner_id'])
        sales_order_id = super(SalesOrder, self).create(vals)
        return sales_order_id

    @api.multi
    def write(self, vals):
        """ Override write method to export when any details is changed """
        _logger.info("write vals %s", vals)
        for sale_order in self:
          res = super(SalesOrder, sale_order).write(vals)
        return True

    @api.multi
    def sync_sale_order(self):
        for backend in self.backend_id:
            self.export(backend)
        return

    @api.multi
    def sales_line(self, vals):
        res = self.write({'order_line': [[0, 0, vals]]})
        return True

    # @api.multi
    # # @job
    # def importer(self, backend, date=None):
    #     """ import and create or update backend mapper """
    #     if len(self.ids) > 1:
    #         for obj in self:
    #             obj.single_importer(backend)
    #         return

    #     method = 'sales_order_import'
    #     arguments = [None, self]
    #     importer = WpSaleOrderImport(backend)

    #     count = 1
    #     data = True
    #     sale_ids = []
    #     while(data):
    #       res = importer.import_sales_order(method, arguments, count, date)['data']
    #       if(res):
    #         sale_ids.extend(res)
    #       else:
    #         data = False
    #       count += 1
    #     for sale_id in sale_ids:
    #       self.single_importer(backend, sale_id)

    # @api.multi
    # # @job
    # def single_importer(self, backend, sale_id, woo_id=None):
    #     method = 'sales_order_import'
    #     mapper = self.backend_mapping.search(
    #         [('backend_id', '=', backend.id), ('woo_id', '=', sale_id)], limit=1)
    #     arguments = [sale_id or None, mapper.order_id or self]

    #     importer = WpSaleOrderImport(backend)
    #     res = importer.import_sales_order(method, arguments)
    #     partner_id = self.env['wordpress.odoo.res.partner'].search(
    #         [('backend_id', '=', backend.id), ('woo_id', '=', res['data']['customer_id'])])
    #     record = res['data']
    #     if partner_id:
    #       pass
    #     else:
    #       partner = self.env['res.partner']
    #       partner.single_importer(backend, res['data']['customer_id'],False)
    #       partner_id = self.env['wordpress.odoo.res.partner'].search(
    #         [('backend_id', '=', backend.id), ('woo_id', '=', res['data']['customer_id'])])

    #     if mapper:
    #       # importer.write_sale_order(record, mapper, backend)
    #       sale_order_id = mapper.order_id
    #       if 'line_items' in record:
    #         product_ids = []
    #         for lines in record['line_items']:
    #           if 'product_id' in lines:
    #             product_template_id = self.env['wordpress.odoo.product.template'].search(
    #                 [('backend_id', '=', backend.id),
    #                     ('woo_id', '=', lines['product_id'])])
    #             product=product_template_id.product_id.product_variant_id
    #             if not product_template_id:
    #               product_template_id = self.env['wordpress.odoo.mu.product'].search(
    #                 [('backend_id', '=', backend.id),
    #                  ('woo_id', '=', lines['product_id'])])
    #               product=product_template_id.major_unit_id.product_id
    #             if not product_template_id:
    #               product_template_id = self.env['wordpress.odoo.majorunit'].search(
    #                 [('backend_id', '=', backend.id),
    #                  ('woo_id', '=', lines['product_id'])])
    #               product=product_template_id.majorunit_id.product_id
    #             for prod in product:
    #               result = {'product_id': product.id,
    #                           'price_unit': lines['price'],
    #                           'product_uom_qty': lines['quantity'],
    #                           'product_uom': 1,
    #                           'price_subtotal': lines['subtotal'],
    #                           'name': lines['name'],
    #                           'order_id': sale_order_id.id,
    #                           'backend': lines['id']
    #                           }
    #               product_ids.append(result)
    #         for details in product_ids:
    #           order = self.env['sale.order.line'].search(
    #               [('backend', '=', details['backend'])])
    #           if order:
    #             order.write(details)

    #     else:
    #       # importer.create_sale_order(record, partner_id, backend)
    #       product_ids = []
    #       if record['date_created']:
    #         date_created = record['date_created']
    #       else:
    #         date_created = ''
    #       if partner_id:
    #         values = {
    #             'partner_id': partner_id[0].customer_id.id,
    #             'date_order': date_created.replace('T',' ')
    #         }

    #         sale_order = self.create(values)

    #         if 'line_items' in record:
    #           product_ids = []
    #           for lines in record['line_items']:
    #             if 'product_id' in lines:
    #               product_template_id = self.env['wordpress.odoo.product.template'].search(
    #                   [('backend_id', '=', backend.id),
    #                    ('woo_id', '=', lines['product_id'])])
    #               product=product_template_id.product_id.product_variant_id
    #               if not product_template_id:
    #                 product_template_id = self.env['wordpress.odoo.mu.product'].search(
    #                   [('backend_id', '=', backend.id),
    #                    ('woo_id', '=', lines['product_id'])])
    #                 product=product_template_id.major_unit_id.product_id
    #               if not product_template_id:
    #                 product_template_id = self.env['wordpress.odoo.majorunit'].search(
    #                   [('backend_id', '=', backend.id),
    #                    ('woo_id', '=', lines['product_id'])])
    #                 product=product_template_id.majorunit_id.product_id
    #               for prod in product:
    #                 result = [0,0,{
    #                         'product_id': prod.id,
    #                         'price_unit': lines['price'],
    #                         'product_uom_qty': lines['quantity'],
    #                         'product_uom': 1,
    #                         'price_subtotal': lines['subtotal'],
    #                         'name': lines['name'],
    #                         'order_id': sale_order.id,
    #                         'backend': lines['id'],
    #                         }]
    #                 product_ids.append(result)
    #           sale_order.update({'order_line': product_ids})
    #     if mapper and (res['status'] == 200 or res['status'] == 201):
    #       vals = {
    #           'woo_id': res['data']['id'],
    #           'backend_id': backend.id,
    #           'order_id': mapper.order_id.id,
    #       }
    #       self.backend_mapping.write(vals)
    #     else:
    #       if(partner_id):
    #         vals = {
    #             'woo_id': res['data']['id'],
    #             'backend_id': backend.id,
    #             'order_id': sale_order.id,
    #         }

    #         self.backend_mapping.create(vals)

    # @api.multi
    # # @job
    # def export(self, backend):
    #     """ export and create or update backend mapper """
    #     if len(self.ids) > 1:
    #         for obj in self:
    #             obj.export(backend)
    #         return
    #     mapper = self.backend_mapping.search(
    #         [('backend_id', '=', backend.id), ('order_id', '=', self.id)], limit=1)
    #     method = 'sales_order'
    #     arguments = [mapper.woo_id or None, self]
    #     export = WpSaleOrderExport(backend)
    #     res = export.export_sales_order(method, arguments)
    #     if mapper and (res['status'] == 200 or res['status'] == 201):
    #         mapper.write(
    #             {'order_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
    #     elif (res['status'] == 200 or res['status'] == 201):
    #         self.backend_mapping.create(
    #             {'order_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})

    # @api.multi
    # def _prepare_invoice(self):
    #     invoice_id = super(SalesOrder, self)._prepare_invoice()
    #     invoice_id['backend_id'] = [[6, 0, self.backend_id.ids]]
    #     invoice_id['sale_order_id'] = self.id
    #     return invoice_id


class SalesOrderMapping(models.Model):

    """ Model to store woocommerce id for particular Sale Order"""
    _name = 'wordpress.odoo.sale.order'
    _description ='wordpress.odoo.sale.order'

    order_id = fields.Many2one(comodel_name='sale.order',
                               string='Sale Order',
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


def import_record(cr, uid, ids, context=None):
    """ Import a record from woocommerce """
    importer.run(woo_id)
