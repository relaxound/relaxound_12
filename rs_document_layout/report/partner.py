# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class InvoiceJournal(models.Model):
    _inherit = 'sale.order'

    order_by = fields.Many2one('res.partner', string="Order By")
    order_date = fields.Date(string='Order Date')

    @api.multi
    def _prepare_invoice(self):
        res=super(InvoiceJournal,self)._prepare_invoice()
        res.update({'order_date':self.order_date,
            'order_by':self.order_by.id
            })
        return res



    
