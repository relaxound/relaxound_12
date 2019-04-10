# -*- coding: utf-8 -*-

from odoo import models, api


class ReportPaperformat(models.Model):
    _inherit = "report.paperformat"

    @api.model
    def set_default_paperformat(self):
        # Ränder für die Berichte setzen
        for pf in self.search([('name', '=ilike', 'European A4')]):
            pf.write(
                {'margin_top': 50, 'margin_left': 5, 'margin_bottom': 25, 'margin_right': 5, 'header_spacing': 40})

            # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
