from odoo import models,api,fields

class AddTags(models.Model):
    _inherit = 'sale.order'

    category_id_sale = fields.Many2many('crm.lead.tag', 'sale_order_tag_rel', 'order_id', 'tag_id', string='Tags')

    # @api.multi
    # @api.depends('partner_id')
    # def _add_tags(self):
    #     list_tag_ids = []
    #
    #     for rec in self:
    #         if rec.tag_ids:
    #             for tag_idss in rec.tag_ids:
    #                 list_tag_ids.append(tag_idss.id)
    #
    #         # By using char field
    #         # rec.category_id_sale = ','.join([x.name for x in list_tag_ids])
    #
    #         rec.category_id_sale = [(6, 0, list_tag_ids)]









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



# class CustomProductTemplate(models.Model):
#     _inherit = "product.template"

#     @api.model_create_multi
#     def create(self, vals_list):

#         list_invoice_id = ['59965']
#         for rec in list_invoice_id:
#             obj= self.env['sale.order'].search([('name','=',rec)])
#             obj._compute_amount()
#             print(obj)
#         return super(CustomProductTemplate, self).create(vals_list)

