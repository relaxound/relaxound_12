# -*- coding: utf-8 -*-

from odoo import models, api, fields

class InvoiceJournalField(models.Model):
    _inherit = 'account.invoice'


    journal_id = fields.Many2one('account.journal', string="Journal", required=True)
    @api.onchange('partner_id')
    def onchange_partner(self):
        pro=self.env['res.partner'].search([])
        pro1=self.env['account.journal'].search([])
        for item in pro:
            if item==self.partner_id:
                if item.customer and not item.is_retailer:
                    for temp in pro1:
                        if temp.name=='Export Invoices':
                            self.update({'journal_id':temp.id})


                elif item.customer and item.is_retailer:
                    for temp in pro1:
                        if temp.name=='Retail Invoices':
                            self.update({'journal_id':temp.id})

                # else:
                #     if temp.name=='Vendor Bills':
                #         self.update({'journal_id':temp.id})



class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _get_shipping_address(self):
        shipping = self.env['res.partner'].search([('parent_id', '=', self.partner_id.id), ('type', '=', 'delivery')])
        so_shipping = self.env['stock.picking'].search([('origin', '=', self.origin), ('state', '!=', 'cancel')])
        if self.origin:
            if so_shipping:
                return so_shipping[0].partner_id.street + ', ' + so_shipping[0].partner_id.city + ', ' + so_shipping[0].partner_id.country_id.name
        else:
            if shipping:
                return shipping[0].street + ', ' + shipping[0].city + ', ' + shipping[0].country_id.name
        return False

class ReportInvoiceWithPayment(models.AbstractModel):
    _inherit = 'report.account.report_invoice_with_payments'

    @api.model
    def _get_report_values(self, docids, data=None):
        del_chrg = 0
        untx_amt = 0
        invoice = self.env['account.invoice'].browse(docids[0])
        inv_lines = self.env['account.invoice.line'].search([('invoice_id','=',invoice.id)])
        
        for line in inv_lines:
            
            try:
                del_prod = self.env['delivery.carrier'].search([('product_id','=',line.product_id.id)])
                if del_prod:
                    del_chrg = line.price_subtotal
                    untx_amt = invoice.amount_untaxed - del_chrg
                    break
            
            except AssertionError:
                continue
            
        return {
            'd_chrg': del_chrg,
            'utx_amt': untx_amt,
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': self.env['account.invoice'].browse(docids),
            'report_type': data.get('report_type') if data else '',
        }


class ReportJournal(models.AbstractModel):
    _name = 'report.account.report_invoice'
    _description = 'Report Invoice Without Payment'


    @api.model
    def _get_report_values(self, docids, data=None):
        del_chrg = 0
        untx_amt = 0
        invoice = self.env['account.invoice'].browse(docids[0])
        inv_lines = self.env['account.invoice.line'].search([('invoice_id','=',invoice.id)])
        
        for line in inv_lines:
            
            try:
                del_prod = self.env['delivery.carrier'].search([('product_id','=',line.product_id.id)])
                if del_prod:
                    del_chrg = line.price_subtotal
                    untx_amt = invoice.amount_untaxed - del_chrg
                    break
            
            except AssertionError:
                continue
            
        return {
            'd_chrg': del_chrg,
            'utx_amt': untx_amt,
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': self.env['account.invoice'].browse(docids),
            'report_type': data.get('report_type') if data else '',
        }