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

                else:
                    self.update({'journal_id':'Tax Invoices'})



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

