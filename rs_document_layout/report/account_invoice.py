# -*- coding: utf-8 -*-

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # @api.model
    # def _get_shipping_address(self):
    #     # shipping = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id), ('type', '=', 'delivery')])
    #     shipping = self.env['stock.picking'].search([('origin', '=', self.origin), ('state', '!=', 'cancel')])
    #     if shipping:
    #         return shipping[0].partner_id.street + ', ' + shipping[0].partner_id.city + ', ' + shipping[
    #             0].partner_id.country_id.name
    #     return False

    def _get_shipping_address(self):
        shipping = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id), ('type', '=', 'delivery')])
        so_shipping = self.env['stock.picking'].search([('origin', '=', self.origin), ('state', '!=', 'cancel')])
        if self.origin:
          if so_shipping:
            return so_shipping[0].partner_id.street + ', ' + so_shipping[0].partner_id.city + ', ' + so_shipping[0].partner_id.country_id.name
        else:
          if shipping:
            return shipping[0].street + ', ' + shipping[0].city + ', ' + shipping[0].country_id.name
        return False

