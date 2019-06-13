# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', oldname='payment_term')

    @api.onchange('partner_id')
    def payment_term(self):
        import pdb;pdb.set_trace()
        res=self.env['account.payment.term'].search([])
        for item in res:
            if item.name=='14 days after receipt of invoice':
                self.update({'payment_term_id':item.id})


    @api.multi
    def _prepare_invoice(self):
        res=super(SaleOrder,self)._prepare_invoice()
        res.update({'payment_term_id':self.payment_term_id.id})
        

        return res



