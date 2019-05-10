# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class InvoiceJournal(models.Model):
    _inherit = 'sale.order'

    order_by = fields.Many2one('res.partner', string="Order By")
    order_date = fields.Date(string='Order Date')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')

    @api.depends('order_line.price_total')
    def _amount_all(self):
        
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            if order.partner_id.vat and 'EU' in order.partner_id.property_account_position_id.name:
                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': 0.0,
                    'amount_total': amount_untaxed,
                })
            else:
                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': amount_tax,
                    'amount_total': amount_untaxed + amount_tax,
                })

    @api.multi
    def _prepare_invoice(self):
        res=super(InvoiceJournal,self)._prepare_invoice()
        res.update({'order_date':self.order_date,
            'order_by':self.order_by.id,
            'amount_tax':self.amount_tax
            })
        return res



    
