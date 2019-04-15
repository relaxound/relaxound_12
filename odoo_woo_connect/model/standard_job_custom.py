from odoo import api, fields, models

import odoo.addons.decimal_precision as dp

class StandardJobPartCustom(models.Model):
    _inherit = 'service.standard_job.product'

    product_id = fields.Many2one(
        'product.product', 'Part/Labor', required=True, domain=[('details_model', 'in', ['product.template.details', 'labor'])])

class RepairOrderJobPartCustom(models.Model):
    _inherit = 'service.repair_order.product'

    product_id = fields.Many2one(
        'product.product', 'Parts/Labor', required=True, domain=[('details_model', 'in', ['product.template.details', 'labor'])])

class ServiceSuggestedJobLinesCustom(models.TransientModel):
    _inherit = "confirm.suggested.job.line"

    product_id = fields.Many2one('product.product',
                                 'Parts/Labor',
                                 required=True,
                                 domain=[('details_model', 'in', ['product.template.details', 'labor'])])

class StandardJobPartCustom(models.Model):
    _inherit = 'service.suggested.standard_job'

    product_id = fields.Many2one('product.product',
                                 'Parts/Labor',
                                 required=True,
                                 domain=[
                                     ('details_model', 'in', ['product.template.details', 'labor'])],
                                 states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]})

class RepairOrderJobPartCustom(models.Model):
    _inherit = 'service.repair_order.product'

    product_id = fields.Many2one(
        'product.product', 'Parts/Labor', required=True, domain=[('details_model', 'in', ['product.template.details', 'labor'])])