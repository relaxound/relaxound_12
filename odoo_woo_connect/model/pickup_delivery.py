from odoo import api, fields, models
import odoo.addons.decimal_precision as dp
from odoo.addons.queue_job.job import job


class PickupRides(models.Model):

    """ Models for woocommerce product category """
    _inherit = 'drm.pickup'
    

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
    backend_mapping = fields.One2many(comodel_name='wordpress.odoo.service.pickup',
                                      string='Majorunit mapping',
                                      inverse_name='pickup_id',
                                      readonly=False,
                                      required=False,
                                      )


class PickupRidesMapping(models.Model):

    """ Model to store woocommerce id for particular product category"""
    _name = 'wordpress.odoo.service.pickup'

    pickup_id = fields.Many2one(comodel_name='drm.pickup',
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
