
from odoo import models, fields, api, _


class Limal(models.Model):
    _inherit = 'sale.order'


    @api.onchange('partner_id')
    def onchange_warehouse(self):
        pro=self.env['stock.warehouse'].search([])
        for item in pro:
            if item.name == 'LIMAL':
                self.update({'warehouse_id':item})

