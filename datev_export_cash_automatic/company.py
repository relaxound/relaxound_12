# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Openfellas (http://openfellas.com) All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract support@openfellas.com
#
##############################################################################

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    last_successfull_datev_export_cash = fields.Date(string='Last export Cash Registers Date', help="Date of last sucessfully autmatically exported for DATEV Cash Registers.")
    must_save_cash_file_to_disk = fields.Boolean('Must save Cash Register files on disk')
