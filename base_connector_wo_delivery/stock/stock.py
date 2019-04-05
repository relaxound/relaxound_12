# -*- coding: utf-8 -*-

from odoo import models,fields

class StockPicking(models.Model):
    _inherit='stock.picking'
    
    tracking_send=fields.Boolean('Tracking send')
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: