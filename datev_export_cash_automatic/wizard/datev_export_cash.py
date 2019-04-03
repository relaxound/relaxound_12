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

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import time
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


def save_file_to_disc(self, file, file_name='noname.txt', path='/'):
    if not file:
        return False
    with open('%s/%s' % (path, file_name), 'w') as zip:
        zip.write(base64.b64decode(file))
        zip.close

    return True


class DatevExportOptions(models.TransientModel):
    _inherit = "datev.export.options.cash"

    @api.multi
    def do_export_file(self):
        res = super(DatevExportOptions, self).do_export_file()
        path = self.env['ir.config_parameter'].get_param('datev_export_cash_file_location')
        try:
            save_file_to_disc(self, self.datev_file, self.datev_filename, path)
        except Exception as e:
            if self.env.user.company_id.must_save_cash_file_to_disk:
                raise ValidationError(_(str(e)))
            else:
                return res
        return res

    @api.model
    def do_export_cash_file_cron(self):

        logging.info('DATEV Export Cash Registers crone Started!')

        journals = self.env['account.journal'].search([('auto_export_to_datev', '=', True)])

        for journal in journals:

            logging.info('DATEV Export Cash Registers crone for Journal: %s!' % journal.name)
            wizard = self.env['datev.export.options.cash'].create({
                'date_start': time.strftime("%Y-%m-%d"), 'date_stop': time.strftime("%Y-%m-%d"), 'journal_id': journal.id
            })

            wizard.date_start = wizard.company_id and wizard.company_id.last_successfull_datev_export_cash or '2000-01-01'

            if datetime.strptime(wizard.date_start, '%Y-%m-%d').month != datetime.strptime(wizard.date_stop, '%Y-%m-%d').month:
                wizard.date_start = datetime.strptime(wizard.date_stop, '%Y-%m-%d').replace(day=1).strftime('%Y-%m-%d')

            res = wizard.do_export_file()

            wizard.company_id.last_successfull_datev_export_cash = wizard.date_stop

            logging.info('DATEV Export Cash Registers crone Finished for Journal: %s! Response message: \n%s' % (journal.name, wizard.response_message))

            path = self.env['ir.config_parameter'].get_param('datev_export_cash_file_location')
            save_file_to_disc(self, base64.b64encode(wizard.response_message), '%s%s' % (wizard.datev_filename, '.log'), path)

        logging.info('DATEV Export Cash Registers crone Finished!')
        return True


class DatevExport(models.TransientModel):
    _inherit = "datev.export.cash"

    @api.multi
    def do_export_file(self):
        res = super(DatevExport, self).do_export_file()
        path = self.env['ir.config_parameter'].get_param('datev_export_cash_file_location')
        try:
            save_file_to_disc(self, self.file, self.filename, path)
        except Exception as e:
            if self.env.user.company_id.must_save_cash_file_to_disk:
                raise ValidationError(_(str(e)))
            else:
                return res
        return res



