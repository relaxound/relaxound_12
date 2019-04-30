# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Sale Order Retailers"

    is_retailer = fields.Boolean(string='Retailer', related='partner_id.is_retailer', store=True)


