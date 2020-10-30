from odoo import models, fields, api


class Wizard(models.TransientModel):
    _name = 'sale.wizard'
    _description = "Set Tags wizard"

    tag_ids = fields.Many2many('crm.lead.tag',string='Set Tags')

    @api.multi
    def Add(self):
        active_ids = self._context.get('active_ids')
        orders = self.env['sale.order'].browse(active_ids)

        for order in orders:
            order.tag_ids = self.tag_ids

class ContactWizard(models.TransientModel):
    _name = 'partner.wizard'
    _description = "Set Tags wizard for contacts"

    category_id = fields.Many2many('res.partner.category',string='Set Tags')

    @api.multi
    def Add(self):

        active_ids = self._context.get('active_ids')
        contacts = self.env['res.partner'].browse(active_ids)

        for cont in contacts:
            cont.category_id = self.category_id
