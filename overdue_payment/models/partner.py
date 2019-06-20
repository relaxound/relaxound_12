# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _, exceptions, tools
from datetime import datetime, date


class ResPartner(models.Model):
    # _name = 'overdue'
    _inherit = 'res.partner'

    over_credit = fields.Boolean('Allow Over Credit?')
    customer_credit = fields.Float("Customer Credit",compute='_compute_customer_credit', readonly=True)
    # total_receivable = fields.Float(string='Total Receivable', readonly=True)
    customer_moves = fields.One2many('account.move.line', compute="_compute_customer_credit", string='Moves', readonly=True)
    customer_invoices = fields.One2many('account.invoice', compute="_compute_customer_invoice", string='invoice', readonly=True)
    property_payment_term_id = fields.Many2one('account.payment.term', company_dependent=True,string='Customer Payment Terms',help="This payment term will be used instead of the default one for sales orders and customer invoices", oldname="property_payment_term")
    property_supplier_payment_term_id = fields.Many2one('account.payment.term', company_dependent=True,string='Vendor Payment Terms',help="This payment term will be used instead of the default one for purchase orders and vendor bills", oldname="property_supplier_payment_term")
    property_account_position_id = fields.Many2one('account.fiscal.position', company_dependent=True,string="Fiscal Position",help="The fiscal position determines the taxes/accounts used for this contact.", oldname="property_account_position")
    # new_credit = fields.Monetary(string='Total Receivable', readonly=False)
    debit = fields.Monetary(compute='_credit_debit_get',string='Total Payable',help="Total amount you have to pay to this vendor.")
    credit = fields.Monetary(compute='_credit_debit_get',string='Total Receivable', help="Total amount this customer owes you.")
    @api.multi
    def _compute_customer_credit(self):
        receivable = self.env.ref('account.data_account_type_receivable').id
        payable = self.env.ref('account.data_account_type_payable').id
        for partner in self:
            moveline_obj = self.env['account.move.line']
            movelines = moveline_obj.search(
                [('partner_id', '=', partner.id),
                 ('account_id.user_type_id', 'in', [receivable, payable]),
                 ('full_reconcile_id', '=', False)]
            )
            debit, credit = 0.0, 0.0
            for line in movelines:
                    credit += line.debit
                    debit += line.credit
            partner.customer_credit = (credit - debit)
            partner.customer_moves = movelines

    @api.multi
    def _compute_customer_invoice(self):
        for partner in self:
            accountinvoice_obj = self.env['account.invoice']
            invoicelines = accountinvoice_obj.search(
                [('partner_id', '=', partner.id),
                 ('state', 'in', ['open']),
                 ('date_due', '<=', date.today())]
            )
            partner.customer_invoices = invoicelines

    @api.multi
    def action_overdue_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('overdue_payment.email_template_edi_overdue2', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='res.partner',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            custom_layout="overdue_payment.mail_notification_paynow_ex",
            default_composition_mode='comment',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def action_due_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('overdue_payment.email_template_edi_due116', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx =dict(
            default_model='res.partner',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            # mark_so_as_sent= True,
            custom_layout="overdue_payment.mail_notification_paynow_ex",
            # force_email= True
            )


        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def _send_overdue_mass_mails(self):
        partners = self.env['res.partner'].search([('name', '=', '7Mind GmbH')])
        # partners = self.env['res.partner'].search([(1, '=', 1)])
        for partner in partners:
            if partner.customer_invoices:
                template = self.env.ref('overdue_payment.email_template_edi_overdue', False)
                if template:
                    template.send_mail(partner.id, force_send=True)




class CustomAccount(models.Model):
    _inherit = 'account.banking.mandate'

    new_credit1 = fields.Float(compute='_partner_id_credit1',string='Total Receivable', readonly=False)

    @api.depends('partner_id')
    def _partner_id_credit1(self):
        for rec in self:
            if rec.partner_id:
                rec.new_credit1 = rec.partner_id.credit


