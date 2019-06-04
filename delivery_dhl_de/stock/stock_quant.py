# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    sale_price_total = fields.Monetary(compute='_compute_sale_price_total', help='unit price of one product')
    currency_id = fields.Many2one('res.currency', compute='_compute_sale_price_total')


    @api.one
    def _compute_sale_price_total(self):
        stock_move = self.env['stock.move'].search(
            [('quant_ids', '=', self.id), ('picking_id', '!=', False), ('group_id', '!=', False)])
        for move in stock_move:
            if move and move.procurement_id and move.procurement_id.sale_line_id:

                line = move.procurement_id.sale_line_id
                self.currency_id = line.currency_id

                if line:
                    self.sale_price_total = line.price_total / line.product_uom_qty
                    return
        self.sale_price_total = self.product_id.list_price
