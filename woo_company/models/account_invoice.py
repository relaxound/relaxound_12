# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models,fields,api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    woo_company_name_ept = fields.Char(string='Company Name', related='partner_id.woo_company_name_ept')

