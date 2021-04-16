# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_order_is_print = fields.Boolean(string='Print',related='company_id.sale_order_is_print', readonly=False)
    sale_order_is_email = fields.Boolean(string='Send Email',related='company_id.sale_order_is_email', default=True, readonly=False)
    sale_order_is_snailmail = fields.Boolean(string='Send by Post',related='company_id.sale_order_is_snailmail',  readonly=False)


