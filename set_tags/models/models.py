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
        res_partners = self.env['res.partner'].browse(active_ids)

        for res in res_partners:
            if res.category_id:
                old_list = []
                for old_category in res.category_id:
                    old_list.append(old_category.id)
            if self.category_id:
                new_list = []
                for new_category in self.category_id:
                    new_list.append(new_category.id)

            if not res.category_id:
                old_list = []

            final_lst = old_list + new_list

            res.category_id = [(6, 0, final_lst)]

