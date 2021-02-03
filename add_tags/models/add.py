from odoo import models,api,fields

class AddTags(models.Model):
    _inherit = 'sale.order'

    category_id_sale = fields.Many2many(related='partner_id.category_id',string="Tags")

    # category_id_sale = fields.Many2many('res.partner.category',string="Tags", compute='_add_tags')

    # @api.multi
    # @api.depends('partner_id')
    # def _add_tags(self):
    #     for rec in self:
    #         if rec.partner_id.category_id:
    #             list_tag_ids = []
    #             for tag_ids in rec.partner_id.category_id:
    #                 list_tag_ids.append(tag_ids.id)
    #
    #         # By using char field
    #         # rec.category_id_sale = ','.join([x.name for x in list_tag_ids])
    #
    #         rec.category_id_sale = [(6, 0, list_tag_ids)]
    #
