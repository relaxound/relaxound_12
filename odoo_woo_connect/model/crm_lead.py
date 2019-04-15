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
from ..unit.crm_lead_importer import WpCrmLeadImport
from odoo.exceptions import Warning


_logger = logging.getLogger(__name__)


class CrmLead(models.Model):

    """ Models for woocommerce sales order """
    _inherit = 'crm.lead'

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
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.crm.lead',
                                      string='Crm Lead mapping',
                                      inverse_name='crm_lead_id',
                                      readonly=False,
                                      required=False,
                                      )
    your_ride = fields.Char(string="Your Ride")
    location = fields.Char(string="City")
    demo_unit = fields.Char(string="Demo Unit")
    hours_of_operation = fields.Text(string="Hours of Operation")
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    test_ride_date = fields.Date(string="Test Ride Date")
    test_ride_time = fields.Char(string="Test Ride Time")
    date_of_birth = fields.Date(string="DOB")
    location_att=fields.Char(string="Location")

    payment = fields.Selection(
      selection=[('N/A','N/A'),
      ('Cash','Cash'),
      ('Financing','Financing'),
    ],string="Payment Method")

    valid_driver_license = fields.Binary()
    valid_insurance = fields.Binary()
    current_motorcycle_own = fields.Char(string="Current Motocycle Owned")

    mileage = fields.Float(string="Mileage")
    condition = fields.Text(string="Condition")
    attach_img = fields.Binary(string="Attach Image")

    make = fields.Char(string="Make")
    model = fields.Char(string="Model")
    year = fields.Char(string="Year")
    # check_one = fields.Selection(selection=[('registered_owner', 'I certify that I am the registered owner and that there is still a lien on the vehicle. The lien holder is:'),('legal_owner','I certify that I am the registered and legal owner of this vehicle and that I have clean and clear title in hand.')])
    check_one = fields.Char(string="Check One")
    u_name = fields.Char(string="Name")
    ac_no = fields.Char(string="Account Number")
    phone_no = fields.Char(string="Phone Number")
    u_bal =  fields.Char(string="The unpaid balance of the lien is $")
    amount = fields.Char(string="Owner will accept price $")
    date = fields.Date(string="As of (Date)")
    form_type = fields.Selection(
      selection=[('reserve','Reserve Ride'),
      ('test','Test Ride'),
      ('sell_your_ride', 'Buy my Bike'),
      ('consignment_form', 'Consignment Form'),
      ('quote','Get a Quote')])

    credit_card_type = fields.Char(string="Credit Card Type")
    card_number = fields.Char(string="Card Number")
    name_on_card = fields.Char(string="Name on Card")
    expiry_date = fields.Date(string="Expiry Date")
    month = fields.Char(string="Month")
    year_deposite = fields.Char(string="Year")
    cvv = fields.Char(string="cvv")
    store = fields.Char(string="Store")

    initial_1 = fields.Char(string="Initial 1")
    initial_2 = fields.Char(string="Initial 2")
    initial_3 = fields.Char(string="Initial 3")
    initial_4 = fields.Char(string="Initial 4")
    initial_5 = fields.Char(string="Initial 5")
    initial_6 = fields.Char(string="Initial 6")
    initial_7 = fields.Char(string="Initial 7")
    initial_8 = fields.Char(string="Initial 8")
    signature = fields.Char(string="Signature")
    date_of_sign = fields.Date(string="Date") 

    @api.model
    def create(self, vals):
        """ Override create method to export"""
        _logger.info(vals)
        crm_lead_id = super(CrmLead, self).create(vals)
        return crm_lead_id

    @api.multi
    def write(self, vals):
        return super(CrmLead, self).write(vals)

    # @api.multi
    # def sync_crm_lead(self):
    #     for backend in self.backend_id:
    #         self.with_delay().export(backend)
    #     return

    @api.multi
    def sync_crm_status(self):
      for backend in self.backend_id:
        self.with_delay().export(backend)
      return

    @api.multi
    def crm_ro_to_lead(self):
        self.ensure_one()
        loc_name = self.env['stock.location'].search([('name','=',self.store)])

        repair_order_vals = {
            'partner_id' : self.partner_id.id,
            'details_model_exists' : True,
            'opportunity_id': self.id,
        }
        if self.major_unit_id:
            repair_order_vals.update({
                'major_unit_id': self.major_unit_id.id,
                'repair_type': 'repair_order',
            })
        repair_order = self.env['service.repair_order'].create(repair_order_vals)
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'service.repair_order',
            'target': 'current',
            'res_id': repair_order.id
        }
        return

    @api.multi
    @job
    def importer(self, backend):
        """ import and create or update backend mapper """
        
        if len(self.ids)>1:
            for obj in self:
                obj.with_delay().single_importer(backend)
            return
        
        method = 'my_import_form'
        arguments = [None,self]
        importer = WpCrmLeadImport(backend)
        res = importer.import_crm_lead(method, arguments)
        if (res['status'] == 200 or res['status'] == 201):
          if isinstance(res['data'],list):
            for crm_id in res['data']:
              self.with_delay().single_importer(backend,crm_id)

    @api.multi
    @job
    def single_importer(self,backend,crm_id,id=None):
        method = 'my_import_form'
        mapper = self.backend_mapping.search(
          [('backend_id', '=', backend.id),('woo_id', '=', crm_id)], limit=1)
        
        arguments = [crm_id or None,mapper.crm_lead_id or self]
        
        importer = WpCrmLeadImport(backend)
        res = importer.import_crm_lead(method, arguments)
        record = res['data']
        if res['data']['user_id']:
          partner_id = self.env['wordpress.odoo.res.partner'].search(
              [('backend_id', '=', backend.id), ('woo_id', '=', res['data']['user_id'])])
          if partner_id:
            partner=partner_id.customer_id
            pass
          else:
            partner = self.env['res.partner']
            partner.single_importer(backend, res['data']['user_id'])
            partner_id = self.env['wordpress.odoo.res.partner'].search(
              [('backend_id', '=', backend.id), ('woo_id', '=', res['data']['user_id'])])
            partner=partner_id.customer_id

        major_unit_id = self.env['wordpress.odoo.majorunit'].search(
            [('backend_id', '=', backend.id), ('woo_id', '=', res['data']['ride_id'])])
        if major_unit_id:
          mu=major_unit_id.majorunit_id
        else:
          major_unit_id = self.env['wordpress.odoo.mu.product'].search(
            [('backend_id', '=', backend.id), ('woo_id', '=', res['data']['ride_id'])])
          if major_unit_id:
            mu=major_unit_id.major_unit_id
          else:

            major_unit = self.env['major_unit.major_unit']
            major_unit.single_importer(backend, res['data']['ride_id'])
            major_unit_id = self.env['wordpress.odoo.majorunit'].search(
              [('backend_id', '=', backend.id), ('woo_id', '=', res['data']['ride_id'])])
            mu=major_unit_id
        if mapper:
          importer.write_form(backend,mapper,res,partner,mu)
           
        else:
          res_partner = importer.create_form(backend,mapper,res,partner,mu)
        
        if mapper and (res['status'] == 200 or res['status'] == 201):
          vals = {
            'woo_id' : res['data']['ID'],
            'backend_id' : backend.id,
            'crm_lead_id' : mapper.crm_lead_id.id,
          }
          self.backend_mapping.write(vals)
        else:
            vals = {
              'woo_id' : res['data']['ID'],
              'backend_id' : backend.id,
              'crm_lead_id' : res_partner.id,
            }
            self.backend_mapping.create(vals)

    @api.multi
    @job
    def export(self, backend):
        """ export and create or update backend mapper """
        if len(self.ids)>1:
            for obj in self:
                obj.with_delay().export(backend)
            return
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('crm_lead_id', '=', self.id)], limit=1)
        method = 'crm_lead_status'
        arguments = [mapper.woo_id or None, self]
        export = WpCrmLeadExport(backend)
        res = export.export_crm_lead(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            mapper.write(
                {'crm_lead_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['ID']})


class SalesOrderMapping(models.Model):

    """ Model to store woocommerce id for particular Sale Order"""
    _name = 'wordpress.odoo.crm.lead'

    crm_lead_id = fields.Many2one(comodel_name='crm.lead',
                               string='Crm Lead',
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
