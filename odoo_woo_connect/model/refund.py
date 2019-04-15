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
from ..unit.sale_order_exporter import WpSaleOrderExport

from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class account_invoice_wp(models.Model):
    _inherit = 'account.invoice'

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
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.account.invoice',
                                      string='Account invoice mapping',
                                      inverse_name='refund_id',
                                      readonly=False,
                                      required=False,
                                      )
    sale_order_id = fields.Many2one(comodel_name='sale.order',
                                    string='Sale Order Refrenc Id',
                                    readonly=False,
                                    required=False,
                                    )

    @api.multi
    def write(self, vals):
        if self.type == 'out_refund' and 'state' in vals.keys():
            if vals['state'] == 'paid':
                for backend in self.backend_id:
                    self.export(backend)
        invoice_id = super(account_invoice_wp, self).write(vals)
        return invoice_id

    @api.multi
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        data = super(account_invoice_wp, self)._prepare_refund(
            invoice, date_invoice, date, description, journal_id)
        data['backend_id'] = [[6, 0, invoice.backend_id.ids]]
        data['sale_order_id'] = invoice.sale_order_id.id
        return data

    @api.multi
    def sync_invoice_refund(self):
        for backend in self.backend_id:
            self.with_delay().export(backend)
        return

    @api.multi
    @job
    def export(self, backend):
        """ export and create or update backend mapper """
        if len(self.ids)>1:
            for obj in self:
                obj.with_delay().export(backend)
            return
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('refund_id', '=', self.id)], limit=1)
        sale_id = self.env['sale.order'].search(
            [('id', '=', self.sale_order_id.id)])
        order_mapper = sale_id.backend_mapping.search(
            [('backend_id', '=', backend.id), ('order_id', '=', sale_id.id)], limit=1)
        method = 'account_invoice'
        arguments = [mapper.woo_id or None, self, order_mapper]
        export = WpSaleOrderExport(backend)
        res = export.export_invoice_refund(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            mapper.write(
                {'refund_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 200 or res['status'] == 201):
            self.backend_mapping.create(
                {'refund_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})


class RefundInvoiceMapping(models.Model):

    """ Model to store woocommerce id for particular invoice refund"""
    _name = 'wordpress.odoo.account.invoice'

    refund_id = fields.Many2one(comodel_name='account.invoice',
                                string='Account Invoice',
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
