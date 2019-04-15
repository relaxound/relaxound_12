
from odoo import models, fields, api, _



class MuProductMapping(models.Model):

    """ Model to store woocommerce id for particular product attribute """
    _name = 'wordpress.odoo.mu.product'

    major_unit_id = fields.Many2one(comodel_name='major_unit.major_unit',
                                   string='Major unit',
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