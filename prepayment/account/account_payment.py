# -*- coding: utf-8 -*-

from odoo import models,api

class account_payment(models.Model):
    _inherit='account.payment'

    @api.multi
    def post(self):
        res=super(account_payment,self).post()

        for inv in self.invoice_ids:
            print('inv.state')
            if inv.state!='paid':
                continue            
            #sales= self.env['sale.order'].search([('invoice_ids','in',inv.ids)])
            #sales= self.env['sale.order'].search([('invoice_ids','=',[inv.id])])
            sales= self.env['sale.order'].search([])
            for sa in sales:
                if inv in sa.invoice_ids:                    
                    for picking in sa.picking_ids:
                        print ('picking.state')
                        if picking.state=='to_pay':
                            picking.action_payed()    
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:        