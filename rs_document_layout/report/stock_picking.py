# -*- coding: utf-8 -*-

from odoo import models, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _get_invoicing_address(self):
        if not self.partner_id.parent_id:
            invoicing = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id), ('type', '=', 'invoice'), ('email', '!=', False)])
        else:
            invoicing = self.env['res.partner'].search(
                [('parent_id', '=', self.partner_id.parent_id.id), ('type', '=', 'invoice'), ('email', '!=', False)])
        # shipping = self.env['stock.picking'].search([('origin', '=', self.origin)])
        email = False
        if invoicing:
            return invoicing[0].email
        if self.partner_id.email:
            return self.partner_id.email
        return False
        # if shipping:
        #     return str(shipping[0].partner_id.street) + ', ' + str(shipping[0].partner_id.city) + ', ' + str(shipping[0].partner_id.country_id.name)
        # return False

