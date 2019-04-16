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
from ..unit.customer_exporter import WpCustomerExport
from odoo.exceptions import Warning
import re
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)


class Customer(models.Model):

    """ Models for woocommerce res partner """
    _inherit = 'res.partner'

    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    username = fields.Char(string='WP User Name')
    company = fields.Char(string='WP Company Name')
    password = fields.Char(string='WP password')

    shipping_ids = fields.One2many(comodel_name='res.partner.shipping.address',
                                   inverse_name='partner_id',
                                   string='Multi Shipping',
                                   required=False,)

    backend_id = fields.Many2many(comodel_name='wordpress.configure',
                                  string='WP Backend',
                                  store=True,
                                  readonly=False,
                                  required=True,
                                  )

    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.res.partner',
                                      string='Customer mapping',
                                      inverse_name='customer_id',
                                      readonly=False,
                                      required=False,
                                      )
    # email = fields.Char(related='partner_id.email', inherited=True)

    @api.model
    def create(self, vals):
        """ Override create method """
        customer_id = super(Customer, self).create(vals)
        return customer_id

    @api.multi
    def write(self, vals):
        """ Override write method to export customers when any details is changed """
        customer = super(Customer, self).write(vals)
        return customer

    @api.multi
    def sync_customer(self):
        for backend in self.backend_id:
            self.export_customer(backend)
        return

    @api.onchange('email')
    def  ValidateEmail(self):
        if not self.email:
            return
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", self.email) != None:
            pass
        else:
            raise UserError(_('Invalid Email'))
            # raise UserError(_("No opening move defined !"))

    @api.multi
    def export_customer(self, backend):
        """ export customer details, save username and create or update backend mapper """
        if not self.customer:
            return
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('customer_id', '=', self.id)])
        method = 'customer'
        arguments = [mapper.woo_id or None, self]
        export = WpCustomerExport(backend)
        res = export.export_customer(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            self.write({'username': res['data']['username']})
            mapper.write(
                {'customer_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 200 or res['status'] == 201):
            self.write({'username': res['data']['username']})
            self.backend_mapping.create(
                {'customer_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})


class CustomerMapping(models.Model):

    """ Model to store woocommerce id for particular customer"""
    _name = 'wordpress.odoo.res.partner'
    _description = 'wordpress.odoo.res.partner'

    customer_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        ondelete='cascade',
        readonly=False,
        required=True,
    )

    backend_id = fields.Many2one(
        comodel_name='wordpress.configure',
        string='Backend',
        ondelete='set null',
        store=True,
        readonly=False,
        required=False,
    )

    woo_id = fields.Char(string='Woo id')


def import_record(cr, uid, ids, context=None):
    """ Import a record from woocommerce """
    importer.run(woo_id)
