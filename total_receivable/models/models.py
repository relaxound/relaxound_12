# -*- coding: utf-8 -*-

from openerp import models, fields, api


class CustomSaleOrder(models.Model):
    _inherit = 'sale.order'

    new_overdue = fields.Float(compute='_partner_id_overdue', string='Total Overdue',store=True,readonly=False)

    @api.depends('partner_id')
    def _partner_id_overdue(self):
        for rec in self:
            if rec.partner_id:
                rec.new_overdue = rec.partner_id.total_overdue

    # Change total receivable code column logic
    # new_credit = fields.Monetary(compute='_partner_id_credit', string='Total Receivable', readonly=False)
    #
    # @api.depends('partner_id')
    # def _partner_id_credit(self):
    #     for rec in self:
    #         if rec.partner_id:
    #             rec.new_credit = rec.partner_id.credit

