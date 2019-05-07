from odoo import models, fields, api, _


class OrderLine(models.Model):
    _inherit = 'account.invoice.line'

    single_unit=fields.Integer(string="Single Unit",)