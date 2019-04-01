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

# from odoo.tools import config

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
# import base64
# import time
import logging
_logger = logging.getLogger(__name__)


def save_file_to_disc(self, file, file_name='noname.txt', path='/'):
    # config.filestore(self._cr.dbname)
    if not file:
        return False
    with open('%s/%s' % (path, file_name), 'w') as zip:
        zip.write(base64.b64decode(file))
        zip.close

    return True


class DatevExportOptionsautomate(models.TransientModel):

    _name = "datev.export.options.automate"
    _description = "Export to XML Datev format using automated options"
    # _inherit = "datev.export.options"

    @api.model
    def do_export_file(self):
        self.ensure_one()
        logging.getLogger('DATEV EXPORT').warn("Begin of export with options"+str(self._context))
        if self._context is None:
            context = {}
        wizard = self
        company_id = wizard.company_id.id
        invoice_type_list = []
        if wizard.in_invoice:
            invoice_type_list.append('in_invoice')
        if wizard.out_invoice:
            invoice_type_list.append('out_invoice')
        if wizard.in_refund:
            invoice_type_list.append('in_refund')
        if wizard.out_refund:
            invoice_type_list.append('out_refund')
        if not len(invoice_type_list):
            raise ValidationError(_('Please check at least one invoice type to export'))
        inv_obj = self.env['account.invoice']
        if wizard.date_start:
            if wizard.date_stop:
                invoice_ids = inv_obj.search([('date_invoice','>=',wizard.date_start),('date_invoice','<=',wizard.date_stop),('type','in',invoice_type_list),('company_id','=',company_id)])
            else:
                invoice_ids = inv_obj.search([('date_invoice','>=',wizard.date_start),('type','in',invoice_type_list),('company_id','=',company_id)])
        else:
            raise ValidationError(_('Please select at least Start Date'))
        logging.getLogger('DATEV EXPORT').warn("Invoices "+str(invoice_ids._ids))
        zip_file, res_msg = self.env['datev.export'].generate_zip(invoice_ids._ids)
        ret= {
            'company_id': self.env['res.users'].browse(self._uid).company_id.id,
            'datev_file': zip_file,
            'datev_filename': time.strftime('%Y_%m_%d_%H_%M')+'_xml.zip',
            'state': 'get',
            'response_message': res_msg,
            }

        res = self.write(ret)
        logging.getLogger('DATEV EXPORT').warn("End of export with options"+str(self._context)+" IDS: "+str(self._ids)+ " RES: "+str(res))
        record = self.browse(self._ids[0])
        return _reopen(self, record.id, 'datev.export.options', view_id='datev_export.view_datev_export_options')

        # res = super(DatevExportOptions, self).do_export_file()
        path = self.env['ir.config_parameter'].get_param('datev_export_file_location')
        try:
            save_file_to_disc(self, self.datev_file, self.datev_filename, path)
        except Exception as e:
            if self.env.user.company_id.must_save_file_to_disk:
                raise ValidationError(_(str(e)))
            

    @api.model
    def do_export_file_cron(self, out_invoice=False, out_refund=False, in_invoice=False, in_refund=False):

        logging.info('DATEV Export Invoices crone Started!')
        wizard = self.env['datev.export.options'].create({})
        if not (out_invoice or out_refund or in_invoice or in_refund):
            logging.getLogger('DATEV EXPORT CRONE').warn("No invoice type selected!")
            return False

        wizard.out_invoice = out_invoice
        wizard.out_refund = out_refund
        wizard.in_invoice = in_invoice
        wizard.in_refund = in_refund

        last_date = time.strftime("%Y-%m-%d")
        if (out_invoice or out_refund) and ((wizard.company_id and wizard.company_id.last_successfull_datev_export_out or time.strftime("%Y-%m-%d")) < last_date):
            last_date = wizard.company_id and wizard.company_id.last_successfull_datev_export_out or time.strftime("%Y-%m-%d")

        if (in_invoice or in_refund) and ((wizard.company_id and wizard.company_id.last_successfull_datev_export_in or time.strftime("%Y-%m-%d")) < last_date):
            last_date = wizard.company_id and wizard.company_id.last_successfull_datev_export_in or time.strftime("%Y-%m-%d")

        wizard.date_start = last_date
        wizard.date_stop = time.strftime("%Y-%m-%d")

        res = wizard.do_export_file()

        if (out_invoice or out_refund):
            wizard.company_id.last_successfull_datev_export_out = wizard.date_stop

        if (in_invoice or in_refund):
            wizard.company_id.last_successfull_datev_export_in = wizard.date_stop

        logging.info('DATEV Export Invoices crone Finished! Response message: \n%s' % wizard.response_message)

        path = self.env['ir.config_parameter'].get_param('datev_export_file_location')
        save_file_to_disc(self, base64.b64encode(wizard.response_message), '%s%s' % (wizard.datev_filename, '.log'), path)

        return True


class DatevExportautomate(models.TransientModel):
    _name = "datev.export.automate"

    @api.model
    def do_export_file(self):
        self.ensure_one()
        logging.getLogger('DATEV EXPORT').warn("Begin of export with options"+str(self._context))
        if self._context is None:
            context = {}
        wizard = self
        company_id = wizard.company_id.id
        invoice_type_list = []
        if wizard.in_invoice:
            invoice_type_list.append('in_invoice')
        if wizard.out_invoice:
            invoice_type_list.append('out_invoice')
        if wizard.in_refund:
            invoice_type_list.append('in_refund')
        if wizard.out_refund:
            invoice_type_list.append('out_refund')
        if not len(invoice_type_list):
            raise ValidationError(_('Please check at least one invoice type to export'))
        inv_obj = self.env['account.invoice']
        if wizard.date_start:
            if wizard.date_stop:
                invoice_ids = inv_obj.search([('date_invoice','>=',wizard.date_start),('date_invoice','<=',wizard.date_stop),('type','in',invoice_type_list),('company_id','=',company_id)])
            else:
                invoice_ids = inv_obj.search([('date_invoice','>=',wizard.date_start),('type','in',invoice_type_list),('company_id','=',company_id)])
        else:
            raise ValidationError(_('Please select at least Start Date'))
        logging.getLogger('DATEV EXPORT').warn("Invoices "+str(invoice_ids._ids))
        zip_file, res_msg = self.env['datev.export'].generate_zip(invoice_ids._ids)
        ret= {
            'company_id': self.env['res.users'].browse(self._uid).company_id.id,
            'datev_file': zip_file,
            'datev_filename': time.strftime('%Y_%m_%d_%H_%M')+'_xml.zip',
            'state': 'get',
            'response_message': res_msg,
            }

        res = self.write(ret)
        logging.getLogger('DATEV EXPORT').warn("End of export with options"+str(self._context)+" IDS: "+str(self._ids)+ " RES: "+str(res))
        record = self.browse(self._ids[0])
        return _reopen(self, record.id, 'datev.export.options', view_id='datev_export.view_datev_export_options')






        # res = super(DatevExport, self).do_export_file()
        path = self.env['ir.config_parameter'].get_param('datev_export_file_location')
        try:
            save_file_to_disc(self, self.file, self.filename, path)
        except Exception as e:
            if self.env.user.company_id.must_save_file_to_disk:
                raise ValidationError(_(str(e)))
            

