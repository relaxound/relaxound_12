# -*- coding: utf-8 -*-

from odoo import models, api, fields


class sale_order(models.Model):
    _inherit = "sale.order"

    shipping_cost = fields.Monetary(compute='_compute_shipping_cost')

    @api.one
    def _compute_shipping_cost(self):
        """
        calculate shipping cost with VAT
        :return:
        """
        shipping_cost = 0.00
        for line in self.order_line:
            if line.is_delivery:
                shipping_cost += line.price_total
        self.shipping_cost = shipping_cost

    @api.multi
    def open_return_website(self):
        self.ensure_one()

        client_action = {'type': 'ir.actions.act_url',
                         'name': "DHL Return Page",
                         'target': 'new',
                         'url': 'https://amsel.dpwn.net/abholportal/gw/lp/portal/zwitscherbox/customer/RpOrder.action?delivery=RetourenLager01'
                         }
        return client_action
