from odoo import models, fields, api


class Wizard(models.TransientModel):
    _name = 'editfilter.wizard'
    _description = "Edit Filter"

    name = fields.Char(string='Filter Name')
    user_id = fields.Many2one('res.users', string='User', ondelete='cascade')