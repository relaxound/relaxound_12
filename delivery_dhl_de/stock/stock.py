# -*- coding: utf-8 -*-

from odoo import models,fields,api

class stock_picking(models.Model):
    _inherit = "stock.picking"
    
    ignore_warnings=fields.Boolean('Warnings Checked')
    
    @api.multi
    def open_return_website(self):
        self.ensure_one()

        client_action = {'type': 'ir.actions.act_url',
                         'name': "DHL Return Page",
                         'target': 'new',
                         'url': 'https://amsel.dpwn.net/abholportal/gw/lp/portal/zwitscherbox/customer/RpOrder.action?delivery=RetourenLager01'
                         }
        return client_action
