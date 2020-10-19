from odoo import models, fields, api


class Wizard(models.TransientModel):
    _name = 'sale.wizard'
    _description = "Set Tags wizard"

    tag_ids = fields.Many2one('crm.lead.tag',string='Set Tags')

    @api.multi
    def Add(self):
        active_ids = self._context.get('active_ids')
        orders = self.env['sale.order'].browse(active_ids)
        for order in orders:
            order.tag_ids = self.tag_ids
