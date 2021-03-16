from odoo import models,api,fields

class AddTags(models.Model):
    _inherit = 'sale.order'

    # category_id_sale = fields.Many2many('crm.lead.tag', related='tag_ids', string="Tags")

    category_id_sale = fields.Many2many('crm.lead.tag',string="Tags",readonly=True,compute='_add_tags')

    @api.multi
    def _add_tags(self):
        list_tag_ids = []
        for rec in self:
            if rec.tag_ids:
                for tag_idss in rec.tag_ids:
                    list_tag_ids.append(tag_idss.id)

            # By using char field
            # rec.category_id_sale = ','.join([x.name for x in list_tag_ids])

            rec.category_id_sale = [(6, 0, list_tag_ids)]

