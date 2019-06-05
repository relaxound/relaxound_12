# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

# from odoo import models, fields, api, _


# class sale_invoice_fun(models.Model):
#     _inherit = 'account.invoice'

#     @api.onchange('partner_id')
#     def action_set_journal(self):
#         res=self.env['res.partner'].search([])
#         pro1=self.env['account.journal'].search([])
#         if self.partner_id.customer and self.partner_id.is_retailer:
#             for item in pro1:
#                 if item.name=='Retailer Invoices':
#                     self.update({'journal_id':item.id})

#         elif self.partner_id.customer:
#             for item in pro1:
#                 if item.name=='Customer Invoices':
#                     self.update({'journal_id':item.id})

#         else:
#             for item in pro1:
#                 if item.name=='Export Invoices':
#                     self.update({'journal_id':item.id})


