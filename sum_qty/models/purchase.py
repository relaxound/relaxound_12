# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class Purchase1(models.Model):
    _inherit = "purchase.order"
    _description = "Purchase Sum Qty"

    qty_delivered = fields.Integer("Total Qty", compute='_get_delivered_qty')

    # @api.multi
    # def sum_qty(self):
    #     qty = 0
    #     for order in self:
    #         for line in order.order_line:
    #             if line.product_id.type != 'service':
    #                 qty = qty + line.quantity
    #     return int(qty)

    # @api.multi
    # def _get_delivered_qty(self):
    #     for order in self:
    #         qty = order.sum_qty()
    #         order.qty_delivered = qty