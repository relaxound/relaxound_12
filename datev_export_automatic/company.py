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

from odoo import models, fields,api, _


class ResCompany(models.Model):
    _inherit = "res.company"
    _description ="ResCompany"

    last_successfull_datev_export_in = fields.Date(string='Last export Date of Incoming Invoices/Refunds', help="Date of last sucessfully autmatically exported for DATEV Invoice/Refunds.")
    last_successfull_datev_export_out = fields.Date(string='Last export Date of Outgoing Invoices/Refunds', help="Date of last sucessfully autmatically exported for DATEV Invoice/Refunds.")
    must_save_file_to_disk = fields.Boolean('Must save files on disk')
