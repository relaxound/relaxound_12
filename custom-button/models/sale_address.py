# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPicking(models.TransientModel):
    _inherit = "res.config.settings"

    group_sale_delivery_address = fields.Boolean("Customer Addresses", implied_group='point_of_sale.group_delivery_invoice_address')


