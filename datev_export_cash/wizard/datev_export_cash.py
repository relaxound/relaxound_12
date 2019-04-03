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

import time
from datetime import datetime
from xml.dom import minidom
import re
import zipfile
# import StringIO
import base64
import logging
from lxml import etree
from odoo import tools
from odoo.tools import float_compare
from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


def _reopen(self, res_id, model, view_id=None):
    if not view_id:
        view_id = 'datev_export_cash.datev_export_cash_view'

    return {'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': res_id,
            'res_model': self._name,
            'view_id': self.env.ref(view_id).id,
            'target': 'new',
            'context': {
                'default_model': model,
            },
    }


class DatevExportOptionsCash(models.TransientModel):
    _name = "datev.export.options.cash"
    _description = "Export to XML Datev format using options"

    @api.model
    def _get_period(self):
        ids = self.env['account.period'].find()
        if len(ids):
            return ids[0]
        return False

    date_start = fields.Date(string='From Date', help="Ignored if Period is selected", required=True)
    date_stop = fields.Date(string='To Date', help="Ignored if Period is selected", required=True)
    company_id = fields.Many2one('res.company', string='Company', required = True, default=lambda self: self.env['res.users'].browse(self._uid).company_id.id)
    datev_file = fields.Binary(string='.zip File', readonly = True)
    datev_filename = fields.Char(string='Filename', size=64, readonly=True, default=lambda *a: 'xml.zip')
    state = fields.Selection([('choose','choose'),('get','get')], string='State', default=lambda *a: 'choose')
    journal_id = fields.Many2one('account.journal', string="Journal", required=True)
    response_message = fields.Text(string='Response Message', readonly=True)

    def act_destroy(self, *args):
        return {'type':'ir.actions.act_window_close' }

    @api.multi
    def do_export_file(self):
        self.ensure_one()
        logging.getLogger('DATEV EXPORT').warn("Begin of export with options"+str(self._context))
        if self._context is None:
            context = {}
        wizard = self
        company_id = wizard.company_id.id
        acc_bank_s_obj = self.env['account.bank.statement']
        if wizard.date_start:
            if wizard.date_stop:
                if datetime.strptime(wizard.date_start,'%Y-%m-%d').month != datetime.strptime(wizard.date_stop,'%Y-%m-%d').month:
                    raise ValidationError(_("'From Date' and 'To Date' must be in same month for Cash Registers to be exported!"))
                acc_bank_s_ids = acc_bank_s_obj.search([('date','>=',wizard.date_start),('date','<=',wizard.date_stop),('company_id','=',company_id),('journal_id','=',wizard.journal_id.id)])
            else:
                acc_bank_s_ids = acc_bank_s_obj.search([('date','>=',wizard.date_start),('company_id','=',company_id)])
        else:
            raise ValidationError(_('Please select at least Start Date'))
        logging.getLogger('DATEV EXPORT').warn("Cash Registers "+str(acc_bank_s_ids._ids))
        zip_file, res_msg = self.env['datev.export.cash'].generate_zip(acc_bank_s_ids._ids)
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
        return _reopen(self, record.id, 'datev.export.options.cash', view_id='datev_export_cash.view_datev_export_options_cash')

