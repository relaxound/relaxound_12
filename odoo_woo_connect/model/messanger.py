from odoo import api, fields, models
from odoo.addons.queue_job.job import job
import odoo.addons.decimal_precision as dp
from ..unit.service_messanger_exporter import WpServiceMessangerExport


class ServiceMessanger(models.Model):

    """ Models for woocommerce product category """
    _inherit = 'service.messanger'

    woo_id = fields.Char(string='woo_id')
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
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.messanger',
                                      string='Service Messanger mapping',
                                      inverse_name='messanger_id',
                                      readonly=False,
                                      required=False,
                                      )

    @api.multi
    def sync_service_messanger(self):
        for backend in self.backend_id:
            self.export(backend)
        return

    @api.multi
    @job
    def export(self, backend):
        """ export customer details, save username and create or update backend mapper """
        if len(self.ids) > 1:
            for obj in self:
                obj.export(backend)
            return
        mapper = self.backend_mapping.search(
            [('backend_id', '=', backend.id), ('messanger_id', '=', self.id)])
        method = 'alerts_msgs'
        arguments = [mapper.woo_id or None, self]
        export = WpServiceMessangerExport(backend)
        res = export.export_service_messanger(method, arguments)

        ##############################################################
        if mapper and (res['status'] == 200 or res['status'] == 201):
            # self.write({'username': res['data']['messanger_id']})
            mapper.write(
                {'messanger_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['Id']})
        elif (res['status'] == 200 or res['status'] == 201):
            # self.write({'username': res['data']['customer_id']})
            self.backend_mapping.create(
                {'messanger_id': self.id, 'backend_id': backend.id, 'woo_id': res['data']['Id']})


class ServiceMessangerMapping(models.Model):

    """ Model to store woocommerce id for particular product category"""
    _name = 'wordpress.odoo.messanger'

    messanger_id = fields.Many2one(comodel_name='service.messanger',
                                   string='Service Messanger',
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
