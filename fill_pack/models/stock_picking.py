# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _description = "Stock picking"

    sale_description = fields.Text(related='sale_id.note', string='Note', readonly=True)

    @api.multi
    def fill_pack(self):
        for operation in self.move_ids_without_package:
            operation.quantity_done = operation.product_uom_qty