class DatevExportCash(models.TransientModel):
    _name = "datev.export.cash"
    _description = "Export to XML Datev format"

    file = fields.Binary(string='.zip File', readonly = True)
    filename = fields.Char(string='Filename', size=64, readonly=True)
    state = fields.Selection([('choose','choose'),('get','get')], string='State', default='choose')
    response_message = fields.Text(string='Response Message', readonly=True)

    @api.model
    def toprettyxml_fixed(self, input_string):
        fix = re.compile(r'((?<=>)(\n[\t]*)(?=[^<\t]))|(?<=[^>\t])(\n[\t]*)(?=<)')
        return re.sub(fix, '', input_string)

    @api.model
    def createTextElement(self, doc, parent_element, element, text):
        text_element = doc.createElement(element)
        parent_element.appendChild(text_element)
        text_node = doc.createTextNode(text)
        text_element.appendChild(text_node)
        return True

    @api.model
    def include_doc_header(self, doc, company):
        archive = doc.createElement("archive")
        doc.appendChild(archive)
        archive.setAttribute("version", "3.0")
        archive.setAttribute("generatingSystem", "OpenERP")
        archive.setAttribute("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        archive.setAttribute("xsi:schemaLocation", "http://xml.datev.de/bedi/tps/document/v03.0 Document_v030.xsd")
        archive.setAttribute("xmlns", "http://xml.datev.de/bedi/tps/document/v03.0")
        header = doc.createElement("header")
        archive.appendChild(header)
        self.createTextElement(doc, header, "date", time.strftime('%Y-%m-%dT%H:%M:%S'))
        self.createTextElement(doc, header, "description", company.name + " Accounting")
        if company.consultant_number:
            self.createTextElement(doc, header, "consultantNumber", company.consultant_number)
        if company.consultant_number:
            self.createTextElement(doc, header, "clientNumber", company.client_number)
        self.createTextElement(doc, header, "clientName", company.name)
        return archive

    @api.model
    def get_invoices_from_memo(self, line):
        if not line:
            return False
        # TODO: search by Igor case if not found than this
        invoices = self.env['account.invoice'].search([('number', '=', line.name)])
        precision = self.env['decimal.precision'].precision_get('Account')
        return invoices.filtered(lambda x: float_compare(abs(x.amount_total), abs(line.amount), precision_digits=precision or 2) == 0)

    @api.model
    def get_is_memo_invoice(self, line):
        invoices = self.get_invoices_from_memo(line)
        if invoices:
            return True
        return False

    @api.model
    def get_account_no(self, line):

        accs_no = []
        account_moves_with_partner = self.env['account.move'].search([('statement_line_id', '=', line.id)]).filtered(lambda x: x.partner_id.commercial_partner_id)
        for move in account_moves_with_partner:

            if line.amount < 0.0 and move.partner_id.commercial_partner_id.property_account_payable_id and move.partner_id.commercial_partner_id.property_account_payable_id.code and not move.partner_id.commercial_partner_id.property_account_payable_id.code in accs_no:
                accs_no.append(self.line_account_code(move.partner_id.commercial_partner_id.property_account_payable_id.code))

            if line.amount >= 0.0 and move.partner_id.commercial_partner_id.property_account_receivable_id and move.partner_id.commercial_partner_id.property_account_receivable_id.code and not move.partner_id.commercial_partner_id.property_account_receivable_id.code in accs_no:
                accs_no.append(self.line_account_code(move.partner_id.commercial_partner_id.property_account_receivable_id.code))

        return accs_no

    @api.model
    def line_account_code(self, code):
        res_code = code and code.lstrip('0') or ''
        return res_code

    @api.model
    def get_booking_text(self, line):
        res = []
        if not line.partner_id or not line.partner_id.commercial_partner_id:
            return '/'

        if line.ref:
            res.append(line.ref)

        if line.partner_id.commercial_partner_id.is_company:
            res.append(line.partner_id.commercial_partner_id.name)
        else:
            res.append('%s %s' % (line.partner_id.commercial_partner_id.firstname, line.partner_id.commercial_partner_id.lastname))

        return ' - '.join(res) or '/'

    @api.model
    def get_bu_code(self, line):
        if not line.bu_code_b or line.bu_code_b == '0':
            return False
        bu_code = "%s%s" % (line.bu_code_b, line.bu_code_u or '0')
        return bu_code

    @api.model
    def include_bank_statement(self, bank_statement):
        acc_bank_s = minidom.Document()
        ledger_import_el = acc_bank_s.createElement("LedgerImport")
        acc_bank_s.appendChild(ledger_import_el)

        ledger_import_el.setAttribute("generator_info", bank_statement.company_id.name)
        ledger_import_el.setAttribute("generating_system", "OpenERP")
        # ledger_import_el.setAttribute("description", "DATEV Import cash registers")
        ledger_import_el.setAttribute("version", "3.0")
        ledger_import_el.setAttribute("xml_data", "Kopie nur zur Verbuchung berechtigt nicht zum Vorsteuerabzug") # new in v3
        ledger_import_el.setAttribute("xsi:schemaLocation","http://xml.datev.de/bedi/tps/invoice/v030 Belegverwaltung_online_ledger_import_v010.xsd")
        ledger_import_el.setAttribute("xmlns","http://xml.datev.de/bedi/tps/invoice/v030")
        ledger_import_el.setAttribute("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance")

        for line in bank_statement.line_ids:
            cash_ledger_el = acc_bank_s.createElement("cashLedger")
            ledger_import_el.appendChild(cash_ledger_el)

            # if line.date:
            self.createTextElement(acc_bank_s, cash_ledger_el, "date", line.date or '/')

            # if line.amount:
            self.createTextElement(acc_bank_s, cash_ledger_el, "amount", "%.2f" % line.amount or '/')

            accs_no = self.get_account_no(line)

            if accs_no and len(accs_no) > 0:
                self.createTextElement(acc_bank_s, cash_ledger_el, "accountNo", accs_no and ','.join(accs_no) or '')

            if self.get_bu_code(line):
                self.createTextElement(acc_bank_s, cash_ledger_el, "buCode", self.get_bu_code(line) or '00')

            # if line.journal_currency_id and line.journal_currency_id.name:
            self.createTextElement(acc_bank_s, cash_ledger_el, "currencyCode", line.journal_currency_id.name or '/')

            if self.get_is_memo_invoice(line):
                self.createTextElement(acc_bank_s, cash_ledger_el, "invoiceId", line.name.replace(' ','')[:12] or '/')

            # if line.ref:
            self.createTextElement(acc_bank_s, cash_ledger_el, "bookingText", self.get_booking_text(line)) #line.ref or '/'

        acc_bank_s_xml= acc_bank_s.toprettyxml(indent="\t", newl="\n", encoding = "utf-8")
        self.check_xml_file(acc_bank_s_xml, doc_name = bank_statement.name)
        return self.toprettyxml_fixed(acc_bank_s_xml)

    @api.model
    def generate_zip(self, acc_bank_s_ids = []):
        if self._context is None:
            context = {}

        logging.getLogger('DATEV EXPORT').warn("Beginning of generate_zip"+str(self._context))
        acc_bank_s_obj = self.env['account.bank.statement']
        if acc_bank_s_ids:
            active_ids = acc_bank_s_ids
        else:
            active_ids = self._context and self._context.get('active_ids', []) or []
        active_ids = acc_bank_s_obj.search([('id','in',active_ids),('state','in',['confirm']),('exported_to_datev', '=', False)], order='id')
        if len(active_ids) == 0:
            raise ValidationError(_("Only Cash Registers in 'Validated' state and not exported Cash Registers can be exported! There is "))
        bank_statements = active_ids

        company = bank_statements[0].company_id

        # s=StringIO.StringIO()
        # zip = zipfile.ZipFile(s, 'w')

        doc = minidom.Document()
        archive = self.include_doc_header(doc, company)
        content = doc.createElement("content")
        archive.appendChild(content)

        not_exported = []
        response_message = _('Bank Statements successfully exported! \n')
        for bank_statement in bank_statements:
            acc_bank_s_name = bank_statement.name.replace('/','')
            if not bank_statement.line_ids:
                res_msg = _("Bank Statemen %s have been skipped because there are no lines!") % bank_statement.name
                response_message = '%s \n %s' % (response_message, res_msg)
                not_exported.append(bank_statement.id)
                continue
            inv_xml = self.include_bank_statement(bank_statement)
            self.add_to_zip(acc_bank_s_name+".xml", inv_xml, zip)

            document = doc.createElement("document")
            content.appendChild(document)

            
            self.createTextElement(doc, document, "description", bank_statement.name)

            self.createTextElement(doc, document, "keywords", bank_statement.name)
            extension = doc.createElement("extension")
            document.appendChild(extension)
            extension.setAttribute("datafile",acc_bank_s_name+".xml")
            extension.setAttribute("xsi:type","cashLedger")
            property = doc.createElement("property")
            extension.appendChild(property)
            property.setAttribute("key","1")
            property.setAttribute("value", '%s-%s' % (datetime.strptime(bank_statement.date,'%Y-%m-%d').year,'{:02d}'.format(datetime.strptime(bank_statement.date,'%Y-%m-%d').month)))
            property = doc.createElement("property")
            extension.appendChild(property)
            property.setAttribute("key","2")
            property.setAttribute("value", bank_statement.journal_id and bank_statement.journal_id.default_debit_account_id and bank_statement.journal_id.default_debit_account_id.code)

        doc_xml= doc.toprettyxml(indent="\t", newl="\n", encoding = "utf-8")
        doc_xml= self.toprettyxml_fixed(doc_xml)
        self.check_xml_file(doc_xml, doc_name = "Document.xml", doc = True)
        self.add_to_zip("document.xml", doc_xml, zip)

        zip.close()
        zip_file = base64.encodestring(s.getvalue())
        s.close()
        for bank_statement in bank_statements:
            if bank_statement.id not in not_exported:
                bank_statements.write({'exported_to_datev': True})
        logging.getLogger('DATEV EXPORT').warn("End of generat_zip"+str(self._context))
        return zip_file, response_message

    @api.model
    def add_to_zip(self, name, data, zip):
        info = zipfile.ZipInfo(name, date_time=time.localtime(time.time()))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 2175008768
        if not data:
            data = ''
        zip.writestr(info, data)
        return True

    @api.multi
    def do_export_file(self):
        self.ensure_one()
        acc_bank_s_ids = self._context['active_ids']
        zip_file, res_msg = self.env['datev.export.cash'].generate_zip(acc_bank_s_ids)
        ret= {
            'company_id': self.env.user.company_id.id,
            'file': zip_file,
            'filename': time.strftime('%Y_%m_%d_%H_%M')+'_xml.zip',
            'state': 'get',
            'response_message': res_msg
            }
        res = self.write(ret)

        return _reopen(self, self.id, 'datev.export.cash', view_id='datev_export_cash.datev_export_cash_view')
        
    @api.model
    def get_attachment(self, invoice):
        attachment_obj = self.env['ir.attachment']
        attachment_id = attachment_obj.search([('res_model','=','account.bank.statement'),('res_id','=',invoice.id),('type','=','binary')])
        # if len(attachment_id):
        for attachment in attachment_id:
            result = base64.decodestring(attachment_id.datas)
            return (True, attachment_id.datas_fname, result)
        return (False, False, "No file")

    @api.model
    def check_xml_file(self, xml_file, doc_name, doc = False):
    # TODO take the xsd from url online
        if doc:
            f_schema = tools.file_open('Document_v030.xsd',subdir='addons/datev_export_cash/xsd_files')
        else:
            f_schema = tools.file_open('Belegverwaltung_online_ledger_import_v010.xsd',subdir='addons/datev_export_cash/xsd_files')
        schema_doc = etree.parse(f_schema)
        schema = etree.XMLSchema(schema_doc)
        parser = etree.XMLParser(schema = schema)
        try:
            doc = etree.fromstring(xml_file, parser)
        except etree.XMLSyntaxError as e:
            raise ValidationError(_("Try to solve the problem with '%s' according to message below:\n\n") % doc_name + str(e))
        return True
