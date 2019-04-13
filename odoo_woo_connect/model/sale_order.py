# -*- coding: utf-8 -*-
#
#
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
from collections import defaultdict
import base64
from odoo import models, fields, api, _
from ..unit.sale_order_exporter import WpSaleOrderExport
from odoo.exceptions import Warning


_logger = logging.getLogger(__name__)


class SalesOrder(models.Model):

    """ Models for woocommerce sales order """
    _inherit = 'sale.order'

    backend_id = fields.Many2many(comodel_name='wordpress.configure',
                                  string='Backend',
                                  store=True,
                                  readonly=False,
                                  required=False,
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
        if 'partner_id' in vals.keys():
            vals['partner_id'] = int(vals['partner_id'])
        sales_order_id = super(SalesOrder, self).create(vals)
        return sales_order_id

    # @api.multi
    # def write(self, vals):
    #     """ Override write method to export when any details is changed """
    #     return super(SalesOrder, self).write(vals)

    # @api.multi
    # def sync_sale_order(self):
    #     for backend in self.backend_id:
    #         self.export_sales_order(backend)
    #     return

    # @api.multi
    # def sales_line(self, vals):
    #     res = self.write({'order_line': [[0, 0, vals]]})
    #     return

    # @api.multi
    # def export_sales_order(self, backend):
    #     """ export and create or update backend mapper """
    #     mapper = self.backend_mapping.search(
    #         [('backend_id', '=', backend.id), ('order_id', '=', self.id)])
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

    @api.multi
    def _prepare_invoice(self):
        invoice_id = super(SalesOrder, self)._prepare_invoice()
        invoice_id['backend_id'] = [[6, 0, self.backend_id.ids]]
        invoice_id['sale_order_id'] = self.id
        return invoice_id


class SalesOrderMapping(models.Model):

    """ Model to store woocommerce id for particular Sale Order"""
    _name = 'wordpress.odoo.sale.order'
    _description = 'wordpress.odoo.sale.order'

    order_id = fields.Many2one(comodel_name='sale.order',
                               string='Sale Order',
                               ondelete='cascade',
                               readonly=False,
                               required=True,
                               )

    backend_id = fields.Many2one(comodel_name='wordpress.configure',
                                 string='Backend',
                                 ondelete='set null',
                                 store=True,
                                 readonly=False,
                                 required=False,
                                 )
    woo_id = fields.Char(string='woo_id')


# def import_record(cr, uid, ids, context=None):
#     """ Import a record from woocommerce """
#     importer.run(woo_id)
