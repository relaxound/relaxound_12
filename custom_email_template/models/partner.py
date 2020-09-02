# -*- coding: utf-8 -*-
# Copyright 2016-TODAY Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_quotation_send(self):
        if self.partner_id.agent_name == 'Rossmanek':
            emailcc = 'info@agentur-rossmanek.de'

        elif self.partner_id.agent_name == 'Pforte':
            emailcc = 'gunther.pforte@t-online.de'

        elif self.partner_id.agent_name == 'Senft':
            emailcc = 'info@cs-handelsagentur.de'

        elif self.partner_id.agent_name == 'Wirtz':
            emailcc = 'agenturwirtz@t-online.de'

        elif self.partner_id.agent_name == 'Kuhnle':
            emailcc = 's.kuhnle@t-online.de'

        elif self.partner_id.agent_name == 'Werner':
            emailcc = 'werner@buch-raum.de'

        elif self.partner_id.agent_name == 'DEsignLICIOUS':
            emailcc = 'mirjam@designlicious.nl'

        elif self.partner_id.agent_name == 'The Living Connection':
            emailcc = 'anne@thelivingconnection.com'

        elif self.partner_id.agent_name == 'Handelsagentur Schur GbR':
            emailcc = 'info@ha-schur.com'


        else:
            emailcc = ''

        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        # try:
        #     if self.partner_id.agent_name:
        #         template_id = ir_model_data.get_object_reference('custom_email_template', 'email_template_sample_test11')[1]
        #     else:
        #         template_id = ir_model_data.get_object_reference('custom_email_template', 'email_template_sample_test11')[1]
        # except ValueError:
        #     template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False

        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            # 'default_use_template': bool(template_id),
            # 'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'email_cc': emailcc,
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


