# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import fields as fields2
import operator as py_operator
OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}

class CustomSaleOrder(models.Model):
    _inherit = 'sale.order'

    new_overdue = fields.Monetary(compute='_partner_id_overdue',string='Total Overdue',search='_total_overdue_search',store=True)

    @api.multi
    @api.depends('partner_id')
    def _partner_id_overdue(self):
        for rec in self:
            if rec.partner_id:
                rec.new_overdue = rec.partner_id.total_overdue

    def _total_overdue_search(self,operator, value):
        ids = []
        OPERATORS = {
            '<': py_operator.lt,
            '>': py_operator.gt,
            '<=': py_operator.le,
            '>=': py_operator.ge,
            '=': py_operator.eq,
            '!=': py_operator.ne
        }

        for order in self.with_context(prefetch_fields=False).search([]):
            if OPERATORS[operator](order['new_overdue'], value):
                ids.append(order.id)
        return [('id', 'in', ids)]

    # _columns = {
    #     'new_overdue': fields2.Monetary(compute='_partner_id_overdue', multi='new_overdue',string='Total Overdue',fnct_search='_total_overdue_search')
    # }

    # Change total receivable code column logic
    # new_credit = fields.Monetary(compute='_partner_id_credit', string='Total Receivable', readonly=False)
    #
    # @api.depends('partner_id')
    # def _partner_id_credit(self):
    #     for rec in self:
    #         if rec.partner_id:
    #             rec.new_credit = rec.partner_id.credit

