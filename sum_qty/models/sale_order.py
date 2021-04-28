# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

#Trial statement
# trial second
#trial three
class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Sale Order Is Sent"

    is_dispatched = fields.Boolean('Dispatched')

    @api.multi
    def modify_is_dispatched(self):
        for sale in self:
            sale.is_dispatched = False if (sale.is_dispatched == True) else True

    @api.multi
    def mass_modify_is_dispatched(self, sale_ids):
        for sale in self.search([('id', 'in', sale_ids)]):
            sale.is_dispatched = False if (sale.is_dispatched == True) else True
