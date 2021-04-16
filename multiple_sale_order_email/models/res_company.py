
from odoo import  api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    sale_order_is_snailmail = fields.Boolean(string='Send by Letter by default', default=False)
    sale_order_is_email = fields.Boolean('Email by default', default=True)
    sale_order_is_print = fields.Boolean('Print by default', default=False)

