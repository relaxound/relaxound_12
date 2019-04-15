from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from ..unit.service_order_exporter import ServiceOrderExport
from ..unit.service_order_importer import ServiceOrderImport
from ..model.customer import Customer
from odoo.addons.queue_job.job import job


class ServiceRides(models.Model):

    """ Models for woocommerce product category """
    _inherit = 'service.repair_order'

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
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.service.repair_order',
                                      string='Majorunit mapping',
                                      inverse_name='service_rides_id',
                                      readonly=False,
                                      required=False,
                                      )

    @api.multi
    def sync_service_rides(self):
        for backend in self.backend_id:
            self.export(backend)
        return

    @api.multi
    @job
    def importer(self, backend):
        """ import and create or update backend mapper """
        if len(self.ids) > 1:
            for obj in self:
                obj.with_delay().single_importer(backend)
            return

        method = 'my_services'
        arguments = [None, self]
        importer = ServiceOrderImport(backend)
        res = importer.import_service_rides(method, arguments)

        if (res['status'] == 200 or res['status'] == 201):
            if isinstance(res['data']['my_services'], list):
                for service_id in res['data']['my_services']:
                    self.with_delay().single_importer(backend, service_id)
    @api.multi
    @job
    def single_importer(self, backend, service_id, woo_id=None):
        method = 'my_services'

        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('woo_id', '=', service_id)], limit=1)
        arguments = [service_id or None, mapper.service_rides_id or self]

        importer = ServiceOrderImport(backend)
        res = importer.import_service_rides(method, arguments)
        partner_id = self.env['wordpress.odoo.res.partner'].search(
            [('backend_id', '=', backend.id), ('woo_id', '=', res['data']['service_details']['so_customer_id'])])
        if partner_id:
          pass
        else:
          partner = self.env['res.partner']
          partner.single_importer(backend, res['data']['service_details']['so_customer_id'],False)
          partner_id = self.env['wordpress.odoo.res.partner'].search(
            [('backend_id', '=', backend.id), ('woo_id', '=', res['data']['service_details']['so_customer_id'])])

        major_unit = self.env['wordpress.odoo.majorunit'].search(
            [('backend_id','=',backend.id),('woo_id','=',res['data']['service_details']['so_rides_id'])])
        if major_unit:
          pass
        else:
          majorunit_id = self.env['major_unit.major_unit']
          majorunit_id.single_importer(backend,res['data']['service_details']['so_rides_id'])
          major_unit = self.env['wordpress.odoo.majorunit'].search(
            [('backend_id','=',backend.id),('woo_id','=',res['data']['service_details']['so_rides_id'])])

        if mapper:
            importer.write_service_rides(backend, mapper, res, partner_id, major_unit)
        else:
            service_rides_id = importer.create_service_rides(
                backend, mapper, res, partner_id, major_unit)

        if mapper and (res['status'] == 200 or res['status'] == 201):
            vals = {
                'woo_id': res['data']['service_details']['so_service_id'],
                'backend_id': backend.id,
                'service_rides_id': mapper.service_rides_id.id,
            }
            self.backend_mapping.write(vals)
        elif service_rides_id:
            vals = {
                'woo_id': res['data']['service_details']['so_service_id'],
                'backend_id': backend.id,
                'service_rides_id': service_rides_id.id,
            }
            self.backend_mapping.create(vals)

    @api.multi
    @job
    def export(self, backend):
        """ export customer details, save username and create or update backend mapper """
        if len(self.ids) > 1:

            for obj in self:
                obj.export(backend)
            return
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('service_rides_id', '=', self.id)])
        method = 'my_services'
        arguments = [mapper.woo_id or None, self]
        export = ServiceOrderExport(backend)
        res = export.export_service_order(method, arguments)
        if mapper and (res['status'] == 200 or res['status'] == 201):
            self.write({'username': res['data'][
                       'service_details']['so_customer_id']})
            mapper.write(
                {'service_rides_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['service_details']['so_service_id']})
        elif (res['status'] == 200 or res['status'] == 201):
            self.write({'username': res['data'][
                       'service_details']['so_customer_id']})
            self.backend_mapping.create(
                {'service_rides_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['service_details']['so_service_id']})


class ServiceRidesMapping(models.Model):

    """ Model to store woocommerce id for particular product category"""
    _name = 'wordpress.odoo.service.repair_order'

    service_rides_id = fields.Many2one(comodel_name='service.repair_order',
                                       string='Service Order',
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
