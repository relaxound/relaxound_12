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

from odoo import models, fields, exceptions, api, _
from odoo.exceptions import UserError, ValidationError


class AccountBankingMandate(models.Model):
    ''' The banking mandate is attached to a bank account and represents an
        authorization that the bank account owner gives to a company for a
        specific operation (such as direct debit)
    '''
    _name = 'account.banking.mandate'
    _description = "A generic banking mandate"
    _rec_name = 'unique_mandate_reference'
    _inherit = ['mail.thread']
    _order = 'signature_date desc'
    # _track = {
    #     'state': {
    #         'account_banking_mandate.mandate_valid': (
    #             lambda self, cr, uid, obj, ctx=None: obj['state'] == 'valid'),
    #         'account_banking_mandate.mandate_expired': (
    #             lambda self, cr, uid, obj, ctx=None:
    #             obj['state'] == 'expired'),
    #         'account_banking_mandate.mandate_cancel': (
    #             lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel'),
    #     },
    # }

    def _get_states(self):
        return [('draft', 'Draft'),
                ('valid', 'Valid'),
                ('expired', 'Expired'),
                ('cancel', 'Cancelled')]

    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank', string='Bank Account',
        track_visibility='onchange')
    partner_id = fields.Many2one(
        comodel_name='res.partner', related='partner_bank_id.partner_id',
        string='Partner', store=True)
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'account.banking.mandate'))
    unique_mandate_reference = fields.Char(
        string='Unique Mandate Reference', track_visibility='always',
        default='/')
    signature_date = fields.Date(string='Date of Signature of the Mandate',
                                 track_visibility='onchange')
    scan = fields.Binary(string='Scan of the Mandate')
    last_debit_date = fields.Date(string='Date of the Last Debit',
                                  readonly=True)
    type = fields.Char('Type')
    scheme = fields.Selection(
        [('B2B', 'B2B'),
         ('other', 'other')], string='Scheme', default='B2B')
    state = fields.Selection(
        _get_states, string='Status', default='draft',
        help="Only valid mandates can be used in a payment line. A cancelled "
             "mandate is a mandate that has been cancelled by the customer.")
    # payment_line_ids = fields.One2many(
    #     comodel_name='payment.line', inverse_name='mandate_id',
    #     string="Related Payment Lines")

    # def _get_default_partner_bank_id_domain(self):
    #     if 'default_partner_id' in self.env.context:
    #         return [('partner_id', '=', self.env.context.get(
    #             'default_partner_id'))]
    #     else:
    #         return []

    # format = fields.Selection(
    #     [('basic', 'Basic Mandate')], default='basic', required=True,
    #     string='Mandate Format', track_visibility='onchange')
    # type = fields.Selection(
    #     [('generic', 'Generic Mandate')],
    #     string='Type of Mandate',
    #     track_visibility='onchange'
    # )
    # partner_bank_id = fields.Many2one(
    #     comodel_name='res.partner.bank', string='Bank Account',
    #     track_visibility='onchange',
    #     domain=lambda self: self._get_default_partner_bank_id_domain(),)
    # partner_id = fields.Many2one(
    #     comodel_name='res.partner', related='partner_bank_id.partner_id',
    #     string='Partner', store=True)
    # company_id = fields.Many2one(
    #     comodel_name='res.company', string='Company', required=True,
    #     default=lambda self: self.env['res.company']._company_default_get(
    #         'account.banking.mandate'))
    # unique_mandate_reference = fields.Char(
    #     string='Unique Mandate Reference', track_visibility='onchange',
    #     copy=False,
    # )
    # signature_date = fields.Date(string='Date of Signature of the Mandate',
    #                              track_visibility='onchange')
    # scan = fields.Binary(string='Scan of the Mandate')
    # last_debit_date = fields.Date(string='Date of the Last Debit',
    #                               readonly=True)
    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('valid', 'Valid'),
    #     ('expired', 'Expired'),
    #     ('cancel', 'Cancelled'),
    #     ], string='Status', default='draft', track_visibility='onchange',
    #     help="Only valid mandates can be used in a payment line. A cancelled "
    #     "mandate is a mandate that has been cancelled by the customer.")
    # # payment_line_ids = fields.One2many(
    #     comodel_name='account.payment.line', inverse_name='mandate_id',
    #     string="Related Payment Lines")


    _sql_constraints = [(
        'mandate_ref_company_uniq',
        'unique(unique_mandate_reference, company_id)',
        'A Mandate with the same reference already exists for this company !')]

    # @api.one
    # @api.constrains('signature_date', 'last_debit_date')
    # def _check_dates(self):
    #     # import pdb;pdb.set_trace()
    #     for mandate in self:
    #         if (mandate.signature_date and
    #                 mandate.signature_date > fields.Date.context_today(
    #                     mandate)):
    #             raise ValidationError(
    #                 _("The date of signature of mandate '%s' "
    #                   "is in the future!")
    #                 % mandate.unique_mandate_reference)
    #         if (mandate.signature_date and mandate.last_debit_date and
    #                 mandate.signature_date > mandate.last_debit_date):
    #             raise ValidationError(
    #                 _("The mandate '%s' can't have a date of last debit "
    #                   "before the date of signature."
    #                   ) % mandate.unique_mandate_reference)

    # @api.one
    # @api.constrains('state', 'partner_bank_id', 'signature_date')
    # def _check_valid_state(self):
    #     # import pdb;pdb.set_trace()
    #     for mandate in self:
    #         if mandate.state == 'valid':
    #             if not mandate.signature_date:
    #                 raise ValidationError(
    #                     _("Cannot validate the mandate '%s' without a date of "
    #                       "signature.") % mandate.unique_mandate_reference)
    #             if not mandate.partner_bank_id:
    #                 raise ValidationError(
    #                     _("Cannot validate the mandate '%s' because it is not "
    #                       "attached to a bank account.") %
    #                     mandate.unique_mandate_reference)

    # @api.model
    # def create(self, vals=None):
    #     # import pdb;pdb.set_trace()
    #     if vals.get('unique_mandate_reference', '/') == '/':
    #         vals['unique_mandate_reference'] = \
    #             self.env['ir.sequence'].next_by_code('account.banking.mandate') or '/'
    #     return super(AccountBankingMandate, self).create(vals)
    
    # @api.onchange('partner_bank_id')
    # def mandate_partner_bank_change(self):
    #     # import pdb;pdb.set_trace()
    #     self.partner_id = self.partner_bank_id.partner_id

    # @api.multi
    # def validate(self):
    #     # import pdb;pdb.set_trace()
    #     for mandate in self:
    #         if mandate.state != 'draft':
    #             raise UserError(
    #                 _('Mandate should be in draft state.'))
    #     self.write({'state': 'valid'})
    #     return True

    # @api.multi
    # def cancel(self):
    #     # import pdb;pdb.set_trace()
    #     for mandate in self:
    #         if mandate.state not in ('draft', 'valid'):
    #             raise UserError(
    #                 _('Mandate should be in draft or valid state.'))
    #     self.write({'state': 'cancel'})
    #     return True

    # @api.multi
    # def back2draft(self):
    #     # import pdb;pdb.set_trace()
    #     """Allows to set the mandate back to the draft state.
    #     This is for mandates cancelled by mistake.
    #     """
    #     for mandate in self:
    #         if mandate.state != 'cancel':
    #             raise UserError(
    #                 _('Mandate should be in cancel state.'))
    #     self.write({'state': 'draft'})
    #     return True