# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning


class purchase_popup(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id', 'company_id')
    @api.multi
    def onchange_partner_id_warning(self):
        warning = {}
        result = super(purchase_popup, self).onchange_partner_id_warning()
        if self.partner_id and self.state == 'draft':
            self.env['sale.order'].search(
                [('partner_id', '=', self.partner_id.id)])
            draft = self.env['sale.order'].search(
                [('partner_id', '=', self.partner_id.id), ('state', '=', 'draft')])
            unpaid = self.env['account.invoice'].search(
                [('partner_id', '=', self.partner_id.id), ('state', '!=', 'paid')])
            pending_order = len(draft)
            unpaid_invoice = len(unpaid)

            return {'warning': {
                'title': _("Pending Order Detail"),
                'message': "Retailer %s have %s pending orders and %s unpaid orders" % (
                    self.partner_id.name, pending_order, unpaid_invoice)
            }
            }
        return result

    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('purchase_popup', 'email_template_edi_sale_custom')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }