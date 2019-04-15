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
import base64
from odoo import models, fields, api, _
from ..unit.tax_exporter import WpTaxExport
from ..unit.tax_importer import WpTaxImport
from odoo.exceptions import Warning
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class Tax(models.Model):

    """ Models for woocommerce res partner """
    _inherit = 'account.tax'

    slug = fields.Char('slug')
    state_id = fields.Many2one(
        "res.country.state", string='State', ondelete='restrict')
    country_id = fields.Many2one(
        'res.country', string='Country', ondelete='restrict')
    postcode = fields.Char('postcode')
    city = fields.Char('city')
    priority = fields.Integer('priority')
    compound = fields.Boolean('compound')
    shipping = fields.Boolean('shipping')
    order = fields.Integer('order')

    @api.model
    def get_backend(self):
        return self.env['wordpress.configure'].search([]).ids
    backend_id = fields.Many2many(comodel_name='wordpress.configure',
                                  string='Website',
                                  store=True,
                                  readonly=False,
                                  required=True,
                                  default=get_backend,
                                  )
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.tax',
                                      string='Tax mapping',
                                      inverse_name='tax_id',
                                      readonly=False,
                                      required=False,
                                      )

    tax_class = fields.Selection([
        ('standard','Standard'),
        ('showroom','Showroom'),
        ('accessories','Accessories'),
        ('apparel','Apparel'),
        ('parts','Parts'),
        ('service','Service'),
        ('deals','Deals')],
        string="Tax Class")

    @api.model
    def create(self, vals):
        """ Override create method """
        tax_id = super(Tax, self).create(vals)
        return tax_id

    @api.multi
    def write(self, vals):
        """ Override write method to export customers when any details is changed """
        tax = super(Tax, self).write(vals)
        return tax


    @api.multi
    def sync_tax(self):
        for backend in self.backend_id:
            self.export(backend, 'standard')
        return

    @api.multi
    @job
    def importer(self, backend):
        """ import and create or update backend mapper """
        if len(self.ids)>1:
            for obj in self:
                obj.with_delay().single_importer(backend)
            return

        method = 'taxes'
        arguments = [None,self]
        importer = WpTaxImport(backend)

        # count = 1
        # data = True
        # tax_ids = []
        # while(data):
        #   res = importer.import_tax(method, arguments, count)['data']
        #   if(res):
        #     tax_ids.extend(res)
        #   else:
        #     data = False
        #   count += 1
        # for tax_id in tax_ids:
        #   self.with_delay().single_importer(backend, tax_id)

        res = importer.import_tax(method, arguments)
        if (res['status'] == 200 or res['status'] == 201):
            if isinstance(res['data'],list):
                for tax_id in res['data']:
                    self.with_delay().single_importer(backend,tax_id)

        # if len(self.ids)>1:
        #     for obj in self:
        #         obj.with_delay().single_importer(backend)
        #     return

        # method = 'my_import_form'
        # arguments = [None,self]
        # importer = WpCrmLeadImport(backend)
        # res = importer.import_crm_lead(method, arguments)
        # if (res['status'] == 200 or res['status'] == 201):
        #   if isinstance(res['data'],list):
        #     for crm_id in res['data']:
        #       self.with_delay().single_importer(backend,crm_id)

    @api.multi
    @job
    def single_importer(self,backend,tax_id,status=True,woo_id=None):
        method = 'taxes'
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('woo_id', '=', tax_id)], limit=1)
        arguments = [tax_id or None,mapper.tax_id or self]

        importer = WpTaxImport(backend)
        res = importer.import_tax(method, arguments)
        record = res['data']

        if mapper:
            importer.write_tax(backend,mapper,res)

        else:
            account_tax = importer.create_tax(backend,mapper,res,status)

        if mapper and (res['status'] == 200 or res['status'] == 201):
            vals = {
                'woo_id' : res['data']['id'],
                'backend_id' : backend.id,
                'tax_id' : mapper.tax_id.id,
            }
            self.backend_mapping.write(vals)
        elif (res['status'] == 200 or res['status'] == 201):
            vals = {
                'woo_id' : res['data']['id'],
                'backend_id' : backend.id,
                'tax_id' : account_tax.id,
            }
            self.backend_mapping.create(vals)

    @api.multi
    @job
    def export(self, backend, tax_class):
        """ export tax details, save username and create or update backend mapper """
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('tax_id', '=', self.id)], limit=1)
        arguments = [mapper.woo_id or None, self]
        export = WpTaxExport(backend)
        if self.amount_type == 'group':
            res = export.export_tax_class('tax_class', arguments)
        else:
            res = export.export_tax('tax', arguments)
            for child_tax in self.children_tax_ids:
                for backend in child_tax.backend_id:
                    child_tax.export_tax(backend, self.slug)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            if 'slug' in res['data'].keys():
                self.write({'slug': res['data']['slug']})
            mapper.write(
                {'tax_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})
        elif (res['status'] == 200 or res['status'] == 201):
            if 'slug' in res['data'].keys():
                self.write({'slug': res['data']['slug']})
            self.backend_mapping.create(
                {'tax_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['id']})


class TaxMapping(models.Model):

    """ Model to store woocommerce id for particular tax"""
    _name = 'wordpress.odoo.tax'

    tax_id = fields.Many2one(comodel_name='account.tax',
                             string='Tax',
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

    woo_id = fields.Char(string='Woo id')

def import_record(cr, uid, ids, context=None):
    """ Import a record from woocommerce """
    importer.run(woo_id)

