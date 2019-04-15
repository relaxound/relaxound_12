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
from ..unit.crm_lead_exporter import WpCrmLeadExport
from odoo.exceptions import Warning


_logger = logging.getLogger(__name__)


class CreditApp(models.Model):

    """ Models for woocommerce sales order """
    _inherit = 'res.partner.credit.application'

    backend_id = fields.Many2many(comodel_name='wordpress.configure',
                                  string='Website',
                                  store=True,
                                  readonly=False,
                                  required=False,
                                  )
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.credit.application',
                                      string='Credit App Mapping',
                                      inverse_name='credit_app_id',
                                      readonly=False,
                                      required=False,
                                      )

    @api.model
    def create(self, vals):
        """ Override create method to export"""
        crm_lead_id = super(CreditApp, self).create(vals)
        return crm_lead_id

    @api.multi
    def write(self, vals):
        """ Override write method to export when any details is changed """
        return super(CreditApp, self).write(vals)


class CreditAppMapping(models.Model):

    """ Model to store woocommerce id for particular Sale Order"""
    _name = 'wordpress.odoo.credit.application'

    credit_app_id = fields.Many2one(comodel_name='res.partner.credit.application',
                               string='Credit App',
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
